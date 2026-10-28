package main

import (
	"context"
	"crypto/tls"
	"crypto/x509"
	"fmt"
	"log"
	"net"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/oklog/run"
	"google.golang.org/grpc"
	"google.golang.org/grpc/credentials"
	"google.golang.org/grpc/metadata"
	"google.golang.org/grpc/peer"
	"google.golang.org/grpc/status"

	"python_go_grpc/server/api"
)

func loggingInterceptor(ctx context.Context, req interface{}, info *grpc.UnaryServerInfo, handler grpc.UnaryHandler) (interface{}, error) {
	started := time.Now()
	remote, _ := peer.FromContext(ctx)
	md, _ := metadata.FromIncomingContext(ctx)

	response, err := handler(ctx, req)

	log.Printf("server=%q peer=%v method=%q status=%s duration=%s user-agent=%q",
		md.Get(":authority"), remote, info.FullMethod, status.Code(err),
		time.Since(started), md.Get("user-agent"))

	return response, err
}

func main() {
	serverCert, err := tls.LoadX509KeyPair("certs/server.pem", "certs/server-key.pem")
	if err != nil {
		log.Fatal(err)
	}

	caCert, err := os.ReadFile("certs/ca.pem")
	if err != nil {
		log.Fatal(err)
	}

	caCertPool := x509.NewCertPool()
	if !caCertPool.AppendCertsFromPEM(caCert) {
		log.Fatal("failed to parse CA certificate")
	}

	creds := credentials.NewTLS(&tls.Config{
		Certificates: []tls.Certificate{serverCert},
		ClientCAs:    caCertPool,
		ClientAuth:   tls.RequireAndVerifyClientCert,
		MinVersion:   tls.VersionTLS12,
	})

	var group run.Group
	ctx, stop := signal.NotifyContext(context.Background(), syscall.SIGINT, syscall.SIGTERM)
	defer stop()

	group.Add(func() error {
		<-ctx.Done()
		return nil
	}, func(error) { stop() })

	for _, endpoint := range []struct {
		address string
		options []grpc.ServerOption
	}{
		{"127.0.0.1:8443", []grpc.ServerOption{grpc.Creds(creds)}},
		{"127.0.0.1:50051", nil},
	} {
		address := endpoint.address
		options := append(endpoint.options, grpc.UnaryInterceptor(loggingInterceptor))
		server := grpc.NewServer(options...)
		api.RegisterDiceServiceServer(server, api.NewServer())

		group.Add(func() error {
			listener, err := net.Listen("tcp", address)
			if err != nil {
				return fmt.Errorf("listen %s: %w", address, err)
			}

			log.Printf("Starting gRPC server, address=%q", address)
			return server.Serve(listener)
		}, func(error) { server.Stop() })
	}

	if err := group.Run(); err != nil {
		log.Fatal(err)
	}
}

# Практическая работа №4

Django-клиент вызывает DiceService напрямую по gRPC с mTLS (127.0.0.1:8443)
и через nginx с mTLS (127.0.0.1:9448). nginx передаёт запрос Go-серверу
по h2c (127.0.0.1:50051). Метод RollDie возвращает число от 1 до 6.

## Подготовка Ubuntu 24.04

```sh
sudo apt update
sudo apt install -y python3-venv golang nginx protobuf-compiler golang-cfssl
cd python_go_grpc
python3 -m venv venv
. venv/bin/activate
pip install -r requirements.txt
export PATH="$PATH:$(go env GOPATH)/bin"
go install google.golang.org/protobuf/cmd/protoc-gen-go@v1.36.5
go install google.golang.org/grpc/cmd/protoc-gen-go-grpc@v1.5.1
sh certs.sh
sh generate.sh
go mod tidy
python manage.py check
nginx -t -p "$PWD/" -c nginx.conf
```

## Запуск

Команды выполняются из python_go_grpc. Сервер, nginx и каждый клиент
запускаются в отдельных терминалах. Для Python активируйте venv.

```sh
go run server/server.go
nginx -p "$PWD/" -c nginx.conf
python manage.py runserver 127.0.0.1:8000
python manage.py runserver 127.0.0.1:8001
python manage.py runserver 127.0.0.1:8002
```

Откройте http://127.0.0.1:8000 и нажмите Roll it! Слева результат прямого
вызова, справа результат через nginx. Проверьте также клиентов на 8001 и 8002.
Пути /grpc и /nginx отдельно показывают результат соответствующего вызова.

Клиенты останавливаются Ctrl+C; Go-сервер — Ctrl+C; nginx — командой
`nginx -p "$PWD/" -c nginx.conf -s quit`.

В методичке согласованы следующие опечатки: единый порт nginx 9448,
относительный импорт api_pb2, полное имя Go-пакета, маршруты /grpc и /nginx,
передача порта Django позиционным аргументом вместо несуществующего -p.
Шаблон хранится в templates проекта, чтобы не изменять установленный Django.
В случайном генераторе Go добавлена блокировка для одновременных клиентов.
Сгенерированные сертификаты и приватные ключи остаются локально.

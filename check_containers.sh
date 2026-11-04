#!/usr/bin/env bash
set -e

echo "Запуск проверки конфигурации контейнеров..."

if [ ! -f .dockerignore ] || ! grep -q "^\.env" .dockerignore; then
    echo "Ошибка: .env не добавлен в .dockerignore"
    exit 1
fi

if grep -E "^FROM .*:latest" Dockerfile || grep -E "^FROM [^:]+$" Dockerfile; then
    echo "Ошибка: в Dockerfile используется latest или не указана версия образа"
    exit 1
fi

if grep -E "image:.*:latest" docker-compose.yml || grep -E "image:[[:space:]]*[^:]+$" docker-compose.yml; then
    echo "Ошибка: в docker-compose.yml используется latest или образ без тега версии"
    exit 1
fi

if ! grep -q "^USER " Dockerfile || grep -Eq "^USER (root|0)" Dockerfile; then
    echo "Ошибка: контейнер в Dockerfile должен запускаться не от root"
    exit 1
fi

if grep -Eq "user:[[:space:]]*['\"]?(root|0)" docker-compose.yml; then
    echo "Ошибка: в docker-compose.yml найден запуск от root"
    exit 1
fi

if grep -Eq "^(COPY|ADD).*\.env" Dockerfile || grep -Eqi "^ENV .*(PASSWORD|SECRET)" Dockerfile; then
    echo "Ошибка: обнаружена передача секретов или .env напрямую в Dockerfile"
    exit 1
fi

if grep -qi "disable:[[:space:]]*true" docker-compose.yml; then
    echo "Ошибка: отключение healthcheck запрещено"
    exit 1
fi

if ! grep -q "healthcheck:" docker-compose.yml; then
    echo "Ошибка: в docker-compose.yml не настроен healthcheck"
    exit 1
fi

if grep -Eq "(3306:3306|8000:8000)" docker-compose.yml; then
    echo "Ошибка: опубликован лишний порт (БД 3306 или прямой порт приложения 8000)!"
    exit 1
fi

if ! grep -q "limits:" docker-compose.yml || ! grep -q "memory:" docker-compose.yml; then
    echo "Ошибка: не заданы лимиты ресурсов (memory/cpus) в docker-compose.yml"
    exit 1
fi

echo "Все проверки container-check пройдены (OK)"


include .env
export

.PHONY: setup run test quality migrate backup restore verify format

PYTHON=./venv/bin/python
BACKUP_DIR=./backups
TIMESTAMP=$(shell date +"%Y%m%d_%H%M%S")

setup:
	bash setup.sh

run:
	$(PYTHON) manage.py runserver 0.0.0.0:8000


test:
	@if [ -f ./venv/bin/coverage ]; then \
		echo "=== Запуск тестов с покрытием ==="; \
		./venv/bin/coverage run manage.py test apps --settings=alpine_club.test_settings; \
		if [ $$? -ne 0 ]; then echo "ОШИБКА: Тесты упали (см. вывод выше)"; exit 1; fi; \
		echo "=== Проверка порога покрытия (40%) ==="; \
		./venv/bin/coverage report -m --fail-under=40; \
		if [ $$? -ne 0 ]; then echo "ОШИБКА: Покрытие ниже 40%"; exit 1; fi; \
		echo "=== Генерация HTML и XML отчетов ==="; \
		./venv/bin/coverage html -d coverage_html; \
		./venv/bin/coverage xml -o coverage.xml; \
	else \
		echo "=== Coverage не найден, запуск обычных тестов ==="; \
		$(PYTHON) manage.py test apps --settings=alpine_club.test_settings --verbosity=2; \
		if [ $$? -ne 0 ]; then echo "ОШИБКА: Тесты упали (см. вывод выше)"; exit 1; fi; \
	fi
	@echo "=== Тесты успешно пройдены ==="


quality:
	@if [ -f ./venv/bin/ruff ]; then \
		echo "=== Проверка форматирования (Ruff) ==="; \
		./venv/bin/ruff check .; \
		./venv/bin/ruff format --check .; \
		if [ $$? -ne 0 ]; then echo "ОШИБКА: Ruff нашел проблемы"; exit 1; fi; \
	else \
		echo "Ruff не найден в venv. Пропуск линтинга."; \
	fi
	@if [ -f ./venv/bin/bandit ]; then \
		echo "=== Статический анализ безопасности (Bandit) ==="; \
		./venv/bin/bandit -r . -ll -x ./venv,./migrations; \
		if [ $$? -ne 0 ]; then echo "ОШИБКА: Bandit нашел уязвимости"; exit 1; fi; \
	else \
		echo "Bandit не найден. Выполняется базовая проверка Django:"; \
		$(PYTHON) manage.py check --deploy; \
	fi
	@echo "=== Проверки качества пройдены ==="


format:
	@if [ -f ./venv/bin/ruff ]; then \
		./venv/bin/ruff check . --fix; \
		./venv/bin/ruff format .; \
	else \
		echo "Ruff не найден."; \
	fi

migrate:
	$(PYTHON) manage.py makemigrations
	$(PYTHON) manage.py migrate

backup:
	mkdir -p $(BACKUP_DIR)
	mysqldump --no-tablespaces --skip-lock-tables -h $(DB_HOST) -P $(DB_PORT) -u $(DB_USER) -p$(DB_PASSWORD) $(DB_NAME) > $(BACKUP_DIR)/alpine_club_$(TIMESTAMP).sql
	@echo "Резервная копия создана: $(BACKUP_DIR)/alpine_club_$(TIMESTAMP).sql"

restore:
	@if [ -z "$(FILE)" ]; then echo "Укажите файл: make restore FILE=backups/имя_файла.sql"; exit 1; fi
	mysql -h $(DB_HOST) -P $(DB_PORT) -u $(DB_USER) -p$(DB_PASSWORD) $(DB_NAME) < $(FILE)
	@echo "База данных восстановлена из $(FILE)"

verify:
	@echo "========================================"
	@echo "1. Проверка конфигурации Django"
	@echo "========================================"
	$(PYTHON) manage.py check
	@echo ""
	@echo "========================================"
	@echo "2. Проверка качества кода (Ruff + Bandit)"
	@echo "========================================"
	$(MAKE) quality
	@echo ""
	@echo "========================================"
	@echo "3. Запуск тестов и проверка покрытия"
	@echo "========================================"
	$(MAKE) test
	@echo ""
	@echo "=== Все проверки (make verify) успешно пройдены! ==="

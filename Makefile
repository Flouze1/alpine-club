-include .env
export

.PHONY: setup run test quality migrate backup restore verify container-check up down c-migrate c-backup c-restore

PYTHON=./venv/bin/python
BACKUP_DIR=./backups
TIMESTAMP=$(shell date +"%Y%m%d_%H%M%S")

setup:
	bash setup.sh

run:
	$(PYTHON) manage.py runserver 0.0.0.0:8000

test:
	@if [ -f ./venv/bin/coverage ]; then \
		./venv/bin/coverage run manage.py test apps.accounts --settings=alpine_club.test_settings && \
		./venv/bin/coverage report -m --fail-under=40; \
	else \
		$(PYTHON) manage.py test apps.accounts --settings=alpine_club.test_settings --verbosity=2; \
	fi

quality:
	@if [ -f ./venv/bin/flake8 ]; then ./venv/bin/flake8 . --max-line-length=120 --exclude=venv,migrations; else python3 -m py_compile manage.py alpine_club/*.py apps/accounts/*.py && echo "Синтаксический анализ (py_compile): OK"; fi
	@if [ -f ./venv/bin/bandit ]; then ./venv/bin/bandit -r . -ll -x ./venv; else $(PYTHON) manage.py check --deploy && echo "Проверка безопасности: OK"; fi

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
	$(PYTHON) manage.py check
	$(MAKE) quality
	$(MAKE) test
	@echo "=== Все проверки (make verify) успешно пройдены! ==="

container-check:
	bash check_containers.sh

up: container-check
	docker compose up -d --build

down:
	docker compose down

c-migrate: container-check
	docker compose exec app1 python manage.py migrate

c-backup:
	mkdir -p $(BACKUP_DIR)
	docker compose exec -T db mysqldump --no-tablespaces --skip-lock-tables -u $(DB_USER) -p$(DB_PASSWORD) $(DB_NAME) > $(BACKUP_DIR)/db_$(TIMESTAMP).sql
	@echo "Бэкап сохранен в $(BACKUP_DIR)/db_$(TIMESTAMP).sql"

c-restore:
	@if [ -z "$(FILE)" ]; then echo "Укажите файл: make c-restore FILE=backups/..."; exit 1; fi
	docker compose exec -T db mysql -u $(DB_USER) -p$(DB_PASSWORD) $(DB_NAME) < $(FILE)
	@echo "БД восстановлена из $(FILE)"


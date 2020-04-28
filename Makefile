DOCKER_COMPOSE_ENV_FILE=conf/docker-compose_dev.yml
DJANGO_SETTINGS_MODULE=project.settings

.PHONY: init
init: start_services export_settings
	@make broker_create
	@echo "Initiliazing application's data and state"
	./manage.py makemigrations
	./manage.py migrate
	./manage.py loaddata 000_site_dev
	./manage.py loaddata 001_admin
	@make services
	@echo "\nAddress: http://localhost:8000/admin"
	@echo "Credentials:\n  - user: admin\n  - pass: 123"

.PHONY: export_settings
export_settings:
	export DJANGO_SETTINGS_MODULE=$(DJANGO_SETTINGS_MODULE)

.PHONY: start_services
start_services:
	docker-compose -f $(DOCKER_COMPOSE_ENV_FILE) up -d

.PHONY: services
services:
	docker-compose -f $(DOCKER_COMPOSE_ENV_FILE) ps

.PHONY: stop
stop:
	docker-compose -f $(DOCKER_COMPOSE_ENV_FILE) stop

.PHONY: restart_ngrok
restart_ngrok:
	docker-compose -f $(DOCKER_COMPOSE_ENV_FILE) stop ngrok
	docker-compose -f $(DOCKER_COMPOSE_ENV_FILE) rm ngrok
	docker-compose -f $(DOCKER_COMPOSE_ENV_FILE) up -d
	docker-compose -f $(DOCKER_COMPOSE_ENV_FILE) logs -f ngrok

.PHONY: down
down:
	rm -f db.sqlite3
	docker-compose -f $(DOCKER_COMPOSE_ENV_FILE) down --remove-orphans

.PHONY: build
build:
	docker build -f conf/Dockerfile -t mercadopago_service .

.PHONY: broker_kill
broker_kill:
	ps x --no-header -o pid,cmd | awk '!/awk/&&/celery/{print $$1}' | xargs -r kill;


.PHONY: broker_create
broker_create: export_settings broker_kill
	celery -E $(CELERY_SERVICES) --loglevel=INFO --pidfile="/tmp/celery.pid" --detach;


.PHONY: broker_debug
broker_debug: export_settings broker_kill
	celery -E $(CELERY_SERVICES) --loglevel=INFO;

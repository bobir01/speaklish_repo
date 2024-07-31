dc := docker compose
js_path := /home/app/web/data.json

build:
	${dc} build

pull:
	git pull origin

up:
	${dc} up -d

down:
	${dc} down

restart:
	${dc} down
	${dc} up -d

logs:
	${dc} logs -f

shell:
	${dc} exec -it web sh

build-up:
	${dc} up -d --build

dumpdata:
	${dc} exec -it web ./manage.py dumpdata --indent 4 -e auth.permission -e contenttypes -e sessions.session -e admin.logentry > data.json && \
	${dc} cp web:${js_path} $(shell pwd) && \
	${dc} exec -it web rm ${js_path}

local-up:
	${dc} -f docker-compose-prod.yaml up --build -d

local-down:
	${dc} -f docker-compose-prod.yaml down

local-shell:
	${dc} -f docker-compose-prod.yaml exec web sh

local-logs:
	${dc} -f docker-compose-prod.yaml logs -f

local-restart:
	${dc} -f docker-compose-prod.yaml down
	${dc} -f docker-compose-prod.yaml up -d

local-build:
	${dc} -f docker-compose-prod.yaml build
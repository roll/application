.PHONY: docs install start _check_virtual_env

## Show this output
help: _showhelp

## Runs Astro dev server to serve documentation.
docs:
	cd portal && npm start

## Install application requirements and documentation npm dependencies.
install: _check_virtualenv
	pip install wheel
	pip install -r requirements.txt
	cd portal && npm install

## Runs the application for development mode.
start: _check_virtualenv
	python -m ode.main

## Create/update all the translation files (.ts) for the supported languages: de, es, fr, pt
update-translations:
	pyside6-lupdate -extensions py -recursive ode -ts ode/assets/translations/de.ts -target-language de
	pyside6-lupdate -extensions py -recursive ode -ts ode/assets/translations/es.ts -target-language es
	pyside6-lupdate -extensions py -recursive ode -ts ode/assets/translations/fr.ts -target-language fr
	pyside6-lupdate -extensions py -recursive ode -ts ode/assets/translations/pt.ts -target-language pt

## Compile all the translation files (.ts) to .qm files.
compile-translations:
	pyside6-lrelease ode/assets/translations/de.ts -qm ode/assets/translations/de.qm
	pyside6-lrelease ode/assets/translations/es.ts -qm ode/assets/translations/es.qm
	pyside6-lrelease ode/assets/translations/fr.ts -qm ode/assets/translations/fr.qm
	pyside6-lrelease ode/assets/translations/pt.ts -qm ode/assets/translations/pt.qm

## Open PySide6 Linguistic application
linguist:
	pyside6-linguist

# Private target
_check_virtualenv:
	@if [ -z "$(VIRTUAL_ENV)" ]; then \
		echo "You need to first activate your virtual environment by running: source venv/bin/activate"; \
		exit 1; \
	fi

## Show help
GREEN  := $(shell tput -Txterm setaf 2)
YELLOW := $(shell tput -Txterm setaf 3)
WHITE  := $(shell tput -Txterm setaf 7)
RESET  := $(shell tput -Txterm sgr0)
TARGET_MAX_CHAR_NUM := 20

_showhelp:
	@echo ''
	@echo 'Usage:'
	@echo '  ${YELLOW}make${RESET} ${GREEN}<target>${RESET}'
	@echo ''
	@echo 'Targets:'
	@awk '/^[a-zA-Z\-\_0-9]+:/ { \
	  helpMessage = match(lastLine, /^## (.*)/); \
	  if (helpMessage) { \
	    helpCommand = substr($$1, 0, index($$1, ":")-1); \
	    helpMessage = substr(lastLine, RSTART + 3, RLENGTH); \
	    printf "  ${YELLOW}%-$(TARGET_MAX_CHAR_NUM)s${RESET} ${GREEN}%s${RESET}\n", helpCommand, helpMessage; \
	  } \
	} \
	{ lastLine = $$0 }' $(MAKEFILE_LIST)

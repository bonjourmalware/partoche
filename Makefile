default: help

## help : Show this help
help: Makefile
	@printf "\n 🎼 Partoche helpers\n\n"
	@sed -n 's/^##//p' $< | column -t -s ':' |  sed -e 's/^/ /'
	@printf ""

## demo : Start Partoche with a demo dataset
demo:
	./venv/bin/python ./partoche.py --demo

## check : Check if everything is setup correctly
check:
    ifeq ($(shell which asciiworld),)
		@echo "[><] Missing required 'asciiworld' binary. Please refer to the instruction at 'https://www.uninformativ.de/git/asciiworld/file/README.html' to install asciiworld"
    else
		@echo "[OK] asciiworld found"
    endif

    ifeq ($(shell which virtualenv),)
		@echo "[><] 'virtualenv' binary not found. Although not required, we recommend to use a virtualenv to properly isolate python projects requirements. Note that this script will use 'virtualenv' to automate setup and run"
    else
		@echo "[OK] virtualenv found"
    endif

    ifeq ($(wildcard data/listbot/live/iprep.yaml),)
		@echo "[><] Missing IP reputation file ('data/listbot/live/iprep.yaml')"
    else
		@echo "[OK] IP reputation file found (last updated $(shell date --date='$(stat --format '%y' data/listbot/live/iprep.yaml)' +'%Y-%m-%d'))"
    endif

    ifeq ($(wildcard data/geoip/GeoLite2-City.mmdb),)
		@echo "[><] Missing required GeoLite2-City database"
    else
		@echo "[OK] GeoLite2-City found"
    endif

    ifeq ($(wildcard data/geoip/GeoLite2-ASN.mmdb),)
		@echo "[><] Missing required GeoLite2-ASN database"
    else
		@echo "[OK] GeoLite2-ASN found"
    endif

    ifeq ($(wildcard config/config.yml),)
		@echo "[><] Missing configuration file (config/config.yml)"
    else
		@echo "[OK] Config file found"
    endif

## install : Setup Partoche environment
install: venv reqs

## reqs : Install required dependencies
reqs:
	./venv/bin/pip install -r requirements.txt

venv:
	virtualenv ./venv --python=$(which python3)

## iprep : Pull IP reputation data
iprep:
	@echo "[!!] This can take several minutes to build, please be patient"
	cd ./data/listbot/ && bash listbot.sh

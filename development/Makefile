INTEGRATION_DIR=../custom_components/vestaboard
TRANSLATIONS_DIR=$(INTEGRATION_DIR)/translations

.DEFAULT_GOAL=dev-restart

check-json: $(TRANSLATIONS_DIR)/*.json
	python -m json.tool < $^ 1>/dev/null

check-python:
	pyflakes $(INTEGRATION_DIR)/**.py


dev: check-json check-python
	sudo docker-compose up -d
	
dev-restart: check-json check-python dev
	sudo docker-compose restart

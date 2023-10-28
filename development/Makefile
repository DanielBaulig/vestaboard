INTEGRATION_DIR=../custom_components/vestaboard
TRANSLATIONS_DIR=$(INTEGRATION_DIR)/translations
PYTHON := python

.DEFAULT_GOAL=dev-restart

check-json: $(INTEGRATION_DIR)/manifest.json $(TRANSLATIONS_DIR)/*.json
	@(for file in $^ ; do \
		echo "$(PYTHON) -m json.tool < $${file}" ; \
		$(PYTHON) -m json.tool < $${file} 1>/dev/null || exit ; \
	done)

check-python:
	pyflakes $(INTEGRATION_DIR)/**.py


dev: check-json check-python
	sudo docker-compose up -d
	
dev-restart: check-json check-python dev
	sudo docker-compose restart

.PHONY: check-json check-python dev-restart dev

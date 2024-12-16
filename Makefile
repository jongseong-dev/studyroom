ifeq ($(OS),Windows_NT)
	DETECTED_OS := Windows
else
	DETECTED_OS := $(shell uname -s)
endif

.PHONY: setup-python setup-venv check-poetry-lock setup-poetry
.PHOMY: infra-benchmark

setup-venv: setup-python check-poetry-lock setup-poetry setup-library

setup-python:
	@echo "Setting up python..."
	pyenv install 3.11.9
	pyenv local 3.11.9

check-poetry-lock:
ifeq ($(DETECTED_OS),Windows)
	@if not exist poetry.lock (	\
		echo poetry.lock file not found. Running poetry init... && \
		poetry init --no-interaction \
	) else ( \
		echo poetry.lock file already exists. \
	)
else
	@if [ ! -f poetry.lock ]; then \
		echo "poetry.lock file not found. Running poetry init..."; \
		poetry init --no-interaction; \
	else \
		echo "poetry.lock file already exists."; \
	fi
endif

setup-poetry:
	@echo "Setting up poetry..."
	poetry env use 3.11.9
	poetry shell

setup-library:
	@echo "Setting up library..."
	poetry install


infra-benchmark:
	@echo "Infra settings benchmark..."
	docker-compose -f benchmark/infra/docker-compose.yaml up -d
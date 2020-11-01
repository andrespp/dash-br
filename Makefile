IMAGE_NAME=dash-dwbra

.PHONY: help
help:
	@echo "Usage: make [target]"
	@echo
	@echo "Targets:"
	@echo "  help\t\tPrint this help"
	@echo "  test\t\tLookup for docker and docker-compose binaries"
	@echo "  setup\t\tCreate required directories and build docker images"
	@echo "  run\t\tRun Dash App"
	@echo "  stop\t\tStop Dash App"

.PHONY: test
test:
	which docker
	which docker-compose

setup: Dockerfile
	docker image build -t $(IMAGE_NAME) .

.PHONY: run
run:
	docker run -d --rm --name $(IMAGE_NAME) -v $(PWD):/usr/src/app -p 8050:8050 $(IMAGE_NAME) python index.py

.PHONY: stop
stop:
	docker stop $(IMAGE_NAME)

.PHONY: runi
runi:
	docker run -it --rm -v $(PWD):/usr/src/app $(IMAGE_NAME) bash

BRANCH ?= $(shell git rev-parse --abbrev-ref HEAD)
API_PORT ?= 6000-6100
SAMPLES_1000g ?= /media/oyvinev/Storage/1000g/samples
CONTAINER_NAME ?= spiked1000g-$(BRANCH)-$(USER)
IMAGE_NAME = local/spiked1000g-$(BRANCH)
.PHONY: help

#---------------------------------------------
# DEVELOPMENT
#---------------------------------------------
.PHONY: any build run dev kill shell logs restart automation

any:
	$(eval CONTAINER_NAME = $(shell docker ps | awk '/spiked1000g-.*-$(USER)/ {print $$NF}'))
	@true

build:
	docker build -t $(IMAGE_NAME) $(BUILD_OPTS) .

run:
	docker run -d \
	$(RUN_OPTS) \
	--name $(CONTAINER_NAME) \
	-p $(API_PORT):6000 \
	-v $(shell pwd):/spiked1000g \
	-v $(SAMPLES_1000g):/samples \
	$(IMAGE_NAME)

dev: run

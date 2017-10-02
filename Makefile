all: build

build:
	@docker build --tag=projectdc/blog:dev .

release: build
	@docker build --tag=projectdc/blog:$(shell cat VERSION) .

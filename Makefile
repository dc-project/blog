all: build

build:
	@docker build --tag=ysicing/blog:latest .

release: build
	@docker build --tag=ysicing/blog:$(shell cat VERSION) .

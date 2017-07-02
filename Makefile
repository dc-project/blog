all: build

build:
	@docker build --tag=blog:dev .

release: build
	@docker build --tag=ysicing/blog:$(shell cat VERSION) .

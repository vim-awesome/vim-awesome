SHELL=/bin/bash

.PHONY: local setup deploy clean

local:
	tools/local_server.sh

setup:
	tools/setup.sh

deploy:
	# TODO

clean:
	find . -name '*.pyc' -delete
	rm -rf server/static/css

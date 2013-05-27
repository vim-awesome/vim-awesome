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
	compass clean --config conf/compass.rb

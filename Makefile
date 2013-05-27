SHELL=/bin/bash

.PHONY: local setup deploy clean

local:
	tools/local_server.sh

setup:
	tools/setup.sh

deploy:
	@if [ `whoami` = 'vim' ]; then \
		tools/deploy.sh; \
	else \
		cat tools/deploy.sh | ssh vim@vim.benalpert.com sh; \
	fi

clean:
	find . -name '*.pyc' -delete
	compass clean --config conf/compass.rb

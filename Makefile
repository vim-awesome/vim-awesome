SHELL=/bin/bash

.PHONY: local deploy clean

local:
	tools/local_server.sh

deploy:
	@if [ `whoami` = 'vim' ]; then \
		tools/deploy.sh; \
	else \
		cat tools/deploy.sh | ssh vim@vim.benalpert.com sh; \
	fi

clean:
	find . -name '*.pyc' -delete
	bundle exec compass clean --config conf/compass.rb

SHELL=/bin/bash

.PHONY: local deploy seed_data aggregate_tags test clean

local:
	tools/local_server.sh

deploy:
	@if [ `whoami` = 'vim' ]; then \
		tools/deploy.sh; \
	else \
		cat tools/deploy.sh | ssh vim@vimawesome.com sh; \
	fi

seed_data:
	@echo "Creating tables with some example data"
	PYTHONPATH=. python db/seed.py
	@echo
	PYTHONPATH=. python tools/scrape/scrape.py 40

aggregate_tags:
	PYTHONPATH=. python tools/aggregate.py

test:
	PYTHONPATH=. nosetests -v

clean:
	find . -name '*.pyc' -delete
	bundle exec compass clean --config conf/compass.rb

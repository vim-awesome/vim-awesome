SHELL=/bin/bash

.PHONY: local deploy seed_data aggregate_tags test clean

local:
	tools/local_server.sh

deploy:
	@if [ `whoami` = 'vim' ]; then \
		tools/deploy.sh; \
	else \
		cat tools/deploy.sh | ssh vim@vimawesome.com DEPLOYER=`whoami` sh; \
	fi

ensure_tables_and_indices:
	PYTHONPATH=. python db/init_db.py

# TODO(david): This probably no longer works and needs to be updated.
seed_data:
	@echo "*** Warning! This has not been updated in a while and is not guaranteed to work. ***"
	@echo
	@echo
	@echo "Creating tables with some example data"
	PYTHONPATH=. python db/seed.py
	@echo "Scraping 100 plugins from vim.org."
	PYTHONPATH=. python tools/scrape/scrape.py -s vim.org 100
	@echo "Extracting GitHub repo URLs from descriptions."
	PYTHONPATH=. python tools/scrape/build_github_index.py -s vim.org
	@echo "Scraping discovered GitHub repos."
	PYTHONPATH=. python tools/scrape/scrape.py -s github 30

aggregate_tags:
	PYTHONPATH=. python tools/aggregate.py

build_github_index:
	PYTHONPATH=. python tools/scrape/build_github_index.py

test:
	PYTHONPATH=. nosetests -v

dump:
	rethinkdb dump -e vim_awesome -f rethinkdb_dump.tar.gz

restore:
	scp vim@vimawesome.com:~/vim-awesome/rethinkdb_dump.tar.gz \
		rethinkdb_dump_remote.tar.gz
	rethinkdb restore rethinkdb_dump_remote.tar.gz --force

auto_categorize:
	PYTHONPATH=. python tools/auto_categorize.py

clean:
	find . -name '*.pyc' -delete
	bundle exec compass clean --config conf/compass.rb

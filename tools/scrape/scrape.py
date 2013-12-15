import argparse
import logging
import sys

from tools.scrape import vimorg, github, db_upsert


def scrape_github(num):
    print "\nScraping from github.com..."
    github.scrape_repos(num)


def scrape_vimorg(num):
    print "\nScraping from vim.org..."
    for plugin in vimorg.get_plugin_list(num):
        print "    scraping %s ..." % plugin['name'],  # Print w/o newline
        sys.stdout.flush()
        db_upsert.upsert_plugin(plugin)
        print "done"


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    scrape_fns = {
        "vim.org": scrape_vimorg,
        "github": scrape_github,
    }

    parser.add_argument("number", nargs="?", default=6000, type=int,
            help="Maximum # of plugins to scrape from each source"
            " (default: 6000)")
    parser.add_argument("--source", "-s", choices=scrape_fns.keys(),
            default="all", help="Source to scrape from (default: all)")

    args = parser.parse_args()

    sources = scrape_fns.keys() if args.source == "all" else [args.source]
    for source in sources:
        scrape_fn = scrape_fns[source]
        try:
            scrape_fn(args.number)
        except:
            logging.exception("scrape.py: error in %s " % (scrape_fn))

import datetime
import logging
import re
import sys

import requests
import lxml.html
import lxml.html.html5parser

import db
import util


class HTMLParser(lxml.html.html5parser.HTMLParser):
    """An html parser that doesn't add weird xml tags to things"""
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('namespaceHTMLElements', False)
        super(HTMLParser, self).__init__(*args, **kwargs)


PARSER = HTMLParser()


def scrape_scripts(num):
    """Scrapes and upserts the num most recently created scripts on vim.org."""
    res = requests.get(
            'http://www.vim.org/scripts/script_search_results.php?show_me=%d' %
                num)

    html = lxml.html.html5parser.document_fromstring(res.text, parser=PARSER)

    # Since there are no identifying classes or ids, this is the best way to
    # find the correct table
    scripts = html.xpath('//table[tbody/tr/th[contains(text(),"Script")]]/*/*')

    # the first two rows and the last row aren't scripts
    for tr in scripts[2:-1]:
        link = tr[0][0].attrib['href']

        vimorg_id = re.search("script_id=(\d+)", link).group(1)
        name = tr[0][0].text

        # Print w/o newline.
        print "    scraping %s (vimorg_id=%s) ..." % (name, vimorg_id),
        sys.stdout.flush()

        # TODO(david): Somehow also get a count of how many plugins failed to
        #     be scraped in total. Maybe return a tuple with error status.
        # TODO(david): Fix error scraping vimcat (id=4325) (something about
        #     only unicode and ascii allowed, no null bytes or control chars)
        # TODO(david): Fix error scraping
        #     http://www.vim.org/scripts/script.php?script_id=4099 (unicode
        #     chars in plugin name) due to invalid escape sequence \\xe0 in the
        #     Rql regex match in db_upsert._find_by_similar_name.
        try:
            # Merge the data we get here with extra data from the details page.
            plugin = dict({
                "vimorg_url": "http://www.vim.org/scripts/%s" % link,
                "vimorg_id": vimorg_id,
                "vimorg_name": tr[0][0].text,
                "vimorg_type": tr[1].text,
                "vimorg_rating": int(tr[2].text),
                "vimorg_downloads": int(tr[3].text),
                "vimorg_short_desc": tr[4][0].text,
            }, **get_plugin_info(vimorg_id))
            db.plugins.add_scraped_data(plugin)
            print "done"
        except Exception:
            logging.exception(
                    '\nError scraping %s (vimorg_id=%s) from vim.org' %
                    (name, vimorg_id))


def get_plugin_info(vimorg_id):
    """Gets some more detailed information about a vim.org script

    Scrapes a given vim.org script page, and returns some detailed information
    about the plugin that is not available from the search page, like how many
    people rated a plugin, the author's name, and a long description.
    """
    res = requests.get('http://www.vim.org/scripts/script.php?script_id=%s' %
            vimorg_id, timeout=10)

    html = lxml.html.html5parser.document_fromstring(res.text, parser=PARSER)

    rating = html.xpath('//td[contains(text(),"Rating")]/b')[0]
    rating_denom = int(re.search("(\d+)/(\d+)", rating.text).group(2))

    body_trs = html.xpath(
            '//table[tbody/tr/td[contains(@class,"prompt")]]/*/*')

    assert body_trs[0][0].text == "created by"
    creator = body_trs[1][0][0].text

    assert body_trs[6][0].text == "description"
    description_node = body_trs[7][0]

    assert body_trs[9][0].text == "install details"
    install_node = body_trs[10][0]

    download_trs = html.xpath(
            '//table[tbody/tr/th[text()="release notes"]]/*/*')

    # Parse created and updated dates
    assert download_trs[0][2].text == "date"
    updated_date_text = download_trs[1][2][0].text
    created_date_text = download_trs[-1][2][0].text

    date_format = "%Y-%m-%d"
    updated_date = datetime.datetime.strptime(updated_date_text, date_format)
    created_date = datetime.datetime.strptime(created_date_text, date_format)

    return {
        "vimorg_num_raters": rating_denom,
        "vimorg_author": creator,
        "vimorg_long_desc": _get_inner_text(description_node),
        "vimorg_install_details": _get_inner_text(install_node),
        "updated_at": util.to_timestamp(updated_date),
        "created_at": util.to_timestamp(created_date),
    }


def _get_inner_text(html_node):
    """Returns the plaintext of an HTML node.

    This turns out to do exactly what we want:
        - strips out <br>s and other markup
        - replace <a> tags with just their text
        - converts HTML entities like &nbsp; and smart quotes into their
          unicode equivalents
    """
    return lxml.html.tostring(html_node, encoding='utf-8', method='text',
            with_tail=False)

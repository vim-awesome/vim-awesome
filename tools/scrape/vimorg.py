import datetime
import re

import requests
import lxml.html
import lxml.html.html5parser

import util


class HTMLParser(lxml.html.html5parser.HTMLParser):
    """An html parser that doesn't add weird xml tags to things"""
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('namespaceHTMLElements', False)
        super(HTMLParser, self).__init__(*args, **kwargs)


PARSER = HTMLParser()


def get_plugin_list(num):
    """Get plugin information from vim.org

    This scrapes a given number of scripts (reverse ordered by vim.org id) and
    returns a dict of the important data about the plugin.
    """
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
        # Parse out the script id
        script_id = int(re.search("script_id=(\d+)", link).group(1))
        # Merge the data we get here with the extra data from get_plugin_info
        yield dict({
            "vimorg_url": "http://www.vim.org/scripts/%s" %
                   tr[0][0].attrib['href'],
            "vim_script_id": script_id,
            "name": tr[0][0].text,
            "vimorg_type": tr[1].text,
            "vimorg_rating": int(tr[2].text),
            "vimorg_downloads": int(tr[3].text),
            "short_desc": tr[4][0].text,
        }, **get_plugin_info(script_id))


def get_plugin_info(script_id):
    """Gets some more detailed information about a vim.org script

    Scrapes a given vim.org script page, and returns some detailed information
    about the plugin that is not available from the search page, like how many
    people rated a plugin, the author's name, and a long description
    """
    res = requests.get(
            'http://www.vim.org/scripts/script.php?script_id=%d' % script_id)

    html = lxml.html.html5parser.document_fromstring(res.text, parser=PARSER)

    rating = html.xpath('//td[contains(text(),"Rating")]/b')[0]
    rating_denom = int(re.search("(\d+)/(\d+)", rating.text).group(2))

    body_trs = html.xpath(
            '//table[tbody/tr/td[contains(@class,"prompt")]]/*/*')

    assert body_trs[0][0].text == "created by"
    assert body_trs[6][0].text == "description"

    creator = body_trs[1][0][0].text
    description_node = body_trs[7][0]

    # Sometimes there's an <a> at the beginning of the description, and that
    # breaks some code down below because there's no text in the body. This
    # fixes that.
    if len(description_node) > 0 and not description_node[0].getparent().text:
        description_node[0].getparent().text = ""

    # Iterate through the tags of the description
    for elem in description_node:
        # Remove <br> tags completely
        if elem.tag == 'br':
            # lxml wizardry to remove the tag but keep the text
            if elem.tail:
                if elem.getprevious():
                    elem.getprevious().tail += elem.tail
                else:
                    elem.getparent().text += elem.tail
            elem.getparent().remove(elem)
        # Replace <a> tags with the text of the link
        elif elem.tag == 'a':
            # We've only identified links where the text is the same as the
            # href, or which look like "vimscript #1923"
            if elem.text == elem.attrib["href"] or 'vimscript' in elem.text:
                # lxml wizardry to remove the tag but keep the text
                if elem.getprevious():
                    elem.getprevious().tail += elem.text
                    if elem.tail:
                        elem.getprevious().tail += elem.tail
                else:
                    elem.getparent().text += elem.text
                    if elem.tail:
                        elem.getparent().text += elem.tail
            else:
                # Throw an error if it's not one of those types
                raise ("Weird link to %s with text %s" %
                        (elem.attrib["href"], elem.text))
            elem.getparent().remove(elem)

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
        "rating_denom": rating_denom,
        "author": creator,
        "long_desc": _get_innerhtml(description_node),
        # TODO(david): Upgrade rethink to >= 1.8 to get native datetime support
        "updated_at": util.to_timestamp(updated_date),
        "created_at": util.to_timestamp(created_date),
    }


# Stolen from KA scraping script
def _get_outerhtml(html_node):
    """Get a string representation of an HTML node.

    (lxml doesn't provide an easy way to get the 'innerHTML'.)
    Note: lxml also includes the trailing text for a node when you
          call tostring on it, we need to snip that off too.
    """
    html_string = lxml.html.tostring(html_node)
    return re.sub(r'[^>]*$', '', html_string, count=1)


# Stolen from KA scraping script
def _get_innerhtml(html_node):
    """Get a string representation of the contents of an HTML Node

    This takes the outerhtml and pulls the two tags surrounding it off
    """
    html_string = _get_outerhtml(html_node)
    html_string = re.sub(r'^<[^<>]*?>', '', html_string, count=1)
    return re.sub(r'<[^<>]*?>$', '', html_string, count=1)

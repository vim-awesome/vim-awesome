import json
from urlparse import urlparse


class DummyResponse(object):
    status_code = 200


def fixture_data(path):
    fixture = 'test/fixtures/github/' + path + '.json'
    return json.load(open(fixture, 'r'))


def mock_api_response(url):
    return DummyResponse(), fixture_data(urlparse(url).path)

"use strict"

jest.unmock('../utils.js');

var utils = require('../utils.js');

describe('getQueriesWithPrefix', function() {
  it('can handle an empty string', function() {
    var queryObj = utils.getQueriesWithPrefix('', 'foo');
    expect(queryObj).toEqual([]);
  });
  it('can parse tags', function() {
    var queryObj = utils.getQueriesWithPrefix('tag:foo tag:bar', 'tag');
    expect(queryObj).toEqual(['foo', 'bar']);
  });
  it('ignores other types', function() {
    var queryObj = utils.getQueriesWithPrefix('cat:foo tag:bar', 'tag');
    expect(queryObj).toEqual(['bar']);
  });
  it('ignores generic queries', function() {
    var queryObj = utils.getQueriesWithPrefix('foo tag:bar', 'tag');
    expect(queryObj).toEqual(['bar']);
  });
  it('does not include keys that lack values', function() {
    var queryObj = utils.getQueriesWithPrefix('tag', 'tag');
    expect(queryObj).toEqual([]);
  });
  it('uses `:` to delineate key:value', function() {
    var queryObj = utils.getQueriesWithPrefix('tag>biz tag:bar', 'tag');
    expect(queryObj).toEqual(['bar']);
  });
});

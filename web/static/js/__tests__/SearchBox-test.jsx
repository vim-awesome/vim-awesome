"use strict"

jest.unmock('../SearchBox.jsx');

var React = require('react');
var TestUtils = require('react-dom/test-utils');

var SearchBox = require('../SearchBox.jsx');

describe('SearchBox', function() {
  it('renders without throwing', function() {
    TestUtils.renderIntoDocument(
      <SearchBox />
    );
  });
});

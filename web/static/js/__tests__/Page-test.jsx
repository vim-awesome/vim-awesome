"use strict"

jest.unmock('../Page.jsx');

var React = require('react');
var TestUtils = require('react-dom/test-utils');

var Page = require('../Page.jsx');

describe('Page', function() {
  it('renders without throwing', function() {
    TestUtils.renderIntoDocument(
      // Normally react-routes adds a location. For tests we do it ourselves.
      <Page location={{query: ''}} />
    );
  });
});

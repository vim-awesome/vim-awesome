"use strict"

jest.unmock('../Tags.jsx');

var React = require('react');
var TestUtils = require('react-dom/test-utils');

var Tags = require('../Tags.jsx');

describe('Tags', function() {
  it('renders without throwing', function() {
    TestUtils.renderIntoDocument(
      <Tags />
    );
  });
});

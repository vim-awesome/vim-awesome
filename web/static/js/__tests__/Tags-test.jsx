"use strict"

var React = require('react');
var TestUtils = require('react-addons-test-utils');

var Tags = require('../Tags.jsx');

describe('Tags', function() {
  it('renders without throwing', function() {
    TestUtils.renderIntoDocument(
      <Tags />
    );
  });
});

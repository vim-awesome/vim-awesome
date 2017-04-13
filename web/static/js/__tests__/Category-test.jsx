"use strict"

jest.unmock('../Category.jsx');

var React = require('react');
var TestUtils = require('react-dom/test-utils');

var Category = require('../Category.jsx');

describe('Category', function() {
  it('renders without throwing', function() {
    TestUtils.renderIntoDocument(
      <Category />
    );
  });
});

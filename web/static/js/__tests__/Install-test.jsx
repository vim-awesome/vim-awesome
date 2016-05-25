"use strict"

jest.unmock('../Install.jsx');

var React = require('react');
var TestUtils = require('react-addons-test-utils');

var Install = require('../Install.jsx');

describe('Install', function() {
  it('renders without throwing', function() {
    TestUtils.renderIntoDocument(
      <Install />
    );
  });
});


"use strict"

jest.unmock('../Sidebar.jsx');

var React = require('react');
var TestUtils = require('react-dom/test-utils');

var Sidebar = require('../Sidebar.jsx');

describe('Sidebar', function() {
  it('renders without throwing', function() {
    var query = 'cat:code-display tag:css';
    TestUtils.renderIntoDocument(
      <Sidebar query={query} />
    );
  });
});

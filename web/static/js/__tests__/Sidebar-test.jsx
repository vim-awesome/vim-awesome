/** @jsx React.DOM */

"use strict"

var React = require('react');

var Sidebar = require('../Sidebar.jsx');

describe('Sidebar', function() {
  it('renders without throwing', function() {
    var query = 'cat:code-display tag:css';
    var container = document.createElement('div');
    React.renderComponent(
      <Sidebar query={query} />,
      container
    );
  });
});

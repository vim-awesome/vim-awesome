/** @jsx React.DOM */

"use strict"

var React = require('react');

var Page = require('../Page.jsx');

describe('Page', function() {
  it('renders without throwing', function() {
    var container = document.createElement('div');
    React.renderComponent(
      <Page />,
      container
    );
  });
});

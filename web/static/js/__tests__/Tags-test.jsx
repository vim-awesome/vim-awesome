/** @jsx React.DOM */

"use strict"

var React = require('react');

var Tags = require('../Tags.jsx');

describe('Tags', function() {
  it('renders without throwing', function() {
    var container = document.createElement('div');
    React.renderComponent(
      <Tags />,
      container
    );
  });
});

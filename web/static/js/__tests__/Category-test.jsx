/** @jsx React.DOM */

"use strict"

var React = require('react');

var Category = require('../Category.jsx');

describe('Category', function() {
  it('renders without throwing', function() {
    var container = document.createElement('div');
    React.renderComponent(
      <Category />,
      container
    );
  });
});

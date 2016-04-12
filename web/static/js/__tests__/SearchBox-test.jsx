/** @jsx React.DOM */

"use strict"

var React = require('react');

var SearchBox = require('../SearchBox.jsx');

describe('SearchBox', function() {
  it('renders without throwing', function() {
    var container = document.createElement('div');
    React.renderComponent(
      <SearchBox />,
      container
    );
  });
});

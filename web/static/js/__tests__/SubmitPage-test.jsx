/** @jsx React.DOM */

"use strict"

var React = require('react');

var SubmitPage = require('../SubmitPage.jsx');

describe('SubmitPage', function() {
  it('renders without throwing', function() {
    var container = document.createElement('div');
    React.renderComponent(
      <SubmitPage />,
      container
    );
  });
});

/** @jsx React.DOM */

"use strict"

var React = require('react');

var ThanksForSubmittingPage = require('../ThanksForSubmittingPage.jsx');

describe('ThanksForSubmittingPage', function() {
  it('renders without throwing', function() {
    var container = document.createElement('div');
    React.renderComponent(
      <ThanksForSubmittingPage />,
      container
    );
  });
});

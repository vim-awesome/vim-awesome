"use strict"

var React = require('react');
var TestUtils = require('react-addons-test-utils');

var ThanksForSubmittingPage = require('../ThanksForSubmittingPage.jsx');

describe('ThanksForSubmittingPage', function() {
  it('renders without throwing', function() {
    TestUtils.renderIntoDocument(
      <ThanksForSubmittingPage />
    );
  });
});

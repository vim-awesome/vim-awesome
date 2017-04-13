"use strict"

jest.unmock('../ThanksForSubmittingPage.jsx');

var React = require('react');
var TestUtils = require('react-dom/test-utils');

var ThanksForSubmittingPage = require('../ThanksForSubmittingPage.jsx');

describe('ThanksForSubmittingPage', function() {
  it('renders without throwing', function() {
    TestUtils.renderIntoDocument(
      <ThanksForSubmittingPage />
    );
  });
});

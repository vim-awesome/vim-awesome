"use strict"

jest.unmock('../SubmitPage.jsx');

var React = require('react');
var TestUtils = require('react-dom/test-utils');

var SubmitPage = require('../SubmitPage.jsx');

describe('SubmitPage', function() {
  it('renders without throwing', function() {
    TestUtils.renderIntoDocument(
      <SubmitPage />
    );
  });
});

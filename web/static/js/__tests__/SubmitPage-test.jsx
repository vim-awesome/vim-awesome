"use strict"

jest.unmock('../SubmitPage.jsx');

var React = require('react');
var TestUtils = require('react-addons-test-utils');

var SubmitPage = require('../SubmitPage.jsx');

describe('SubmitPage', function() {
  it('renders without throwing', function() {
    TestUtils.renderIntoDocument(
      <SubmitPage />
    );
  });
});

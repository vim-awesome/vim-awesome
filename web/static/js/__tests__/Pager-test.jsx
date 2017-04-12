"use strict"

jest.unmock('../Pager.jsx');

var React = require('react');
var TestUtils = require('react-dom/test-utils');

var Pager = require('../Pager.jsx');

describe('Pager', function() {
  it('renders without throwing', function() {
    TestUtils.renderIntoDocument(
      <Pager currentPage={1} totalPages={5} />
    );
  });
});

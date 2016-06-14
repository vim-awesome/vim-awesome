"use strict"

jest.unmock('../Plaintext.jsx');

var React = require('react');
var render = require('enzyme').render;

var Plaintext = require('../Plaintext.jsx');

describe('Plaintext', function() {
  it('renders without throwing', function() {
    render(<Plaintext />);
  });
});

"use strict"

jest.unmock("marked");
jest.unmock('../Markdown.jsx');

var React = require('react');
var render = require('enzyme').render;

var Markdown = require('../Markdown.jsx');

describe('Markdown', function() {
  it('renders without throwing', function() {
    render(<Markdown />);
  });
  it('converts relative paths to absolute paths', function() {
    var repoUrl = 'github_url';
    var imgPath = 'path/to/image.jpg';
    var readme = "![an image](" + imgPath + ")";

    var node = render(<Markdown githubRepoUrl={repoUrl}>{readme}</Markdown>);

    var actual = node.find('img').attr('src');
    var expected = repoUrl + "/raw/master/" + imgPath;
    expect(actual).toBe(expected);
  });
  it('does not mutate absolute paths', function() {
    var imgPath = 'http://example.com/path/to/image.jpg';
    var readme = "![an image](" + imgPath + ")";

    var node = render(<Markdown>{readme}</Markdown>);

    var actual = node.find('img').attr('src');
    var expected = imgPath;
    expect(actual).toBe(expected);
  });
});

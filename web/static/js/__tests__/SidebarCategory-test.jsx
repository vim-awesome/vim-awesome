/** @jsx React.DOM */

"use strict"

var React = require('react');

var SidebarCategory = require('../SidebarCategory.jsx');

var TEST_CATEGORY = {
  "description": "Plugins and color schemes that enhance code display",
  "icon": "icon-code",
  "id": "code-display",
  "name": "Code display",
  "tags": [
    {
      "count": 15,
      "id": "color-scheme"
    },
    {
      "count": 5,
      "id": "dark"
    }
  ]
};

describe('SidebarCategory', function() {
  it('renders without throwing', function() {
    var container = document.createElement('div');
    React.renderComponent(
      <SidebarCategory category={TEST_CATEGORY} selectedTags={[]} />,
      container
    );
  });
});

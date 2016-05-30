"use strict";

var React = require("react");
var marked = require("marked");

// Renderer used to change relative image URL to absolute in Markdown
var markedRenderer = new marked.Renderer();

var Markdown = React.createClass({
  render: function() {
    markedRenderer.image = this.replaceRelativeUrlWithGithubImgSrc;
    var markedHtml = marked(this.props.children || '',
      {renderer: markedRenderer});
    return <div
      dangerouslySetInnerHTML={{__html: markedHtml}}
    />;
  },

  /**
   * Replaces the relative img URL to the absolute img URL in a README.md file
   * See docs: https://www.npmjs.org/package/marked
   * @param {string} href The source of the image
   * @param {string} title The title of the image
   * @param {string} text The alt of the image
   */
  replaceRelativeUrlWithGithubImgSrc: function(href, title, text) {
    // Checks if the href is not an absolute URL
    // http://stackoverflow.com/questions/10687099/how-to-test-if-a-url-string-is-absolute-or-relative
    if (!href.match(/^(?:[a-z]+:)?\/\//i)) {
      return "<img src='" + this.props.githubRepoUrl + "/raw/master/" +
        href + "' alt='" + text + "' />";
    } else {
      return "<img src='" + href + "' alt='" + text + "' />";
    }
  }
});

module.exports = Markdown;

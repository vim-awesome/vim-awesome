/** @jsx React.DOM */

"use strict";

var _ = require("underscore");
var React = require("react");

var Category = require("./Category.jsx");
var Tags = require("./Tags.jsx");

// TODO(david): Form validation on submit! Not done right now because we
//     currently just save this raw data to be manually reviewed.
var SubmitPage = React.createClass({
  getInitialState: function() {
    return {
      tags: [],
      category: "uncategorized"
    };
  },

  onTagsChange: function(tags) {
    this.setState({tags: _.uniq(tags)});
  },

  onCategoryChange: function(category) {
    this.setState({category: category});
  },

  render: function() {
    return <div className="submit-page">
      <h1>Submit plugin</h1>
      <form className="form-horizontal" action="/api/submit" method="POST">
        <div className="control-group">
          <label className="control-label" htmlFor="name-input">Name</label>
          <div className="controls">
            <input type="text" name="name" id="name-input"
                placeholder="e.g. Fugitive" />
          </div>
        </div>
        <div className="control-group">
          <label className="control-label" htmlFor="author-input">
            Author
          </label>
          <div className="controls">
            <input type="text" name="author" id="author-input"
                placeholder="e.g. Tim Pope" />
          </div>
        </div>
        <div className="control-group">
          <label className="control-label" htmlFor="github-input">
            GitHub link (optional)
          </label>
          <div className="controls">
            <input type="text" name="github-link" id="github-input"
                placeholder="e.g. https://github.com/tpope/vim-fugitive" />
          </div>
        </div>
        <div className="control-group">
          <label className="control-label" htmlFor="vimorg-input">
            Vim.org link (optional)
          </label>
          <div className="controls">
            <input type="text" name="vimorg-link" id="vimorg-input"
                placeholder={"e.g. " +
                    "http://www.vim.org/scripts/script.php?script_id=2975"} />
          </div>
        </div>
        <div className="control-group">
          <label className="control-label" htmlFor="category-input">
            Category
          </label>
          <div className="controls">
            <Category category={this.state.category} editOnly={true}
                onCategoryChange={this.onCategoryChange} />
          </div>
        </div>
        <div className="control-group">
          <label className="control-label" htmlFor="tags-input">
            Tags (up to four keywords for search)
          </label>
          <div className="controls">
            <Tags tags={this.state.tags} editOnly={true}
                onTagsChange={this.onTagsChange} />
          </div>
        </div>
        <div className="control-group">
          <div className="controls">
            <p className="other-info-blurb">
              All other information, including descriptions, will be
              automatically extracted from the GitHub or Vim.org link.
            </p>
          </div>
        </div>
        <div className="control-group">
          <div className="controls">
            <button type="submit">
              Submit
              <span className="right-arrow">{"\u2192"}</span>
            </button>
          </div>
        </div>
        <input type="hidden" name="category"
            value={this.state.category} />
        <input type="hidden" name="tags"
            value={JSON.stringify(this.state.tags)} />
      </form>
    </div>;
  }
});

module.exports = SubmitPage;

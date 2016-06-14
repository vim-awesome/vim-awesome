"use strict";

var _ = require("lodash");
var React = require("react");

var KEYCODES = require("./constants/keycodes.js");

var Pager = React.createClass({
  propTypes: {
    currentPage: React.PropTypes.number.isRequired,
    totalPages: React.PropTypes.number.isRequired
  },

  componentDidMount: function() {
    window.addEventListener("keyup", this.onWindowKeyDown, false);
  },

  componentWillUnmount: function() {
    window.removeEventListener("keyup", this.onWindowKeyDown, false);
  },

  onWindowKeyDown: function(e) {
    var tag = e.target.tagName;
    var key = e.keyCode;

    if (tag !== "INPUT" && tag !== "TEXTAREA") {
      if (key === KEYCODES.P) {
        this.goToPrevPage();
      } else if (key === KEYCODES.N) {
        this.goToNextPage();
      }
    }
  },

  goToPage: function(page) {
    var newPage = _.clamp(page, 1, this.props.totalPages);
    this.props.onPageChange(newPage);
  },

  goToPrevPage: function() {
    this.goToPage(this.props.currentPage - 1);
  },

  goToNextPage: function() {
    this.goToPage(this.props.currentPage + 1);
  },

  onPrevClick: function(e) {
    e.preventDefault();
    this.goToPrevPage();
  },

  onNextClick: function(e) {
    e.preventDefault();
    this.goToNextPage();
  },

  render: function() {
    var currentPage = this.props.currentPage;
    var totalPages = this.props.totalPages;

    if (totalPages <= 1) {
      return <div />;
    }

    // TODO(david): Have buttons for page numbers, including first page, last
    //     page, and current page.
    return <div className="pagination">
      <ul>
        {currentPage > 1 &&
          <li>
            <a className="pager-button prev-page-button" href="#"
                onClick={this.onPrevClick}>
              {"\u2190"}<code>P</code>
            </a>
          </li>
        }
        <li>
          <a className="page-number">Page {currentPage} of {totalPages}</a>
        </li>
        {currentPage < totalPages &&
          <li>
            <a className="pager-button next-page-button" href="#"
                onClick={this.onNextClick}>
              <code>N</code> Next page
              <span className="right-arrow">{"\u2192"}</span>
            </a>
          </li>
        }
      </ul>
    </div>;
  }
});

module.exports = Pager;

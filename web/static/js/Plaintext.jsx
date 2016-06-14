"use strict";

var React = require("react");

var Plaintext = React.createClass({
  render: function() {
    // TODO(david): Linkify <a> tags
    // TODO(david): Linkify "vimscript #2136" references (e.g. surround-vim'
    //     vim.org long description)
    return <div className={"plain " + (this.props.className || '')}>
      {this.props.children}
    </div>;
  }
});

module.exports = Plaintext;

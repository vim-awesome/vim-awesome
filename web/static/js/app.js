/** @jsx React.DOM */
(function() {
"use strict";

var Sidebar = React.createClass({
  render: function() {
    var categories = _.map([
      "Language",
      "Syntax",
      "Navigation",
      "Movement",
      "Buffer",
      "Info",
      "Integrations"
    ], function(cat) {
      return <li>
        <a href="#/blah"><i class="icon-fighter-jet"></i> {cat}</a>
      </li>;
    });

    return <div class="sidebar">
      <h1 class="title">
        <a href="#">
          <span class="vim">Vim</span>Awesome
        </a>
      </h1>
      <div class="tac">
        <div class="subtitle">
          <div class="line1">Awesome Vim plugins</div>
          <div class="from">from</div>
          <div class="line2">across the Universe</div>
        </div>
      </div>
      <ul class="categories">{categories}</ul>
    </div>;
  }
});

var SearchBox = React.createClass({
  componentDidMount: function() {
    window.addEventListener("keyup", this.windowKeyUp, false);
  },

  componentWillUnmount: function() {
    window.removeEventListener("keyup", this.windowKeyUp, false);
  },

  windowKeyUp: React.autoBind(function(e) {
    var tag = e.target.tagName;
    var key = e.keyCode;
    if (tag !== "INPUT" && tag !== "TEXTAREA" &&
        key === 191 /* forward slash */) {
      this.refs.input.getDOMNode().focus();
    }
  }),

  handleKeyUp: React.autoBind(function() {
    var input = this.refs.input.getDOMNode();
    this.props.onInput(input.value);
  }),

  render: function() {
    return <div class="search-container">
      <i class="icon-search"></i>
      <input type="text" class="search" placeholder="Search" ref="input"
        onKeyUp={this.handleKeyUp} />
    </div>;
  }
});

var PluginList = React.createClass({
  getInitialState: function() {
    return {
      plugins: []
    };
  },

  componentDidMount: function() {
    this.fetchPlugins(this.props.searchQuery);
  },

  componentDidUpdate: function(prevProps) {
    if (prevProps.searchQuery !== this.props.searchQuery) {
      this.fetchPlugins(this.props.searchQuery);
    }
  },

  fetchPlugins: function(query) {
    $.ajax({
      url: "/api/plugins",
      dataType: "json",
      data: {query: query},
      success: function(data) {
        if (query === this.props.searchQuery) {
          this.setState({plugins: data});
        }
      }.bind(this)
    });
  },

  render: function() {
    var query = this.props.searchQuery.toLowerCase();
    var plugins = _.chain(this.state.plugins)
      .sortBy("github_stars")
      .reverse()
      .map(function(plugin) {
        return <li class="plugin">
          <div class="hover-bg"></div>
          <div class="hover-buttons">
            <a class="github-link" target="_blank" href={plugin.github_url}>
              github link
            </a>
          </div>
          <h3 class="plugin-name">
            <a href={"#/plugin/" + plugin.name}>{plugin.name}</a>
          </h3>
          <p class="short-desc">{plugin.short_desc}</p>
        </li>
      })
      .value();

    return <div class="content row-fluid">
      <ul class="plugins">{plugins}</ul>
    </div>;
  }
});

var Page = React.createClass({
  getInitialState: function() {
    return {searchQuery: ""};
  },

  onSearchInput: React.autoBind(function(query) {
    this.setState({searchQuery: query});
  }),

  render: function() {
    // TODO(alpert): Support multiple pages, not just the plugin list
    return <div class="page-container">
      <Sidebar />
      <div>
        <SearchBox onInput={this.onSearchInput} />
        <PluginList searchQuery={this.state.searchQuery} />
      </div>
    </div>;
  }
});

// TODO(alpert): Get rid of Backbone?
var Router = Backbone.Router.extend({
  routes: {
    "": "home"
  },

  home: function() {
    React.renderComponent(<Page />, document.body);
  }
});

new Router();
Backbone.history.start({pushState: true});

})();

/** @jsx React.DOM */
(function() {
"use strict";

var clamp = function(num, min, max) {
  return Math.min(Math.max(num, min), max);
};

var scrollToNode = function(domNode) {
  var windowTop = $(window).scrollTop();
  var windowBottom = $(window).height() + windowTop;
  var elementTop = $(domNode).offset().top;
  var elementBottom = elementTop + $(domNode).height();

  if (elementBottom > windowBottom) {
    domNode.scrollIntoView(false /* alignWithTop */);
  } else if (elementTop < windowTop) {
    domNode.scrollIntoView(true /* alignWithTop */);
  }
};

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

  handleKeyUp: React.autoBind(function(e) {
    var input = this.refs.input.getDOMNode();

    if (e.nativeEvent.keyCode === 27 /* escape */) {
      input.blur();
    } else {
      this.props.onInput(input.value);
    }
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
      plugins: [],
      selectedIndex: -1,
      hoverDisabled: false
    };
  },

  componentDidMount: function() {
    this.fetchPlugins(this.props.searchQuery);
    window.addEventListener("keydown", this.onWindowKeyDown, false);
  },

  componentDidUpdate: function(prevProps) {
    if (prevProps.searchQuery !== this.props.searchQuery) {
      this.fetchPlugins(this.props.searchQuery);
    }

    // Scroll to the navigated plugin if available
    if (this.refs.navFocus) {
      scrollToNode(this.refs.navFocus.getDOMNode());
    }
  },

  componentWillUnmount: function() {
    window.removeEventListener("keydown", this.onWindowKeyDown, false);
  },

  resetSelection: function() {
    if (this.state.selectedIndex !== -1) {
      this.setState({selectedIndex: -1});
    }
  },

  onWindowKeyDown: React.autoBind(function(e) {
    // TODO(david): Duplicated code from SearchBox
    // TODO(david): Enter key to go to plugin page
    var tag = e.target.tagName;
    var key = e.keyCode;
    var J_KEYCODE = 74, K_KEYCODE = 75;

    if (tag !== "INPUT" && tag !== "TEXTAREA" &&
        (key === J_KEYCODE || key === K_KEYCODE)) {
      // Go to next or previous plugin
      var direction = (key === J_KEYCODE ? 1 : -1);
      var maxIndex = this.state.plugins.length - 1;
      var newIndex = clamp(this.state.selectedIndex + direction, 0, maxIndex);

      // Disable hover when navigating plugins, because when the screen scrolls,
      // a MouseEnter event will be fired if the mouse is over a plugin, causing
      // the selection to jump back.
      this.setState({selectedIndex: newIndex, hoverDisabled: true});

      // Re-enable hover after a delay
      clearTimeout(this.reenableHoverTimeout);
      this.reenableHoverTimeout = setTimeout(function() {
        this.setState({hoverDisabled: false});
      }.bind(this), 100);
    }
  }),

  onMouseEnter: React.autoBind(function(e, currentTargetId) {
    // TODO(david): Should use e.currentTarget, but it seems like there may be
    //     a react bug that makes this property not available.
    // TODO(david): This is not as quick/snappy as CSS :hover ...
    if (this.state.hoverDisabled) return;
    var currentTarget = document.getElementById(currentTargetId);
    this.setState({selectedIndex: $(currentTarget).index()});
  }),

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
      .map(function(plugin, index) {
        var hasNavFocus = (index === this.state.selectedIndex);
        // TODO(david): Map color from tag/category or just hash of name
        var color = 'accent-' + (index % 9);
        return <li
            class={"plugin" + (hasNavFocus ? " nav-focus" : "")}
            ref={hasNavFocus ? "navFocus" : ""}
            onMouseEnter={this.onMouseEnter}>
          <a href={"#/plugin/" + plugin.name}>
            <div class="hover-bg"></div>
            <h3 class={"plugin-name " + color}>{plugin.name}</h3>
            <span class="by">by</span>
            <span class="author"> Abraham Lincoln</span>
            <div class="github-stars">
              {plugin.github_stars} <i class="icon-star"></i>
            </div>
            <p class="short-desc">{plugin.short_desc}</p>
          </a>
        </li>
      }, this)
      .value();

    return <ul class="plugins">{plugins}</ul>;
  }
});

var Page = React.createClass({
  getInitialState: function() {
    return {searchQuery: ""};
  },

  onSearchInput: React.autoBind(function(query) {
    this.setState({searchQuery: query});
    this.refs.pluginList.resetSelection();
  }),

  render: function() {
    // TODO(alpert): Support multiple pages, not just the plugin list
    return <div class="page-container">
      <Sidebar />
      <div class="content">
        <SearchBox onInput={this.onSearchInput} />
        <div class="keyboard-tips">
          Tip: try <code>/</code> to search and
          <code>ESC</code>, <code>j</code>, <code>k</code> to navigate
        </div>
        <PluginList ref="pluginList" searchQuery={this.state.searchQuery} />
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

/** @jsx React.DOM */
(function() {
"use strict";

// TODO(david): We might want to split up this file eventually.

var clamp = function(num, min, max) {
  return Math.min(Math.max(num, min), max);
};

var capitalizeFirstLetter = function(str) {
  return str.charAt(0).toUpperCase() + str.slice(1);
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
    ], function(category) {
      return <li key={category}>
        <a href="#/blah"><i class="icon-fighter-jet"></i> {category}</a>
      </li>;
    });

    return <div class="sidebar">
      <h1 class="title">
        <a href="/">
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

var Plugin = React.createClass({
  render: function() {
    // TODO(david): Animations on initial render
    var plugin = this.props.plugin;
    if (!plugin || !plugin.name) return <li class="plugin"></li>;

    var hasNavFocus = this.props.hasNavFocus;
    // TODO(david): Map color from tag/category or just hash of name
    var color = "accent-" + (plugin.name.charCodeAt(0) % 9);
    return <li
        class={"plugin" + (hasNavFocus ? " nav-focus" : "")}
        onMouseEnter={this.props.onMouseEnter}>
      <a href={"plugin/" + plugin.name}>
        <div class="hover-bg"></div>
        <h3 class={"plugin-name " + color}>{plugin.name}</h3>
        {plugin.author && <span class="by">by</span>}
        {plugin.author && <span class="author">{" " + plugin.author}</span>}
        {plugin.github_stars && <div class="github-stars">
          {plugin.github_stars} <i class="icon-star"></i>
        </div>}
        <p class="short-desc">{plugin.short_desc}</p>
      </a>
    </li>;
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

  onPluginMouseEnter: function(index, e) {
    // TODO(david): This is not as quick/snappy as CSS :hover ...
    if (this.state.hoverDisabled) return;
    this.setState({selectedIndex: index});
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
      .sortBy("vimorg_rating")
      .sortBy("github_stars")
      .reverse()
      .map(function(plugin, index) {
        var hasNavFocus = (index === this.state.selectedIndex);
        return <Plugin
            ref={hasNavFocus ? "navFocus" : ""}
            key={plugin.id}
            hasNavFocus={hasNavFocus}
            plugin={plugin}
            onMouseEnter={this.onPluginMouseEnter.bind(this, index)} />;
      }, this)
      .value();

    return <ul class="plugins">{plugins}</ul>;
  }
});

// This is the tags widget on the details page.
var Tags = React.createClass({
  getInitialState: function() {
    return {
      isEditing: false
    };
  },

  componentDidMount: function() {
    this.fetchAllTags();
  },

  componentDidUpdate: function() {
    if (this.refs && this.refs.tagInput) {
      this.refs.tagInput.getDOMNode().focus();
    }
  },

  fetchAllTags: function() {
    // TODO(david): This call should be cached across page views (yay
    //     single-page app)
    // TODO(david): this is for autocomplete of tags
    //$.getJSON("/api/tags", function(data) {
      //this.setState(data);
    //}.bind(this));
  },

  onEditBtnClick: React.autoBind(function() {
    this.setState({isEditing: true});
  }),

  onDoneBtnClick: React.autoBind(function() {
    this.setState({isEditing: false});
    this.props.onTagsSave();
  }),

  onRemoveBtnClick: function(tag, e) {
    this.props.onTagsChange(_.without(this.props.tags, tag));
  },

  onKeyUp: React.autoBind(function(e) {
    var key = e.keyCode;
    if (key === 13 /* enter */ || key === 9 /* tab */ ||
        key === 188 /* comma */) {
      var $input = $(this.refs.tagInput.getDOMNode());
      // TODO(david): This needs to use autocomplete
      var tagId = $input.val().replace(/,$/, "").toLowerCase();
      if (!tagId) return;
      $input.val("");
      this.props.onTagsChange(this.props.tags.concat(tagId));
    }
  }),

  render: function() {
    var MAX_TAGS = 5;

    var actionBtn;
    if (this.state.isEditing) {
      actionBtn = <button
          onClick={this.onDoneBtnClick} class="action-btn done-btn">
        <i class="icon-check"></i> Done
      </button>;
    } else {
      actionBtn = <button
          onClick={this.onEditBtnClick} class="action-btn edit-btn">
        <i class="icon-edit"></i> Edit
      </button>;
    }

    var tags = _.map(this.props.tags, function(tag) {
      // TODO(david): Have more info for each tag... # of other plugins maybe,
      //     description maybe
      // TODO(david): Should get tag name from map of tags that we send down.
      var tagName = capitalizeFirstLetter(tag);
      return <li class="tag">
        <a class="tag-link" href={"/tags/" + tag}>{tagName}</a>
        <i onClick={this.onRemoveBtnClick.bind(this, tag)}
            class="icon-remove-sign remove-btn"></i>
      </li>;
    }.bind(this));

    // TODO(david): Tags should be colored appropriately
    // TODO(david): React bug? maxLength and maxlength attrs not recognized
    return <div class={"tags" + (this.state.isEditing ? " editing" : "")}>
      <h3 class="tags-label">Tags</h3>
      <ul class="tags-list">{tags}</ul>
      {this.state.isEditing && this.props.tags.length < MAX_TAGS &&
          <input ref="tagInput" onKeyUp={this.onKeyUp} type="text"
             maxLength="12" class="tag-input" placeholder="Add tag" />}
      {actionBtn}
    </div>;
  }
});

var PluginPage = React.createClass({
  getInitialState: function() {
    return {
      // TODO(david): placeholders
      created_date: 1286809444566,
      updated_date: 1371265409091
    };
  },

  componentDidMount: function() {
    this.fetchPlugin();
  },

  fetchPlugin: function() {
    $.getJSON("/api/plugins/" + this.props.name, function(data) {
      this.setState(data);
    }.bind(this));
  },

  // TODO(david): Should we adopt the "handleTagsChange" naming convention?
  onTagsChange: React.autoBind(function(tags) {
    this.setState({tags: tags});
  }),

  onTagsSave: React.autoBind(function() {
    $.ajax({
      url: "/api/plugins/" + this.props.name + "/tags",
      type: "POST",
      contentType: "application/json",
      dataType: "json",
      data: JSON.stringify({tags: this.state.tags}),
      success: function(data) {
        this.setState({tags: data.tags})
      }.bind(this)
    });
  }),

  render: function() {
    // TODO(david): Should only run markdown on readme.md, not generic long_desc
    var readmeHtml = marked(this.state.long_desc || "");

    return <div class="plugin-page">
      <Plugin plugin={this.state} />

      <div class="row-fluid">
        <div class="span10">
          <div class="row-fluid">

            <div class="span8 accent-box dates">
              <div class="row-fluid">
                <div class="span6">
                  <h3 class="date-label">Created</h3>
                  <div class="date-value">
                    {moment(this.state.created_date).fromNow()}
                  </div>
                </div>
                <div class="span6">
                  <h3 class="date-label">Updated</h3>
                  <div class="date-value">
                    {moment(this.state.updated_date).fromNow()}
                  </div>
                </div>
              </div>
            </div>

            <div class="span4 accent-box links">
              <a href="http://www.vim.org" target="_blank" class="vim-link">
                <i class="vim-icon dark"></i>
                <i class="vim-icon light"></i>
                Vim.org
              </a>
              <a href={this.state.github_url} target="_blank" class="github-link">
                <i class="github-icon dark"></i>
                <i class="github-icon light"></i>
                GitHub
              </a>
            </div>

          </div>
          <div class="row-fluid">

            <div class="span12 install accent-box">
              <h3 class="accent-box-label">Install</h3>
            </div>

          </div>
        </div>

        <div class="span2">
          <Tags tags={this.state.tags} onTagsSave={this.onTagsSave}
              onTagsChange={this.onTagsChange} />
        </div>

      </div>
      <div class="row-fluid">

        <div class="span12 long-desc"
            dangerouslySetInnerHTML={{__html: readmeHtml}}>
        </div>

      </div>
    </div>;
  }
});

var PluginListPage = React.createClass({
  getInitialState: function() {
    return {searchQuery: ""};
  },

  onSearchInput: React.autoBind(function(query) {
    this.setState({searchQuery: query});
    this.refs.pluginList.resetSelection();
  }),

  render: function() {
    return <div>
      <SearchBox onInput={this.onSearchInput} />
      <div class="keyboard-tips">
        Tip: use <code>/</code> to search and
        <code>ESC</code>, <code>j</code>, <code>k</code> to navigate
      </div>
      <PluginList ref="pluginList" searchQuery={this.state.searchQuery} />
    </div>;
  }
});

var Page = React.createClass({
  render: function() {
    return <div class="page-container">
      <Sidebar />
      <div class="content">
        {this.props.content}
      </div>
    </div>;
  }
});

// TODO(alpert): Get rid of Backbone?
var Router = Backbone.Router.extend({
  routes: {
    "": "home",
    "plugin/:name": "plugin"
  },

  _showPage: function(component) {
    React.renderComponent(<Page content={component} />, document.body);
  },

  home: function() {
    this._showPage(<PluginListPage />);
  },

  plugin: function(name) {
    this._showPage(<PluginPage name={name} />);
  }
});

new Router();
Backbone.history.start({pushState: true});

// Hijack internal nav links to use Backbone router to navigate between pages
// Adapted from https://gist.github.com/tbranyen/1142129
if (Backbone.history && Backbone.history._hasPushState) {
  $(document).on("click", "a", function(evt) {
    var href = $(this).attr("href");
    var protocol = this.protocol + "//";

    // Only hijack URL to use Backbone router if it's relative (internal link).
    if (href.substr(0, protocol.length) !== protocol) {
      evt.preventDefault();
      Backbone.history.navigate(href, true);

      // Scroll to top. Chrome has this weird issue where it will retain the
      // current scroll position, even if it's beyond the document's height.
      window.scrollTo(0, 0);
    }
  });
}

})();

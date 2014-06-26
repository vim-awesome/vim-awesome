TODO(david): description of what this repo does

<!-- TODO(david): This section should be in its own file, CONTRIBUTING.md. -->
# Set up

1. Install RethinkDB from http://rethinkdb.com/docs/install/.

1. Install Sass and Compass, which we use to generate our CSS.

  ```sh
  $ gem update --system
  $ gem install bundler
  $ bundle install
  ```

1. Install Python dependencies.

  ```sh
  $ pip install -r requirements.txt
  ```

1. Install Node dependencies.

  ```sh
  $ npm install -g webpack
  $ npm install
  ```

1. Start a local server serving port 5001 by invoking, in the project root
   directory,

  ```sh
  $ make
  ```

1. Seed the database with some test data:

  ```sh
  $ make seed_data
  ```

1. Open the website in your browser!

  ```sh
  $ open http://localhost:5001
  ```

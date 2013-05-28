TODO(david): description of what this repo does

# Setup

1. Install RethinkDB from http://rethinkdb.com/docs/install/.

1. Install Sass and Compass

        $ gem update --system
        $ gem install bundler
        $ bundle install

1. Install Python dependencies.

        $ pip install -r requirements.txt

1. Start a local server serving port 5001 by invoking, in the project root
   directory,

        $ make

1. Seed the database with some test data:

        $ python db/seed.py

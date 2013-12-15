#!/usr/bin/env bash

cd $HOME

# Generate a new directory to clone to
NEW_CLONE=repos/vim-awesome-`date +%s`

# Do the clone
echo "Cloning vim-awesome"
git clone git@github.com:divad12/vim-awesome.git $NEW_CLONE > /dev/null

# TODO(david): Use virtualenv so we don't have to sudo pip install
echo "Installing Python requirements"
sudo pip install -r requirements.txt

echo "Compass compile sass files"
( cd $NEW_CLONE && \
  compass compile --config conf/compass.rb --output-style compressed )

echo "Linking new vim-awesome into place"
ln -snf $NEW_CLONE vim-awesome

# Kill the old gunicorn server, if it exists
# TODO(david): Use a proper daemon.
if [ -e .gunicorn.pid ]
then
    echo "Killing gunicorn"
    kill $(cat .gunicorn.pid)
fi

# Create any new tables and indices.
make ensure_tables_and_indices

echo "Restarting gunicorn"
PYTHONPATH="/home/vim/vim-awesome" \
  FLASK_CONFIG="$HOME/vim-awesome/conf/flask_prod.py" \
  gunicorn --config vim-awesome/conf/gunicorn.py server:app

echo "Removing old vim-awesome clones"
for old in $(ls repos/ | head -n -2)
do
    rm -rf repos/$old
done

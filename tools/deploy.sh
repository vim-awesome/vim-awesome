#!/usr/bin/env bash

cd $HOME

# Generate a new directory to clone to
NEW_CLONE=repos/vim-awesome-`date +%s`

# Do the clone
echo "Cloning vim-awesome"
git clone git@github.com:divad12/vim-awesome.git $NEW_CLONE > /dev/null

echo "Linking new vim-awesome into place"
ln -snf $NEW_CLONE vim-awesome

# Kill the old gunicorn server, if it exists
if [ -e .gunicorn.pid ]
then
    echo "Killing gunicorn"
    kill $(cat .gunicorn.pid)
fi

echo "Restarting gunicorn"
gunicorn --config vim-awesome/conf/gunicorn.py server:app

echo "Restarting nginx"
sudo service nginx restart > /dev/null

echo "Removing old vim-awesome clones"
for old in $(ls repos/ | head -n -2)
do
    rm -rf repos/$old
done

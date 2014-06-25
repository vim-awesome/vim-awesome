#!/usr/bin/env bash

# Updates and restarts the vim-awesome webapp on the machine.
# Can be run either directly on the machine, or by running
#
# $ cat deploy.sh | ssh vim@vimawesome.com DEPLOYER=`whoami` sh
#
# Env Args:
#    $DEPLOYER: `whoami`

cd $HOME

# Generate a new directory to clone to
NEW_CLONE=repos/vim-awesome-`date +%s`

# Do the clone
echo "Cloning vim-awesome"
git clone git@github.com:divad12/vim-awesome.git $NEW_CLONE > /dev/null

# TODO(david): Use virtualenv so we don't have to sudo pip install
echo "Installing Python requirements"
sudo pip install -r $NEW_CLONE/requirements.txt

echo "Installing Node requirements"
npm install

echo "Precompile JSX and bundle JS files"
( cd $NEW_CLONE && NODE_ENV=production node_modules/.bin/webpack --config conf/webpack.config.js )

echo "Compass compile sass files"
( cd $NEW_CLONE && \
  compass compile --config conf/compass.rb --output-style compressed )

echo "Linking in secrets.py"
( cd $NEW_CLONE && ln -s $HOME/secrets.py . )

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
( cd $NEW_CLONE && make ensure_tables_and_indices )

# TODO(david): Log files locations should be consolidated in the Python config
echo "Restarting gunicorn"
PYTHONPATH="/home/vim/vim-awesome" \
  FLASK_CONFIG="$HOME/vim-awesome/conf/flask_prod.py" \
  gunicorn \
  --config vim-awesome/conf/gunicorn.py server:app \
  --access-logfile logs/gunicorn/access-log \
  --error-logfile logs/gunicorn/error-log

echo "Removing old vim-awesome clones"
for old in $(ls repos/ | head -n -2)
do
    rm -rf repos/$old
done

PYTHONPATH=$NEW_CLONE python $NEW_CLONE/tools/notify_deploy.py $DEPLOYER

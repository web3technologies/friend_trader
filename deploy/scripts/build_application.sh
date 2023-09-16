#!/bin/bash

echo "Creating the friend_trader Application"

while getopts ":e:" opt; do
  case $opt in
    e)
      environment=$OPTARG
      ;;
    *)
      echo 'Error in command line parsing' >&2
      exit 1
  esac
done

if [ -z "$environment" ]; then
        echo 'Missing -e' >&2
        exit 1
fi

rm -rf /applications/friend_trader/
mkdir /applications/friend_trader/

echo "BUILDING"

workspace_name="friend_trader_${environment}"
jenkins_proj_path="/var/lib/jenkins/workspace/$workspace_name"
JENKINS_VENV_DIR=$jenkins_proj_path/venv 

python -m venv $JENKINS_VENV_DIR
echo "VENV created"
. "${JENKINS_VENV_DIR}/bin/activate"
pip install --upgrade pip
pip install $jenkins_proj_path .
pip install wheel
python setup.py bdist_wheel 
deactivate
echo "*** Purse Backend Module Created***"

echo "Building the application"
application_build_path=/applications/friend_trader.tar
python -m venv /applications/friend_trader/venv
. "/applications/friend_trader/venv/bin/activate"
pip install --upgrade pip
pip install wheel
pip install $jenkins_proj_path/dist/friend_trader-0.1.0-py3-none-any.whl
cp $jenkins_proj_path/manage.py /applications/friend_trader/
cp $jenkins_proj_path/friend_trader/friend_trader/wsgi.py /applications/friend_trader/
cp "/var/lib/jenkins/envs/friend_trader_${environment}/.env" /applications/friend_trader/
echo "Application packages installed into Venv"

echo "Gzipping Application"
tar -czf /tmp/friend_trader.tar /applications/friend_trader/

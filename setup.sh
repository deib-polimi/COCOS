#!/usr/bin/env bash

cd components

cd actuator_controller
rm -rf env
virtualenv env
source env/bin/activate
pip install -r requirements.txt

cd ../containers_manager
rm -rf env
virtualenv env
source env/bin/activate
pip install -r requirements.txt

cd ../dashboard
rm -rf env
virtualenv env
source env/bin/activate
pip install -r requirements.txt

cd ../dispatcher
rm -rf env
virtualenv env
source env/bin/activate
pip install -r requirements.txt

cd ../requests_store
rm -rf env
virtualenv env
source env/bin/activate
pip install -r requirements.txt
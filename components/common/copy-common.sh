#!/usr/bin/env bash

mkdir ../controller/models/
cp req.py ../controller/models/req.py
cp container.py ../controller/models/container.py
cp model.py ../controller/models/model.py
cp device.py ../controller/models/device.py

mkdir ../containers_manager/models/
cp device.py ../containers_manager/models/device.py
cp model.py ../containers_manager/models/model.py
cp container.py ../containers_manager/models/container.py

mkdir ../dispatcher/models/
cp device.py ../dispatcher/models/device.py
cp req.py ../dispatcher/models/req.py
cp model.py ../dispatcher/models/model.py
cp container.py ../dispatcher/models/container.py

mkdir ../requests_store/models/
cp req.py ../requests_store/models/req.py
cp model.py ../requests_store/models/model.py

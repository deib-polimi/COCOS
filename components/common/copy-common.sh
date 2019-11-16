#!/usr/bin/env bash

mkdir ../controller/models/
cp req.py ../controller/models/req.py
cp device.py ../controller/models/device.py
cp container.py ../controller/models/container.py
cp model.py ../controller/models/model.py

mkdir ../containers_manager/models/
cp device.py ../containers_manager/models/device.py
cp model.py ../containers_manager/models/model.py
cp container.py ../containers_manager/models/container.py

mkdir ../dispatcher/models/
cp req.py ../dispatcher/models/req.py
cp device.py ../dispatcher/models/device.py
cp model.py ../dispatcher/models/model.py
cp container.py ../dispatcher/models/container.py
cp queues_policies.py ../dispatcher/models/queues_policies.py

mkdir ../requests_store/models/
cp req.py ../requests_store/models/req.py
cp device.py ../requests_store//models/device.py
cp model.py ../requests_store/models/model.py
cp container.py ../requests_store/models/container.py

mkdir ../../simulations/gpus_simulation/models/
cp queues_policies.py ../../simulations/gpus_simulation/models/queues_policies.py
cp model.py ../../simulations/gpus_simulation/models/model.py

mkdir ../benchmark/models/models/
cp req.py ../benchmark/models/models/req.py
cp device.py ../benchmark/models/models/device.py
cp model.py ../benchmark/models/models/model.py

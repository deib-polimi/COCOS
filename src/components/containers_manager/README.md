# Containers Manager

- reads containers list from a configuration files ("config.yml")
- communicates with the actuators on each node to get the containers ids
- exposes endpoints to retrieve information about models and containers

### Init
```
virtualenv env
source env/bin/activate
pip install -r requirements.txt
```

### Run
```
python main.py
```

### Endpoints
See "rest-client.rest" for examples 

##### GET /
Get the status of the component

##### GET /models
Get the loaded models

##### GET /containers
Get the loaded containers

##### (draft) POST /models
Add a new model

##### (draft) POST /containers
Add a new container

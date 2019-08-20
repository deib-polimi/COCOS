# Dispatcher
This component:

- reads containers from a configuration files ("config.yml")
- communicates with the actuators on each node to associate models with running containers
- logs incoming requests and outcoming responses
- initializes the dispatcher object that is responsible for routing the requests
- starts a web server
    + where requests can be sent
    + where information about containers and requests can be retrieved (live dashboard)


### Init
```
virtualenv env
source env/bin/activate
pip install -r requirements.txt
```

### Run
```
python3 main.py
```

### Endpoints
See "rest-client.rest" for examples 

##### GET /
Get the component status

##### GET /models
Get the loaded models

##### GET /requests
Get the logged requests

##### GET /metrics
Get metrics about models

##### POST /predict
Send a new request

##### (draft) POST /model
Add a new model


### Dashboard

The dashboard is used to show live information about:

- containers
- metrics
- requests

It is reachable at: http://localhost:5000/static/dashboard/index.html


### Dispatcher
It dispatches the incoming request using a policy.

Available policies:

- round robin
- random
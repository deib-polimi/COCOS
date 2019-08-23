# Dispatcher
This component:

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
gunicorn -w 1 "main:create_app(verbose=1)"
```

### Endpoints
See "rest-client.rest" for examples 

##### GET /
Get the status of the component

##### GET /requests
Get the logged requests

##### GET /metrics
Get metrics about models

##### POST /predict
Send a new request


### Dashboard

The dashboard is used to show live information about:

- containers
- metrics
- requests

It is reachable at: http://localhost:8000/static/dashboard/index.html


### Dispatcher
It dispatches the incoming request using a policy.

Available policies:

- round robin
- random
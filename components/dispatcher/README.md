# Dispatcher
This component takes as input requests and dispatches them to devices.

<img src="../../doc/img/DispatcherView.png">

The dispatcher initializes the information about the models and containers using the services provided by the *Containers Manager*. Furthermore, it sends logged requests to the *Requests Store*.

In particular, for every request the dispatcher:

1. logs the incoming request, adding the request to the requests queue (the request is in the *created* state)
2. selects the device where forward the request using a dispatching policy
3. forwards the request to that device
3. when a response is received, it adds the request to the requests queue (in the waiting *completed* state)
4. forwards the response to the client

A thread is started at the beginning to consume the queue of requests that have to be sent to the *Requests Store*.

#### Dispatching policy
The dispatcher reads the models metadata to find out which devices are available and where the request can be forwarded.

Policies:

1. Round Robin
2. Random
3. (not implemented yet) Probabilities:
The request will be forwarded to the device i with probability P_i.
Sum P_i = 1

The dispatcher should use only devices with quotas > 0 for that model.

## Run
### Init
```
virtualenv env
source env/bin/activate
pip install -r requirements.txt
```
### Start
```
gunicorn -w <num_of_workers> "main:create_app(containers_manager="<containers_manager_host>", requests_store="<requests_store_host>",
verbose=1)"
```

Arguments:

- number of workers
- containers manager host
- requests store host
- verbose

## Required interfaces
The dispatcher requires:

- *Requests Store*: to store the information about the requests
- *Containers Manage*: to get information about models and containers

## Endpoints
See "rest-client.rest" for examples 

DEFAULT PORT (gunicorn): 8000

##### GET /
Get the status of the component

##### POST /predict
Send a new request


#### Improvements
- resubmit the request if timeout
- reqs cache: save the response of a request to avoid recomputing
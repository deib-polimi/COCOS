# Architecture Details
<img src="./doc/img/GeneralView.png">

## Components
### Dispatcher
This component takes as input requests and dispatches them to devices.
[More information here](./components/dispatcher/)

### Containers Manager
This component manages containers and models and all their relative information.
[More information here](./components/containers_manager/)

### Requests Store
This component takes care of requests. It is responsible for storing the information about the requests.
[More information here](./components/requests_store/)

### Controller
(not implemented yet)

This component interacts with the actuator to control nodes.
[More information here](./components/controller/)

### Actuator
This component is used to control the resources of nodes.
[More information here](./components/actuator/)

### Dashboard
This component is used to reach a dashboard where information about the system can be retrieved.
[More information here](./components/dashboard/)


## Deployments
[More information here](./deployments/)

## Models
[More information here](./models/)

## Testing
[More information here](./testing/)


## Pod
### Brief description
The pod contains all the containers running TF serving and the container for the actuator.

<img src="./doc/img/PodView.png">

Where N_m is the number of models

### Description
In every pod are deployed:

- an actuator inside a container
- a TF serving container for each model for the CPU
- a TF serving container for each GPU serving all the models

Given N_m the number of served models and N_g the number of GPUs, the total number of containers for each node is: N_containers =  N_m + N_g

Each TF serving container exposes an RESTful API and gRPC.

## Container initialization
// TODO: are the given models fixed or they could change at runtime?

- static models
- dynamic models

### Static models
1. Produce a K8s deployment, given a config file with the same information in *Containers Manager*
2. populate *Containers Manager*

### Dynamic models
Starting with an empty Models Metadata:

- every time a new model is added:
    + add a new CPU container associated to the model with the given quota if available
    + updates the models available on GPUs with TF serving API
- every time a new model is removed:
    + remove the CPU container associated to the model and release the quota
    + updates the models available on GPUs with TF serving API
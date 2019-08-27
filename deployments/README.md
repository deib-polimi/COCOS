# Deployment
## Pod
The pod contains all the containers running TF serving and the container for the actuator.

<img src="../doc/img/PodView.png">

Where N_m is the number of models

### Description
In every pod are deployed:

- an actuator inside a container
- a TF serving container for each model for the CPU
- a TF serving container for each GPU serving all the models

Given N_m the number of served models and N_g the number of GPUs, the total number of containers for each node is: N_containers =  N_m + N_g

Each TF serving container exposes an RESTful API.

## K8s
K8s files to deploy the system:

- deployment-tfcontrolled: this configuration file deploys the containers for the CPU and GPUs and the actuator. Two volumes are mounted:
    + shared-models: the host shares the served model with the container
    + docker-sock: to allow the actuator to control Docker of the host

- service-tfcontrolled: it is used to expose the endpoints of the containers



### Minikube
- https://kubernetes.io/docs/tasks/tools/install-minikube/


```
minikube start
```


- Build the actuator image with Docker of minikube so that
it is visible to K8s  
```
eval $(minikube docker-env)
cd components/actuator/    
docker build -t tfcontrolled-actuator:local .
```


- Create the K8s deployment and service
```
kubectl create -f deployment-tfcontrolled.yml
kubectl create -f service-tfcontrolled.yml
kubectl get po,no,deploy,svc
```

#### Launch
1. the *Containers Manager*. [More](../components/containers_manager/)
2. the *Requests Store*. [More](../components/requests_store/)
3. the *Dispatcher*. [More](../components/dispatcher/)


#### Test
[More](../testing/)


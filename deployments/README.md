# Deployment

### Minikube
- https://kubernetes.io/docs/tasks/tools/install-minikube/


```
minikube start
```


- Build the actuator image with Docker of minikube so that
it is visible to K8s  
```
eval $(minikube docker-env)
cd src/components/actuator/    
docker build -t tfcontrolled-actuator:local .
```


- Create the K8s deployment and service
```
kubectl create -f deployment-tfcontrolled.yml
kubectl create -f service-tfcontrolled.yml
kubectl get po,no,deploy,svc
```

- Launch the dispatcher (see the README of the dispatcher)

- Test with testing/client.py
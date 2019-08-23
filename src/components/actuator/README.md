# Actuator
This component runs on every node. It uses the dockerd of the node to

- retrieve information about containers
- set limits on container's resources

### Endpoints
See "rest-client.rest" for examples 

##### GET /
Get the status of the component

##### GET /containers
Get the list of running containers

##### POST /containers/<string:container_id>
Set limits on container's resources


#### Required modules 
- Docker for Python https://docker-py.readthedocs.io/en/stable/
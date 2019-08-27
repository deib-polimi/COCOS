# Testing

## Client.py
This script reads JSON requests from a file and posts R requests to the given target using T threads

Example of usage
```
python3 client.py --target "localhost:8000" --requests 1000 --req "./half_plus_two.json" --threads 4 --verbose 1
```

 Arguments:
 
 - target: the host where to send the requests
 - requests: the number of requests to post
 - req: the file with the JSON requests
 - threads: the number of threads to use
 - verbose: to enable / disable printing
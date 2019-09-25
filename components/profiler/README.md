# Profiler
This component is used to profile models.


A profiler can be implemented extending the base Profiler class.

### Profiler class
The profiler class provides some useful functions:
- ```before_profiling```: executed before profiling is started, e.g.:
    - load the requests data,
    - perform some pre profile works
    - warm up the model, etc. 
- ```after_profiling```: executed after profiling is done, e.g.:
    - save profiling data.
    - elaborate response data,
    - save response, etc.
- ```load_requests_from_file```: used to load test requests from a file
- ```warm_up_model```: used to perform some requests in order to warm-up the model

Variables:
- ```self.bench_data```: it is the array of requests used to profile the model.

### Profiling parameters
- ```serving_host```: the TF Serving endpoint
- ```bench_folder```: the folder where the requests file is located
(with the same name of the model)
- ```repeat_measure```: the number of times needed to repeat the response time measure
- ```warm_up_times```: the number of requests needed to warm up the model


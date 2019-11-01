# Benchmark
This component is used to benchmark the system and to profile models.

It can perform a benchmark of the system or it can be used to profile a single model.
A benchmark can be implemented extending the base Benchmark class.

## Benchmark Class
### Init
- init the benchmark with a parameters file containing information about how to run the benchmark

#### Profiling parameters
- ```endpoints_benchmark```: the endpoints of the dispatchers
- ```endpoint_profiler```: the TF Serving endpoint for profiling the model
- ```bench_folder```: the folder where are the data for benchmarking and profiling
- ```validation_folder```: the folder where are the data for validation
- ```repeat_measure```: the number of times needed to repeat the response time measure
- ```warm_up_times```: the number of requests needed to warm up the model

### Benchmark
- start a benchmark with ```profiler.run_benchmark()```: it will profile the system using the data into the folder
specified in the parameters file
- ```before_benchmark()``` is called before the benchmark is started
- ```after_benchmark()``` is called after the benchmark is completed

### Profiling
- start a profiling with ```profiler.run_profiling()```: it will profile the model using the data into the folder
specified in the parameters file
- ```before_profiling()``` is called before the profiling is started
- ```after_profiling()``` is called after the profiling is completed

### Validation
- start a validation with ```profiler.validate()```: it will validate the model using the data into the folder
given in the parameters file
- ```before_validate()``` is called before the validation is started
- ```after_validate()``` is called after the validation is completed
- ```show_data()``` is called before submitting the request, e.g. to show the input data
- ```show_response()``` is called after receiving the response, e.g. to show the output data

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

### Class attributes
- ```self.bench_data```: it is the list of requests used to profile the model
- ```self.validate_data```: it is the list of requests used to validate the model

Each entry in the lists is a dict with the following fields:
- ```"data"```: the raw data read
- ```"request```: the data converted in a ready to be submitted request


## ImageNet Benchmark
It is a specialized benchmark used with imagenet models such as AlexNet, GooLeNet, VGG16.



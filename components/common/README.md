# Common

## Models
- name
- version
- sla

Example:

```json
[
  {
    "name": "half_plus_two",
    "sla": 1000,
    "version": 1
  },
  {
    "name": "half_plus_three",
    "sla": 100,
    "version": 1
  },
  {
    "name": "resnet_NHWC",
    "sla": 100,
    "version": 1
  }
]
```

## Containers
- model
- version
- container
- container_id
- active
- device
- node
- endpoint
- port
- quota

```json
[
  {
    "active": true,
    "container": "tfserving-cpu-0",
    "container_id": "0058c15a6175760d509daa8871edee6b7e9c9fcf6baeb3012835640d2654791f",
    "device": 0,
    "endpoint": "http://192.168.99.103:30001",
    "model": "half_plus_two",
    "node": "192.168.99.103",
    "port": 30001,
    "quota": 100000,
    "version": 1
  },
  {
    "active": true,
    "container": "tfserving-cpu-1",
    "container_id": "cb1c38bedb2dffa82924c27979d80fe7d53b22f4addd5d20742a7a0edc8be355",
    "device": 0,
    "endpoint": "http://192.168.99.103:30002",
    "model": "half_plus_three",
    "node": "192.168.99.103",
    "port": 30002,
    "quota": 100000,
    "version": 1
  },
  {
    "active": true,
    "container": "tfserving-cpu-2",
    "container_id": "ae8c641bcc1de1b5d7b52c5160e3506ddb82e90be069a6991adc65bbed77fcce",
    "device": 0,
    "endpoint": "http://192.168.99.103:30003",
    "model": "resnet_NHWC",
    "node": "192.168.99.103",
    "port": 30003,
    "quota": 100000,
    "version": 1
  },
  {
    "active": true,
    "container": "tfserving-gpu-0",
    "container_id": "59640cc3a76e8831fa438c1b73b2e0e63ceb9e57b87306786e163e10bda2c3be",
    "device": 1,
    "endpoint": "http://192.168.99.103:30004",
    "model": "all",
    "node": "192.168.99.103",
    "port": 30004,
    "quota": 100000,
    "version": 1
  }
]
```

## Requests
- id
- model
- version
- instances
- node
- container
- ts_in
- ts_out
- resp_time
- response
- state

```json
[
  {
    "container": "tfserving-cpu-0",
    "id": "bf7a9924-2e3a-476e-a70e-5d6d81870084",
    "instances": [
      1.0,
      2.0,
      3.0
    ],
    "model": "half_plus_two",
    "node": "192.168.99.103",
    "resp_time": 0.25482821464538574,
    "response": "{\n    \"predictions\": [2.5, 3.0, 3.5\n    ]\n}",
    "state": 2,
    "ts_in": 1566830435.1093774,
    "ts_out": 1566830435.3642056,
    "version": 1
  },
  {
    "container": "tfserving-gpu-0",
    "id": "e20db45e-5188-4d89-a3f2-30e077529020",
    "instances": [
      1.0,
      2.0,
      3.0
    ],
    "model": "half_plus_two",
    "node": "192.168.99.103",
    "resp_time": 0.0153350830078125,
    "response": "{\n    \"predictions\": [2.5, 3.0, 3.5\n    ]\n}",
    "state": 2,
    "ts_in": 1566830440.435635,
    "ts_out": 1566830440.4509702,
    "version": 1
  }
]
```
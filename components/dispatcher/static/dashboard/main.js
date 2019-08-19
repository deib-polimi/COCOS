function deviceFormatter(data) {
    return data === 0 ? "CPU" : "GPU";
}

function floatFormatter(data) {
    return data == null ? null : data.toFixed(6);
}

$('#table-models').bootstrapTable({
    autoRefresh: true,
    autoRefreshInterval: 1,
    url: 'http://localhost:5000/models',
    pagination: false,
    search: true,
    columns: [{
        field: 'model',
        title: 'model'
    }, {
        field: 'container',
        title: 'container'
    }, {
        field: 'container_id',
        title: 'container_id'
    }, {
        field: 'version',
        title: 'version'
    }, {
        field: 'active',
        title: 'active'
    }, {
        field: 'device',
        title: 'device',
        formatter: deviceFormatter
    }, {
        field: 'node',
        title: 'node'
    }, {
        field: 'port',
        title: 'port'
    }, {
        field: 'endpoint',
        title: 'endpoint'
    }, {
        field: 'quota',
        title: 'quota'
    }]
})


$('#table-requests').bootstrapTable({
    autoRefresh: true,
    autoRefreshInterval: 1,
    url: 'http://localhost:5000/requests',
    pagination: true,
    search: true,
    columns: [{
        field: 'id',
        title: 'id'
    }, {
        field: 'model',
        title: 'model'
    }, {
        field: 'node',
        title: 'node'
    }, {
        field: 'container',
        title: 'container'
    }, {
        field: 'instances',
        title: 'instances'
    }, {
        field: 'response',
        title: 'response'
    }, {
        field: 'ts_in',
        title: 'ts_in'
    }, {
        field: 'ts_out',
        title: 'ts_out'
    }, {
        field: 'resp_time',
        title: 'resp_time',
        formatter: floatFormatter
    }]
})


$('#table-metrics').bootstrapTable({
    autoRefresh: true,
    autoRefreshInterval: 1,
    url: 'http://localhost:5000/metrics',
    pagination: false,
    search: false,
    columns: [{
        field: 'model',
        title: 'model'
    }, {
        field: 'container',
        title: 'container'
    }, {
        field: 'metrics.completed',
        title: 'metrics.completed'
    }, {
        field: 'metrics.waiting',
        title: 'metrics.waiting'
    }, {
        field: 'metrics.avg',
        title: 'metrics.avg',
        formatter: floatFormatter
    }, {
        field: 'metrics.dev',
        title: 'metrics.dev',
        formatter: floatFormatter
    }, {
        field: 'metrics.min',
        title: 'metrics.min',
        formatter: floatFormatter
    }, {
        field: 'metrics.max',
        title: 'metrics.max',
        formatter: floatFormatter
    }]
})
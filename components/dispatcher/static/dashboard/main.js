function deviceFormatter(data) {
    return data === 0 ? "CPU" : "GPU";
}

function floatFormatter(data) {
    return data == null ? null : data.toFixed(6);
}

function containerIdFormatter(data) {
    return data.slice(0, 12)
}


$('#table-models').bootstrapTable({
    autoRefresh: true,
    autoRefreshInterval: 1,
    url: 'http://localhost:5000/models',
    pagination: false,
    search: true,
    columns: [{
        field: 'model',
        title: 'model',
        sortable: true
    }, {
        field: 'container',
        title: 'container',
        sortable: true
    }, {
        field: 'container_id',
        title: 'container_id',
        formatter: containerIdFormatter,
        sortable: true
    }, {
        field: 'version',
        title: 'version',
        sortable: true
    }, {
        field: 'active',
        title: 'active',
        sortable: true
    }, {
        field: 'device',
        title: 'device',
        formatter: deviceFormatter,
        sortable: true
    }, {
        field: 'node',
        title: 'node',
        sortable: true
    }, {
        field: 'port',
        title: 'port',
        sortable: true
    }, {
        field: 'endpoint',
        title: 'endpoint',
        sortable: true
    }, {
        field: 'quota',
        title: 'quota',
        sortable: true
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
        title: 'id',
        sortable: true
    }, {
        field: 'model',
        title: 'model',
        sortable: true
    }, {
        field: 'node',
        title: 'node',
        sortable: true
    }, {
        field: 'container',
        title: 'container',
        sortable: true
    }, {
        field: 'instances',
        title: 'instances',
    }, {
        field: 'response',
        title: 'response',
    }, {
        field: 'ts_in',
        title: 'ts_in',
        sortable: true
    }, {
        field: 'ts_out',
        title: 'ts_out',
        sortable: true
    }, {
        field: 'resp_time',
        title: 'resp_time',
        formatter: floatFormatter,
        sortable: true
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
        title: 'model',
        sortable: true
    }, {
        field: 'container',
        title: 'container',
        sortable: true
    }, {
        field: 'metrics.completed',
        title: 'metrics.completed',
        sortable: true
    }, {
        field: 'metrics.waiting',
        title: 'metrics.waiting',
        sortable: true
    }, {
        field: 'metrics.avg',
        title: 'metrics.avg',
        formatter: floatFormatter,
        sortable: true
    }, {
        field: 'metrics.dev',
        title: 'metrics.dev',
        formatter: floatFormatter,
        sortable: true
    }, {
        field: 'metrics.min',
        title: 'metrics.min',
        formatter: floatFormatter,
        sortable: true
    }, {
        field: 'metrics.max',
        title: 'metrics.max',
        formatter: floatFormatter,
        sortable: true
    }]
})
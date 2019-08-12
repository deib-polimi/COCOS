$('#table-models').bootstrapTable({
    autoRefresh: true,
    autoRefreshInterval: 1,
    url: 'http://localhost:5000/models',
    pagination: false,
    search: true,
    columns: [{
        field: 'id',
        title: 'id'
    }, {
        field: 'active',
        title: 'active'
    }, {
        field: 'device',
        title: 'device'
    }, {
        field: 'endpoint',
        title: 'endpoint'
    }, {
        field: 'model',
        title: 'model'
    }, {
        field: 'version',
        title: 'version'
    }, {
        field: 'node',
        title: 'node'
    }, {
        field: 'port',
        title: 'port'
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
        field: 'metrics.completed',
        title: 'metrics.completed'
    }, {
        field: 'metrics.waiting',
        title: 'metrics.waiting'
    }, {
        field: 'metrics.avg',
        title: 'metrics.avg'
    }, {
        field: 'metrics.dev',
        title: 'metrics.dev'
    }, {
        field: 'metrics.min',
        title: 'metrics.min'
    }, {
        field: 'metrics.max',
        title: 'metrics.max'
    }]
})
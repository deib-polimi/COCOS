function deviceFormatter(data) {
    return data === 0 ? "CPU" : "GPU";
}

function floatFormatter(data) {
    return data == null ? null : data.toFixed(6);
}

function containerIdFormatter(data) {
    return data == null ? null : data.slice(0, 12);
}

function responseFormatter(data) {
    return data != null && data.length > 200 ? data.slice(0, 200) + "..." : data
}

function stateFormatter(data) {
    if (data === 0)
        return "CREATED";
    if (data === 1)
        return "WAITING";
    if (data === 2)
        return "COMPLETED";
    if (data === 3)
        return "ERROR";
}

function deviceFormatter(data) {
    if (data === null)
        return data;
    if (data === 0)
        return "CPU";
    if (data === 1)
        return "GPU";
}

function resetRequestsStore() {
    $.ajax({
        url: host_requests + '/requests',
        type: 'DELETE',
        success: function (result) {
        }
    });
}

host_containers = 'http://localhost:5001';
host_requests = 'http://localhost:5002';

$('#table-models').bootstrapTable({
    autoRefresh: true,
    autoRefreshInterval: 1,
    url: host_containers + '/models',
    pagination: false,
    search: true,
    columns: [{
        field: 'name',
        title: 'name',
        sortable: true
    }, {
        field: 'version',
        title: 'version',
        sortable: true
    }, {
        field: 'sla',
        title: 'sla',
        sortable: true
    }, {
        field: 'alpha',
        title: 'alpha',
        sortable: true
    }]
});

$('#table-containers').bootstrapTable({
    autoRefresh: true,
    autoRefreshInterval: 1,
    url: host_containers + '/containers',
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
});


$('#table-requests').bootstrapTable({
    autoRefresh: true,
    autoRefreshInterval: 1,
    url: host_requests + '/requests',
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
        field: 'version',
        title: 'version',
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
        field: 'device',
        title: 'device',
        sortable: true,
        formatter: deviceFormatter
    }, {
        field: 'instances',
        title: 'instances',
    }, {
        field: 'state',
        formatter: stateFormatter,
        title: 'state',
    }, {
        field: 'response',
        title: 'response',
        formatter: responseFormatter
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
});


$('#table-metrics').bootstrapTable({
    autoRefresh: true,
    autoRefreshInterval: 1,
    url: host_requests + '/metrics',
    pagination: false,
    search: false,
    columns: [{
        field: 'model',
        title: 'model',
        sortable: true
    }, {
        field: 'version',
        title: 'version',
        sortable: true
    }, {
        field: 'metrics.completed',
        title: 'metrics.completed',
        sortable: true
    }, {
        field: 'metrics.created',
        title: 'metrics.created',
        sortable: true
    }, {
        field: 'metrics.on_gpu',
        title: 'metrics.on_gpu',
        sortable: true
    }, {
        field: 'metrics.on_cpu',
        title: 'metrics.on_cpu',
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
});

/*
$(function () {
    var ctx = document.getElementById('graph').getContext('2d');
    var chart = new Chart(ctx, {
        // The type of chart we want to create
        type: 'line',

        // The data for our dataset
        data: {
            labels: ['January', 'February', 'March', 'April', 'May', 'June', 'July'],
            datasets: [{
                label: 'My First dataset',
                backgroundColor: 'rgb(255, 99, 132)',
                borderColor: 'rgb(255, 99, 132)',
                data: [0, 10, 5, 2, 20, 30, 45]
            }]
        },

        // Configuration options go here
        options: {}
    });
});
*/
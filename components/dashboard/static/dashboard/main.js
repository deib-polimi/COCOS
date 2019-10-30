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
host_controller = 'http://localhost:5003';

$('#table-controller-log').bootstrapTable({
    autoRefresh: true,
    autoRefreshInterval: 5,
    url: host_controller + '/logs',
    pagination: true,
    search: true,
    columns: [{
        field: 'ts',
        title: 'ts',
        sortable: true
    }, {
        field: 'date',
        title: 'date',
        sortable: true
    }, {
        field: 'msg',
        title: 'msg',
        sortable: true
    }]
});

$('#table-models').bootstrapTable({
    autoRefresh: true,
    autoRefreshInterval: 10,
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
    }, {
        field: 'profiled_rt',
        title: 'profiled_rt',
        sortable: true
    }]
});

$('#table-containers').bootstrapTable({
    autoRefresh: true,
    autoRefreshInterval: 10,
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
    autoRefreshInterval: 2,
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


$('#table-metrics-model').bootstrapTable({
    autoRefresh: true,
    autoRefreshInterval: 1,
    url: host_requests + '/metrics/model',
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

$('#table-metrics-container').bootstrapTable({
    autoRefresh: true,
    autoRefreshInterval: 1,
    url: host_requests + '/metrics/container',
    pagination: false,
    search: false,
    columns: [{
        field: 'container',
        title: 'container',
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

function getRandomColor() {
    var o = Math.round, r = Math.random, s = 255;
    return 'rgba(' + o(r() * s) + ',' + o(r() * s) + ',' + o(r() * s) + ',' + 0.5 + ')';
}


$(function () {
    let tick = 0;
    let max_samples = 100;

    // get the data
    $.get(host_requests + '/metrics/model', function (data) {
        let labels = [0];
        let models = [];
        let datasets_avg = [];
        let datasets_ql = [];

        for (let i = 0; i < data.length; i++) {
            let model = data[i].model;
            models.push(model);
            let color = getRandomColor();
            datasets_avg.push({borderColor: color, backgroundColor: color, label: model, data: [data[i].metrics.avg]});
            datasets_ql.push({borderColor: color, backgroundColor: color, label: model, data: [data[i].metrics.created]});
        }

        let ctx_rt = document.getElementById('chart-rt').getContext('2d');
        let chart_rt = new Chart(ctx_rt, {
            type: 'line',
            data: {
                labels: labels,
                datasets: datasets_avg
            },
            options: {
                animation: false,
                scales: {
                    yAxes: [{
                        ticks: {
                            beginAtZero: true
                        }
                    }]
                }
            }
        });

        let ctx_ql = document.getElementById('chart-ql').getContext('2d');
        let chart_ql = new Chart(ctx_ql, {
            type: 'line',
            data: {
                labels: labels,
                datasets: datasets_ql
            },
            options: {
                animation: false,
                scales: {
                    yAxes: [{
                        ticks: {
                            beginAtZero: true
                        }
                    }]
                }
            }
        });

        // update
        setInterval(function () {
            $.get(host_requests + '/metrics/model', function (data) {
                let avgs = {};
                let ql = {};

                for (let i = 0; i < data.length; i++) {
                    let model = data[i].model;
                    avgs[model] = data[i].metrics.avg;
                    ql[model] = data[i].metrics.created;
                }

                chart_rt.data.labels.push(++tick);

                if (chart_rt.data.labels.length > max_samples) {
                    chart_rt.data.labels.shift();
                    chart_ql.data.labels.shift();
                }

                chart_rt.data.datasets.forEach((dataset) => {
                    dataset.data.push(avgs[dataset.label]);
                    if (dataset.data.length > max_samples) {
                        dataset.data.shift();
                    }
                });

                chart_ql.data.datasets.forEach((dataset) => {
                    dataset.data.push(ql[dataset.label]);
                    if (dataset.data.length > max_samples) {
                        dataset.data.shift();
                    }
                });

                chart_rt.update();
                chart_ql.update();
            });
        }, 1000);
    });


});

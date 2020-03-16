function get_doughnut_config(label, data_labels, data_values, data_colors) {
    // configurations for the doughnut chart
    return {
        // The type of chart we want to create
        type: 'doughnut',

        // The data for our dataset
        data: {
            labels: data_labels,
            datasets: [
                {
                    backgroundColor: data_colors,
                    borderColor: data_colors,
                    data: data_values,
                    fill: true,
                },
            ]
        },

        // Configuration options go here
        options: {
            responsive: true,
            title: {
                display: true,
                text: label + ' users'
            },
            legend: {
                display: true,
                position: 'right',
            },
            tooltips: {
                callbacks: {
                    label: function(item, data) {
                    return data.labels[item.index] +": "+ data.datasets[item.datasetIndex].data[item.index] +" ("+ Math.round((data.datasets[item.datasetIndex].data[item.index]/data_values.reduce((a, b) => a + b, 0))*100) +"%)";
                    }
                }
            },
        }
    }
}


function get_bar_config(label, label_txt, dataset_label, data_labels, data_values, data_colors) {
    // configurations for the bar chart
    return {
        // The type of chart we want to create
        type: 'bar',

        // The data for our dataset
        data: {
            labels: data_labels,
            datasets: [
                {
                    label: dataset_label,
                    backgroundColor: data_colors,
                    borderColor: data_colors,
                    data: data_values,
                    fill: true,
                },
            ]
        },

        // Configuration options go here
        options: {
            responsive: true,
            title: {
                display: true,
                text: label + ' ' + label_txt
            },
            tooltips: {
                mode: 'index',
                intersect: false,
            },
            hover: {
                mode: 'nearest',
                intersect: true
            },
            legend: {
                display: false,
                position: 'top',
            },
            scales: {
                xAxes: [{
                    display: true,
                    scaleLabel: {
                        display: false,
                        labelString: 'Hashtags'
                    }
                }],
                yAxes: [{
                    display: true,
                    scaleLabel: {
                        display: false,
                        labelString: 'Counts'
                    },
                    ticks: {
                        beginAtZero: true,
                        callback: function (value, index, values) {
                            return value;
                        }
                    }
                }]
            }
        }
    }
}


function get_time_config(label, data_labels, data_values) {
    // configurations for the time-series chart
    return {
        type: 'line',
        data: {
            labels: data_labels,
            datasets: [{
            label: 'counts',
            data: data_values,
            backgroundColor: Array(56).fill('rgba(255, 99, 132, 0.5)'),
            borderColor: Array(data_values.length).fill('rgba(255, 99, 132, 1)'),
            borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            title: {
                display: true,
                text: label + ' tweet creation date'
            },
            legend: {
                display: false,
                position: 'top',
            },
            tooltips: {
                mode: 'index',
                intersect: false,
            },
            hover: {
                mode: 'nearest',
                intersect: true
            }
        }
    }
}


function convertDates(elementCreation) {
    // convert date object to Year and Month
    const hatevalTime = [];
    elementCreation.forEach(function (item, index) {
        var d = new Date(item);
        var l = new Date();
        l.setFullYear(d.getFullYear(), d.getMonth()); // d.getDate() kunnen we altijd nog toevoegen
        hatevalTime.push(l);
    });

    // add counts to occurences of dates
    var counts = {};
    for (var i = 0; i < hatevalTime.length; i++) {
        var num = hatevalTime[i].toISOString().slice(0,7).replace(/-/g,"/");
        counts[num] = counts[num] ? counts[num] + 1 : 1;
    }

    // provide correct formatting
    var dataValues = [];
    for (var key of Object.keys(counts)) {
        dataValues.push({'t': key, 'y': counts[key]})
    }
    return [Object.keys(counts), dataValues]
}


function returnCharts(label, users_l, users_v, users_c, hashtag_l, hashtag_v, hashtag_c, creation, text_l, text_v, text_c, tfidf_l, tfidf_v, tfidf_c) {

    // doughnut users
    const user_doughnut_ctx = document.getElementById('doughnut').getContext('2d');
    const user_doughnut_config = get_doughnut_config(label, users_l, users_v, users_c);
    const usersDoughnut = new Chart(user_doughnut_ctx, user_doughnut_config);

    // bar hashtags
    const hashtag_bar = document.getElementById('hashtag').getContext('2d');
    const hashtag_bar_config = get_bar_config(label, 'most used hashtags', 'Amount of hashtags', hashtag_l, hashtag_v, hashtag_c);
    const hashtagBar =  new Chart(hashtag_bar, hashtag_bar_config);

    // time creation
    const creation_time = document.getElementById('time').getContext('2d');
    const [creationLabels, creationValues] = convertDates(creation);
    const creation_time_config = get_time_config(label, creationLabels, creationValues);
    const creationTime = new Chart(creation_time, creation_time_config);

    // bar text
    const text = document.getElementById('text').getContext('2d');
    const text_config = get_bar_config(label, 'most used words (count)','Amount of words', text_l, text_v, text_c);
    const textBar =  new Chart(text, text_config);

    // bar tfidf
    const tfidf = document.getElementById('tfidf').getContext('2d');
    const tfidf_config = get_bar_config(label, 'most used words (tf-idf)','vector score', tfidf_l, tfidf_v, tfidf_c);
    const tfidfBar =  new Chart(tfidf, tfidf_config);

    return [usersDoughnut, hashtagBar, creationTime, textBar, tfidfBar]

}


function showCharts(usersDoughnut, hashtagBar, creationTime, textBar) {
    window.myLine = usersDoughnut;
    window.myLine = hashtagBar;
    window.myLine = creationTime;
    window.myLine = textBar;

}

// Initialize and add the map
function initMap() {
    // The location of Uluru,-3.6945454
        const uluru = { lat: 40.3859417, lng:-3.6945454 };
        // The map, centered at Uluru
        const map = new google.maps.Map(document.getElementById("div_dashboard_map"), {
          zoom: 4,
          center: uluru,
        });
        // The marker, positioned at Uluru
        const marker = new google.maps.Marker({
          position: uluru,
          map: map,
        });
        // Evento click sobre el marker creado
        marker.addListener('click', function() {
          $("#div_dashboard").hide();
          $("#div_dashboard_details").show();


          const config_cpu = {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: "(%)",
                    backgroundColor: 'rgb(255, 99, 132)',
                    borderColor: 'rgb(255, 99, 132)',
                    data: [],
                    fill: false,
                }],
            },
            options: {
                responsive: true,
                title: {
                    display: false,
                    text: 'Creating Real-Time Charts with Flask'
                },
                tooltips: {
                    mode: 'index',
                    intersect: false,
                },
                hover: {
                    mode: 'nearest',
                    intersect: true
                },
                scales: {
                    xAxes: [{
                        display: true,
                        scaleLabel: {
                            display: true,
                            labelString: 'Time'
                        }
                    }],
                    yAxes: [{
                        display: true,
                        scaleLabel: {
                            display: true,
                            labelString: 'Value'
                        }
                    }]
                }
            }
          };

          const config_temp = {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: "(??C)",
                    backgroundColor: 'rgb(255, 99, 132)',
                    borderColor: 'rgb(255, 99, 132)',
                    data: [],
                    fill: false,
                }],
            },
            options: {
                responsive: true,
                title: {
                    display: false,
                    text: 'Creating Real-Time Charts with Flask'
                },
                tooltips: {
                    mode: 'index',
                    intersect: false,
                },
                hover: {
                    mode: 'nearest',
                    intersect: true
                },
                scales: {
                    xAxes: [{
                        display: true,
                        scaleLabel: {
                            display: true,
                            labelString: 'Time'
                        }
                    }],
                    yAxes: [{
                        display: true,
                        scaleLabel: {
                            display: true,
                            labelString: 'Value'
                        }
                    }]
                }
            }
          };

          const context_cpu = document.getElementById('canvas_cpu').getContext('2d');
          const context_temp = document.getElementById('canvas_temp').getContext('2d');

          const lineChart_cpu = new Chart(context_cpu, config_cpu);
          const lineChart_temp = new Chart(context_temp, config_temp);

          const source = new EventSource("/chart-data");
          //const source_temp = new EventSource("/chart-data");
          //var source_cervezas_mahou = new EventSource("/chart-data");
          //var source_cervezas_otras = new EventSource("/chart-data");
          //var source_aperturas = new EventSource("/chart-data");
          //var source_aperturas_tiempo = new EventSource("/chart-data");

          source.onmessage = function(event) {
            const data = JSON.parse(event.data);
            document.getElementById("cervezas_mahou").innerHTML = data.cervezas_mahou;
            document.getElementById("cervezas_otras").innerHTML = data.otros;
            document.getElementById("numero_aperturas").innerHTML = data.num_aperturas;
            document.getElementById("tiempo_medio_aperturas").innerHTML = data.tiempo_aperturas;

            if (config_cpu.data.labels.length === 20) {
                config_cpu.data.labels.shift();
                config_cpu.data.datasets[0].data.shift();
            }
            config_cpu.data.labels.push(data.time);
            config_cpu.data.datasets[0].data.push(data.CPU);
            lineChart_cpu.update();

            if (config_temp.data.labels.length === 20) {
                config_temp.data.labels.shift();
                config_temp.data.datasets[0].data.shift();
            }
            config_temp.data.labels.push(data.time);
            config_temp.data.datasets[0].data.push(data.temp_nevera);
            lineChart_temp.update();
          };
          /*
          source_cervezas_otras.onmessage = function(event) {
            const data_cervezas_otras = JSON.parse(event.data);
            document.getElementById("cervezas_otras").innerHTML = data_cervezas_otras.otros;
          };
          source_aperturas.onmessage = function(event) {
            const data_aperturas = JSON.parse(event.data);
            document.getElementById("numero_aperturas").innerHTML = data_aperturas.num_aperturas;
          };
          source_aperturas_tiempo.onmessage = function(event) {
            const data_aperturas_tiempo = JSON.parse(event.data);
            document.getElementById("tiempo_medio_aperturas").innerHTML = data_aperturas_tiempo.tiempo_aperturas;
          };

          source_cpu.onmessage = function (event) {
            const data_cpu = JSON.parse(event.data);
            if (config_cpu.data.labels.length === 20) {
                config_cpu.data.labels.shift();
                config_cpu.data.datasets[0].data.shift();
            }
            config_cpu.data.labels.push(data_cpu.time);
            config_cpu.data.datasets[0].data.push(data_cpu.CPU);
            lineChart_cpu.update();
          };

          source_temp.onmessage = function (event) {
            const data_temp = JSON.parse(event.data);
            if (config_temp.data.labels.length === 20) {
                config_temp.data.labels.shift();
                config_temp.data.datasets[0].data.shift();
            }
            config_temp.data.labels.push(data_temp.time);
            config_temp.data.datasets[0].data.push(data_temp.temp_nevera);
            lineChart_temp.update();
          }
          */




          $.getJSON($SCRIPT_ROOT + '/leer_datos_sideways', {
            c: $("#selec_proyecto").val()
            }, function(data) {
                    console.log(data.result.asset_name);
                    $("#nombre_dispositivo").text("Nombre - " + data.result.asset_name);
                    $("#modelo").text("Modelo - Prototipo Mahou");// + data.result.model_name);
                    $("#direccion").text("Direcci??n - " + data.result.direccion);
                    $("#fecha_inicio").text("Fecha de inicio - " + data.result.fecha_inicio_uso);
              });
            });
      }

$(document).ready(function(){

    //en la carga de la pagina se mostrar el div dashboard por defecto
    $("#div_dashboard").show()
    $("#div_dashboard_details").hide()
    $("#div_cargar_datos").hide()
    $("#div_ver_datos").hide()
    //gestion de la visibilidad de los div cuando se clica el link de dashboard_menu
    $("#dashboard_menu").click(function(){
                $("#div_dashboard").show()
                $("#div_dashboard_details").hide()
                $("#div_cargar_datos").hide()
                $("#div_ver_datos").hide()
    });

    //gestion de la visibilidad de los div cuando se clica el link de cargar_datos_menu
    $("#cargar_datos_menu").click(function(){
                $("#div_dashboard").hide()
                $("#div_dashboard_details").hide()
                $("#div_cargar_datos").show()
                $("#div_ver_datos").hide()
    });

    //gestion de la visibilidad de los div cuando se clica el link de ver_datos_menu
    $("#ver_datos_menu").click(function(){
                $("#div_dashboard").hide()
                $("#div_dashboard_details").hide()
                $("#div_cargar_datos").hide()
                $("#div_ver_datos").show()
    });

    //click de boton que gestiona el formulario que carga las tablas
    $('#btn_cargar_datos').click(function(){
        $.ajax({
            url: '/insertar',
            data: $('form').serialize(),
            type: 'POST',
            success: function(response){
                console.log(response);
            },
            error: function(error){
                console.log(error);
            }
        });
        $("#div_dashboard").hide()
        $("#div_dashboard_details").hide()
        $("#div_cargar_datos").show()
        $("#div_ver_datos").hide()
    });


    // resetear el numero de cervezas mahou
    $('#reset_mahou').click(function(){
        $.ajax({
            url: '/set_mahou',
            data: $('form').serialize(),
            type: 'POST',
            success: function(response){
                console.log(response);
            },
            error: function(error){
                console.log(error);
            }
        });

    });

    // resetear el numero de otras cervezas
    $('#reset_otros').click(function(){
        $.ajax({
            url: '/set_otros',
            data: $('form').serialize(),
            type: 'POST',
            success: function(response){
                console.log(response);
            },
            error: function(error){
                console.log(error);
            }
        });

    });

    //al hacer la selecci??n de la tabla, se muestran los datos de dicha tabla
    $("#selec_proyecto").change(function() {
        $("#tableWithSearch > tbody").empty();
        $.getJSON($SCRIPT_ROOT + '/leer_datos', {
            c: $("#selec_proyecto").val()
        }, function(data) {
                $.each(data.result, function (i, item) {
                    $('<tr>').append(
                        $('<td>').text(item.id),
                        $('<td>').text(item.nombre),
                        $('<td>').text(item.tipo),
                        $('<td>').text(item.ruta_s3),
                        $('<td>').text(item.clases)
                    ).appendTo('#tableWithSearch');
                });
          });
          return false;
    });

});

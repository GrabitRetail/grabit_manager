#-*-coding=utf-8-*-
#importamos librerias
from flask import Flask, render_template, request, json, jsonify, Response
import random
from datetime import datetime, date
import time
import os
import sys
import boto3
from random import randrange


#constantes

otros=0 #Numero de inicio de cervezas que no sean de mahou
offset_otros=0 #Numero de offset de cervezas que no sean de mahou

cervezas_mahou=0 #Numero de inicio de cervezas que sean de mahou
offset_mahou=0 #Numero de offset de cervezas que sean de mahou

nombre_db = 'grabit_ai'
nombre_columnas=[
    "id",
    "nombre",
    "tipo",
    "ruta_s3",
    "clases"
]
client =boto3.client('iotsitewise',region_name='eu-west-1') #Recordar que nuestros dispositivos estan configurados en Irlanda
#se creat la aplicacion flask
app = Flask(__name__)
random.seed() # initialize the random number generator

############################################################## funciones de ayuda #########################################################
def insertar_datos_db(sql):
    rdsData = boto3.client('rds-data')
    response = rdsData.execute_statement(
        resourceArn=cluster_arn,
        secretArn=secret_arn,
        database=nombre_db,
        sql=sql
    )
    return response

def leer_datos_db(sql):
    rdsData = boto3.client('rds-data')
    response = rdsData.execute_statement(
        resourceArn=cluster_arn,
        secretArn=secret_arn,
        database=nombre_db,
        sql=sql
    )
    return response


# Conseguimos la lista de modelos creados en el IoT SiteWise
def conseguir_modelos():
    modelos = client.list_asset_models(
        maxResults=123
    )

    # Extraemos la informacion necesaria de los modelos para utilizarlos mas adelante
    contenido_modelos = []
    for i in modelos['assetModelSummaries']:
        info_modelos = {
            'id': i['id'],
            'arn': i['arn'],
            'name': i['name']
        }
        contenido_modelos.append(info_modelos)
    return contenido_modelos


# Conseguimos los diferentes assets que puede tener un modelo especifico
def conseguir_assets(id_modelo):
    assets = client.list_assets(
        maxResults=123,
        assetModelId=id_modelo,
        filter='ALL'
    )
    return assets


# Conseguimos toda la informacion de un asset especifico
def conseguir_asset(id_asset):
    asset = client.describe_asset(
        assetId=id_asset
    )
    return asset


# Obtenemos la informacion de una propiedad especifica de un asset
def propiedad_asset(id_asset, fecha_inicio, id_propiedad):
    dt = datetime.today()
    response = client.get_asset_property_value_history(
        assetId=id_asset,
        propertyId=id_propiedad,
        startDate=fecha_inicio,
        endDate=datetime(dt.year, dt.month, dt.day),
        timeOrdering='ASCENDING',
        maxResults=123
    )
    return response


####EXTRAER TODA LA INFORMACION DE UN ASSET####
"""
def conseguir_info_total_asset(asset, id_asset):
    info_total_asset = []  # Donde se almacena toda la informacion obtenida de un asset

    # Repasamos todas las propiedades de un asset especifico
    for j in asset['assetProperties']:

        # Obtenemos la informacion de una propiedad especifica de un asset
        propiedad = propiedad_asset(id_asset, datetime(2022, 1, 18), j['id'])
        # Pasamos la informacion conseguida de una propiedad a una lista de diccionarios
        content = []
        for valores in propiedad['assetPropertyValueHistory']:
            info = {
                'valores': valores['value'],
                'hora': datetime.fromtimestamp(valores['timestamp']['timeInSeconds'])  # .strftime('%Y-%m-%d %H:%M:%S')
            }
            content.append(info)

        # Conseguimos una lista de diccionarios con toda la informacion recibida de cada propiedad
        propiedades = {
            'nombre': j['name'],
            'id': j['id'],
            'contenido': content
        }

        info_total_asset.append(propiedades)
    return info_total_asset
"""


@app.route("/")
def index():
    return render_template("index1.html")

@app.route('/leer_datos')
def leer_datos():
    filas = []
    c = request.args.get('c','pordefecto',type=str)
    if c == "Proyecto":
        sql = "select * from proyecto where id in (22,23)"
        response = leer_datos_db(sql)
        # creamos un diccionario que tendra todos los datos de la query
        for i in range(len(response['records'])):
            fila = {}
            for j in range(len(response['records'][i])):
                for k, v in response['records'][i][j].items():
                    fila[nombre_columnas[j]] = v
                    # print(configuracion_deepstream)
            filas.append(fila)
    else:
        filas.append("nada")
    return  jsonify(result = filas)

@app.route('/insertar', methods=['POST'])
def insertar():

    tabla = request.form['tabla']
    if tabla == "proyecto":
        proyectoID =  request.form['inputProyectoID']
        proyectoNombre = request.form['inputProyectoNombre']
        proyectoTipo = request.form['inputProyectoTipo']
        proyectoRutaS3 = request.form['inputProyectoRutaS3']
        proyectoClases = request.form['inputProyectoClases']
        sql = "insert into proyecto values ('{0}','{1}','{2}','{3}','{4}')".format(proyectoID,proyectoNombre,proyectoTipo,proyectoRutaS3,proyectoClases)
        response = insertar_datos_db(sql)

    print(response)
    print(proyectoID,proyectoNombre,proyectoTipo,proyectoRutaS3,proyectoClases)
    return jsonify({'status':'OK'})

@app.route('/leer_datos_sideways')
def leer_datos_sideways():
    contenido_modelos = conseguir_modelos()
    modelo_elegido = contenido_modelos[2]  # Usamos el id del modelo 'SiteWise Tutorial Device Model'
    assets = conseguir_assets(modelo_elegido['id'])
    asset_elegido = assets['assetSummaries'][0]  # Usamos el id del modelo 'SiteWise Tutorial Device 3'
    asset = conseguir_asset(asset_elegido['id'])

    #info_total_asset = conseguir_info_total_asset(asset, asset_elegido['id'])

    informacion_completa = {
        'model_name': modelo_elegido['name'],
        'asset_name': conseguir_info_momento(asset, asset_elegido['id'], 0)['stringValue'],  # Nombre del equipo
        'fecha_inicio_uso': asset['assetCreationDate'],
        'direccion': conseguir_info_momento(asset, asset_elegido['id'], 1)['stringValue'],
    }
    return jsonify(result=informacion_completa)



@app.route('/chart-data')
def chart_data():
    def generate_random_data():
        datos_sitewise = conseguir_asset_id()
        while True:
            total_otros = otros - offset_otros + int(
                conseguir_info_momento(datos_sitewise[0], datos_sitewise[1], -4)['integerValue'])
            total_mahou = cervezas_mahou - offset_mahou + int(
                conseguir_info_momento(datos_sitewise[0], datos_sitewise[1], -5)['integerValue'])
            json_data = json.dumps(
                {'time': datetime.now().strftime('%H:%M:%S'),
                 #'CPU': conseguir_info_momento(datos_sitewise[0], datos_sitewise[1], 2)['doubleValue'],
                 'CPU': generar_valores(),
                 'thermal':conseguir_info_momento(datos_sitewise[0], datos_sitewise[1],13)['doubleValue'],
                 'temp_nevera':conseguir_info_momento(datos_sitewise[0], datos_sitewise[1],-3)['doubleValue'],
                 'num_aperturas':conseguir_info_momento(datos_sitewise[0], datos_sitewise[1],-6)['integerValue'],
                 'tiempo_aperturas':conseguir_info_momento(datos_sitewise[0], datos_sitewise[1],-2)['stringValue'][7:],
                 'otros':total_otros,
                 'cervezas_mahou':total_mahou
                 })
            yield f"data:{json_data}\n\n"
            print(json_data)
            time.sleep(2)
            print(
                'Numero de inicio de cervezas Mahou: ' + str(cervezas_mahou) + ' Numero de Offset cervezas Mahou' + str(
                    offset_mahou))
            print('Numero de inicio de otras cervezas: ' + str(otros) + '  Numero de Offset cervezas: ' + str(
                offset_otros))

    return Response(generate_random_data(), mimetype='text/event-stream')

#Funcion que devulve los ultimos datos de la CPU y su temperatura
def conseguir_info_momento(asset, id_asset,propiedad):
    info=client.get_asset_property_value(
        assetId=id_asset,
        propertyId=asset['assetProperties'][propiedad]['id'],
    )
    return(info['propertyValue']['value'])

"""ORDEN DE PROPIEDAES DE UN ASSET
nombre
CPU 1 usage
CPU 2 usage
CPU 3 usage
CPU 4 usage
CPU 5 usage
CPU 6 usage
CPU 7 usage
CPU 8 usage
RAM usage
RAM total
GPU usage
CPU Temp
GPU Temp
Thermal
TempAO
TempPPL
IP
Jetpack version
Numero Aperturas
Tiempo Medio Aperturas
Cervezas Mahou
Otros elementos
Temp Nevera
Direccion
"""

def conseguir_asset_id():
    contenido_modelos = conseguir_modelos()
    modelo_elegido = contenido_modelos[2]  # Usamos el id del modelo 'SiteWise Tutorial Device Model'
    assets = conseguir_assets(modelo_elegido['id'])
    

    asset_elegido = assets['assetSummaries'][0]  # Usamos el id del asset de la Jetson del frigorifico de Mahou
    
    asset = conseguir_asset(asset_elegido['id'])

    return asset,asset_elegido['id']


#Funciones para cambiar el valor inicial de numeros de cerveza dentro del frigorifico

@app.route('/set_otros', methods=['POST'])
def set_otros():
    global otros
    global offset_otros
    datos_sitewise=conseguir_asset_id()
    otros=int(request.form['otros']) #Cambiar este valor para mapearlo con la forma que se tienen que recibir los valores
    offset_otros=int(conseguir_info_momento(datos_sitewise[0], datos_sitewise[1],-4)['integerValue'])
    print('Numero de inicio de otras cervezas: '+str(otros)+' Numero de Offset cervezas Mahou'+str(offset_otros))
    return jsonify({'status':'OK'})#Cambiar esto con lo que tenga que ser, el html o lo que haya que mostrar

@app.route('/set_mahou', methods=['POST'])
def set_mahou():
    global cervezas_mahou
    global offset_mahou
    datos_sitewise=conseguir_asset_id()
    cervezas_mahou=int(request.form['cerveza_mahou']) #Cambiar este valor para mapearlo con la forma que se tienen que recibir los valores
    offset_mahou=int(conseguir_info_momento(datos_sitewise[0], datos_sitewise[1],-5)['integerValue'])
    print('Numero de inicio de cervezas Mahou: '+str(cervezas_mahou)+' Numero de Offset cervezas Mahou'+str(offset_mahou))
    return jsonify({'status':'OK'})#Cambiar esto con lo que tenga que ser, el html o lo que haya que mostrar

#Genera valores falsos de la CPU para mostrarlos en la grafica
def generar_valores():
    dc=47 #Valor minimo que se va a mostrar en la grafica
    ac=15 #Desviacion maxima que tendra el valor en la grafica
    valor=dc+ac*randrange(100)*0.01
    return(valor)

if __name__=="__main__":
    app.run()





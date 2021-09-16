#-*-coding=utf-8-*-
from flask import Flask, render_template, request, json, jsonify
import json
import string
import os
import sys

#import boto3
#sys.path.insert(1, '/grabit_ai/scripts/')
#import utils
app = Flask(__name__)

nombre_db = 'grabit_ai'
sFichero_ID_proyecto = '/grabit_ai/conf/proyecto_id.json'
nombre_columnas=[
    "id",
    "nombre",
    "tipo",
    "ruta_s3",
    "clases"
]

#creamos un diccionario que tendra todos los datos de la query
configuracion_deepstream = {}

#se lee el cluster_arn y secret_arn del fichero de config
#proyecto_id_dict = utils.leer_parametros_configuración(sFichero_ID_proyecto)
#cluster_arn = proyecto_id_dict['cluster_arn']
#secret_arn = proyecto_id_dict['secret_arn']


@app.route("/")
def index():
    return render_template("index.html")

@app.route('/leer_datos')
def leer_datos():
    a = request.args.get('a', 0, type=int)
    b = request.args.get('b', 0, type=int)
    return jsonify(result=a + b)

@app.route('/input_datos', methods=['POST'])
def inputProyecto():
    proyectoID =  request.form['inputProyectoID']
    proyectoNombre = request.form['inputProyectoNombre']
    proyectoTipo = request.form['inputProyectoTipo']
    proyectoRutaS3 = request.form['inputProyectoRutaS3']
    proyectoClases = request.form['inputProyectoClases']
    sql = "insert into proyecto values ('{0}','{1}','{2}','{3}','{4}')".format(proyectoID,proyectoNombre,proyectoTipo,proyectoRutaS3,proyectoClases)
    rdsData = boto3.client('rds-data')
    response = rdsData.execute_statement(
            resourceArn = cluster_arn,
            secretArn = secret_arn,
            database = nombre_db,
            sql = sql
    )
    print(proyectoID,proyectoNombre,proyectoTipo,proyectoRutaS3,proyectoClases)
    return jsonify({'status':'OK'})

if __name__=="__main__":
    app.run()





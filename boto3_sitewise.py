import boto3
import json
from datetime import datetime, date

client =boto3.client('iotsitewise',region_name='eu-west-1') #Recordar que nuestros dispositivos estan configurados en Irlanda

def main():
    
    contenido_modelos=conseguir_modelos()
    modelo_elegido=contenido_modelos[1] # Usamos el id del modelo 'SiteWise Tutorial Device Model'
    assets=conseguir_assets(modelo_elegido['id'])

    asset_elegido=assets['assetSummaries'][1] #Usamos el id del modelo 'SiteWise Tutorial Device 3'
    asset=conseguir_asset(asset_elegido['id'])
    
    info_total_asset=conseguir_info_total_asset(asset,asset_elegido['id'])

    informacion_completa={
        'model_name':modelo_elegido['name'],
        'model_id':modelo_elegido['id'],
        'asset_name':asset_elegido['name'],
        'asset_id': asset_elegido['id'],
        'info_total_asset':info_total_asset
    }

    #print(informacion_completa['model_name'],informacion_completa['model_id'],informacion_completa['asset_name'],informacion_completa['asset_id'],
    #informacion_completa['info_total_asset'][0]['nombre'],informacion_completa['info_total_asset'][0]['contenido'][0]['valores'])

    informacion_especifica = {
        'nombre_propiedad': informacion_completa['info_total_asset'][0],
        'CPU1': informacion_completa['info_total_asset'][1],
        'RAM_usage': informacion_completa['info_total_asset'][9],
        'GPU': informacion_completa['info_total_asset'][11],
        'CPU_temp': informacion_completa['info_total_asset'][12],
        'GPU_temp': informacion_completa['info_total_asset'][13],
        'thermal': informacion_completa['info_total_asset'][14]
    }
    print(informacion_especifica['CPU1'])
    #Si devuelve list index out of range no hay informacion


#Conseguimos la lista de modelos creados en el IoT SiteWise 
def conseguir_modelos():
    
    modelos = client.list_asset_models(
        maxResults=123
    )

    #Extraemos la informacion necesaria de los modelos para utilizarlos mas adelante
    contenido_modelos=[]
    for i in modelos['assetModelSummaries']:
        info_modelos={
            'id':i['id'],
            'arn':i['arn'],
            'name':i['name']
        }
        contenido_modelos.append(info_modelos)  
    return contenido_modelos



#Conseguimos los diferentes assets que puede tener un modelo especifico
def conseguir_assets(id_modelo):
    
    assets = client.list_assets(
        maxResults=123,
        assetModelId=id_modelo, 
        filter='ALL'
    )
    return assets



#Conseguimos toda la informacion de un asset especifico
def conseguir_asset(id_asset):
    
    asset=client.describe_asset(
            assetId=id_asset 
        )
    return asset


#Obtenemos la informacion de una propiedad especifica de un asset
def propiedad_asset(id_asset,fecha_inicio ,id_propiedad):    
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
def conseguir_info_total_asset(asset, id_asset):
    
    info_total_asset=[] #Donde se almacena toda la informacion obtenida de un asset

    #Repasamos todas las propiedades de un asset especifico
    for j in asset['assetProperties']:

        #Obtenemos la informacion de una propiedad especifica de un asset
        propiedad = propiedad_asset(id_asset,datetime(2020, 10, 18), j['id'])

        #Pasamos la informacion conseguida de una propiedad a una lista de diccionarios
        content=[]
        for valores in propiedad['assetPropertyValueHistory']:
            info={
                'valores':valores['value'],
                'hora':datetime.fromtimestamp(valores['timestamp']['timeInSeconds']) #.strftime('%Y-%m-%d %H:%M:%S')
            }
            content.append(info)
        
        #Conseguimos una lista de diccionarios con toda la informacion recibida de cada propiedad
        propiedades={
            'nombre':j['name'],
            'id':j['id'],
            'contenido': content
        }

        info_total_asset.append(propiedades)
    return info_total_asset


if __name__ == "__main__":
    main()
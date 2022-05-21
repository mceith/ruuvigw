import json
import boto3
import os
from ruuvitag_sensor.data_formats import DataFormats
from ruuvitag_sensor.decoder import get_decoder


TOPIC = os.getenv('RUUVI_TOPIC')
IOT_DATA_ENDPOINT = os.getenv('IOT_DATA_ENDPOINT')

#client = boto3.client('iot-data', region_name='eu-west-1', endpoint_url=IOT_DATA_ENDPOINT)

def lambda_handler(event, context):
    
    print("Original Event: ", event)
    # convert_data returns tuple which has Data Format type and encoded data
    (data_format, encoded) = DataFormats.convert_data(event['data'])
    sensor_data = get_decoder(data_format).decode_data(encoded)
    # Convert for nanoseconds
    sensor_data['timestamp'] = int(event['ts']) * 1000000000

    #print(json.dumps(sensor_data))

    return sensor_data


import time
import boto3
import os
import json

from botocore.config import Config

DATABASE_NAME = os.environ['DATABASE_NAME']
TABLE_NAME = os.environ['TABLE_NAME']
MEASURE_NAME = os.environ['MEASURE_NAME']
LOCATION = os.environ['LOCATION']

def prepare_common_attributes(mac):
    common_attributes = {
        'Dimensions': [
            {'Name': 'location', 'Value': LOCATION},
            {'Name': 'ruuvitag', 'Value': mac}
        ],
        'MeasureName': MEASURE_NAME,
        'MeasureValueType': 'MULTI'
    }
    return common_attributes


def prepare_record(current_time):
    record = {
        'Time': str(current_time),
        'TimeUnit': 'NANOSECONDS',
        'MeasureValues': []
    }
    return record


def prepare_measure(measure_name, measure_value, type='DOUBLE'):
    measure = {
        'Name': measure_name,
        'Value': str(measure_value),
        'Type': type
    }
    return measure

def write_records(records, common_attributes):
    try:
        result = write_client.write_records(DatabaseName=DATABASE_NAME,
                                            TableName=TABLE_NAME,
                                            CommonAttributes=common_attributes,
                                            Records=records)
        status = result['ResponseMetadata']['HTTPStatusCode']
        print("Processed %d records. WriteRecords HTTPStatusCode: %s" %
              (len(records), status))
    except write_client.exceptions.RejectedRecordsException as err:
        print("RejectedRecords: ", err)
        for rr in err.response["RejectedRecords"]:
            print("Rejected Index " + str(rr["RecordIndex"]) + ": " + rr["Reason"])
        print("Other records were written successfully. ")
    except Exception as err:
        print("Error:", err)

session = boto3.Session()
write_client = session.client('timestream-write', config=Config(
  read_timeout=20, max_pool_connections=5000, retries={'max_attempts': 10}))

def lambda_handler(event, context):

  print("writing data to database {} table {}".format(
        DATABASE_NAME, TABLE_NAME))

  event = event["transformed_payload"]

  common_attributes = prepare_common_attributes(event['mac'])  
  records = []
  record = prepare_record(event['timestamp'])
  for key,value in event.items():
    #print("key: {} | value: {}".format(key, value))
    if (key == 'mac'):
      record['MeasureValues'].append(prepare_measure(key, value, 'VARCHAR'))
    elif (key == 'humidity') or (key == 'temperature') or (key == 'pressure') or (key == 'acceleration'):
      record['MeasureValues'].append(prepare_measure(key, value)) 
    else:
      record['MeasureValues'].append(prepare_measure(key, value, 'BIGINT')) 
  records.append(record)

  write_records(records, common_attributes)

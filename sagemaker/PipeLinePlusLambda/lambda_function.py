import boto3
import json
from arize.api import Client
from datetime import datetime
from uuid import uuid4

if __name__ != "__main__":
    runtime = boto3.client('runtime.sagemaker')


# Arize Test LambdaHandler
def lambda_handler(event, context):
    print('Lambda Handler V 1.2')
    API_KEY_ARIZE = "INSERT_YOUR_KEY_HERE"
    try:
        # Get the body from the event
        data_send = event['body']
        if isinstance(data_send, dict):
            # Turn the data send object into a JSON string
            data_send = json.dumps(data_send)
        data_send_byte_array = bytearray(data_send, encoding='utf8')
        # Call endpoint running prediction pipeline
        response = runtime.invoke_endpoint(
            EndpointName='inference-pipeline-ep-2020-04-17-16-00-2511',
            ContentType='application/json',
            Body=data_send_byte_array)
        response_data = float(response['Body'].read())
    except Exception:
        return "ERROR DATA - " + str(event['body'])

    # setup columns to send as labels
    columns = [
        "sex", "length", "diameter", "height", "whole_weight", "shucked_weight",
        "viscera_weight", "shell_weight"
    ]
    arize = Client(space_key='space_key',
                   api_key=API_KEY_ARIZE,
)
    labels = {}
    data = json.loads(data_send)
    # Map labels to values
    for index, col in enumerate(columns):
        labels[columns[index]] = str(data['data'][index])
    # Unique ID based on time - This works only if you don't want to connect prediction back
    id = datetime.now().strftime('%Y%m-%d%H-%M%S-') + str(uuid4())
    # LOG TO ARIZE
    arize.log(model_id='sage-maker-lambda',
              model_version='v0.1',
              prediction_id=id,
              prediction_label=response_data,
              features=labels,
              actual_label=None)
    del arize
    print([labels, response_data, id])
    print('result is!!!!')
    print(response_data)
    return json.loads('{"predict":' + str(response_data) + '}')

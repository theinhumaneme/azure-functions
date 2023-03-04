import logging

import azure.functions as func
from azure.storage.blob import BlobServiceClient
from PIL import Image
import json

connect_str = "<URL>"

# Create the BlobServiceClient object
blob_service_client = BlobServiceClient.from_connection_string(connect_str)

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    id = req.params.get('id')
    width = int(req.params.get('w'))
    height = int(req.params.get('h'))
    if not id:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            id = req_body.get('id')
            width = int(req_body.get('w'))
            height = int(req_body.get('h'))

    if id:
        uploaded_files=[]
        blob_client = blob_service_client.get_blob_client(container="azure-blob-demo", blob=id+".webp")
        downloaded_bytes = blob_client.download_blob().readall()
        with open(f"/tmp/{id}.webp", "wb") as file:
            file.write(downloaded_bytes)
        Image.open(f"/tmp/{id}.webp").crop((0,0,width,height)).save(f"/tmp/{id}_{width}_{height}.webp","webp")
        blob_client = blob_service_client.get_blob_client(container="azure-blob-demo", blob=f"/tmp/{id}_{width}_{height}.webp".split("/")[-1])
        blob_client.upload_blob(open(f"/tmp/{id}_{width}_{height}.webp","rb"),overwrite=True)
        uploaded_files.append(blob_client.url)
        return func.HttpResponse(json.dumps(uploaded_files),mimetype="application/json",)
    else:
        return func.HttpResponse(
             "This HTTP triggered function executed successfully. Pass a id in the query string or in the request body for a personalized response.",
             status_code=200
        )

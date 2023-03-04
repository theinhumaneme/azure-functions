import logging
from azure.storage.blob import BlobServiceClient
import azure.functions as func
import requests
from uuid import uuid4
from PIL import Image
import json


connect_str = "<URI>"

# Create the BlobServiceClient object
blob_service_client = BlobServiceClient.from_connection_string(connect_str)

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    url = req.params.get('url')
    if not url:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            url = req_body.get('url')
    file_name = str(uuid4())

    if url:
        file = requests.get(url, allow_redirects=True)
        with open("/tmp/"+file_name,"wb") as file_downloaded:
            file_downloaded.write(file.content)
        
        jpg_name = "/tmp/"+file_name+".jpg"
        webp_name = "/tmp/"+file_name+".webp"
        extensions = {jpg_name:"jpeg",
                      webp_name:"webp"}
        for fn,ext in extensions.items():
            Image.open("/tmp/"+file_name).convert("RGB").save(fn,ext)
        
        
        print("\nUploading to Azure Storage as blob:\n\t" + file_name)
        uploaded_files = []
        blob_client = blob_service_client.get_blob_client(container="azure-blob-demo", blob=file_name)
        for file_path in extensions.keys():
            blob_client = blob_service_client.get_blob_client(container="azure-blob-demo", blob=file_path.split("/")[-1])
            with open(file=file_path, mode="rb") as data:
                blob_client.upload_blob(data,overwrite=True)
                uploaded_files.append(blob_client.url)


        return func.HttpResponse(json.dumps(uploaded_files),mimetype="application/json",)
    else:
        return func.HttpResponse(
             "This HTTP triggered function executed successfully. Pass a url in the query string or in the request body for a personalized response.",
             status_code=200
        )

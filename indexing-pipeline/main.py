from fastapi import FastAPI, HTTPException, File, UploadFile
import weaviate
import requests
import os
import json
from pyvi.ViTokenizer import tokenize
import logging
import numpy as np

WEAVIATE_URL = os.getenv("WEAVIATE_URL")
VECTORIZE_URL = os.getenv("VECTORIZE_URL")
APP_PORT =int(os.getenv("SERVICE_PORT"))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING) 

app = FastAPI(title="Indexing Pipeline")

client = weaviate.Client(WEAVIATE_URL, startup_period=40)


@app.get("/health")
async def healthCheck():
    return {"status": "ok"}


def initVectorDBSchema(client):
    schema = {
        "classes": [{
            "class": "Document",
            "vectorizer": "none",  
            "properties": [{
                "name": "content",
                "dataType": ["text"],
            }]
        }]
    }
    client.schema.delete_all()
    client.schema.create(schema)

def vectorizeDocuments(document):

    response = requests.post(VECTORIZE_URL, json={"text": document})  
    if response.status_code == 200:
        vector=np.array(response.json().get("vector"), dtype=object)
        return vector
    else:
        logger.error(f"Failed to vectorize document {document}")
        raise HTTPException(status_code=response.status_code, detail="Failed to vectorize document")

def saveDocsToDB(documents, vectors, client):
    if len(documents) != len(vectors):
        raise HTTPException(status_code=400, detail="Number of documents and vectors do not match")
        
    for i, document in enumerate(documents):
        try:
            client.data_object.create(
                data_object={"content": document},
                class_name='Document',
                vector=vectors[i]
            )
        except Exception as e:
            logger.error(f"Failed to save document {document} to Weaviate: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to save document to Weaviate")
        
@app.post("/embedding-process")
async def embeddingProcess(file: UploadFile = File(...)):
    try:
        json_data = json.load(file.file)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="JSON file is invalid")

    logger.info("CONVERTING JSON DATA TO TEXT")
    processed_documents = []
    for item in json_data:
        combined_text = f"Trích dẫn ở: {item['title']} \n Nội dung như sau: {item['context']}"
        processed_documents.append(combined_text)
    
    tokenizer_sent = [tokenize(sent) for sent in processed_documents]

    initVectorDBSchema(client)

    vectors = []
    for _, tokenized_text in enumerate(tokenizer_sent):
        vector = vectorizeDocuments(tokenized_text)
        vectors.append(vector)
    
    vectors = np.array(vectors, dtype=object)
    saveDocsToDB(processed_documents, vectors, client)

    return {"message": "Successfully imported documents with vectors"}

if __name__ == "__main__":
    initVectorDBSchema(client)
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=APP_PORT, reload=True)

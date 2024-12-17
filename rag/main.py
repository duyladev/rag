from fastapi import FastAPI, HTTPException
import weaviate
import requests
from pyvi.ViTokenizer import tokenize
from llama_index.core import PromptTemplate
import os
import logging
import uvicorn
from fastapi.middleware.cors import CORSMiddleware

WEAVIATE_URL = "http://weaviate:8080"
VECTORIZE_URL = os.getenv("VECTORIZE_URL", "")
LLM_API_URL = os.getenv("LLM_API_URL", "")
APP_PORT= int(os.getenv("SERVICE_PORT", 3000))

MAX_NEW_TOKENS = int(os.getenv("MAX_NEW_TOKENS", 30))
TEMPERATURE = float(os.getenv("TEMPERATURE", 0.5))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING) 

app = FastAPI(
    title="Rag",
    docs_url="/rag/docs",
    redoc_url="/rag/redoc",
    openapi_url="/rag/openapi.json")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

@app.get("/healthz")
async def health_check():
    return {"status": "ok"}

def query_rag_llm(query_str, limit=3):
    # Tokenize query
    logger.warning("Đã nhận query và đang chuẩn bị tokenizing")
    tokenized_query = tokenize(query_str)
    logger.warning(f"Tokenizing done: {tokenized_query}")
    logger.warning("Đang kết nối Weaviate và tìm top K",WEAVIATE_URL)
    # Weaviate search
    logger.warning("Connecting to Weaviate and finding top K")
    
    client = weaviate.Client(WEAVIATE_URL,trust_env=True)

    text_data = {"text": tokenized_query}
    response = requests.post(VECTORIZE_URL, json=text_data)

    if response.status_code == 200:
        vec = response.json().get("vector")
    else:
        print("Failed to get vector, status code:", response.status_code)
        return None

    near_vec = {"vector": vec}
    res = client \
        .query.get("Document", ["content", "_additional {certainty}"]) \
        .with_near_vector(near_vec) \
        .with_limit(limit) \
        .do()

    context_str = []
    for document in res["data"]["Get"]["Document"]:
        logger.warning(f"Content similarity: {document['_additional']['certainty']}: {document['content']}")
        context_str.append("{:.4f}: {}".format(document["_additional"]["certainty"], document["content"]))

    context_str = "\n".join(context_str)

    # Create prompt and call LLM
    logger.warning("Creating template and going into LLM")
    template = (
        "We have provided context information below. \n"
        "---------------------\n"
        "{context_str}"
        "\n---------------------\n"
        "Given this information, please answer the question: {query_str}\n"
    )
    qa_template = PromptTemplate(template)
    messages = qa_template.format_messages(context_str=context_str, query_str=query_str)
    prompt = messages[0].content

    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        json={
            "model": "llama-3.1-70b-versatile",
            
            "messages": [{
            "role": "user",
            "content": prompt
        }],
            
        },
        verify=False ,
        headers={"Authorization": "Bearer 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"}
    )
    if response.status_code == 200:
        response_json = response.json()
        logger.warning(f"Answer from LLM: {response_json}")
        return response_json
    else:
        print("Failed to get response from LLM, status code:", response.status_code)
        return None

@app.post("/query-with-rag")
async def query(query_str: str):
    response = query_rag_llm(query_str)
    if response:
        return {"response": response}
    else:
        raise HTTPException(status_code=500, detail="Failed to process the query")
    
@app.post("/query")
async def query(query_str: str):
    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        json={
            "model": "llama-3.1-70b-versatile",
            
            "messages": [{
            "role": "user",
            "content": query_str
        }],
            
        },
        verify=False ,
        headers={"Authorization": "Bearer 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"}
    )
    if response:
        return {"response": response.json()}
    else:
        raise HTTPException(status_code=500, detail="Failed to process the query")    

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=APP_PORT, reload=True)

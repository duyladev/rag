from fastapi import FastAPI, HTTPException
import weaviate
import requests
from pyvi.ViTokenizer import tokenize
from llama_index.core import PromptTemplate
import os
import logging
import uvicorn
from fastapi.middleware.cors import CORSMiddleware

WEAVIATE_URL = os.getenv("WEAVIATE_URL", "http://weaviate:8080")
VECTORIZE_URL = os.getenv("VECTORIZE_URL", "http://embeddings:6000/vectorize")
LLM_API_URL = os.getenv("LLM_API_URL", "https://api.groq.com/openai/v1/chat/completions")
LLM_TOKEN=os.getenv("LLM_TOKEN", "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")
APP_PORT= int(os.getenv("SERVICE_PORT", 3000))
TOP_K = int(os.getenv("TOP_K", 10))

# MAX_NEW_TOKENS = int(os.getenv("MAX_NEW_TOKENS", 30))
# TEMPERATURE = float(os.getenv("TEMPERATURE", 0.5))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING) 
app = FastAPI(title="Rag service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

@app.get("/health")
async def healthCheck():
    return {"status": "ok"}

def llmApi(prompt):
    
    response = requests.post(
        LLM_API_URL,
        json={
            "model": "llama-3.1-70b-versatile",
            "messages": [{"role": "user", "content": prompt}],
        },
        verify=False,
        headers={"Authorization": "Bearer " + LLM_TOKEN},
    )
    if response.status_code == 200:
        return response.json()
    else:
        return None

def queryWithRAG(message):

    tokenized_query = tokenize(message)

    client = weaviate.Client(WEAVIATE_URL,trust_env=True)

    text_data = {"text": tokenized_query}
    
    response = requests.post(VECTORIZE_URL, json=text_data)

    if response.status_code == 200:
        vec = response.json().get("vector")
    else:
        logger.error("Failed to get vector from embeddings service")
        return None

    near_vec = {"vector": vec}
    res = client \
        .query.get("Document", ["content", "_additional {certainty}"]) \
        .with_near_vector(near_vec) \
        .with_limit(TOP_K) \
        .do()

    context_str = []
    for document in res["data"]["Get"]["Document"]:
        context_str.append("{:.4f}: {}".format(document["_additional"]["certainty"], document["content"]))

    context_str = "\n".join(context_str)


    template = (
        "Bạn có những thông tin như sau về Luật giao thông. \n"
        "---------------------\n"
        "{context_str}"
        "\n---------------------\n"
        "Hãy dựa vào những thông tin được cung cấp đó để trả lời câu hỏi sau: {message}\n"
    )
    qa_template = PromptTemplate(template)
    messages = qa_template.format_messages(context_str=context_str, message=message)
    prompt = messages[0].content

    response = llmApi(prompt)
    return response

@app.post("/chat-with-rag")
async def chatWithRAG(message: str):
    response = queryWithRAG(message)
    if response:
        return {"response": response}
    else:
        raise HTTPException(status_code=500, detail="Internal server error")
    
@app.post("/chat-with-llm")
async def chatWithLLM(message: str):
    response = llmApi(message)
    if response:
        return {"response": response}
    else:
        raise HTTPException(status_code=500, detail="Internal server error")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=APP_PORT, reload=True)

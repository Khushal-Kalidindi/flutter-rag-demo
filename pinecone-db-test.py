import requests
import os
import re
from dotenv import load_dotenv
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from typing import List, Dict
import hashlib
from pinecone import Pinecone
import sys
from tqdm import tqdm

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX = os.getenv("PINECONE_INDEX")
EMBEDDINGS = OpenAIEmbeddings(api_key=OPENAI_API_KEY)
DATA_FOLDER = os.getenv("DATA_FOLDER")

class DocumentChunk:
    def __init__(self, chunk_text: str):
        self.id = self._generate_id(chunk_text)
        self.embedding = self._generate_embedding(chunk_text)
        self.chunk_text = chunk_text


    def _generate_id(self, content: str) -> str:
        hash_obj = hashlib.sha256()
        hash_obj.update(content.encode("utf-8"))
        return hash_obj.hexdigest()
    
    def _generate_embedding(self, content: str) -> list[float]:
        return EMBEDDINGS.embed_documents([content])[0]


class Document:
    def __init__(self, title: str, filename: str,content: str):
        self.title = title
        self.filename = filename
        self.content = content
        self.chunks: list[DocumentChunk] = []
    
def read_text_file(filename: str) -> Document:
    with open(filename, "r") as file:
        content = file.read()
        split_filename: list[str] = re.split("[/.]", filename)

    return Document(title=split_filename[len(split_filename)-2], filename=filename, content=content)

def recursive_split(paragraph: str, max_chunk_size: int):
    res = []
    if(len(paragraph) <= max_chunk_size):
        res.append(paragraph)
        return res
    split_point = paragraph.find(".", len(paragraph)//2)
    res.extend(recursive_split(paragraph[:split_point], max_chunk_size))
    res.extend(recursive_split(paragraph[split_point:], max_chunk_size))
    return res

def chunk_document(doc: Document, min_chunk_size:int, max_chunk_size: int) -> list[DocumentChunk]:
    # Ensure each text ends with a double newline to correctly split paragraphs
    content = doc.content
    if not content.endswith("\n\n"):
        content += "\n\n"
    # Split text into paragraphs
    paragraphs = content.split("\n\n")
    chunks: list[DocumentChunk] = []
    for p in tqdm(paragraphs, total=len(paragraphs), desc=f"Loading Chunks from {doc.filename}"):
        p = p.strip()
        if len(p) > max_chunk_size:
            new_pgraphs = recursive_split(p, max_chunk_size)
            chunks.extend(DocumentChunk(chunk_text=x) for x in new_pgraphs if len(x) >= min_chunk_size)
        elif len(p) >= min_chunk_size:
            chunks.append(DocumentChunk(chunk_text=p))
    return chunks

def load_document_to_index(d: Document):
    pc = Pinecone(api_key=PINECONE_API_KEY)
    index = pc.Index(PINECONE_INDEX)
    vectors: List[Dict] = []
    for chunk in d.chunks:
        v = {
            "id" : chunk.id,
            "values" : chunk.embedding,
            # TODO: Adding text to metadata is quick and dirty, load chunk text to firebase instead
            "metadata" : {"title" : d.title, "filename" : d.filename, "text": chunk.chunk_text}
        }
        vectors.append(v)
    index.upsert(vectors, show_progress=True)

def load_text_files_to_documents(folder_path: str) -> list[Document]:
    if not os.path.exists(folder_path):
        raise Exception(f"Folder '{folder_path}' does not exist.")
    
    docs = []

    for file in os.listdir(folder_path):
        if file.endswith('.txt'):
            print(f"Found {file}")
            docs.append(read_text_file(f"{folder_path}/{file}"))
    if not docs:
        raise Exception("No text files found in the folder.")
    
    return docs
        
    
def load_data():
    docs = load_text_files_to_documents(folder_path=DATA_FOLDER)
    for d in docs:
        print(f"Loading {d.filename} to index")
        d.chunks = chunk_document(d, min_chunk_size=10, max_chunk_size=500)
        load_document_to_index(d)
        print(f"Loaded file {d.filename} to index")

def query_pinecone_index(index_name, query_embeddings: list[float], top_k: int = 2, include_metadata: bool = True) -> dict[str, any]:
    pc = Pinecone(api_key=PINECONE_API_KEY)
    index = pc.Index(index_name)
    query_response = index.query(
        vector=query_embeddings, top_k=top_k, include_metadata=include_metadata
    )
    return query_response

def query_data(query: str, index_name: str):
    query_embedding = EMBEDDINGS.embed_query(query)
    search_res = query_pinecone_index(index_name=index_name, query_embeddings=query_embedding)
    print(generate_llm_response(query=query, context=search_res))

def generate_llm_response(query: str, context: dict) -> str:
    context_string = " ".join(doc['metadata']['text'] for doc in context['matches'])

    prompt_template = (
        "Context: {context}\n"
        "Question: {query}\n"
        "If this context contains information that can answer the question,"
        "give a better and summarized answer. "
        'Else say "I don\'t have enough info to answer."'
    )

    llm = ChatOpenAI(temperature=0, model_name="gpt-4", openai_api_key=OPENAI_API_KEY)
    prompt = PromptTemplate(input_variables=["context", "query"], template=prompt_template)
    chain = LLMChain(llm=llm, prompt=prompt)

    try:
        response = chain.run(context=context_string, query=query)
        return response
    except Exception as e:
        return f"Error generating LLM response: {str(e)}"
    
def main():
    print(sys.argv)
    
    if(sys.argv[1] == "-L"):
        load_data()
    elif(sys.argv[1] == "-Q"):
        query_data(sys.argv[2], PINECONE_INDEX)
    

if __name__ == "__main__":
    main()
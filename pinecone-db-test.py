import requests
import os
import re
from dotenv import load_dotenv
from langchain_community.embeddings import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from typing import List, Dict
import hashlib
from pinecone import Pinecone
import sys

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
EMBEDDINGS = OpenAIEmbeddings(api_key=OPENAI_API_KEY)

class DocumentChunk:
    def __init__(self, chunk_text: str):
        self.id = self._generate_id(chunk_text)
        print("generating embedding...")
        self.embedding = self._generate_embedding(chunk_text)
        print("embedding generated")
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
    
    def generate_chunks(self):
        self.chunks = chunk_content(self.content, min_chunk_size=10, max_chunk_size=500)
    
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

def chunk_content(content: str, min_chunk_size:int, max_chunk_size: int) -> list[DocumentChunk]:
    # Ensure each text ends with a double newline to correctly split paragraphs
    if not content.endswith("\n\n"):
        content += "\n\n"
    # Split text into paragraphs
    paragraphs = content.split("\n\n")
    chunks: list[DocumentChunk] = []
    for p in paragraphs:
        p = p.strip()
        if len(p) > max_chunk_size:
            new_pgraphs = recursive_split(p, max_chunk_size)
            chunks.extend(DocumentChunk(chunk_text=x) for x in new_pgraphs if len(x) >= min_chunk_size)
        elif len(p) >= min_chunk_size:
            chunks.append(DocumentChunk(chunk_text=p))
    return chunks

def load_document_to_index(d: Document):
    pc = Pinecone(api_key=PINECONE_API_KEY)
    index = pc.Index("rag-test1")
    vectors: List[Dict] = []
    for chunk in d.chunks:
        v = {
            "id" : chunk.id,
            "values" : chunk.embedding,
            # TODO: Adding text to metadata is quick and dirty, load chunk text to firebase instead
            "metadata" : {"title" : d.title, "filename" : d.filename, "text": chunk.chunk_text}
        }
        vectors.append(v)
    # print(vectors)
    index.upsert(vectors, show_progress=True)
    
def load_data():
    d = read_text_file(sys.argv[1])
    print(f"Loading {d.filename} to index")
    d.generate_chunks()
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
    # Combine the context into a single string
    context_string = " ".join(doc['metadata']['text'] for doc in context['matches'])

    prompt_template = (
        "Context: {context}\n"
        "Question: {query}\n"
        "Evaluate if this context contains information that can answer the question. "
        "If yes, using the provided information, give a better and summarized answer. "
        'Else say "I don\'t have enough info to answer."'
    )

    # Initialize LangChain with OpenAI's newer API setup
    llm = ChatOpenAI(temperature=0, model_name="gpt-4", openai_api_key=OPENAI_API_KEY)
    prompt = PromptTemplate(input_variables=["context", "query"], template=prompt_template)
    chain = LLMChain(llm=llm, prompt=prompt)

    try:
        response = chain.run(context=context_string, query=query)
        return response
    except Exception as e:
        return f"Error generating LLM response: {str(e)}"
    

    


def main():
    # print("loading data")
    # load_data()
    # print("done loading")
    # query_data("What grades in 2020?", "rag-test1")
    query_data("What grades in Math 407", "rag-test1")
    

if __name__ == "__main__":
    main()
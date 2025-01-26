import requests
import os
import re
from dotenv import load_dotenv
from langchain.embeddings.openai import OpenAIEmbeddings

load_dotenv()

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
EMBEDDINGS = OpenAIEmbeddings(api_key=os.environ["OPENAI_API_KEY"])
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

class DocumentChunk:
    def __init__(self, embedding: any, chunk_text: str):
        self.embedding = embedding
        self.chunk_text = chunk_text

class Document:
    def __init__(self, title: str, content: str):
        self.title = title
        self.content = content
        self.chunks: list[DocumentChunk] = []
    
def read_text_file(filename: str) -> Document:
    with open(filename, "r") as file:
        content = file.read()
    return Document(title=re.split("[/.]", filename), content=content)

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
            chunks.extend(DocumentChunk(None, chunk_text=x) for x in new_pgraphs if len(x) >= min_chunk_size)
        elif len(p) >= min_chunk_size:
            chunks.append(DocumentChunk(None, chunk_text=p))
    return chunks


def main():
    print("hello world")
    d  = read_text_file("txts/inauguration.txt")
    chunks = chunk_content(d.content, min_chunk_size=10, max_chunk_size=500)
    for i in range(len(chunks)):
        print(f"Chunk {i}")
        print(ascii(chunks[i].chunk_text))

if __name__ == "__main__":
    main()
import os
import shutil
import uuid
from tempfile import NamedTemporaryFile
from typing import Annotated, Union
from dotenv import load_dotenv
from fastapi import FastAPI, File, UploadFile, Form
from langchain.chains.question_answering import load_qa_chain
from langchain.llms.openai import OpenAI
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from PyPDF2 import PdfReader
import docx

load_dotenv()

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/create")
async def create_embedding(
        files: Annotated[list[Union[UploadFile]], File()] = '',
        text: Annotated[str, Form()] = '',
):
    context = ''
    for file in files:
        if file.filename.endswith('.pdf'):
            with NamedTemporaryFile(delete=True, suffix=".pdf") as temp_file:
                shutil.copyfileobj(file.file, temp_file)
                context += (read_pdf(temp_file.name))
        elif file.filename.endswith('.txt'):
            contents = await file.read()
            context += contents.decode('utf-8')
        elif file.filename.endswith('.docx'):
            with NamedTemporaryFile(delete=True, suffix=".docx") as temp_file:
                shutil.copyfileobj(file.file, temp_file)
                context += (read_word(temp_file.name))
        else:
            continue
    context += text
    if len(context) == 0:
        return {
            "result": None,
            "error": "No valid context"
        }
    session = uuid.uuid4()  # Create strongly hashed session
    location = f"{os.getenv('SESSION_STORAGE')}/{session}"
    char_text_splitter = CharacterTextSplitter(separator="\n", chunk_size=1000,
                                               chunk_overlap=200, length_function=len)
    text_chunks = char_text_splitter.split_text(context)
    embeddings = OpenAIEmbeddings()
    docsearch = FAISS.from_texts(text_chunks, embeddings)
    docsearch.save_local(location)
    return {
            "result": session,
            "error": None
        }

@app.post("/chat")
def query_embedding(session: str, query: str):
    location = f"{os.getenv('SESSION_STORAGE')}/{session}"
    # create embeddings
    embeddings = OpenAIEmbeddings()
    docsearch = FAISS.load_local(location, embeddings)

    llm = OpenAI()
    chain = load_qa_chain(llm, chain_type="stuff")

    docs = docsearch.similarity_search(query)
    return chain.run(input_documents=docs, question=query)


def read_pdf(file_path):
    with open(file_path, "rb") as file:
        pdf_reader = PdfReader(file)
        text = ""
        for page_num in range(len(pdf_reader.pages)):
            text += pdf_reader.pages[page_num].extract_text()
    return text


def read_word(file_path):
    doc = docx.Document(file_path)
    text = ""
    for paragraph in doc.paragraphs:
        text += paragraph.text + "\n"
    return text

import os
import shutil
import uuid
from tempfile import NamedTemporaryFile
from typing import Annotated, Union
from dotenv import load_dotenv
from fastapi import FastAPI, File, UploadFile, Depends, status
from langchain.chains.question_answering import load_qa_chain
from langchain.llms.openai import OpenAI
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from PyPDF2 import PdfReader
import docx
from src.Database.Database import SessionLocal, Base, engine
from src.Entity.Session import Session
from src.Entity.User import User as UserModel
from src.Repository import UserRepository, AuthTokenRepository, SessionRepository
from src.Repository.SessionRepository import get_session_by_session_id
from src.Repository.UserRepository import get_user_by_auth_token
from src.Schema.AuthToken.AuthToken import AuthToken as AuthTokenSchema
from src.Schema.User.User import User as UserSchema
from src.Schema.Session.Session import Session as SessionSchema
from fastapi.responses import JSONResponse

Base.metadata.create_all(bind=engine)


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


load_dotenv()

app = FastAPI()


@app.post("/parseFiles")
async def create_embedding_files(
        context: Annotated[list[Union[UploadFile]], File()],
        user_id: str,
        db: Session = Depends(get_db)
):
    user = get_user_by_auth_token(db=db, auth_token=user_id)
    if user is None:
        content = {
            "result": None,
            "error": "Invalid authentication token"
        }
        return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content=content)
    strinput = ''
    for file in context:
        if file.filename.endswith('.pdf'):
            with NamedTemporaryFile(delete=True, suffix=".pdf") as temp_file:
                shutil.copyfileobj(file.file, temp_file)
                strinput += (read_pdf(temp_file.name))
        elif file.filename.endswith('.txt'):
            contents = await file.read()
            strinput += contents.decode('utf-8')
        elif file.filename.endswith('.docx'):
            with NamedTemporaryFile(delete=True, suffix=".docx") as temp_file:
                shutil.copyfileobj(file.file, temp_file)
                strinput += (read_word(temp_file.name))
        else:
            continue
    if len(context.strip()) == 0:
        content = {
            "result": None,
            "error": "No valid context"
        }
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=content)
    session = uuid.uuid4()  # Create strongly hashed session
    location = f"{os.getenv('SESSION_STORAGE')}/{session}"
    char_text_splitter = CharacterTextSplitter(separator="\n", chunk_size=1000,
                                               chunk_overlap=200, length_function=len)
    text_chunks = char_text_splitter.split_text(strinput)
    embeddings = OpenAIEmbeddings()
    docsearch = FAISS.from_texts(text_chunks, embeddings)
    docsearch.save_local(location)
    SessionRepository.create_session(db=db, user_id=user_id, session_id=session)
    content = {
        "result": str(session),
        "error": None
    }
    return JSONResponse(status_code=status.HTTP_200_OK, content=content)


@app.post("/parseText")
async def create_embedding_text(
        context: str,
        user_id: str,
        db: Session = Depends(get_db)
):
    user = get_user_by_auth_token(db=db, auth_token=user_id)
    if user is None:
        content = {
            "result": None,
            "error": "Invalid authentication token"
        }
        return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content=content)

    if len(context.strip()) == 0:
        content = {
            "result": None,
            "error": "No valid context"
        }
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=content)

    session = uuid.uuid4()
    location = f"{os.getenv('SESSION_STORAGE')}/{session}"
    char_text_splitter = CharacterTextSplitter(separator="\n", chunk_size=1000,
                                               chunk_overlap=200, length_function=len)
    text_chunks = char_text_splitter.split_text(context)
    embeddings = OpenAIEmbeddings()
    docsearch = FAISS.from_texts(text_chunks, embeddings)
    docsearch.save_local(location)
    SessionRepository.create_session(db=db, user_id=user.id, session_id=session)
    content = {
        "result": str(session),
        "error": None
    }
    return JSONResponse(status_code=status.HTTP_200_OK, content=content)


@app.post("/chat")
async def query_embedding(
    session: str,
    query: str,
    user_id: str,
    db: Session = Depends(get_db)
):
    user = get_user_by_auth_token(db=db, auth_token=user_id)
    if user is None:
        content = {
            "result": None,
            "error": "Invalid authentication token"
        }
        return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content=content)

    session = get_session_by_session_id(db=db, session_id=session)
    if session is None:
        content = {
            "result": None,
            "error": "Invalid session"
        }
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=content)

    if len(query.strip()) == 0:
        content = {
            "result": None,
            "error": "No valid context"
        }
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=content)


    location = f"{os.getenv('SESSION_STORAGE')}/{session.session_id}"
    embeddings = OpenAIEmbeddings()
    docsearch = FAISS.load_local(location, embeddings)
    llm = OpenAI()
    chain = load_qa_chain(llm, chain_type="stuff")
    docs = docsearch.similarity_search(query)
    content = {
        "result": chain.run(input_documents=docs, question=query).strip(),
        "error": None
    }
    return JSONResponse(status_code=status.HTTP_200_OK, content=content)


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


@app.post("/create_user", response_model=UserSchema)
async def create_user(api_token: str, db: Session = Depends(get_db)):
    if api_token == os.getenv('SECRET_KEY'):
        user = UserRepository.create_user(db=db)
        return JSONResponse(status_code=status.HTTP_200_OK, content=user)
    else:
        return JSONResponse(status_code=status.HTTP_403_FORBIDDEN, content="Not Authorized")



@app.post("/users/generate_token", response_model=AuthTokenSchema)
async def generate_token(
    user_id: int,
    api_token: str,
    db: Session = Depends(get_db)
):
    if api_token == os.getenv('SECRET_KEY'):
        user = AuthTokenRepository.create_auth_token(db=db, user_id=user_id)
        return JSONResponse(status_code=status.HTTP_200_OK, content=user)
    else:
        return JSONResponse(status_code=status.HTTP_403_FORBIDDEN, content="Not Authorized")




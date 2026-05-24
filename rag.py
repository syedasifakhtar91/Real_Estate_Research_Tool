from uuid import uuid4
from dotenv import load_dotenv
from pathlib import Path

from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings

load_dotenv()

# Constants
CHUNK_SIZE = 1000
VECTORSTORE_DIR = Path("vectorstore")

# LLM (updated working model)
llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0.7
)

# Embeddings
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# Vector DB
vector_store = Chroma(
    collection_name="real_estate",
    embedding_function=embeddings,
    persist_directory=str(VECTORSTORE_DIR)
)

# -------- Process URLs --------
def process_urls(urls):
    # Better loader (fix for CNBC issue)
    loader = WebBaseLoader(urls)
    data = loader.load()

    # Split text
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=200
    )
    docs = splitter.split_documents(data)

    # Add to vector DB
    ids = [str(uuid4()) for _ in docs]
    vector_store.add_documents(docs, ids=ids)

    return "Processed ✅"


# -------- Generate Answer --------
def generate_answer(query):
    retriever = vector_store.as_retriever()

    # New LangChain method
    docs = retriever.invoke(query)

    # Build context
    context = "\n\n".join([d.page_content for d in docs])

    prompt = f"""
    Answer using ONLY the context below.

    If the answer is not present, say "Not found in context".

    Context:
    {context}

    Question: {query}
    """

    res = llm.invoke(prompt)

    # Extract sources
    sources = "\n".join(
        list(set([d.metadata.get("source", "") for d in docs]))
    )

    return res.content, sources
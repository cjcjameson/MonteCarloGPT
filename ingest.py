import pickle

import nest_asyncio
import pinecone
from langchain.document_loaders.sitemap import SitemapLoader
from langchain.embeddings import HuggingFaceEmbeddings, OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores.faiss import FAISS
from langchain.vectorstores.pinecone import Pinecone
from langchain.document_loaders import NotionDirectoryLoader


from constants import (
    EMBEDDING_MODEL,
    EMBEDDING_MODEL_TYPE,
    OPENAI_API_KEY,
    PINECONE_API_KEY,
    PINECONE_ENVIRONMENT,
    PINECONE_INDEX,
    VECTORSTORE_TYPE,
)

nest_asyncio.apply()


def ingest_docs(
    vectorstore_type=VECTORSTORE_TYPE, embedding_model_type=EMBEDDING_MODEL_TYPE
):
    """Ingest documents from docs into a vectorstore"""
    ### Create documents from README
    sitemap_loader = SitemapLoader(
        web_path="https://raw.githubusercontent.com/mvfolino68/MonteCarloGPT/master/sitemap.xml"
    )
    readme_raw_documents = sitemap_loader.load()

    # Split documents into chunks
    readme_text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=2000,
        chunk_overlap=200,
    )
    readme_documents = readme_text_splitter.split_documents(readme_raw_documents)

    ### Create documents from internal product docs
    internal_product_docs_notion_loader = NotionDirectoryLoader("Notion_Internal_Product_Docs_DB")
    internal_product_docs_notion_raw_documents = internal_product_docs_notion_loader.load()

    # Split documents into chunks
    internal_product_docs_notion_text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=2000,
        chunk_overlap=200,
    )
    internal_product_docs_notion_documents = internal_product_docs_notion_text_splitter.split_documents(internal_product_docs_notion_raw_documents)

    ### Create documents from knowledge base
    knowledge_base_notion_loader = NotionDirectoryLoader("Notion_Knowledge_Base_DB")
    knowledge_base_notion_raw_documents = knowledge_base_notion_loader.load()

    # Split documents into chunks
    knowledge_base_notion_text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=2000,
        chunk_overlap=200,
    )
    knowledge_base_notion_documents = knowledge_base_notion_text_splitter.split_documents(knowledge_base_notion_raw_documents)

    ### Combine documents
    documents = readme_documents + internal_product_docs_notion_documents + knowledge_base_notion_documents


    # Create Embeddings
    if embedding_model_type == "HUGGINGFACE":
        # Use hugging face embeddings for free
        model_name = EMBEDDING_MODEL
        embeddings = HuggingFaceEmbeddings(model_name=model_name)

    elif embedding_model_type == "OPENAI":
        # Use OpenAI embeddings at a cost
        embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)

    # Create vectorstore
    if vectorstore_type == "PINECONE":
        # Uinitialize Pinecone and create index
        pinecone.init(api_key=PINECONE_API_KEY, environment=PINECONE_ENVIRONMENT)
        index_name = PINECONE_INDEX
        vectorstore = Pinecone.from_documents(
            documents, embeddings, index_name=index_name
        )

    elif vectorstore_type == "FAISS":
        # Use FAISS vectorstore
        vectorstore = FAISS.from_documents(documents, embeddings)

        # Save FAISS vectorstore
        with open("vectorstore.pkl", "wb") as f:
            pickle.dump(vectorstore, f)


if __name__ == "__main__":
    ingest_docs()

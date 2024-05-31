import openai
import os  
from dotenv import load_dotenv
from langchain_openai import AzureOpenAIEmbeddings
from langchain.vectorstores.azuresearch import AzureSearch
from azure.search.documents.indexes.models import (
    SemanticSearch,
    SemanticConfiguration,
    SemanticPrioritizedFields,
    SemanticField
)
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter

# Configure environment variables  
load_dotenv()  
openai.api_type: str = "azure"  
openai.api_key = os.getenv("AZURE_OPENAI_API_KEY")  
openai.api_base = os.getenv("AZURE_OPENAI_ENDPOINT")  
openai.api_version = os.getenv("AZURE_OPENAI_API_VERSION")  
model: str = "text-embedding-ada-002"

vector_store_address: str = os.getenv("AZURE_SEARCH_SERVICE_ENDPOINT")  
vector_store_password: str = os.getenv("AZURE_SEARCH_ADMIN_KEY") 
index_name: str = "langchain-vector-demo"

embeddings: AzureOpenAIEmbeddings = AzureOpenAIEmbeddings(deployment=model, chunk_size=1, azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT") )
index_name: str = "langchain-vector-demo"
vector_store: AzureSearch = AzureSearch(
    azure_search_endpoint=vector_store_address,
    azure_search_key=vector_store_password,
    index_name=index_name,
    embedding_function=embeddings.embed_query,
    semantic_configuration_name='config',
        semantic_search=SemanticSearch(
            default_configuration='config',
            configurations=[
                SemanticConfiguration(
                    name='config',
                    prioritized_fields=SemanticPrioritizedFields(
                        title_field=SemanticField(field_name='content'),
                        prioritized_content_fields=[SemanticField(field_name='content')],
                        prioritized_keywords_fields=[SemanticField(field_name='metadata')]
                    ))
            ])
)
    

loader = TextLoader("fantasy_story.txt", encoding="utf-8")

documents = loader.load()

# Check if documents are loaded
assert documents, "Documents failed to load"
print(f"Loaded {len(documents)} documents")

text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
docs = text_splitter.split_documents(documents)

vector_store.add_documents(documents=docs)

# Check if documents are added to vector store
search_results = vector_store.similarity_search("what is a name of friendly sea turtle", k=1)
assert search_results, "Documents failed to add to vector store"
print(f"Documents successfully added to vector store, retrieved {len(search_results)} documents for test query")

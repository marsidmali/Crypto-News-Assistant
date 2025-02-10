from datetime import datetime
import json
import os

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.retrievers import BM25Retriever
from langchain.retrievers import EnsembleRetriever
from langchain.retrievers.document_compressors import CohereRerank
from langchain.retrievers import ContextualCompressionRetriever
from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain.callbacks import StdOutCallbackHandler
from langchain_openai import ChatOpenAI
from langchain_cohere import CohereRerank


def load_config(file_path='config.json'):
    with open(file_path, 'r') as file:
        config = json.load(file)
    return config

class RAGSystem:
    """
    Retrieval Augmented Generation (RAG) System for processing and querying crypto news.
    
    This system combines vector search (FAISS), keyword search (BM25), and reranking (Cohere)
    to provide accurate responses to user queries. It supports both OpenAI and Ollama models
    for text generation.
    
    Features:
    - Hybrid document retrieval
    - Smart context reranking
    - Flexible LLM support
    - Streaming responses
    """
    def __init__(self, df, config_path='../config.json'):
        self.df = df
        self.documents = []
        self.chunks = []
        self.embeddings = HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2')
        self.config = load_config(config_path)
        
        # Set up the language model based on the configuration
        if self.config['model_type'] == 'openai':
            os.environ["OPENAI_API_KEY"] = self.config['openai_api_key']
            self.llm = ChatOpenAI(model_name=self.config['openai_model'], temperature=0)
        elif self.config['model_type'] == 'ollama':
            self.llm = Ollama(model=self.config['ollama_model'])

        self.handler = StdOutCallbackHandler()
        self.retriever = None
        self.QA_chain = None

    def create_documents(self):
        for idx, row in self.df.iterrows():
            # Combine title and text to create full content
            content = f"News Title: {row['title']}\n\nTime of publication of news: {row['time']}, Source newsletter: {row['source']}\n\nContent of news: {row['text']}"
            metadata = {
                'source': row['source'],
                'url': row['url'],
                'time': row['time'],
                'id': row['id']
            }
            doc = Document(page_content=content, metadata=metadata)
            self.documents.append(doc)

    def split_documents(self):
        # Initialize the text splitter
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=100,
            length_function=len,
            separators=["\n\n", "\n"]
        )
        # Split documents into chunks
        self.chunks = text_splitter.split_documents(self.documents)

    def create_hybrid_retriever(self):
        vectorstore = FAISS.from_documents(self.chunks, self.embeddings)
        vectorstore.save_local("faiss_index_")
        persisted_vectorstore = FAISS.load_local("../faiss_index_", self.embeddings, allow_dangerous_deserialization=True)
        vector_retriever = persisted_vectorstore.as_retriever(search_type="mmr", search_kwargs={"k": 7})

        bm25_retriever = BM25Retriever.from_documents(self.chunks)
        bm25_retriever.k = 7

        ensemble_retriever = EnsembleRetriever(
            retrievers=[bm25_retriever, vector_retriever],
            weights=[0.4, 0.6]
        )

        # Add Cohere reranker
        cohere_reranker = CohereRerank(
            cohere_api_key=self.config['cohere_api_key'],
            top_n=3,
            model="rerank-english-v2.0"
        )

        reranked_retriever = ContextualCompressionRetriever(
            base_retriever=ensemble_retriever,
            base_compressor=cohere_reranker
        )

        return reranked_retriever

    def setup_qa_chain(self):
        custom_prompt_template = PromptTemplate(
            input_variables=["question", "context"],
            template="""As a knowledgeable analyst assistant on the market of crypto-currency, use the following context news on the market: to analyze the trends of crypto-currencies and explain the possible impacts of the news on the market. If you think the provided news are not sufficient or too old, just say that you can not provide reliable information.Always give your answer in markdown format(not for markdown cell).\n\n
                        - The current time which this query is generated is {current_time}, so be aware of the difference between current time and the time of the news when you want to induce some analysis based on the news.\n\n
                        - Context : {context}\n\n
                        - Question: {question}\n\n
                        - Answer:""",
            partial_variables={"current_time": self.current_timestamp()},
        )

        self.QA_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            retriever=self.retriever,
            chain_type_kwargs={"prompt": custom_prompt_template},
            callbacks=[self.handler],
            return_source_documents=True
        )

    def current_timestamp(self):
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def initialize_rag(self):
        self.create_documents()
        self.split_documents()
        self.retriever = self.create_hybrid_retriever()
        self.setup_qa_chain()

    def query(self, question):
        result = self.QA_chain.invoke({"query": question, "current_time": self.current_timestamp()})
        return result["result"]
# chatbot.py

from langchain.chains import ConversationalRetrievalChain
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.memory import ConversationBufferMemory

def get_chain(openai_key: str):
    embeddings = OpenAIEmbeddings(openai_api_key=openai_key)
    db = FAISS.load_local("vector_store", embeddings, allow_dangerous_deserialization=True)

    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True,
        output_key="answer"  # ✅ fix memory save_context crash
    )

    llm = ChatOpenAI(temperature=0, openai_api_key=openai_key)

    qa_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=db.as_retriever(search_kwargs={"k": 3}),
        memory=memory,
        return_source_documents=True,
        output_key="answer",  # ✅ ensures memory knows what to store
        verbose=False
    )

    return qa_chain

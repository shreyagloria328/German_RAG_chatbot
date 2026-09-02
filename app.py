#@ This is the user interface 

import os
from dotenv import load_dotenv
import streamlit as st # ui library
from generator import generate_answer # importing RAG pipeline 

load_dotenv() # reads.env file and makes API key available


st.set_page_config( # browser tab configuration 
    page_title="German Study Assistant", # txt shown in browser tab
    page_icon="🇩🇪",
    layout="centered" # center content
)


with st.sidebar: # left side bar 
    st.divider() # seperator line 
    if st.button("🗑️ Clear chat history"):
        st.session_state.messages = []
        st.rerun()
    st.header("⚙️ Settings")
    level_filter = st.selectbox(
        "Filter by level:",
        options=["All levels", "A1", "A2", "B1"],
        index=0 # index for the options seletced 0-all levels
    )

    if level_filter == "All levels":
        level_filter = None

    st.divider()

    st.header("ℹ️ About")
    st.markdown("""
    This chatbot answers questions using 
    your German study PDFs.

    **Powered by:**
    - 🔍 ChromaDB (vector search)
    - 🤖 Groq LLM (answer generation)
    - 📚 Your A1/A2/B1 study materials
    """)

    st.divider()

    st.header("💡 Example questions")
    st.markdown("""
    - What is der die das?
    - How do I introduce myself?
    - What are German numbers?
    - How do I say goodbye in German?
    - What is the accusative case?
    """)


st.title("German Study Assistant")
st.markdown("Ask me anything about your German A1/A2/B1 study materials!")
st.divider()

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [] # stores all the chat messages 

# Display chat history 
for message in st.session_state.messages: # loops thru all the prev messages
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message.get("sources"):
            st.caption(f"📚 Sources: {', '.join(message['sources'])}")




prompt = st.chat_input("Ask a question about German...") # input 

if prompt:
    # Show user message
    st.session_state.messages.append({
        "role": "user",
        "content": prompt,
        "sources": []
    })
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate and show answer
    with st.chat_message("assistant"):
        with st.spinner("🔍 Searching your study materials..."): # spinning animation while loading
            try:
                result = generate_answer( # calling functioon 
                    question=prompt,
                    level_filter=level_filter
                )

                st.markdown(result['answer'])

                if result['sources']:
                    st.divider()
                    st.caption(f"📚 Sources: {', '.join(result['sources'])}")
                    st.caption(f"🔍 Chunks used: {result['chunks_used']}")

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": result['answer'],
                    "sources": result['sources']
                })

            except Exception as e:
                st.error(f"Error: {e}")

# Footer
st.divider()
st.caption("Built with RAG — ChromaDB + Groq | German Study Assistant")
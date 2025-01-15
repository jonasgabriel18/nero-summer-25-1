import streamlit as st
from llm import create_chain

chain = create_chain()

st.set_page_config(page_title="NeroAI Simple RAG ChatBot", page_icon="🧠")

st.title('NeroAI Simple RAG ChatBot 🧠')

if "messages" not in st.session_state.keys():
    st.session_state.messages = [{"role": "assistant", "content": "Ask me a question about NLP or CS Theory!"}]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

try:
    if prompt := st.chat_input("Ask something"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                # response = chain.invoke(prompt)
                # st.markdown(response)
                response = st.write_stream(chain.stream(prompt))
        
        message = {"role": "assistant", "content": response}
        st.session_state.messages.append(message)
except Exception as e:
    # Expecting a BadRequestError, in case if the prompt passes the maximum token limit
    st.error(f"An error occurred: {e}")
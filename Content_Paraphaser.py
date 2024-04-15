import streamlit as st
from streamlit_quill import st_quill 
import pandas as pd
import anthropic
from dotenv import load_dotenv
import os

if 'user_input' not in st.session_state:
    st.session_state.user_input = ''
    
#### Claude API setup ####
load_dotenv()
client = anthropic.Anthropic(
    api_key = os.getenv('claude_api_key')
)

# message = client.messages.create(
#     model="claude-3-opus-20240229",
#     max_tokens=4000,
#     temperature=0,
#     system="\nYour role as a Thai Content Paraphraser involves the meticulous task of rephrasing Thai content to enhance its comprehensiveness, ensuring that the meaning, context, and keywords are enriched and effectively conveyed. Your expertise lies in skillfully crafting paraphrased versions that not only capture the essence of the original content but also broaden its scope, depth, and relevance. Through your adeptness in language and comprehension, you strive to elevate the quality and accessibility of the information presented, catering to a diverse audience and optimizing its impact across various platforms and mediums, AND YOU MUST RESPONSE IN THAI",
#     messages=[]
# )

##### Title of the app #####

st.title ('Thai Content Paraphraser')
st.divider()

##### Front End #####
user_input = st_quill(placeholder="Enter your content here...", html=True, readonly=False, key='user_input')

paraphase_button = st.button('Paraphrase')

#### Button ####
if paraphase_button:
    message = client.messages.create(
        model="claude-3-opus-20240229",
        max_tokens=4000,
        temperature=0,
        system="\nYour role as a Thai Content Paraphraser involves the meticulous task of rephrasing Thai content to enhance its comprehensiveness, ensuring that the meaning, context, and keywords are enriched and effectively conveyed. Your expertise lies in skillfully crafting paraphrased versions that not only capture the essence of the original content but also broaden its scope, depth, and relevance. Through your adeptness in language and comprehension, you strive to elevate the quality and accessibility of the information presented, catering to a diverse audience and optimizing its impact across various platforms and mediums, AND YOU MUST RESPONSE IN THAI",
        messages=[
        {"role": "user", "content": user_input}
        ]
    )
    
    raw_text = message.content
    text_cleaned = raw_text[0].text
    st.write(text_cleaned)
    
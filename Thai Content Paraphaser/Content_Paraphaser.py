import streamlit as st
from streamlit_quill import st_quill 
from streamlit_extras.stylable_container import stylable_container 
import pandas as pd
import anthropic
from dotenv import load_dotenv
import os
import re

#### CSS Customization ####

def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
        
local_css("style.css")

#### Session State ####

if 'user_input' not in st.session_state:
    st.session_state.user_input = None
    
#### Claude API setup ####
load_dotenv()
client = anthropic.Anthropic(
    api_key = os.getenv('claude_api_key')
)

tone_prompts = {
    'Business': "As a Thai Content Paraphraser, your primary duty is to meticulously rephrase Thai content to enhance its depth and clarity. You ensure that the essence, context, and key points remain intact and are effectively conveyed. Your expertise lies in crafting paraphrased versions that maintain the core message of the original content while expanding its significance and relevance. DO NOT expand the character further than the original content only to creating paraphrased versions",
    
    'Neutral': "As a Thai Content Paraphraser, your main responsibility is to carefully reword Thai content to improve its depth and clarity. You ensure that the essence, context, and key points are retained and effectively communicated. Your skill lies in creating paraphrased versions that not only maintain the core message of the original content but also expand its significance and applicability but, do not expand the character further than the original content only to creating paraphrased versions , AND YOU MUST RESPONSE IN THAI",

    'Academic': "As a a Thai content paraphraser, your main duty is to carefully reword Thai text such that its clarity and depth are improved. It critical to successfully communicate the essential ideas, context, and points without losing any of them. You are an expert at creating condensed versions that capture the essence of the original material while expanding its relevance and application while staying within the original character count. This academic project necessitates a sophisticated comprehension of linguistic subtleties and contextual significance in order to preserve the original content integrity and increase its scholarly effect.  DO NOT expand the character further than the original content only to creating paraphrased versions"
    
}


##### Title of the app #####
st.title ('Thai Content Paraphraser')

##### Front End #####
user_input = st_quill(placeholder="Enter your content here...", html=True, readonly=False, key='quill_input')
st.session_state.user_input = user_input

#### Paraphrase_button ####
with stylable_container( 
    "paraphrase_button",
    css_styles= """
    [data-testid="baseButton-secondary"] {
        background-color: #EEEEEE;
        color: #000000; /* Sets the text color to black */
    }

    [data-testid="baseButton-secondary"] p {
        color: inherit; /* Inherits color from parent (button) */
    }
    """,
):
    tone_select = st.selectbox('Select Tones', tone_prompts.keys(), key='tone_select')
    paraphase_button = st.button("Paraphrase", key="paraphrase_button")
    # Create a select box for tone selection
# paraphase_button = st.button('Paraphrase')
if paraphase_button:
    message = client.messages.create(
        model="claude-3-sonnet-20240229",
        max_tokens=4000,
        temperature=0,
        system= tone_prompts[tone_select],
        messages=[
        {"role": "user", "content": user_input}
        ]
    )
    
    raw_text = message.content
    text_cleaned = raw_text[0].text
    
    #Remove markdown and html tags from the text using regex
    text_cleaned = re.sub(r'<[^>]*>', '', text_cleaned)
    text_cleaned = re.sub(r'\*\*', '', text_cleaned)
    
    #Display the paraphrased content in the text area
    st.subheader('Paraphrased Content')
    with stylable_container(
        key = 'paraphrased_content',
        css_styles= """
        {   border: 1px solid #EEEEEE;
            border-radius: 10px;
            padding: 15px;
            width: auto;
            overflow: auto;
            text-color: #EEEEEE;
            }
        """,
    ):
        st.markdown(text_cleaned)

    #Count the number of words in the text_cleaned
    c1, c2, c3, c4 = st.columns(4)
    
    with c1:
        character_count = len(text_cleaned.replace(" ", ""))
        st.metric(label='No. Characters', value=character_count)
        
    with c2:
        word_count = len(text_cleaned.split())
        st.metric(label='No. Words', value=word_count)
        
    with c3:
        original_word_count = len(user_input.split())
        st.metric(label='Original No. Words', value=original_word_count)
    
    with c4:
        original_character_count = len(user_input.replace(" ", ""))
        st.metric(label='Original No. Characters', value=original_character_count)
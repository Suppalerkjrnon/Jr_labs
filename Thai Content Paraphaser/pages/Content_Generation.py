import streamlit as st
from streamlit_quill import st_quill 
from streamlit_extras.stylable_container import stylable_container 
import pandas as pd
import anthropic
from dotenv import load_dotenv
import os
import re
import ast


#### CSS Customization ####

# def local_css(file_name):
#     with open(file_name) as f:
#         st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
        
# local_css("style.css")

#### Session State ####

if 'user_input' not in st.session_state:
    st.session_state.user_input = None
    
#### Claude API setup ####
load_dotenv()
client = anthropic.Anthropic(
    api_key = os.getenv('claude_api_key')
)

# tone_prompts = {
    
#     # 'Business': "As a Thai content paraphrasing, your main task is to carefully translate Thai text to improve its lucidity and nuance in a business setting make sure that you are using business wording or rewriting in business style. Make sure the primary concepts, context, and pertinent facts are effectively communicated while boosting relevance and applicability. but, do not expand the character further than the original only to creating paraphrased versions. (IMPORTANT: YOU MUST RESPONSE IN THAI)",
    
#     'Neutral': "As a Thai Content Paraphraser, your main task is to carefully reword Thai content to improve its depth and clarity. You ensure that the essence, context, and key points are retained and effectively communicated. Your skill lies in creating paraphrased versions that not only maintain the core message of the original content but also expand its significance and applicability but, do not expand the character further than the original content only to creating paraphrased versions , (IMPORTANT: YOU MUST RESPONSE IN THAI)",

#     # 'Academic': "As a Thai content paraphrasing, your main task is to carefully translate Thai text to improve its lucidity and nuance in an academic context make sure the word that you are using is academic professional rewrite style. Ensure effective communication of the main ideas, context, and important details while enhancing relevance and applicability but, do not expand the character further than the original content only to creating paraphrased versions. (IMPORTANT: YOU MUST RESPONSE IN THAI)"
    
# }

tone_select = ['Business', 'Neutral', 'Academic']

topic_prompts = """

You are an expert in content writing. Your task is to help a user generate 5 content topics that align with their high-level idea and a specified tone. 

The user will provide their content idea as a message

They will also specify the desired tone for the topics along with the message.

First, carefully analyze the user's idea. Consider the key themes, concepts, and potential angles to explore.

Then, brainstorm a list of at least 10 possible content topics that build upon the user's core idea. As you brainstorm, keep the specified {{ TOPIC_TONE }} at the forefront of your mind. Each topic should align with and convey that tone.

Once you have your initial list, critically evaluate each topic. Refine the phrasing and focus of the strongest ones. Eliminate any that don't fully align with the {{ TOPIC_TONE }} or only tangentially relate to the user's idea. 

Select the top 5 topics that most effectively combine the user's idea with the target tone. Aim for topics that are specific, engaging, and have clear potential to be developed into full content pieces.

Present your final 5 recommended topics in a numbered list, with each topic concisely summarized in 1-2 sentences. Enclose your list in <topics> tags.

After your list, explain in a few sentences how the topics effectively build upon the user's idea while aligning with the specified tone. Enclose your explanation in <explanation> tags.

Remember, your role is to use your content expertise to guide the user from a general idea to specific, tone-aligned content topics they can move forward with. Choose topics with that end goal in mind.

            """

##### Title of the app #####
st.title ('Thai Content Generation')

##### Front End #####
user_topic_input = st.text_input("โปรดใส่เรื่องที่คุณสนใจเพื่อทำหัวข้อของ Content", key='user_input')
# st.session_state.user_input = user_input

#### Paraphrase_button ####
with stylable_container( 
    "generate_content_button",
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
    tone_select = st.selectbox('Select Tones', tone_select, key='tone_select')
    generate_content_button = st.button("Generate", key="generate_content_button")
    # Create a select box for tone selection
# paraphase_button = st.button('Paraphrase')
if generate_content_button:
    message = client.messages.create(
        model="claude-3-sonnet-20240229",
        max_tokens=4000,
        temperature=0,
        system= topic_prompts,
        messages=[
        {"role": "user", "content": user_topic_input+" "+tone_select}
        ]
    )
    
    raw_text = message.content
    # Extracting the string from the TextBlock object
    raw_text = raw_text[0].text

    # Define the regex patterns
    topics_pattern = r'<topics>(.*?)</topics>'
    explanation_pattern = r'<explanation>(.*?)</explanation>'

    # Find the text content using regex
    topics_match = re.search(topics_pattern, raw_text, re.DOTALL)
    explanation_match = re.search(explanation_pattern, raw_text, re.DOTALL)

    # Extract the matched text content
    topics_text = topics_match.group(1).strip() if topics_match else None
    explanation_text = explanation_match.group(1).strip() if explanation_match else None

    # Print the extracted text content
    st.write("Topics:")
    st.write(topics_text)
    st.write("\nExplanation:")
    st.write(explanation_text)

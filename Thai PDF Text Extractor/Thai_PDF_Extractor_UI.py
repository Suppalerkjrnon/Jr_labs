
######## Import ########
import streamlit as st
import time
import requests
import tempfile
import os
from io import BytesIO
import fitz
import re
from html import unescape
import requests
import random
from datetime import datetime

################ Page Name ################
st.set_page_config(layout="wide", page_title="Thai Text Extractor UI", page_icon=":robot_face:")

################ Initializing Session States ################

if 'thread_id' not in st.session_state:
    st.session_state.thread_id = None
if 'resume_upload' not in st.session_state:
    st.session_state.resume_upload = False
if 'html_status' not in st.session_state:
    st.session_state.html_status = False
if 'messages' not in st.session_state:
    st.session_state.messages= []
if 'file_id_list' not in st.session_state:
    st.session_state.file_id_list = []
    
def generate_unique_id():
    if 'unique_id' not in st.session_state:
        # Create a datetime object and get its timestamp in milliseconds
        current_time_unix = int(datetime.now().timestamp() * 1000)
        st.session_state.unique_id = current_time_unix

    unique_id = st.session_state.unique_id
    st.session_state.unique_id += 1
    return unique_id

# Check if unique_id is not already set in the session state
if 'unique_id' not in st.session_state:
    # Generate and set the unique_id in the session state
    unique_id = generate_unique_id()
    st.session_state.unique_id = unique_id

def create_bytesio():
    return BytesIO()

if 'doc_content' not in st.session_state:
    st.session_state.doc_content = create_bytesio()

################ Header Section ################
header_column1, header_column2 = st.columns([0.9,0.1])

with header_column1:
    st.title("Thai PDF Text Extractor UI")

with header_column2:
    clear_button = st.button(":red[เริ่มต้นใหม่]")
    if clear_button:
        st.session_state.resume_upload = False
        st.session_state.html_status = False
        st.session_state.messages = []
        st.session_state.file_id_list = []
        st.session_state.doc_content = create_bytesio()
        st.rerun()

st.divider()

################ Upload Section ################
if not st.session_state.resume_upload:
    st.write("กรุณา <span style='color:red;'>'อัพโหลด' </span>ไฟล์เอกสาร", unsafe_allow_html=True)
    uploaded_file = st.file_uploader("โปรดเลือกไฟล์ PDF ของท่าน", type="pdf")
    if uploaded_file is not None:
        file_detail = {"name": uploaded_file.name, "type": uploaded_file.type}
        file_directory = "F:\\For work\\Thai PDF Text Extractor\\PDF_Files"     #Replace with your own directory
        file_name, file_extension = os.path.splitext(uploaded_file.name)
        full_file_name = file_name + "_" +  str(st.session_state.unique_id) + file_extension
        full_file_directory = file_directory + '/' +  str(st.session_state.unique_id)
        if not os.path.exists(full_file_directory):
            os.makedirs(full_file_directory)
        
        if uploaded_file.type == "application/pdf":
            base_file_name = uploaded_file.name.split('.pdf')[0]
            pdf_filename = os.path.join(full_file_directory, uploaded_file.name)
            with open(pdf_filename, "wb") as file:
                file.write(uploaded_file.getbuffer())

        def extract_thai_text(pdf_filename):
            pdf_document = fitz.open(pdf_filename)
            text = ""
            for page_number in range(pdf_document.page_count):
                if page_number == 0:  # PDF page numbers start from 0
                    first_page = pdf_document[page_number]
                    text += first_page.get_text()
                    first_page = text

                else:
                    page = pdf_document[page_number]
                    text += page.get_text()

            pdf_document.close()

            return text, first_page
    
        # Function to create HTML content from extracted text
        def create_html_content(pdf_filename):
            html_content = ""
            html_first_page_content = ""

            #Precess PDF File 
            text, first_page = extract_thai_text(pdf_filename)

            #Concat Text to html_content
            html_content += text

            #Concat First page to html_content_first_page
            html_first_page_content += first_page

            return html_content, html_first_page_content

        # Create HTML content
        html_content, html_first_page_content= create_html_content(pdf_filename=pdf_filename)

        #Save Html content
        base_file_name_full = base_file_name

        # Save first page content to HTML file
        base_file_name_first_page = base_file_name + "_first_page"

        # List of HTML file names to be processed
        html_objects = { 
            base_file_name_full:html_content, 
            base_file_name_first_page:html_first_page_content
            }
        
        pua = {
            '63233': '&#3636;', '63234': '&#3637;', '63235': '&#3638;', '63236': '&#3639;', '63237': '&#3656;',
            '63238': '&#3657;', '63242': '&#3656;', '63243': '&#3657;', '63246': '&#3660;', '63248': '&#3633;',
            '63250': '&#3655;', '63251': '&#3656;', '63252': '&#3657;'
        }

        def replace_special_characters(html_text, replacement_dict):
            pattern = re.compile(r'&#(\d{5});')
            replaced_content = pattern.sub(lambda m: replacement_dict.get(m.group(1), m.group(0)), html_text)
            replaced_content = unescape(replaced_content)
            return replaced_content

        st.session_state.html_status = True

        def custom_substitution(text):
            p4 = re.compile(r'[ ]+$', re.MULTILINE)
            p5 = re.compile(r'[0-9]+\n+คณะกรรมการร่างรัฐธรรมนูญ 29 มีนาคม 2559\n+')
            p6 = re.compile(r'^\s+มาตรา\s+([0-9]+)(.*?)(?=(\n\s+มาตรา\s+[0-9]+))', re.DOTALL | re.MULTILINE)
            p7 = re.compile(r'\s+(?=[ัุูิีึื])')

            text = p4.sub('', text)
            text = p5.sub('', text)
            text = p6.sub('\nมาตรา \\1\\2', text)
            text = p7.sub('', text)
            
            special_characters = {
                '&#63233;': 'อะ',
                '&#63234;': 'อั',
                '#63235;': 'อา',
                '#63236;': 'อิ',
                '#63237;': 'อี',
                '#63238;': 'อึ',
                '#63242;': 'อุ',
                '#63243;': 'อู',
                '#63246;': 'เอ',
                '#63248;': 'แอ',
                '#63250;': 'ใอ',
                '#63251;': 'ไอ',
                '#63252;': 'โอ',
            }

            for code, char in special_characters.items():
                text = text.replace(code, char)

            text = re.sub(r'([่้๊๋])([ัุูิีึื])', r'\2\1', text)
            text = re.sub(r'([ัุูิีึื])\s+([่้๊๋])', r'\1\2', text)
            text = text.replace("Applicant #", "\nApplicant #")
            text = re.sub(r'\.\s+', '.\n', text)
            text = re.sub(r'^\s+|\s+$', '', text, flags=re.MULTILINE)
            text = ''.join(char for char in text if (32 <= ord(char) <= 126) or (3584 <= ord(char) <= 3711))

            return text     

        def process_html(html_objects, replacement_dict):
            text_dict = {}

            for name, content in html_objects.items():
                replaced_content = replace_special_characters(content, replacement_dict)
                processed_content = custom_substitution(replaced_content)

                #Change file to path
                text_temp_file_name = name + ".txt"
                text_file_path = os.path.join(full_file_directory, text_temp_file_name)
                text_dict[text_file_path] = processed_content

            return text_dict
    
        # Process HTML and save to a text file
        if st.session_state.html_status:
            text_dict = process_html(html_objects, pua)
            for path, content in text_dict.items():
                with open(path, 'w', encoding='utf-8') as text_file:
                    text_file.write(content)
                st.success(f"Processed content saved to: {path}")

######## Import ########
import time
from docx import Document
import requests
import tempfile
import os
from io import BytesIO
import fitz
import re
import requests 
import random
import streamlit as st
import streamlit.components.v1 as components
from streamlit_quill import st_quill
from streamlit_geolocation import streamlit_geolocation
import sqlite3
import html
import pandas as pd
from datetime import datetime
from geopy.geocoders import Nominatim
import folium
import json
from openai import OpenAI
import openai
import requests


geolocator = Nominatim(user_agent="Offline Toxic report", timeout= 30)

# import streamlit_authenticator as stauth
# import yaml 
# from yaml.loader import SafeLoader

###### page config ######

st.set_page_config(
    page_title="Lan Parties Toxic Report",
    page_icon="🎮",
    layout="centered",
    initial_sidebar_state="expanded",
)

###### Session State ######

if 'selected_language' not in st.session_state:
    st.session_state.selected_language = ''
    
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

# st.write("Unique ID: ", st.session_state.unique_id)

if 'user_query_location' not in st.session_state:
    st.session_state.user_query_location = []

###### List of incident types ######

user_input = []
    
language_info = {
    "English": {
        'location_query_info': "Please enter the location name",
        'location_desc_info': "Enter the detail of the location",
        'toxic_type_info': "Select type of toxic behavior",
        'selected_time_info': "Enter the Time of the Case",
        'description_info': "Enter the description of the case",
        'information_box': "You can upload multiple files, photos and videos. Please make sure to upload the correct files, photos and videos.",
        'submit_button_label': "Submit",
        'upload_files_header': "Upload Files",
        'upload_files': "Choose a files",
        'upload_photos': "Upload a photo",
        'upload_videos': "Upload a video",
        'case_sucess_message': "Case Submitted",
        'case_database_sucess_message': "Data has been saved to the database",
        'location_methods': ["Select the method to get the location", "Use Current Location", "Enter Location Name"]},  # 'Use Current Location', 'Enter Location Name

    "Bahasa Melayu": { 
        'location_query_info': "Sila masukkan nama lokasi",
        'location_desc_info': "Masukkan Butiran Lokasi",
        'toxic_type_info': "Pilih Jenis Perilaku Toksik",
        'selected_time_info': "Masukkan Masa Kes",
        'description_info': "Masukkan Keterangan Kes",
        'information_box': "Anda boleh memuat naik beberapa fail, gambar dan video. Sila pastikan untuk memuat naik fail, gambar dan video yang betul.",
        'submit_button_label': "Hantar",
        'upload_files_header': "Muat Naik Fail",
        'upload_files': "Pilih fail",
        'upload_photos': "Muat naik gambar",
        'upload_videos': "Muat naik video",
        'case_sucess_message': "Kes telah dihantar",
        'case_database_sucess_message': "Data telah disimpan ke pangkalan data",
        'location_methods': ["Pilih kaedah untuk mendapatkan lokasi", "Gunakan Lokasi Semasa", "Masukkan Nama Lokasi"]},

    "ภาษาไทย": {
        'location_query_info': "กรุณาระบุชื่อสถานที่",
        'location_desc_info': "กรุณาระบุข้อมูลเกี่ยวกับสถานที่",
        'toxic_type_info': "กรุณาเลือกประเภทของพฤติกรรมที่ไม่พึงประสงค์",
        'selected_time_info': "กรุณาระบุเวลาของเหตุการณ์",
        'description_info': "กรุณาระบุคำอธิบายของเหตุการณ์",
        'information_box': "คุณสามารถอัปโหลดไฟล์หลายรายการ รูปภาพและวิดีโอ โปรดตรวจสอบให้แน่ใจว่าไฟล์ รูปภาพและวิดีโอที่อัปโหลดถูกต้อง",
        'submit_button_label': "ส่ง",
        'upload_files_header': "อัปโหลดไฟล์",
        'upload_files': "เลือกไฟล์",
        'upload_photos': "อัปโหลดรูปภาพ",
        'upload_videos': "อัปโหลดวิดีโอ",
        'case_sucess_message': "เรื่องได้ถูกส่ง",
        'case_database_sucess_message': "ข้อมูลได้รับการบันทึกลงในฐานข้อมูล",
        'location_methods': ["เลือกวิธีการในการรับสถานที่", "ใช้ตำแหน่งปัจจุบัน", "ป้อนชื่อสถานที่"]}
}

location_methods_lang = {
    "English": ["Select the method to get the location", "Use Current Location", "Enter Location Name"],
    "Bahasa Melayu": ["Pilih kaedah untuk mendapatkan lokasi", "Gunakan Lokasi Semasa", "Masukkan Nama Lokasi"],
    "ภาษาไทย": ["เลือกวิธีการในการรับสถานที่", "ใช้ตำแหน่งปัจจุบัน", "ป้อนชื่อสถานที่"]

}

# Incident Type IDs : [Thai 0, Malay 1, English 2]
toxic_types = {
    1: ['การล่วงละเมิดด้านคำพูด','Penyalahgunaan' ,'Verbal Abuse'],
    2: ['การทำให้ความเดือดร้อน', 'Mengganggu','Griefing'],
    3: ['การโกง', 'Penipuan','Cheating'],
    4: ['ไม่มีน้ำใจนักกีฬา', 'Tidak Beretika' ,'Unsportsmanlike'],
    5: ['การเลือกปฏิบัติ', 'Diskriminasi','Discrimination'],
    6: ['การข่มขู่', 'Intimidasi', 'Intimidation'],
    7: ['การเล่นตลกส่อเสียด','Trolling', 'Trolling'],
    8: ['การละเมิดความเป็นส่วนตัว:', 'Penyusupan Privasi','Invasion of Privacy'],
    9: ['การคุกคาม', 'Ancaman', 'Threats'],
    10: ['การคุกคามทางเพศ', 'Perangai Seksual:','Sexual Harassment'],
    11: ['อื่นๆ', 'Other', 'Other'],
}

# Language key for above dict
language_keys = {
    'English': 2,
    'ภาษาไทย': 0,
    'Bahasa Melayu': 1,
}

################################################################################

###### Date picker as Header columns ######
h_col1, h_col2, h_col3 = st.columns(3)

with h_col3:
    st.subheader("Please Select Date")
    selected_date = st.date_input("Start Date")

st.divider()

###### Title of the page ########
st.title("🎮 LAN Parties Toxic Behavior Report")

######User selected Lanaguage######
st.write("Please select a language. | กรุณาเลือกภาษาเพื่อดำเนินการต่อ | Sila pilih bahasa untuk meneruskan.")
selected_language = st.selectbox("Please select a language", list(language_info.keys()))
st.session_state.selected_language = selected_language

info = language_info[st.session_state.selected_language]

st.write("You selected: ", st.session_state.selected_language)

################################################################################
###### Function ######

def find_location(place, language="en"):
    if place:
        location = geolocator.geocode(place, language=language)
        if location is not None:
            return location.address, location.latitude, location.longitude, location.raw
        else:
            return "Not Found", "Not Found", "Not Found", "Not Found"
    else:
        return "Please enter a location name", "Not Found", "Not Found", "Not Found"

location_methods = st.selectbox(location_methods_lang.get(st.session_state.selected_language, ["Select the method to get the location"])[0], location_methods_lang.get(st.session_state.selected_language, ["Select the method to get the location"])[1:])
selected_method_translation = location_methods_lang.get(st.session_state.selected_language, ["Select the method to get the location"])


toxic_behavior_list = toxic_types.values()  # Retrieve all incident types lists
selected_language_key = language_keys[st.session_state.selected_language]
selected_toxic_behavior_list = [types[selected_language_key] for types in toxic_behavior_list]

################################################################################

if location_methods == selected_method_translation[1]:
    get_geo_location = streamlit_geolocation()
    # st.write("Your current location is: ", get_geo_location)
    latitude = get_geo_location.get("latitude")
    longitude = get_geo_location.get("longitude")
    user_geo_location = f"{latitude}, {longitude}"

    if latitude is not None and longitude is not None:
        user_geo_location = f"{latitude}, {longitude}"

        address = geolocator.reverse(user_geo_location, language="en")
        address = address[0]


        map = folium.Map(location=[latitude, longitude], zoom_start=15)
        folium.Marker([latitude, longitude]).add_to(map)
        st_folium = components.html(map._repr_html_(), width=700, height=500)
    else:
        st.write("Please click the button the get your location")

if location_methods == selected_method_translation[2]:
    user_query_location = st.text_input("Enter Location Name")
            
    address, latitude, longitude, location_raw = find_location(user_query_location)
    
    if latitude != "Not Found" and longitude != "Not Found":
        map = folium.Map(location=[latitude, longitude], zoom_start=15)
        folium.Marker([latitude, longitude], popup=address).add_to(map)
        st_folium = components.html(map._repr_html_(), width=700, height=500)

user_geo_location = f"{latitude}, {longitude}"
user_location_desc = st.text_input(info['location_desc_info'])
user_toxic_behavior_type = st.selectbox(info['toxic_type_info'], selected_toxic_behavior_list)
user_selected_date = selected_date
user_selected_time = st.time_input(info['selected_time_info']) #should be time selection
user_desc_input = st_quill(key='quill', value='', html=True, toolbar=None, readonly=False)

################################################################################

###### File Uploader ######
st.subheader(info['upload_files_header'])

upload_file_name = None  
upload_photo_name = None  
upload_video_name = None 

###### Multi language information box ######

information_box = st.info(info['information_box'])


###### File Uploader ######

# uploaded_files = st.file_uploader("Choose a files", type=None, accept_multiple_files=True)
uploaded_files = st.file_uploader(info['upload_files'], type=None, accept_multiple_files=True)

if uploaded_files is not None:
    for uploaded_file in uploaded_files:
        file_details = {"FileName": uploaded_file.name, "FileType": uploaded_file.type}
        file_directory = 'Media Directory'
        file_name, file_extension = os.path.splitext(uploaded_file.name)
        full_file_name = file_name + "_" + str(st.session_state.unique_id) + file_extension    
        full_directory = file_directory + '/' + str(st.session_state.unique_id)
        if not os.path.exists(full_directory):
            os.makedirs(full_directory)
        
        if uploaded_file.type == file_details["FileType"]:
            upload_file_name = os.path.join(full_directory, full_file_name)
            with open(upload_file_name, "wb") as file:
                file.write(uploaded_file.getbuffer()) 
        
###### Photo Uploader ######
                
photo_uploaded = st.file_uploader(info['upload_photos'], type=None, accept_multiple_files=True)

if photo_uploaded is not None:
    for photo in photo_uploaded:
        photo_details = {"FileName": photo.name, "FileType": photo.type}
        photo_directory = '/Media Directory'
        photo_name, photo_extension = os.path.splitext(photo.name)
        full_photo_name = photo_name + "_" +  str(st.session_state.unique_id) + photo_extension
        full_photo_directory = photo_directory + '/' +  str(st.session_state.unique_id)
        if not os.path.exists(full_photo_directory):
            os.makedirs(full_photo_directory)

        if photo.type == photo_details["FileType"]:
            upload_photo_name = os.path.join(full_photo_directory, full_photo_name)
            with open(upload_photo_name, "wb") as f:
                f.write(photo.read())
        
        # st.image(photo, caption='Uploaded Image', use_column_width=True)

###### Video Uploader ######

video_uploaded = st.file_uploader(info['upload_videos'], type=None, accept_multiple_files=True)
if video_uploaded is not None:
    for video in video_uploaded:
        video_details = {"FileName": video.name, "FileType": video.type}
        video_name = video.name
        video_directory = '/Media Directory'
        video_name, video_extension = os.path.splitext(video.name)
        full_video_name = video_name + "_" +  str(st.session_state.unique_id) + video_extension

        full_video_directory = video_directory + '/' +  str(st.session_state.unique_id)
        if not os.path.exists(full_video_directory):
            os.makedirs(full_video_directory)

        if video.type == video_details["FileType"]:
            upload_video_name = os.path.join(full_video_directory, full_video_name)
            with open(upload_video_name, "wb") as f:
                f.write(video.read())

        # st.video(video, start_time=0)

st.divider()

################################################################################

# Define a dictionary to map selected language to description fields
language_description_mapping = {
    "English": user_desc_input,
    "Thai": user_desc_input,
    "Malay": user_desc_input
}

description_value = language_description_mapping.get(st.session_state.selected_language, "")

st.write(description_value)


### Submit Button ###

if st.button(info['submit_button_label']):

    upload_file_name_logic = full_file_name if upload_file_name is not None else None
    upload_photo_name_logic = full_photo_name if upload_photo_name is not None else None
    upload_video_name_logic = full_video_name if upload_video_name is not None else None

    user_input.append({
        "Unique_ID": st.session_state.unique_id,
        "Geo_Location": user_geo_location,
        "Address": address,
        "Location_desc": user_location_desc,
        "Toxic_Type": user_toxic_behavior_type,
        "Date": user_selected_date,
        "Time": user_selected_time,
        "Description_en": description_value if st.session_state.selected_language == "English" else "",
        "Description_th": description_value if st.session_state.selected_language == "Thai" else "",
        "Description_malay": description_value if st.session_state.selected_language == "Malay" else "",
        "Files": upload_file_name_logic,
        "Photos": upload_photo_name_logic,
        "Videos": upload_video_name_logic
    })

    st.success(info['case_sucess_message'])

    # Generate a new unique ID for the next record
    st.session_state.unique_id += 1

    st.dataframe(user_input)

    ###### Create a connection to the database ######

    db_paths = 'database.db'

    # if st.session_state.selected_language in db_paths:
    conn = sqlite3.connect(db_paths)
    # Data type Prep
    user_input_df = pd.DataFrame(user_input)

    user_input_df["Geo_Location"] = user_input_df["Geo_Location"].astype(str)
    user_input_df["Location_desc"] = user_input_df["Location_desc"].astype(str)
    user_input_df["Toxic_Type"] = user_input_df["Toxic_Type"].astype(str)
    user_input_df['Address'] = user_input_df['Address'].astype(str)
    user_input_df["Date"] = user_input_df["Date"].astype(str)
    user_input_df["Time"] = user_input_df["Time"].astype(str)
    user_input_df["Description_en"] = user_input_df["Description_en"]
    user_input_df["Description_th"] = user_input_df["Description_th"]
    user_input_df["Description_malay"] = user_input_df["Description_malay"]
    user_input_df["Files"] = user_input_df["Files"].astype(str)
    user_input_df["Photos"] = user_input_df["Photos"].astype(str)
    user_input_df["Videos"] = user_input_df["Videos"].astype(str)
    user_input_df['Unique_ID'] = user_input_df['Unique_ID'].astype(str)

    user_input_df.to_sql('database', conn, if_exists='append', index=False)

    conn.close()

    st.success(info['case_database_sucess_message'])    

################################################################################

################################################################################
        
    # def translate(text, target_lang):
    #     # Define translation messages based on language pairs
    #     translation_messages = {
    #         ("English", "Malay"): "Kindly translate the following text from english to malay. DO NOT NARRORATE, ONLY PROVIDE THE TRANSLATED TEXT, Please keep html and markdown element",
    #         ("English", "Thai"): "Kindly translate the following text from english to thai. DO NOT NARRORATE, ONLY PROVIDE THE TRANSLATED TEXT, Please keep html and markdown element",
    #         ("Malay", "English"): "Kindly translate the following text from malay to english. DO NOT NARRORATE, ONLY PROVIDE THE TRANSLATED TEXT, Please keep html and markdown element",
    #         ("Malay", "Thai"): "Kindly translate the following text from malay to thai. DO NOT NARRORATE, ONLY PROVIDE THE TRANSLATED TEXT, Please keep html and markdown element", 
    #         ("Thai", "English"): "Kindly translate the following text from thai to english. DO NOT NARRORATE, ONLY PROVIDE THE TRANSLATED TEXT, Please keep html and markdown element",
    #         ("Thai", "Malay"): "Kindly translate the following text from thai to malay. DO NOT NARRORATE, ONLY PROVIDE THE TRANSLATED TEXT, Please keep html and markdown element"
    #     }
        
    #     # Get the source language from the selected language
    #     source_lang = st.session_state.selected_language
        
    #     # Get the translation message based on the source and target languages
    #     translation_message = translation_messages.get((source_lang, target_lang), "")
    
    #     # Perform the translation
    #     translated_text = ""
    #     if translation_message:

    #         # Split the text into chunks of maximum length
    #         max_chunk_length = 1000  # Adjust as needed
    #         text_chunks = [text[i:i+max_chunk_length] for i in range(0, len(text), max_chunk_length)]
            
    #         # Translate each chunk individually
    #         translated_chunks = []
    #         for chunk in text_chunks:
    #             response = client.chat.completions.create(
    #                 model="gpt-4-turbo-preview",
    #                 messages=[
    #                     {"role": "system", "content": translation_message},
    #                     {"role": "user", "content": f"{chunk}"}
    #                 ]
    #             )
    #             translated_chunks.append(response.choices[0].message.content)
        
    #         # Concatenate the translated chunks
    #         translated_text = " ".join(translated_chunks)
    
    #     return translated_text
    
    # # Perform the translation

    # translated_text_en = translate(description_value, "English")
    # translated_text_malay = translate(description_value, "Malay")
    # translated_text_thai = translate(description_value, "Thai")

    # # Save the translated text to the database according to the columns, only save if the columns are empty
    # conn = sqlite3.connect(db_paths)

    # if not user_input_df["Description_en"].all():
    #     user_input_df["Description_en"] = translated_text_en
    #     user_input_df.to_sql('ceasefire', conn, if_exists='replace', index=False)

    # if not user_input_df["Description_malay"].all():
    #     user_input_df["Description_malay"] = translated_text_malay
    #     user_input_df.to_sql('ceasefire', conn, if_exists='replace', index=False)

    # if not user_input_df["Description_th"].all():
    #     user_input_df["Description_th"] = translated_text_thai
    #     user_input_df.to_sql('ceasefire', conn, if_exists='replace', index=False)

    # conn.close()
















    













# aysnc translation when submit button is clicked, ถ้าเจอภาษาไทยใน location ให้ regex ดูภาษาให้เจอเป็นภาษาไทย และ ส่งไปให้ GPT Translation, ที่เหลือต้องส่ง description ทั้งสามภาษาไปแปล
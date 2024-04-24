import pandas as pd 
import streamlit as st

class StreamlitApp:     # Create a class to run the Streamlit app
    def __init__(self, data):  
        self.data = data

    def run(self):     ## Create a function to run the Streamlit app
        st.title('Streamlit App')
        st.write('This is a simple Streamlit app to display the data')
        st.write(self.data)
        st.write('This is all of your data!')

    def get_data(self): # Create a function to get the data, accessing the data attribute from Streamlit class
        return self.data
    
    def file_uploader(self, file_type): # Create a function to upload a file
        return st.file_uploader('Upload a file', type=[file_type])
    
    def get_file(self, file): # Create a function to get the file
        return pd.read_csv(file)
    
# Create a file uploader and then run the streamlit app to automatically display the data
streamlit_ui = st.file_uploader('Upload a file', type=['csv'])

if streamlit_ui is not None:
    streamlit_app = StreamlitApp(pd.read_csv(streamlit_ui))
    streamlit_app.run()





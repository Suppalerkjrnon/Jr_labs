import streamlit as st
from streamlit_star_rating import st_star_rating
import pandas as pd
from datetime import datetime
import os

internship_questions_dict = {
    "question1": ['Not so much', 'For sure'],
    "question3": ['Team', 'Individual', 'Mixed'],
    "question4": ['WFH', 'Office', 'Mixed'],
    "question6": ["Not familiar", "Somewhat familiar", "I know at least one of those", "I am a master!", "I'm leaning and excited to learn more!"],
    "question16": ['Stay quiet', 'Run Away', 'Research Try out multiple tools and land on one which work the best', 'Make up an answer, and hope for the best.']
}

class file_uploader:
    def __init__(self, index):
        self.index = index
        self.resume = st.file_uploader(label=f"Upload your resume {self.index}", type=["pdf", "docx", "txt", "doc"])
        self.file_details = {"Filename": "", "FileType": "", "FileSize": ""}
        if self.resume is not None:
            self.resume_path = 'F:\For work\Streamlit form stuff\Resumes'
            self.resume_directory = os.path.join(self.resume_path,self.resume.name)
            if not os.path.exists(self.resume_path):
                os.makedirs(self.resume_path)
            with open (self.resume_directory, "wb") as file:
                file.write(self.resume.getbuffer())
            

class InternshipForm:
    def __init__(self):
        self.resume = file_uploader(index=1)
        self.question1 = (st.selectbox("Are you familiar with Agile project management practices?", internship_questions_dict["question1"]))
        self.question2 = st.text_area("Are you familiar with any applications of DS? If so list them below")
        self.question3 = st.selectbox("Do you prefer to work as a team or individually?", internship_questions_dict["question3"])
        self.question4 = st.selectbox("Do you prefer to work remotely or on site?", internship_questions_dict["question4"])
        self.question5 = st_star_rating(label= "How familiar are you with data science processes?", maxValue=5, defaultValue=1, key="rating", dark_theme=False)
        self.question6 = st.selectbox("How familiar are you with the following programming languages?", internship_questions_dict["question6"])
        self.question7 = st_star_rating("How much do you enjoy finding answers to really complex or really uncertain questions?", maxValue=5, defaultValue=1, key="rating2", emoticons=True)
        self.question8 = st.text_area("Tell us (in a nutshell) why you think you have what it takes to be a data intern?")
        self.question9 = st.text_area("What interests you about data science/analysis?")
        self.question10 = st.text_input("What is your name?")
        self.question11 = st.text_input("What is your nickname?")
        self.question12 = st.text_input("What is your number?")
        self.question13 = st.date_input("When can you start?", datetime.now())
        self.question14 = st.date_input("When do you think you will finish your internship?", datetime.now())
        self.question15 = st.date_input("When you were born?", datetime.now())
        self.question16 = st.selectbox("When you don't know the answer to something what do you do?", internship_questions_dict["question16"])
        
    
    def to_dict(self):
        return {
            "question1": self.question1,
            "question2": self.question2,
            "question3": self.question3,
            "question4": self.question4,
            "question5": self.question5,
            "question6": self.question6,
            "question7": self.question7,
            "question8": self.question8,
            "question9": self.question9,
            "question10": self.question10,
            "question11": self.question11,
            "question12": self.question12,
            "question13": self.question13,
            "question14": self.question14,
            "question15": self.question15,
            "question16": self.question16
        }

# Create a Form
form = InternshipForm()

# Save the form data to a dictionary
form_dict = form.to_dict()











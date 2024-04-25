import streamlit as st
from streamlit_star_rating import st_star_rating
import csv
from datetime import datetime
import os

class Question:
    def __init__(self, text, question_type, options=None):
        self.text = text
        self.type = question_type
        self.options = options if options else []

    def __str__(self):
        return f"{self.text} ({self.type})"
 
    def get_widget(self):
      if self.type == "text_input":
        return st.text_input(self.text, '')
      elif self.type == "text_area":
        return st.text_area(self.text)
      elif self.type == "select_box":
        return st.selectbox(self.text, self.options)
      elif self.type == "star_rating":
        return st_star_rating(self.text, maxValue=5, defaultValue=1, key="rating", dark_theme=False)
      elif self.type == "emoji_rating":
        return st_star_rating(self.text, maxValue=5, defaultValue=1, key="rating2", emoticons=True)
      elif self.type == "date_input":
        return st.date_input(self.text, datetime.now())
                
def read_questions(file_path):
    questions = []
    with open (file_path, "r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            question_text = row['question']
            question_type = row['type']
            options = [option.strip().strip("'") for option in row['options'].split(",")] if row['options'] else None
            question = Question(question_text, question_type, options)
            questions.append(question)
    return questions

class file_uploader:
    def __init__(self, index):
        self.index = index
        self.resume = st.file_uploader(label=f"Upload your resume {self.index}", type=["pdf", "docx", "txt", "doc"])
        self.file_details = {"Filename": "", "FileType": "", "FileSize": ""}
        self.resume_path = 'F:\For work\Streamlit form stuff\Resumes'

    def save_resume(self):
        if self.resume is not None:
            self.resume_directory = os.path.join(self.resume_path,self.resume.name)
            if not os.path.exists(self.resume_path):
                os.makedirs(self.resume_path)
            with open (self.resume_directory, "wb") as file:
                file.write(self.resume.getbuffer())

def main():
    st.title("Internship Application Form")
    resume = file_uploader(index=1)
    questions = read_questions('F:\Junior_Lab\Jr_labs\Streamlit stuff\question_clean.csv')
    form_dict = {}
    form_dict['resume'] = resume.file_details

    for question in questions:
        question_text = question.text
        # st.write(question) # Just for Debugging
        response = question.get_widget()
        # st.write(response)
        form_dict[question_text] = response

    # st.write(f"You answered: {form_dict}")

if __name__ == '__main__':
    main()

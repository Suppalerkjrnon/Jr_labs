import streamlit as st

# Define the custom Form class
class Form:
    def __init__(self, title):
        self.title = title
        self.inputs = []
        self.submitted = False

    # Methods for adding input widgets
    def text_input(self, label):
        input_value = st.text_input(label)
        self.inputs.append((label, input_value))

    def number_input(self, label):
        input_value = st.number_input(label)
        self.inputs.append((label, input_value))

    # Method for adding a submit button
    def submit_button(self, label):
        self.submitted =st.form_submit_button(label)

    # Method for displaying input values
    def display_inputs(self):
        for label, value in self.inputs:
            st.write(f"{label}: {value}")

    # Method for checking if the form has been submitted
    def is_submitted(self):
        return self.submitted

# Create instances of Form for different requirements
form1 = Form("Basic Information")
form2 = Form("Additional Details")

# Use each form instance within st.form contexts
with st.form("Form 1 - Basic Information"):
    form1.text_input("Enter your name")
    form1.number_input("Enter your age")
    form1.text_input("Enter your occupation")
    form1.submit_button("Submit")

    if form1.is_submitted():
        form1.display_inputs()

with st.form("Form 2 - Additional Details"):
    form2.text_input("Enter your email address")
    form2.text_input("Enter your geographical location")
    form2.submit_button("Submit")

    if form2.is_submitted():
        form2.display_inputs()


# Create a Dictionary which contains the concatenated data from both forms
concatenated_data = dict(form1.inputs + form2.inputs)

import pandas as pd 
import streamlit as st

class Expense:
    def __init__(self):
        # Read the expense and service data
        expense = pd.read_csv('/media/dr01/work/jovyan/work/Misc/Junior Lab/Fun project/Personal_Finance/page/asset/expense - expense - filled.csv')
        service = pd.read_csv('/media/dr01/work/jovyan/work/Misc/Junior Lab/Fun project/Personal_Finance/page/asset/expense - service.csv')
        
        # Display service data by using checkbox
        self.checkbox = st.checkbox('Service Overide')
        
        # If the checkbox is checked, display the service data in a Streamlit data editor
        if self.checkbox:
            self.service = st.data_editor(service, num_rows='dynamic')
        
            self.service_total = self.service['cost'].sum()
            
            #Create a new row in the expense DataFrame for the total service cost
            service_row = pd.DataFrame({'expense': ['service'], 'cost': [self.service_total]})
            expense = pd.concat([expense, service_row], ignore_index=True)
            
            # Display the merged expense DataFrame in a Streamlit data editor
            self.expense_df = st.data_editor(expense, num_rows='dynamic', width=1000, height=310)
            
        else:
            st.divider()
            self.service_total = service['cost'].sum()
        
            #Create a new row in the expense DataFrame for the total service cost
            service_row = pd.DataFrame({'expense': ['service'], 'cost': [self.service_total]})
            expense = pd.concat([expense, service_row], ignore_index=True)
            
            # Display the merged expense DataFrame in a Streamlit data editor
            self.expense_df = st.data_editor(expense, num_rows='dynamic', width=1000)

def main():
    st.title('Expense')
    expense = Expense()

if __name__ == '__main__':
    main()

import pandas as pd 
import streamlit as st

class Expense:
    def __init__(self):
        # Read the expense and service data
        expense = pd.read_csv('/media/dr01/work/jovyan/work/Misc/Junior Lab/Fun project/Personal_Finance/pages/asset/Expense File Template - expense.csv')
        
        # Display service data by using service_checkbox
        #Populate checkbox by using variable in expense data as a label, using st.multiselect
        self.expense_overide = st.checkbox('Expense Overide')
        
        if self.expense_overide:
            self.expense_list = st.multiselect('Expense Override', expense['expense'])
            
            if self.expense_list:
                self.success = st.success(f"Selected to Override {len(self.expense_list)} expenses")
                
                self.edit_df_list = []
                self.overide_list = []
                
                selected_expenses_df = pd.DataFrame()  # Initialize an empty DataFrame to store selected expenses
                
                # Concatenate selected expense rows into a single DataFrame
                for expense_item in self.expense_list:
                    expense_row = expense[expense['expense'] == expense_item]
                    if not expense_row.empty:
                        selected_expenses_df = pd.concat([selected_expenses_df, expense_row])
                    else:
                        st.warning(f"No expense found for {expense_item}.")
                
                # Append the data editor widget for the selected expenses
                unique_key = "selected_expenses_editor"  # Use a single key for the combined editor
                self.edit_df_list.append(st.data_editor(selected_expenses_df, key=unique_key, num_rows='dynamic'))
                
        else: # Default behavior if no overide is selected
            
            st.dataframe(expense, width=1200)

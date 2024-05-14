import pandas as pd 
import streamlit as st

class Expense:
    def __init__(self):
        # Read the expense and service data
        expense = pd.read_csv('F:\\For work\\Personal Finance\\pages\\asset\\Expense File Template - expense.csv')
        #Display expense data as a dataframe
        self.df = pd.DataFrame(expense)
        self.total_df = pd.DataFrame({'cost': self.df['cost'].sum()}, index=['Total'])
        self.total_df = pd.concat([self.df, self.total_df])
        
        #Last row in the dataframe, column expense write string 'Total'
        self.total_df.loc['Total', 'expense'] = 'Total Expense'

        #Create a checkbox to allow user to select expenses to overide
        self.expense_overide = st.checkbox('Expense Overide')
        
        #If the checkbox is ticked, display a multiselect widget to allow user to select expenses to overide
        if self.expense_overide:
            self.expense_list = st.multiselect('Expense Override', expense['expense'])
            #If the user has selected expenses to overide, display a success message
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
                #Make edit df list to be a dataframe
                self.edit_df = pd.concat(self.edit_df_list)
                
                # Going inside the data editor index and row to get the overide data
                for self.index, self.row in self.edit_df.iterrows():
                    self.df.loc[self.df['expense'] == self.row['expense'], 'cost'] = self.row['cost']
                    
                #Recalculate the total cost
                self.total_df = pd.DataFrame({'cost': [self.df['cost'].sum()]}, index=['Total'])
                self.total_df = pd.concat([self.df, self.total_df])
                self.total_df.loc['Total', 'expense'] = 'Total Expense'
                
        # Default behavior if no overide is selected   
        st.dataframe(self.total_df, width=1200)

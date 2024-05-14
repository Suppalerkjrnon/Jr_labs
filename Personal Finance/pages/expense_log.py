import pandas as pd 
import streamlit as st
from streamlit_gsheets import GSheetsConnection

class Expense_Log:
    def __init__(self):
        try:
            # Establish connection to Google Sheets
            self.conn = st.connection('gsheets', type=GSheetsConnection)
            # Read data from Google Sheets
            self.existing_data = self.conn.read(spreadsheet= 'https://docs.google.com/spreadsheets/d/1D3sD13BEx8B7HEr-wSsZPlqB_9YIH0LFDbOmMoaoLhY/edit?usp=sharing')
            # Convert data to DataFrame
            self.df = pd.DataFrame(self.existing_data)
            
            last_row = pd.DataFrame({'cost': self.df['cost'].sum()}, index=['Total'])
            
            self.total_df = pd.concat([self.df, last_row])
            
        except Exception as e:
            st.error(f"Error: {e}")

def main():
    st.title('Expense Log')
    st.divider()
    expense_log = Expense_Log()
    
    if hasattr(expense_log, 'df'):
        st.dataframe(expense_log.total_df, width=1000)
    else:
        st.error("Failed to load data.")

if __name__ == "__main__":
    main()


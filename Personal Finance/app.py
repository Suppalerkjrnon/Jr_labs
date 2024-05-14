import streamlit as st
import pandas as pd 
from Expense import Expense

def main():
    st.title('Personal Finance')
    income = st.number_input('Income', value=0)
    expense = Expense()
    
    
    # Display Saving amount only when user has entered income
    if income: 
        saving = income - expense.total_df['cost'].iloc[-1]
        st.metric(value=saving, label='Saving')
    else:
        st.error('Please enter income')
        
if __name__ == '__main__':
    main()
    
    
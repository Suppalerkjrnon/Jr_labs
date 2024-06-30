import pandas as pd 
import streamlit as st
from streamlit_gsheets import GSheetsConnection
import plotly.express as px

#################### Session State ####################

if 'gsheets' not in st.session_state:
    st.session_state.gsheets = False
    
if 'generate_report' not in st.session_state:
    st.session_state.generate_report = False
    
if 'existing_data' not in st.session_state:
    st.session_state.existing_data = None
    
if 'expense_log' not in st.session_state:
    st.session_state.df = None
    
if 'previous_expense_log' not in st.session_state:
    st.session_state.previous_expense_log = None

class Expense_Log:
    def __init__(self):
        try:
            # Establish connection to Google Sheets
            self.conn = st.connection('gsheets', type=GSheetsConnection)
            st.session_state.gsheets = True
            
            # Read data from Google Sheets
            self.existing_data = self.conn.read(spreadsheet= '#Replace with your Google Sheets URL') 
            st.session_state.existing_data = self.existing_data
            
            #Convert Existing Data to DataFrame
            self.df = pd.DataFrame(self.existing_data)
            st.session_state.df = self.df
            self.df['date'] = pd.to_datetime(self.df['date'])
            self.df['month'] = self.df['date'].dt.month
            self.df['year'] = self.df['date'].dt.year
            self.df['year'] = self.df['year'].astype(str)
            self.df['year'] = self.df['year'].str.replace(',', '')
            self.df['date'] = self.df['date'].dt.strftime('%Y-%m-%d')

        except Exception as e:
            st.error(f"Error: {e}")
            
def main():
    st.title('Expense Log')
    st.divider()
    expense_log = Expense_Log()
    st.session_state.expense_log = expense_log
    
    selector_month_year_col = st.columns(2)

    with selector_month_year_col[1]:
        st.warning("Please Select Month and Year")
        selected_year = st.selectbox("Year", expense_log.df['year'].unique())
        
        if selected_year: 
            selected_month = st.selectbox("Month", expense_log.df['month'].unique())

    if hasattr(expense_log, 'df'):
        st.divider()
        if selected_month and selected_year:
        
            filtered_expense_log_df = expense_log.df[expense_log.df['month'] == selected_month]
            filtered_expense_log_df = filtered_expense_log_df.reset_index(drop=True)

            #Create Previous Month DataFrame for Comparison
            previous_month = selected_month - 1
            filtered_previous_expense_log_df = expense_log.df[expense_log.df['month'] == previous_month]
            st.session_state.previous_expense_log = filtered_previous_expense_log_df
            
            st.dataframe(filtered_expense_log_df, width=1000)
            
            #Generate Report Button
            generate_report = st.button("Generate Report")
            
            if generate_report:
                st.session_state.generate_report = True
                # Summary the total cost
                #Format the cost column to 2 decimal places
                filtered_expense_log_df['cost'] = filtered_expense_log_df['cost'].apply(lambda x: round(x, 2))
                st.success(f"Total Expense: {filtered_expense_log_df['cost'].sum()} Bath")
                #Comparison total sum of cost between filtered_expense_log_df and filtered_previous_expense_log_df
                if filtered_previous_expense_log_df.empty:
                    st.warning("No data available for comparison.")
                    
                else:
                    previous_total = filtered_previous_expense_log_df['cost'].sum()
                    current_total = filtered_expense_log_df['cost'].sum()
                    #Format the total cost to 2 decimal places and delete comma
                    formatted_current_total = int(abs(current_total))             
                    formatted_previous_total = int(abs(previous_total))
                    
                    if previous_total > current_total:
                        st.success(f"Total Expense Decreased by {formatted_previous_total - formatted_current_total} Bath")
                    elif previous_total < current_total:
                        st.error(f"Total Expense Increased by {formatted_previous_total - formatted_current_total} Bath")
                    else:
                        st.success("Total Expense Remained the Same")

                #Visualization Columns
                visualzation_col = st.columns(2)
                with visualzation_col[0]:
                    pie_source = filtered_expense_log_df[filtered_expense_log_df['cost'].notnull()]
                    fig_pie = px.pie(pie_source, values='cost', names='type', title='Expense Distribution')
                    st.plotly_chart(fig_pie)

        else:
            st.error("Failed to load data.")

if __name__ == "__main__":
    main()


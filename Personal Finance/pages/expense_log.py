# General Libraries #
import pandas as pd 
from datetime import datetime

# Streamlit Libraries #
import streamlit as st
from streamlit_gsheets import GSheetsConnection
from streamlit_extras.metric_cards import style_metric_cards

# Visualization Libraries #
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt

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
            self.existing_data = self.conn.read(spreadsheet= 'Replace with your Google Sheet shared link url')
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
                #Comparison total sum of cost between filtered_expense_log_df and filtered_previous_expense_log_df
                if filtered_previous_expense_log_df.empty:
                    st.warning("No data available for comparison.")

                else:
                    current_total = filtered_expense_log_df['cost'].sum()
                    previous_total = filtered_previous_expense_log_df['cost'].sum()
                    
                    #Format the total cost to 2 decimal places and delete comma
                    formatted_current_total = int(abs(current_total))
                    formatted_previous_total = int(abs(previous_total))

                #Visualization Column Header
                st.write("# Visualization")
                st.divider()
                #Metric value column
                
                metric_col = st.columns(2)
                
                with metric_col[0]:
                    st.metric(label="Total Expense", value=formatted_current_total, delta=formatted_previous_total - formatted_current_total)
                    
                    style_metric_cards(border_left_color="#672E6D")
                    
                    st.success(f"Total Expense: {filtered_expense_log_df['cost'].sum()} Bath")
                    
                    #Logic statement to compare the total cost between current and previous month
                    if previous_total > current_total:
                        st.success(f"Total Expense Decreased by {formatted_previous_total - formatted_current_total} Bath")
                    elif previous_total < current_total:
                        st.error(f"Total Expense Increased by {formatted_previous_total - formatted_current_total} Bath")
                    else:
                        st.success("Total Expense Remained the Same")  
                
                #Visualization column
                visualzation_col = st.columns(2)
                
                with visualzation_col[0]:
                    pie_source = filtered_expense_log_df[filtered_expense_log_df['cost'].notnull()]
                    fig_pie = px.pie(pie_source, values='cost', names='type', title = 'Expense Proportion by Type')
                    st.plotly_chart(fig_pie, use_container_width=True)
                    
                with visualzation_col[1]:
                    bar_source_current = filtered_expense_log_df[filtered_expense_log_df['cost'].notnull()].groupby(['month'])['cost'].sum().reset_index()
                    bar_source_previous = filtered_previous_expense_log_df[filtered_previous_expense_log_df['cost'].notnull()].groupby(['month'])['cost'].sum().reset_index()
                    delta_cost = abs(bar_source_current['cost'].iloc[-1] - bar_source_previous['cost'].iloc[-1])
                    formatted_delta_cost = int(delta_cost)
                    
                    # Coordinate of the line to connect the cost between current and previous month
                    x_coords = [bar_source_current['month'].iloc[-1], bar_source_previous['month'].iloc[-1]]
                    y_coords = [bar_source_current['cost'].iloc[-1], bar_source_previous['cost'].iloc[-1]]
                    mid_x = (x_coords[0] + x_coords[1]) / 2
                    mid_y = (y_coords[0] + y_coords[1]) / 2

                    
                    fig_bar = go.Figure()
                    # Add current costs bar trace
                    fig_bar.add_trace(go.Bar(
                        x=bar_source_current['month'],
                        y=bar_source_current['cost'],
                        text=bar_source_current['cost'],
                        name='Current Cost',
                        marker_color='blue'
                    ))
                    # Add previous costs bar trace
                    fig_bar.add_trace(go.Bar(
                        x=bar_source_previous['month'],
                        y=bar_source_previous['cost'],
                        text=bar_source_previous['cost'],
                        name='Previous Cost',
                        marker_color='red'
                    ))
                    
                    
                    #Add line to connect the cost between current and previous month, and add the text to show the difference cost between the month
                    fig_bar.add_trace(go.Scatter(
                        x= [x_coords[0], mid_x, x_coords[1]],
                        y= [y_coords[0], mid_y, y_coords[1]],
                        mode='lines',
                        name='Connection',
                        textposition='top center',
                        line=dict(color='green', width=2, dash='dash')
                    ))
                    
                    # Add annotation for the delta cost at the midpoint of the line
                    fig_bar.add_annotation(
                        x=mid_x,
                        y=mid_y,
                        text=formatted_delta_cost,
                        showarrow=False,
                        arrowhead=4,
                        ax=20,
                        ay=-80,
                        font=dict(
                            size = 16,
                            color = 'red'
                        ))
                    
                    # Update the layout
                    fig_bar.update_layout(
                        title='Expense Distribution by Month',
                        xaxis_title='Month',
                        yaxis_title='Cost',
                        barmode='group',
                        showlegend=True,
                        legend=dict(
                            bgcolor='rgba(255, 255, 255, 0)',
                            bordercolor='rgba(255, 255, 255, 0)'
                        ),
                        width=700,
                        height=500
                    )
                    
                    # Plot the chart using Streamlit
                    st.plotly_chart(fig_bar)
                    
                    #Visualization Column2
                    
                visualzation_col2 = st.columns(2)
                
                with visualzation_col2[0]:
                    fig_line = px.line(filtered_expense_log_df, x='date', y='cost', title='Expense Frequency by Date')
                    fig_line.update_layout(
                        xaxis_title='Date',
                        yaxis_title='Cost',
                        width=1000,
                        height=500
                    )
                    
                    st.plotly_chart(fig_line)

        else:
            st.error("Failed to load data.")

if __name__ == "__main__":
    main()


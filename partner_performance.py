import pandas as pd
import re
import streamlit as st
from datetime import datetime
from io import BytesIO
import base64
import xlsxwriter
import io

##########################################################

#### Function Section ####

def get_website_data():
    df_website = pd.read_csv("/media/dr01/work/jovyan/work/TOJO/Data/Scrape/TOJO Website Update.csv")

    # Group by website by cleaned_title
    df_website = df_website.groupby(['cleaned_title'], as_index=False).agg({'post_date':'first',
                                                                            'author_name':'first',
                                                                            'post_author':'first'}).sort_values('post_date', ascending=False).reset_index(drop=True)
    # Map Author Groupings
    df_website['author_name'] = df_website['post_author'].map({
        4: 'Min', 1: 'Jump', 15: 'Haah', 16: 'Simon', 17: 'Tyler', 18: 'Phattraporn', 19: 'Foam', 20: 'Buay',
        21: 'SL', 22: 'Fon', 23: 'TJ_editor', 24: 'Junior', 25: 'Petch', 26: 'Nook', 27: 'Bomb', 28: 'Greenlight',
        29: 'Ake', 30: 'Rin', 31: 'Pop', 33: 'Baibua', 35: 'Mata', 36: 'O2O Forum', 37: 'Akepass', 40: 'Chompuu',
        41: 'Boom'
    })

    df_website['post_date'] = pd.to_datetime(df_website['post_date'])

    df_website['month'] = df_website.post_date.dt.month.astype(str)
    df_website['year'] = df_website.post_date.dt.year.astype(str)
    df_website['year_month'] = df_website["year"] + "-" + df_website['month']

    return df_website

def clean_titles(s):
    pattern = re.compile(r"[\u0E00-\u0E7Fa-zA-Z0-9]")
    char_to_remove = re.findall(pattern, s)
    result_string = ''.join(char_to_remove)
    return result_string

def process_uploaded_file(uploaded_file):
    # Check if the file is uploaded
    if uploaded_file is not None:
        try:
            # Use pd.read_excel for Excel files
            excel_file = pd.ExcelFile(uploaded_file)

            # Read "Summary" sheet into summary_df
            summary_df = excel_file.parse(sheet_name='Summary')

            # Read "Article" sheet into tojo_df
            tojo_df = excel_file.parse(sheet_name='TOJO NEWS')

            return summary_df, tojo_df

        except pd.errors.EmptyDataError:
            st.warning("Uploaded file is empty or not in a valid Excel format")

    return None, None # Return None if the file is not uploaded

def main():
    st.title("TOJO NEWS Partner Performance Report")

    # Set up date filter & date variables
    h_col_1, h_col_2, h_col_3 = st.columns(3)
    with h_col_3:
        st.header(":blue[Date Filter]")
        start_date, end_date = st.date_input(
            "Choose a date range:",
            [default_start_date, default_end_date]
        )
        pm_start_date = start_date - pd.DateOffset(months=1)
        pm_end_date = end_date - pd.DateOffset(months=1)

        pm_start_date = pd.to_datetime(pm_start_date)
        pm_start_date = pm_start_date.replace(hour=0, minute=0, second=0)
        pm_end_date = pd.to_datetime(pm_end_date)
        pm_end_date = pm_end_date.replace(hour=23, minute=59, second=59)
        start_date = pd.to_datetime(start_date)
        start_date = start_date.replace(hour=0, minute=0, second=0)
        end_date = pd.to_datetime(end_date)
        end_date = end_date.replace(hour=23, minute=59, second=59)

    # Initialize excel_file_path
    excel_file_path = None

    # File upload
    uploaded_file = st.file_uploader("Choose an Excel file", type=["xlsx", "xls"])

    if uploaded_file is not None:
        # Read both sheets into DataFrames using the process_uploaded_file function
        summary_df, tojo_df = process_uploaded_file(uploaded_file)

        if summary_df is not None and tojo_df is not None:
            # Apply the clean_titles function to the 'Article' column in tojo_df
            tojo_df['cleaned_title'] = tojo_df['Article'].apply(clean_titles)

            # Get the unique author names from df_website
            author_names = df_website['author_name'].dropna().unique().tolist()

            authors_to_exclude = ['Mata', 'Akepass', 'Bomb', 'Rin', 'Tyler', 'Junior', 'Jump', 'Greenlight', 'Min', 'TJ_editor', 'Phattraporn']
            author_names = [author for author in author_names if author not in authors_to_exclude]

            # Create a Streamlit dropdown for author selection
            selected_author = st.selectbox("Select Author", author_names)

            # Filter df_website based on the selected author and date range
            df_website['post_date'] = pd.to_datetime(df_website['post_date'])  # Convert 'post_date' to Timestamp
            filtered_df = df_website[(df_website['author_name'] == selected_author) & (df_website['post_date'] >= start_date) & (df_website['post_date'] <= end_date)]

            # Merge filtered_df with tojo_df on 'cleaned_title' to include 'PV' and 'Outlinks click sum'
            filtered_df = filtered_df.merge(tojo_df[['cleaned_title', 'PV', 'Outlinks click sum', 'Category']], on='cleaned_title', how='left')

            # Calculate the sum of PV for the selected author
            author_pv_sum = filtered_df['PV'].astype(float).sum()
            author_outclick_sum = filtered_df['Outlinks click sum'].fillna(0).astype(int).sum()
            author_article_sum = filtered_df['cleaned_title'].count()

            # Add a new column 'all_viewcounts' to summary_df with the sum of PV for the selected author
            summary_df['Partner Viewcounts'] = author_pv_sum
            summary_df['Outclick Sum'] = author_outclick_sum
            summary_df['Partner Article Count'] = author_article_sum
            summary_df['Partner Article Percentage'] = author_pv_sum / summary_df['Total PV'] * 100
            summary_df['Partner Article Percentage'].round(2)

            # Let the user input TOJO Revenue in USD
            tojo_revenue_usd = st.number_input("Enter TOJO Revenue (USD)", value=0.0)

            # Set the exchange rate
            exchange_rate = 36.4500

            # Round to two decimal places
            rounded_exchange_rate = round(exchange_rate, 2)

            # Convert TOJO Revenue from USD to THB
            tojo_revenue_thb = tojo_revenue_usd * rounded_exchange_rate

            # Update the 'TOJO Revenue' columns in summary_df
            summary_df['TOJO Revenue (USD)'] = tojo_revenue_usd
            summary_df['TOJO Revenue (THB)'] = tojo_revenue_thb

            # Calculate the revenue from the partner
            summary_df['Revenue From Partner'] = summary_df['TOJO Revenue (THB)'] * (summary_df['Partner Article Percentage'] / 100)
            summary_df['Revenue From Partner'] = summary_df['Revenue From Partner'].round(2)

            summary_df['Partner Revenue 75%'] = summary_df['Revenue From Partner'] * 0.75
            summary_df['Partner Revenue 75%'] = summary_df['Partner Revenue 75%'].round(2)

            summary_df['TOJO Revenue 25%'] = summary_df['Revenue From Partner'] * 0.25 
            summary_df['TOJO Revenue 25%'] = summary_df['TOJO Revenue 25%'].round(2)

            # Partner Performance Sheet
            partner_df = pd.DataFrame()

            # Add the 'Category' column to partner_df
            partner_df['Category'] = filtered_df['Category'].unique()

            # Create a new DataFrame for the sums of PV per category
            category_sums = filtered_df.groupby('Category')['PV'].sum().reset_index()
            category_sums.columns = ['Category', 'Viewcounts']

            # Merge partner_df with the sums DataFrame on 'Category'
            partner_df = pd.merge(partner_df, category_sums, on='Category', how='left')

            # Fill NaN values in 'PV' column with a placeholder (e.g., 'Not Available')
            filtered_df['PV'] = filtered_df['PV'].fillna('0')

            filtered_df['Outlinks click sum'] = filtered_df['Outlinks click sum'].fillna('0')

            # If PV and Outlinks = 0, line_pickup = False, Else True
            filtered_df['line_pickup'] = (filtered_df['PV'].astype(float) > 0) | (filtered_df['Outlinks click sum'].astype(float) > 0)

            filtered_df['line_pickup'] = filtered_df['line_pickup'].astype(bool)

            # Display the filtered DataFrame
            st.write("Filtered DataFrame:", filtered_df)

            st.write("Summary Sheet", summary_df)
            st.write("Partner Performance", partner_df)

        else:
            st.warning("Uploaded file is empty or not in a valid Excel format")

        # Create a BytesIO buffer
        excel_buffer = BytesIO()

        # Write DataFrames to the buffer using Pandas ExcelWriter
        with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
            filtered_df.to_excel(writer, sheet_name='Article data', index=False)
            partner_df.to_excel(writer, sheet_name='Partner Performance', index=False)

        # Create a download button
        download = st.download_button(
            label="Download Performance Report",
            data=excel_buffer.getvalue(),
            file_name="Performance Report.xlsx",
            mime='application/vnd.ms-excel'
        )

if __name__ == "__main__":
    df_website = get_website_data()  # Call the function to get df_website
    default_start_date = datetime.today().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    default_end_date = datetime.today().replace(hour=23, minute=59, second=59, microsecond=999999)
    main()

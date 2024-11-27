import streamlit as st
import pandas as pd
import data_query

# Function to generate CSV data
def generate_csv():

    all_tokens = data_query.query()
    data = data_query.xform_data(all_tokens)

    df = pd.DataFrame(data)
    
    # Convert DataFrame to CSV
    return df.to_csv(index=False).encode('utf-8'), df

# Streamlit UI
st.title("Base Chain Token Data Export")

st.write("Click the button below to generate and download the token data as a CSV file.")

# Button to generate and display data
if st.button("Generate Data"):
    csv_data, df = generate_csv()
    st.write("Base Token Data (1st five rows)")
    st.dataframe(df.head())  # Display the DataFrame as a table

    # Button to trigger CSV download
    st.download_button(
        label="Download CSV",
        data=csv_data,
        file_name="tokens.csv",
        mime="text/csv",
    )
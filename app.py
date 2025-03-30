import streamlit as st
import hl7
import pandas as pd

# Function to parse HL7 messages from raw.txt
def parse_hl7_messages():
    try:
        with open("fixed.txt", "r", encoding="utf-8") as file:
            fixed_data = file.read()
        with open("raw.txt", "r", encoding="utf-8") as file:
            raw_data = file.read()
        
        fixed_messages = ["MSH|" + msg.strip().replace('\n', '\r') for msg in fixed_data.split('MSH|') if msg.strip()]
        raw_messages = ["MSH|" + msg.strip().replace('\n', '\r') for msg in raw_data.split('MSH|') if msg.strip()]
        parsed_messages = []
        
        raw_messages_count = 0
        for message in fixed_messages:
            current_raw_message = raw_messages[raw_messages_count]
            raw_messages_count += 1
            h = hl7.parse(message)
            for segment in h:
                if str(segment[0]).strip() == 'MSH':
                    MessageID = str(segment[10]).strip()
                if str(segment[0]).strip() == 'PID':
                    mrn = str(segment[4]).strip() if len(segment) > 4 else "N/A"
                    lname, fname = str(segment[5]).split("^")[:2] if len(segment) > 5 else ("N/A", "N/A")
                    birthdate = str(segment[7]).strip() if len(segment) > 7 else "N/A"
                    parsed_messages.append({"Message Control ID": MessageID, "MRN": mrn, "Last Name": lname, "First Name": fname, "Birthdate": birthdate, "Fixed Message": message, "Raw Message": current_raw_message})
        
        return pd.DataFrame(parsed_messages)
    except FileNotFoundError:
        st.error("Error: raw.txt file not found. Please place the file in the same directory as this script.")
        return pd.DataFrame()

# Streamlit UI
st.title("HL7 Message Viewer")

# Parse messages from raw.txt
df = parse_hl7_messages()

if not df.empty:
    st.write("### HL7 Messages")

    # Search filter
    search_MessageID = st.text_input("Search by MessageID")
    search_mrn = st.text_input("Search by MRN")
    search_name = st.text_input("Search by Last Name")

    filtered_df = df.copy()
    if search_MessageID:
        filtered_df = filtered_df[filtered_df["Message Control ID"].str.contains(search_MessageID, na=False)]
    if search_mrn:
        filtered_df = filtered_df[filtered_df["MRN"].str.contains(search_mrn, na=False)]
    if search_name:
        filtered_df = filtered_df[filtered_df["Last Name"].str.contains(search_name, na=False)]

    st.dataframe(filtered_df.iloc[:, :6])

    # Select a message to view details
    if not filtered_df.empty:
        selected_index = st.selectbox("Select a message to view details", filtered_df.index)
        st.write(f"### Fixed Message {selected_index} Details")
        st.text_area("Fixed HL7 Message", filtered_df.loc[selected_index, "Fixed Message"], height=200)
        st.write(f"### Raw Message {selected_index} Details")
        st.text_area("Raw HL7 Message", filtered_df.loc[selected_index, "Raw Message"], height=200)

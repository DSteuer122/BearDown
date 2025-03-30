import streamlit as st
import hl7
import pandas as pd
import math
import os

# Function to parse HL7 messages from fixed.txt and raw.txt
def parse_hl7_messages():
    try:
        # Check if files exist before opening
        if not os.path.exists("fixed.txt") or not os.path.exists("raw.txt"):
            missing_files = []
            if not os.path.exists("fixed.txt"):
                missing_files.append("fixed.txt")
            if not os.path.exists("raw.txt"):
                missing_files.append("raw.txt")
            st.error(f"Error: {', '.join(missing_files)} file(s) not found. Please place the file(s) in the same directory as this script.")
            return pd.DataFrame()
        
        with open("fixed.txt", "r", encoding="utf-8") as file:
            fixed_data = file.read()
        with open("raw.txt", "r", encoding="utf-8") as file:
            raw_data = file.read()
        
        # Split the data by MSH| markers
        fixed_messages = [
            "MSH|" + msg.strip().replace('\n', '\r')
            for msg in fixed_data.split('MSH|') if msg.strip()
        ]
        raw_messages = [
            "MSH|" + msg.strip().replace('\n', '\r')
            for msg in raw_data.split('MSH|') if msg.strip()
        ]
        
        # Validate message counts
        if len(fixed_messages) != len(raw_messages):
            st.warning(f"Warning: Number of messages in fixed.txt ({len(fixed_messages)}) does not match raw.txt ({len(raw_messages)}). Some messages may be misaligned.")
        
        parsed_messages = []
        for idx, message in enumerate(fixed_messages):
            # Ensure we don't go out of bounds
            current_raw_message = raw_messages[idx] if idx < len(raw_messages) else "Raw message not available"
            
            try:
                h = hl7.parse(message)
                MessageID = "N/A"
                mrn = "N/A"
                lname = "N/A"
                fname = "N/A"
                birthdate = "N/A"
                
                for segment in h:
                    segment_type = str(segment[0]).strip()
                    
                    if segment_type == 'MSH':
                        # Message Control ID is usually in MSH-10
                        MessageID = str(segment[10]).strip() if len(segment) > 10 else "N/A"
                    
                    elif segment_type == 'PID':
                        # MRN is usually in PID-3
                        mrn = str(segment[3]).strip() if len(segment) > 3 else "N/A"
                        
                        # Patient name is usually in PID-5
                        if len(segment) > 5:
                            name_parts = str(segment[5]).split("^")
                            lname = name_parts[0] if len(name_parts) > 0 else "N/A"
                            fname = name_parts[1] if len(name_parts) > 1 else "N/A"
                        
                        # Birthdate is usually in PID-7
                        birthdate = str(segment[7]).strip() if len(segment) > 7 else "N/A"
                
                parsed_messages.append({
                    "Message Control ID": MessageID, 
                    "MRN": mrn, 
                    "Last Name": lname, 
                    "First Name": fname, 
                    "Birthdate": birthdate, 
                    "Fixed Message": message, 
                    "Raw Message": current_raw_message
                })
            except Exception as e:
                st.warning(f"Warning: Failed to parse message {idx+1}: {str(e)}")
                # Still add the message with error indicators
                parsed_messages.append({
                    "Message Control ID": f"ERROR-{idx}", 
                    "MRN": "ERROR", 
                    "Last Name": "ERROR", 
                    "First Name": "ERROR", 
                    "Birthdate": "ERROR", 
                    "Fixed Message": message, 
                    "Raw Message": current_raw_message
                })
        
        if not parsed_messages:
            st.warning("No valid HL7 messages found in the input files.")
            return pd.DataFrame()
            
        return pd.DataFrame(parsed_messages)
    except Exception as e:
        st.error(f"Error: An unexpected error occurred: {str(e)}")
        return pd.DataFrame()

# Render the inline representation with tooltips.
# Render the inline representation with tooltips.
def render_line_inline(line):
    fields = line.split("|")
    seg_name = fields[0]
    rendered_fields = []
    rendered_fields.append(
        f'<span title="{seg_name}-00" style="border:1px solid #ccc; padding:2px 4px; margin:2px; display:inline-block;">{seg_name}</span>'
    )
    
    # Special handling for MSH segment
    if seg_name == "MSH":
        # For MSH, the first pipe is actually MSH-01
        rendered_fields.append(
            f'<span title="MSH-01" style="border:1px solid #ccc; padding:2px 4px; margin:2px; display:inline-block;">|</span>'
        )
        # Start indexing from 2 for remaining fields in MSH
        start_idx = 2
        
        # Process first field (index 1 in the original fields array) without a leading pipe
        if len(fields) > 1:
            field = fields[1]
            field_label = f"{seg_name}-{start_idx:02d}"
            if "^" in field and field != "^~\&":
                subfields = field.split("^")
                rendered_subfields = []
                for sub_idx, sub in enumerate(subfields, start=1):
                    sub_label = f"{field_label}.{sub_idx}"
                    rendered_subfields.append(
                        f'<span title="{sub_label}" style="border:1px dashed #aaa; padding:2px 4px; margin:2px; display:inline-block;">{sub}</span>'
                    )
                field_html = " ^ ".join(rendered_subfields)
            else:
                field_html = f'<span title="{field_label}" style="border:1px solid #ccc; padding:2px 4px; margin:2px; display:inline-block;">{field}</span>'
            rendered_fields.append(field_html)
            
            # Process remaining fields (index 2+ in the original fields array) with leading pipes
            for idx, field in enumerate(fields[2:], start=start_idx+1):
                field_label = f"{seg_name}-{idx:02d}"
                if "^" in field and field != "^~\&":
                    subfields = field.split("^")
                    rendered_subfields = []
                    for sub_idx, sub in enumerate(subfields, start=1):
                        sub_label = f"{field_label}.{sub_idx}"
                        rendered_subfields.append(
                            f'<span title="{sub_label}" style="border:1px dashed #aaa; padding:2px 4px; margin:2px; display:inline-block;">{sub}</span>'
                        )
                    field_html = " ^ ".join(rendered_subfields)
                else:
                    field_html = f'<span title="{field_label}" style="border:1px solid #ccc; padding:2px 4px; margin:2px; display:inline-block;">{field}</span>'
                rendered_fields.append(" | " + field_html)
        
        return "".join(rendered_fields)
    else:
        # Normal handling for non-MSH segments
        for idx, field in enumerate(fields[1:], start=1):
            field_label = f"{seg_name}-{idx:02d}"
            if "^" in field and field != "^~\&":
                subfields = field.split("^")
                rendered_subfields = []
                for sub_idx, sub in enumerate(subfields, start=1):
                    sub_label = f"{field_label}.{sub_idx}"
                    rendered_subfields.append(
                        f'<span title="{sub_label}" style="border:1px dashed #aaa; padding:2px 4px; margin:2px; display:inline-block;">{sub}</span>'
                    )
                field_html = " ^ ".join(rendered_subfields)
            else:
                field_html = f'<span title="{field_label}" style="border:1px solid #ccc; padding:2px 4px; margin:2px; display:inline-block;">{field}</span>'
            rendered_fields.append(field_html)
        
        return " | ".join(rendered_fields)

# Build a two-column table (HTML) for the dropdown details.
def render_field_details_table(line):
    fields = line.split("|")
    seg_name = fields[0]
    rows = []
    rows.append(
        f"<tr><td style='padding:2px 4px; border:1px solid #555;'><strong>{seg_name}-00</strong></td>"
        f"<td style='padding:2px 4px; border:1px solid #555;'>{fields[0]}</td></tr>"
    )
    
    # Special handling for MSH segment
    if seg_name == "MSH":
        # Add MSH-01 row for the pipe character
        rows.append(
            f"<tr><td style='padding:2px 4px; border:1px solid #555;'><strong>MSH-01</strong></td>"
            f"<td style='padding:2px 4px; border:1px solid #555;'>|</td></tr>"
        )
        # Start indexing from 2 for remaining fields in MSH
        start_idx = 2
    else:
        start_idx = 1
    
    for idx, field in enumerate(fields[1:], start=start_idx):
        field_label = f"{seg_name}-{idx:02d}"
        if "^" not in field:
            rows.append(
                f"<tr><td style='padding:2px 4px; border:1px solid #555;'><strong>{field_label}</strong></td>"
                f"<td style='padding:2px 4px; border:1px solid #555;'>{field}</td></tr>"
            )
        else:
            subfields = field.split("^")
            rows.append(
                f"<tr><td style='padding:2px 4px; border:1px solid #555;'><strong>{field_label}</strong></td>"
                f"<td style='padding:2px 4px; border:1px solid #555;'></td></tr>"
            )
            for sub_idx, sub in enumerate(subfields, start=1):
                rows.append(
                    f"<tr><td style='padding:2px 4px; border:1px solid #555; padding-left:16px;'><em>{field_label}.{sub_idx}</em></td>"
                    f"<td style='padding:2px 4px; border:1px solid #555; padding-left:16px;'>{sub}</td></tr>"
                )
    table_html = (
        "<table style='width:100%; border-collapse:collapse; font-size:0.9em;'>"
        + "".join(rows)
        + "</table>"
    )
    return table_html

# Build a two-column table (HTML) for the dropdown details.
def render_field_details_table(line):
    fields = line.split("|")
    seg_name = fields[0]
    rows = []
    rows.append(
        f"<tr><td style='padding:2px 4px; border:1px solid #555;'><strong>{seg_name}-00</strong></td>"
        f"<td style='padding:2px 4px; border:1px solid #555;'>{fields[0]}</td></tr>"
    )
    
    # Special handling for MSH segment
    if seg_name == "MSH":
        # Add MSH-01 row for the pipe character
        rows.append(
            f"<tr><td style='padding:2px 4px; border:1px solid #555;'><strong>MSH-01</strong></td>"
            f"<td style='padding:2px 4px; border:1px solid #555;'>|</td></tr>"
        )
        # Start indexing from 2 for remaining fields in MSH
        start_idx = 2
    else:
        start_idx = 1
    
    for idx, field in enumerate(fields[1:], start=start_idx):
        field_label = f"{seg_name}-{idx:02d}"
        if "^" not in field:
            rows.append(
                f"<tr><td style='padding:2px 4px; border:1px solid #555;'><strong>{field_label}</strong></td>"
                f"<td style='padding:2px 4px; border:1px solid #555;'>{field}</td></tr>"
            )
        else:
            subfields = field.split("^")
            rows.append(
                f"<tr><td style='padding:2px 4px; border:1px solid #555;'><strong>{field_label}</strong></td>"
                f"<td style='padding:2px 4px; border:1px solid #555;'></td></tr>"
            )
            for sub_idx, sub in enumerate(subfields, start=1):
                rows.append(
                    f"<tr><td style='padding:2px 4px; border:1px solid #555; padding-left:16px;'><em>{field_label}.{sub_idx}</em></td>"
                    f"<td style='padding:2px 4px; border:1px solid #555; padding-left:16px;'>{sub}</td></tr>"
                )
    table_html = (
        "<table style='width:100%; border-collapse:collapse; font-size:0.9em;'>"
        + "".join(rows)
        + "</table>"
    )
    return table_html
# Build a two-column table (HTML) for the dropdown details.
def render_field_details_table(line):
    fields = line.split("|")
    seg_name = fields[0]
    rows = []
    rows.append(
        f"<tr><td style='padding:2px 4px; border:1px solid #555;'><strong>{seg_name}-00</strong></td>"
        f"<td style='padding:2px 4px; border:1px solid #555;'>{fields[0]}</td></tr>"
    )
    
    # Special handling for MSH segment
    if seg_name == "MSH":
        # Add MSH-01 row for the pipe character
        rows.append(
            f"<tr><td style='padding:2px 4px; border:1px solid #555;'><strong>MSH-01</strong></td>"
            f"<td style='padding:2px 4px; border:1px solid #555;'>|</td></tr>"
        )
        # Start indexing from 2 for remaining fields in MSH
        start_idx = 2
    else:
        start_idx = 1
    
    for idx, field in enumerate(fields[1:], start=start_idx):
        field_label = f"{seg_name}-{idx:02d}"
        if "^" not in field:
            rows.append(
                f"<tr><td style='padding:2px 4px; border:1px solid #555;'><strong>{field_label}</strong></td>"
                f"<td style='padding:2px 4px; border:1px solid #555;'>{field}</td></tr>"
            )
        else:
            subfields = field.split("^")
            rows.append(
                f"<tr><td style='padding:2px 4px; border:1px solid #555;'><strong>{field_label}</strong></td>"
                f"<td style='padding:2px 4px; border:1px solid #555;'></td></tr>"
            )
            for sub_idx, sub in enumerate(subfields, start=1):
                rows.append(
                    f"<tr><td style='padding:2px 4px; border:1px solid #555; padding-left:16px;'><em>{field_label}.{sub_idx}</em></td>"
                    f"<td style='padding:2px 4px; border:1px solid #555; padding-left:16px;'>{sub}</td></tr>"
                )
    table_html = (
        "<table style='width:100%; border-collapse:collapse; font-size:0.9em;'>"
        + "".join(rows)
        + "</table>"
    )
    return table_html

# Render a full HTML box for one HL7 segment line.
def render_line_with_dropdown(line):
    if not line or "|" not in line:
        return f"<div style='background-color:#faa; padding:4px 8px; margin:4px 0; border-radius:4px;'>Invalid segment: {line}</div>"
    
    seg_name = line.split("|")[0]
    inline_html = render_line_inline(line)
    details_table = render_field_details_table(line)
    
    # Color-code different segment types
    bg_color = "#333"  # default
    if seg_name == "MSH":
        bg_color = "#225"  # darker blue for header
    elif seg_name == "PID":
        bg_color = "#252"  # green for patient info
    elif seg_name == "OBR":
        bg_color = "#522"  # red for orders
    elif seg_name == "OBX":
        bg_color = "#552"  # yellow-ish for observations
    
    # The container is compact. The details element is now inline so when opened, it pushes the box to expand.
    html = f"""<div style="background-color:{bg_color}; padding:4px 8px; margin:4px 0; border-radius:4px; color:white; font-family:Arial, sans-serif; line-height:1.2em;">
  <div style="font-weight:bold; font-size:1.1em;">{seg_name}</div>
  <div style="margin-top:2px;">{inline_html}</div>
  <div style="text-align:right; margin-top:2px;">
    <details style="color:white; display:inline-block;">
      <summary style="cursor:pointer; font-size:0.9em; margin:0;">Details</summary>
      <div style="margin-top:2px;">{details_table}</div>
    </details>
  </div>
</div>"""
    return html

# Display each line of the message (Fixed or Raw) as its own compact box.
def display_message_details(message_text):
    if not message_text or message_text == "Raw message not available":
        st.info("No message data available")
        return
        
    lines = message_text.replace('\r', '\n').split("\n")
    for line in lines:
        if line.strip():
            box_html = render_line_with_dropdown(line)
            st.markdown(box_html, unsafe_allow_html=True)

# Function to display differences between fixed and raw messages
def display_message_diff(fixed_message, raw_message):
    st.write("### Message Comparison")
    
    if fixed_message == "Raw message not available" or raw_message == "Raw message not available":
        st.warning("Cannot compare messages - one or both messages are not available")
        return
        
    fixed_lines = fixed_message.replace('\r', '\n').split("\n")
    raw_lines = raw_message.replace('\r', '\n').split("\n")
    
    # Create side-by-side columns
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("#### Fixed Message")
        for line in fixed_lines:
            if line.strip():
                st.code(line, language=None)
    
    with col2:
        st.write("#### Raw Message")
        for line in raw_lines:
            if line.strip():
                st.code(line, language=None)

# --- Streamlit UI ---
def main():
    st.set_page_config(page_title="HL7 Message Viewer", page_icon="🏥", layout="wide")
    
    st.title("HL7 Message Viewer")
    
    # Fixed items per page
    items_per_page = 50
    
    # Process data
    df = parse_hl7_messages()

    if not df.empty:
        st.write("### HL7 Messages")
        
        # Create 3 columns for search inputs
        col1, col2, col3 = st.columns(3)
        with col1:
            search_MessageID = st.text_input("Search by Message ID")
        with col2:
            search_mrn = st.text_input("Search by MRN")
        with col3:
            search_name = st.text_input("Search by Last Name")

        # Apply filters
        filtered_df = df.copy()
        if search_MessageID:
            filtered_df = filtered_df[filtered_df["Message Control ID"].str.contains(search_MessageID, case=False, na=False)]
        if search_mrn:
            filtered_df = filtered_df[filtered_df["MRN"].str.contains(search_mrn, case=False, na=False)]
        if search_name:
            filtered_df = filtered_df[filtered_df["Last Name"].str.contains(search_name, case=False, na=False)]

        # Pagination
        total_items = filtered_df.shape[0]
        total_pages = math.ceil(total_items / items_per_page) if total_items > 0 else 1

        # Initialize page state
        if "page" not in st.session_state:
            st.session_state.page = 0
            
        # Page navigation
        col1, col2, col3, col4, col5 = st.columns([1, 1, 3, 1, 1])
        with col1:
            if st.button("⏮ First"):
                st.session_state.page = 0
        with col2:
            if st.button("◀ Previous"):
                if st.session_state.page > 0:
                    st.session_state.page -= 1
        with col3:
            st.write(f"Showing page {st.session_state.page + 1} of {total_pages} ({total_items} messages total)")
        with col4:
            if st.button("Next ▶"):
                if st.session_state.page < total_pages - 1:
                    st.session_state.page += 1
        with col5:
            if st.button("Last ⏭"):
                st.session_state.page = total_pages - 1

        # Calculate slice for current page
        start_idx = st.session_state.page * items_per_page
        end_idx = start_idx + items_per_page
        current_page_df = filtered_df.iloc[start_idx:end_idx]

        # Display dataframe with all columns including the fixed message
        display_cols = ["Message Control ID", "MRN", "Last Name", "First Name", "Birthdate", "Fixed Message"]
        st.dataframe(current_page_df[display_cols], use_container_width=True)

        # Message selection - moved above the output section but below the main table
        if not current_page_df.empty:
            # Select message
            selected_index = st.selectbox("Select a message to view details", 
                                        current_page_df.index,
                                        format_func=lambda x: f"{filtered_df.loc[x, 'Message Control ID']} - {filtered_df.loc[x, 'Last Name']}, {filtered_df.loc[x, 'First Name']}")
            
            # Tabs for different views
            tab1, tab2, tab3 = st.tabs(["Message Details", "Message Comparison", "Raw Data"])
            
            with tab1:
                # Details view
                st.write(f"### Fixed Message Details")
                display_message_details(filtered_df.loc[selected_index, "Fixed Message"])
                st.write(f"### Raw Message Details")
                display_message_details(filtered_df.loc[selected_index, "Raw Message"])
            
            with tab2:
                # Comparison view
                display_message_diff(
                    filtered_df.loc[selected_index, "Fixed Message"],
                    filtered_df.loc[selected_index, "Raw Message"]
                )
            
            with tab3:
                # Raw Data view
                st.write("### Fixed Message (Raw Text)")
                st.text_area("Fixed Message", filtered_df.loc[selected_index, "Fixed Message"], height=200)
                st.write("### Raw Message (Raw Text)")
                st.text_area("Raw Message", filtered_df.loc[selected_index, "Raw Message"], height=200)
    else:
        st.info("No messages to display. Please check your HL7 files (fixed.txt and raw.txt).")

if __name__ == "__main__":
    main()

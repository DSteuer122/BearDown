import streamlit as st
import hl7
import pandas as pd
import math

# Function to parse HL7 messages from fixed.txt and raw.txt
def parse_hl7_messages():
    try:
        with open("fixed.txt", "r", encoding="utf-8") as file:
            fixed_data = file.read()
        with open("raw.txt", "r", encoding="utf-8") as file:
            raw_data = file.read()
        
        fixed_messages = [
            "MSH|" + msg.strip().replace('\n', '\r')
            for msg in fixed_data.split('MSH|') if msg.strip()
        ]
        raw_messages = [
            "MSH|" + msg.strip().replace('\n', '\r')
            for msg in raw_data.split('MSH|') if msg.strip()
        ]
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
                    mrn = str(segment[3]).strip() if len(segment) > 4 else "N/A"
                    if len(segment) > 5 and "^" in str(segment[5]):
                        lname, fname = str(segment[5]).split("^")[:2]
                    else:
                        lname, fname = "N/A", "N/A"
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
        return pd.DataFrame(parsed_messages)
    except FileNotFoundError:
        st.error("Error: raw.txt file not found. Please place the file in the same directory as this script.")
        return pd.DataFrame()

# Render the inline representation with tooltips.
def render_line_inline(line):
    fields = line.split("|")
    seg_name = fields[0]
    rendered_fields = []
    rendered_fields.append(
        f'<span title="{seg_name}-00" style="border:1px solid #ccc; padding:2px 4px; margin:2px; display:inline-block;">{seg_name}</span>'
    )
    for idx, field in enumerate(fields[1:], start=1):
        field_label = f"{seg_name}-{idx:02d}"
        if "^" in field:
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
    for idx, field in enumerate(fields[1:], start=1):
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
    seg_name = line.split("|")[0]
    inline_html = render_line_inline(line)
    details_table = render_field_details_table(line)
    # The container is compact. The details element is now inline so when opened, it pushes the box to expand.
    html = f"""<div style="background-color:#333; padding:4px 8px; margin:4px 0; border-radius:4px; color:white; font-family:Arial, sans-serif; line-height:1.2em;">
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
    lines = message_text.replace('\r', '\n').split("\n")
    for line in lines:
        if line.strip():
            box_html = render_line_with_dropdown(line)
            st.markdown(box_html, unsafe_allow_html=True)

# --- Streamlit UI ---
st.title("HL7 Message Viewer")
df = parse_hl7_messages()

if not df.empty:
    st.write("### HL7 Messages")
    search_MessageID = st.text_input("Search by MessageID")
    search_mrn = st.text_input("Search by MRN")
    search_name = st.text_input("Search by Last Name")

    filtered_df = df.copy()
    if search_MessageID:
        filtered_df = filtered_df[filtered_df["Message Control ID"].str.contains(search_MessageID, case=False, na=False)]
    if search_mrn:
        filtered_df = filtered_df[filtered_df["MRN"].str.contains(search_mrn, case=False, na=False)]
    if search_name:
        filtered_df = filtered_df[filtered_df["Last Name"].str.contains(search_name, case=False, na=False)]

    items_per_page = 50
    total_items = filtered_df.shape[0]
    total_pages = math.ceil(total_items / items_per_page) if total_items > 0 else 1

    if "page" not in st.session_state:
        st.session_state.page = 0

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("⏮ First"):
            st.session_state.page = 0
    with col2:
        if st.button("◀ Previous"):
            if st.session_state.page > 0:
                st.session_state.page -= 1
    with col3:
        if st.button("Next ▶"):
            if st.session_state.page < total_pages - 1:
                st.session_state.page += 1
    with col4:
        if st.button("Last ⏭"):
            st.session_state.page = total_pages - 1

    start_idx = st.session_state.page * items_per_page
    end_idx = start_idx + items_per_page
    current_page_df = filtered_df.iloc[start_idx:end_idx]

    st.write(f"Showing page {st.session_state.page + 1} of {total_pages}")
    st.dataframe(current_page_df.iloc[:, :6])

    if not current_page_df.empty:
        selected_index = st.selectbox("Select a message to view details", current_page_df.index)
        st.write(f"### Fixed Message Details (Index: {selected_index})")
        display_message_details(filtered_df.loc[selected_index, "Fixed Message"])
        st.write(f"### Raw Message Details (Index: {selected_index})")
        display_message_details(filtered_df.loc[selected_index, "Raw Message"])

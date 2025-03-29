import hl7  
import re   

# Function to parse HL7 messages from a file
def parse_hl7_messages(file_path):
    # Open the file
    with open(file_path, 'r', encoding='utf-8') as file:
        data = file.read()
    
    # Split the content by the 'MSH|' separator
    messages = data.split('MSH|')
    
    # For each message, remove extra spaces, replace newline characters with carriage returns, and reattach 'MSH|' at the beginning
    parsed_messages = ["MSH|" + msg.strip().replace('\n', '\r\n') + '\r' for msg in messages if msg.strip()]
    
    # Return the list of parsed messages
    return parsed_messages

# Function to extract timestamp from an HL7 message
def extract_timestamp(hl7_message):
    try:
        # Parse the HL7 message using the hl7 module
        h = hl7.parse(hl7_message)
        
        # Extract the timestamp field 
        timestamp_field = h[0][7]  

        # If the timestamp is a hl7.Field object, extract its first value
        if isinstance(timestamp_field, hl7.Field):
            timestamp = str(timestamp_field[0]) 
        else:
            # Otherwise, directly convert it to a string
            timestamp = str(timestamp_field)  
        timestamp_without_timezone = timestamp
        if "-" in timestamp:
            timestamp_without_timezone = re.sub(r'[-+]\d{4}$', '', timestamp.strip())
            integer_timestamp = int(timestamp_without_timezone)
            integer_timestamp += 500
            timestamp_without_timezone = str(integer_timestamp)
        else:
            timestamp_without_timezone = timestamp
        # Remove the timezone information from the timestamp
        # timestamp_without_timezone = re.sub(r'[-+]\d{4}$', '', timestamp.strip())
        # Return the timestamp as an integer after stripping any unwanted characters
        return int(timestamp_without_timezone) 
    
    except Exception as e:
        print(f"Error parsing message: {e}")
        return 99999999999999  

# Function to sort HL7 messages based on their timestamps
def sort_hl7_messages(input_file, output_file):
    # Parse HL7 messages from the input file
    messages = parse_hl7_messages(input_file)
    
    # Sort the messages by their timestamp using the extract_timestamp function as the sorting key
    sorted_messages = sorted(messages, key=extract_timestamp)
    
    # Write the sorted messages to the output file
    with open(output_file, 'w', encoding='utf-8') as file:
        file.write('\n'.join(sorted_messages))

# Specify the input and output file paths
input_file = 'raw2.txt'  
output_file = 'messages_sorted.txt' 

sort_hl7_messages(input_file, output_file)

print(f"Sorted HL7 messages saved to {output_file}")
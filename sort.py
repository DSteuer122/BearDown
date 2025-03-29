import hl7
import re

def parse_hl7_messages(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = file.read()
    
    messages = data.split('MSH|')
    
    
    parsed_messages = ["MSH|" + msg.strip().replace('\n', '\r\n') + '\r' for msg in messages if msg.strip()]
    
    return parsed_messages

def extract_timestamp(hl7_message):
    try:
        h = hl7.parse(hl7_message)
        timestamp_field = h[0][7]  

        if isinstance(timestamp_field, hl7.Field):
            timestamp = str(timestamp_field[0]) 
        else:
            timestamp = str(timestamp_field)  
        
        timestamp_without_timezone = re.sub(r'[-+]\d{4}$', '', timestamp.strip())
        
        return int(timestamp_without_timezone) 
    
    except Exception as e:
        print(f"Error parsing message: {e}")
        return 99999999999999  

def sort_hl7_messages(input_file, output_file):
    messages = parse_hl7_messages(input_file)
    
    sorted_messages = sorted(messages, key=extract_timestamp)
    
    with open(output_file, 'w', encoding='utf-8') as file:
        file.write('\n'.join(sorted_messages))

input_file = 'raw.txt'  
output_file = 'sorted.txt'

sort_hl7_messages(input_file, output_file)

print(f"Sorted HL7 messages saved to {output_file}")

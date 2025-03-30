import re

# redact function
def redact_hl7_line(line, first_name, last_name):
    # parse by |
    temp = line.split('|')

    # sections phi may be
    sensitive_indices = {
        'PID': [2, 3, 4, 5, 6, 7, 9, 11, 12, 13, 14, 18, 19, 20, 21, 29, 30, 31],  
        'NK1': [2, 3, 4, 5, 6, 7, 8, 10, 12, 16, 26, 30, 31, 32, 33, 37],  
        'PV1': [5, 7, 8, 9, 17, 19, 50, 52],  
        'EVN': [5],  
    }

    # only analyze phi topics
    segment_type = temp[0]

    if segment_type in sensitive_indices:
        for i in sensitive_indices[segment_type]:
            # redacts with *
            if i < len(temp): 
                temp[i] = "*"  

    #takes names out of obx comments
    if len(temp) > 5 and segment_type == 'OBX':
        text_to_redact = temp[5]

        if first_name and last_name:
            full_name = f"{first_name} {last_name}"
            if full_name in text_to_redact:
                text_to_redact = text_to_redact.replace(full_name, "*")

        temp[5] = text_to_redact

    # takes names out of nte comments
    if len(temp) > 2 and segment_type == 'NTE':
        text_to_redact = temp[2]


        
        # takes out ssn numbers
        if "ID" in text_to_redact:
            
            text_to_redact = re.sub(r'[0-9]', '*', text_to_redact)  # Replace all digits (0-9) with #

        # checks to see if birthdates are in comments
        if "birthdate" in text_to_redact.lower():
            # replaces with #
            text_to_redact = re.sub(r'\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s+\d{4}\b', '*', text_to_redact)

        # Check for 'cinco de mayo' and replace with #
        if "cinco de mayo" in text_to_redact.lower():  # Case-insensitive check
            text_to_redact = re.sub(r'cinco de mayo', '*', text_to_redact, flags=re.IGNORECASE)

        


        

        temp[2] = text_to_redact

    if len(temp) > 3 and segment_type == 'NTE':
        text_to_redact = temp[3]

        if "ID" in text_to_redact:
            
            text_to_redact = re.sub(r'\d{3}-\d{2}-\d{4}', '*', text_to_redact)  # takes out ssn
        temp[3] = text_to_redact
        

    # Put the line back together
    redacted_line = '|'.join(temp)
    return redacted_line


# Will go line by line and call other method to break it down and check
def redact_hl7_file(input_file, output_file):
    first_name = None
    last_name = None
    with open(input_file, "r") as inFile, open(output_file, "w") as outFile:
        for line in inFile:
            line = line.rstrip()

            # resets info for every msh header
            if line.startswith("MSH"):
                first_name = None
                last_name = None

            # stores names for later use
            if line.startswith("PID"):
                temp = line.split('|')
                if len(temp) > 5:
                    
                    name_parts = temp[5].split('^') 
                    if len(name_parts) > 1:
                        first_name = name_parts[1]
                        last_name = name_parts[0] 

            # Process the line and redact if necessary
            if line.strip():  # Process only non-empty lines
                redacted_line = redact_hl7_line(line, first_name, last_name)  
                outFile.write(redacted_line + "\n")  # Ensure line count stays the same
            else:
                outFile.write("\n")  # Preserve blank lines


# Usage
redact_hl7_file("source_hl7_messages_v2.txt", "messages_redacted.txt")



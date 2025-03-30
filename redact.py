import re

def redact_hl7_line(line, first_name, last_name):
    temp = line.split('|')
    
    sensitive_indices = {
        'PID': [2, 3, 4, 5, 6, 7, 9, 11, 12, 13, 14, 18, 19, 20, 21, 29, 30, 31],  
        'NK1': [2, 3, 4, 5, 6, 7, 8, 10, 12, 16, 26, 30, 31, 32, 33, 37],  
        'PV1': [5, 7, 8, 9, 17, 19, 50, 52],  
        'EVN': [5],  
    }

    segment_type = temp[0]

    if segment_type in sensitive_indices:
        for i in sensitive_indices[segment_type]:
            if i < len(temp) and temp[i]:  # Check if field exists and is not empty
                # Split by caret and preserve them, redacting components
                components = temp[i].split('^')
                redacted_components = []
                for comp in components:
                    if comp:  # Only redact non-empty components
                        redacted_components.append('*')
                    else:
                        redacted_components.append('')  # Preserve empty components
                temp[i] = '^'.join(redacted_components)

    # Handle OBX comments
    if len(temp) > 5 and segment_type == 'OBX':
        text_to_redact = temp[5]
        if first_name and last_name:
            full_name = f"{first_name} {last_name}"
            if full_name in text_to_redact:
                # Preserve carets while redacting around them
                components = text_to_redact.split('^')
                redacted_components = []
                for comp in components:
                    if full_name in comp:
                        redacted_components.append(comp.replace(full_name, '*'))
                    else:
                        redacted_components.append(comp)
                text_to_redact = '^'.join(redacted_components)
        temp[5] = text_to_redact

    # Handle NTE comments
    if len(temp) > 2 and segment_type == 'NTE':
        text_to_redact = temp[2]
        
        # Handle SSN
        if "ID" in text_to_redact:
            components = text_to_redact.split('^')
            redacted_components = []
            for comp in components:
                if "ID" in comp:
                    redacted_comp = re.sub(r'[0-9]', '*', comp)
                    redacted_components.append(redacted_comp)
                else:
                    redacted_components.append(comp)
            text_to_redact = '^'.join(redacted_components)

        # Handle birthdates
        if "birthdate" in text_to_redact.lower():
            components = text_to_redact.split('^')
            redacted_components = []
            for comp in components:
                if "birthdate" in comp.lower():
                    redacted_comp = re.sub(r'\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s+\d{4}\b', '*', comp)
                    redacted_components.append(redacted_comp)
                else:
                    redacted_components.append(comp)
            text_to_redact = '^'.join(redacted_components)

        # Handle 'cinco de mayo'
        if "cinco de mayo" in text_to_redact.lower():
            components = text_to_redact.split('^')
            redacted_components = []
            for comp in components:
                if "cinco de mayo" in comp.lower():
                    redacted_comp = re.sub(r'cinco de mayo', '*', comp, flags=re.IGNORECASE)
                    redacted_components.append(redacted_comp)
                else:
                    redacted_components.append(comp)
            text_to_redact = '^'.join(redacted_components)

        temp[2] = text_to_redact

    if len(temp) > 3 and segment_type == 'NTE':
        text_to_redact = temp[3]
        if "ID" in text_to_redact:
            components = text_to_redact.split('^')
            redacted_components = []
            for comp in components:
                if "ID" in comp:
                    redacted_comp = re.sub(r'\d{3}-\d{2}-\d{4}', '*', comp)
                    redacted_components.append(redacted_comp)
                else:
                    redacted_components.append(comp)
            text_to_redact = '^'.join(redacted_components)
        temp[3] = text_to_redact

    redacted_line = '|'.join(temp)
    return redacted_line

def redact_hl7_file(input_file, output_file):
    first_name = None
    last_name = None
    with open(input_file, "r") as inFile, open(output_file, "w") as outFile:
        for line in inFile:
            line = line.rstrip()
            
            if line.startswith("MSH"):
                first_name = None
                last_name = None

            if line.startswith("PID"):
                temp = line.split('|')
                if len(temp) > 5:
                    name_parts = temp[5].split('^') 
                    if len(name_parts) > 1:
                        first_name = name_parts[1]
                        last_name = name_parts[0]

            if line.strip():
                redacted_line = redact_hl7_line(line, first_name, last_name)
                outFile.write(redacted_line + "\n")
            else:
                outFile.write("\n")

# Usage
redact_hl7_file("raw.txt", "messages_redacted.txt")

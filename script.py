with open("studio.txt", "r") as input_file, open("output.txt", "w") as output_file:
    for line in input_file:
        studio_name = line.strip()
        output_line = f'<option value="{studio_name}">{studio_name}</option>\n'
        output_file.write(output_line)
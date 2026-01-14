def md_to_string(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as md:
            stringmd = md_file.read()
        return stringmd
    except FileNotFoundError:
        return f"Error: The file {filename} was not found."
    except Exception as e:
        return f"An error occurred: {e}"
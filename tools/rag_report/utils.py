import os
import glob
from datetime import date


def extract_url_from_comment(comment) -> str:
    """
    Extract URL from the comment.
    """
    url_string = comment.split('::')[1]
    return url_string


def name_list_writer(output_file = 'tools\rag_report\name_list_data.txt', directory = 'tools\rag_report\data'):
    """
    Writes the file names from "data" directory to the output txt file "name_list.txt"
    """
    file_names = os.listdir(directory)
    # Write the file names to the output file
    with open(output_file, 'w') as f:
        for file_name in file_names:
            f.write(file_name + " \n")
    print(f"In total {len(file_names)} files names from '{directory}' have been written to '{output_file}'.")


def parse_txt_file(file_path):
    '''
    Reads the txt file with html names
    '''
    raw_documents = []
    with open(file_path, 'r') as file:
        lines = file.readlines()
    for line in lines:
        raw_documents.append({'name': line.strip()})
    return raw_documents


def read_file(file_path):
    """
    Reads content from a file.
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()
    

def save_output(output: str, output_path: str, marketvenueid: str) -> None:
    """
    Saves the output to a markdown file in the specified directory, creating a subdirectory for the market venue.
    """
    output_subdir = os.path.join(output_path, f"{marketvenueid}")  
    os.makedirs(output_subdir, exist_ok=True)  

    # Added debug to confirm path creation
    print(f"Output path: {output_subdir}")

    base_file_name = f"index-rag-{date.today()}"
    file_path = os.path.join(output_subdir, base_file_name)
    
    existing_files = glob.glob(f"{file_path}*.md")
    if existing_files:
        numbers = [int(file_name.split('_')[-1].split('.md')[0]) for file_name in existing_files if file_name.split('_')[-1].split('.md')[0].isdigit()]
        file_number = max(numbers, default=0) + 1
        full_path = f"{file_path}_{file_number}.md"
    else:
        full_path = f"{file_path}.md"
    
    with open(full_path, 'w', encoding='utf-8') as file:
        file.write(output)
    print(f"Output saved to: {full_path}")


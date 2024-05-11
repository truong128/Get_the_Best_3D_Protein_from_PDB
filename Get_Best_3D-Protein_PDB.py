import argparse
import os
import requests
def get_pdb_with_best_resolution(uniprot_id):
    # Function to retrieve PDB information for a given UniProt ID
    url = f"https://www.uniprot.org/uniprot/{uniprot_id}.txt"
    response = requests.get(url)
    if response.ok:
        data_lines = response.text.splitlines()
        best_pdb_id = None
        best_resolution = float('inf')
        best_length = 0
        for line in data_lines:
            if line.startswith("DR   PDB; "):
                pdb_id, method, resolution, length, chains = parse_pdb_line(line)
                if length > best_length or (length == best_length and resolution < best_resolution):
                    best_pdb_id = pdb_id
                    best_resolution = resolution
                    best_length = length
                    chains = line.strip().split("; ")[4]
        if best_pdb_id:
            return best_pdb_id, best_length, best_resolution, chains
        else:
            return "NULL", "NULL", "NULL", "NULL"
    else:
        print(f"Failed to retrieve data from Uniprot for UniProt ID: {uniprot_id}")
        return None
def extract_numeric_length(length_str):
    numeric_length = ''
    for char in length_str:
        if char.isdigit():
            numeric_length += char
    return int(numeric_length)
def parse_pdb_line(line):
    line_parts = line.strip().split("; ")
    pdb_id = line_parts[1]
    method = line_parts[2]
    resolution_str = line_parts[3].split(" ")[0]
    resolution = None
    if resolution_str != '-':
        resolution = float(resolution_str)
    length_parts = line_parts[4].split("=")[1].split("-")
    length = extract_numeric_length(length_parts[1]) - extract_numeric_length(length_parts[0]) + 1
    chain_ids = line_parts[4]
    return pdb_id, method, resolution, length, chain_ids
def download_pdb(pdb_id, output_folder, best_resolution):
    # Function to download PDB file and save it to output folder
    url = f"https://files.rcsb.org/download/{pdb_id}.pdb"
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print(f"Error: {e}")
        return
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    file_path = os.path.join(output_folder, f"{pdb_id}.pdb")
    with open(file_path, "wb") as pdb_file:
        pdb_file.write(response.content)
    print(f"PDB file for {pdb_id} has been downloaded with resolution {best_resolution} and saved as '{file_path}'.")
def run_optimalpdb(uniprot_id, output_folder):
    # Function to run optimalpdb for a given UniProt ID
    best_pdb_id, best_length, best_resolution, chains = get_pdb_with_best_resolution(uniprot_id)
    if best_pdb_id:
        print(f"UniProt ID: {uniprot_id}, Best PDB ID: {best_pdb_id}, Best Resolution: {best_resolution}")
        download_pdb(best_pdb_id, output_folder, best_resolution)
def main():
    parser = argparse.ArgumentParser(description='Run optimalpdb script')
    parser.add_argument('input_file', help='Text file containing UniProt IDs (one per line)')
    parser.add_argument('output_folder', help='Output folder to save PDB files')
    args = parser.parse_args()
    with open(args.input_file, 'r') as file:
        uniprot_ids = file.readlines()
    for uniprot_id in uniprot_ids:
        uniprot_id = uniprot_id.strip()  # Remove leading/trailing whitespace and newline characters
        run_optimalpdb(uniprot_id, args.output_folder)
if __name__ == "__main__":
    main()

 #Modified from "Waqar Hanif"

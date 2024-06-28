import pandas as pd
import requests
import re
import os

def get_citation(doi, style="frontiers-of-biogeography", locale="en-UK"):
    url = f"https://doi.org/{doi}"
    headers = {
        "Accept": f"text/x-bibliography; style={style}; locale={locale}"
    }
    
    response = requests.get(url, headers=headers)
    response.encoding = 'utf-8'

    if response.status_code == 200:
        return response.text
    elif response.status_code == 204:
        return "No metadata available."
    elif response.status_code == 404:
        return "DOI not found."
    elif response.status_code == 406:
        return "Cannot serve any requested content type."
    else:
        return f"Unexpected response code: {response.status_code}"

def read_dois_and_catalogue_from_csv(csv_file_path):
    df = pd.read_csv(csv_file_path)
    if 'URL' in df.columns and 'catalogue link' in df.columns:
        df = df[df['URL'].notna()]  # Filter out rows where URL is NaN
        df = df[df['URL'].str.contains("doi.org")]  # Filter out rows where URL does not contain "doi.org"
        return df[['URL', 'catalogue link']].to_dict('records')
    else:
        return []

def read_urls_from_csv(csv_file_path):
    df = pd.read_csv(csv_file_path)
    if 'URL' in df.columns and 'catalogue link' in df.columns:
        df = df[df['URL'].notna()]  # Filter out rows where URL is NaN
        df = df[~df['URL'].str.contains("doi.org")]
        return df[['Authors', 'Publication year', 'Title' ,'URL', 'Vol(issue)/Report no', 'pagination', 'catalogue link']].to_dict('records')
    else:
        return []

def read_no_urls(csv_file_path):
    df = pd.read_csv(csv_file_path)
    empty_url_rows = df[df['URL'].isnull() | (df['URL'] == '')]
    return empty_url_rows

def sanitize_filename(filename):
    # Remove or replace characters not allowed in filenames
    return re.sub(r'[<>:"/\\|?*]', '_', filename)

def save_records_to_files(records_no_urls, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    grouped_records = records_no_urls.groupby('Dataset')  

    for dataset, group in grouped_records:
        sanitized_dataset = sanitize_filename(dataset)
        with open(os.path.join(output_dir, f"{sanitized_dataset}.txt"), 'w', encoding='utf-8') as output_file:
            for index, record in group.iterrows():
                authors = record['Authors']
                publication_year = record['Publication year']
                title = record['Title']
                vol_issue = record['Vol(issue)/Report no']
                pagination = record['pagination']
                ceda_catalogue_record = record['catalogue link']
                citation = (f"{authors} ({publication_year}). {title}. {vol_issue}. {pagination}. |{ceda_catalogue_record}\n")
                output_file.write(citation)

def main():
    csv_file_path = "references.csv"
    output_dir = "C:\\Users\\fdq63749\\Desktop\\testing\\"

    # records_dois = read_dois_and_catalogue_from_csv(csv_file_path)
    # records_urls = read_urls_from_csv(csv_file_path)
    records_no_urls = read_no_urls(csv_file_path)

    # # Process DOIs and save to a single file
    # with open(os.path.join(output_dir, "citations.txt"), "w", encoding='utf-8') as output_file:
    #     for record in records_dois:
    #         doi = record['URL']
    #         ceda_catalogue_record = record['catalogue link']
    #         citation = get_citation(doi)
    #         citation = re.sub(r'http\S+', '', citation)
    #         output_file.write(f"{citation.strip()}|{doi}|{ceda_catalogue_record}\n")
    #         print(f"Processed DOI: {doi}")
    #         print(citation)
        
    #     # Process URLs and save to the same file
    #     for record in records_urls:
    #         authors = record['Authors']
    #         publication_year = record['Publication year']
    #         title = record['Title']
    #         url = record['URL']
    #         vol_issue = record['Vol(issue)/Report no']
    #         pagination = record['pagination']
    #         ceda_catalogue_record = record['catalogue link']
    #         citation = (f"{authors} ({publication_year}). {title}. {vol_issue}. {pagination}. {url}|{ceda_catalogue_record}\n")
    #         output_file.write(citation)
    #         print(citation)
    
    # Save records with no URLs to separate files
    save_records_to_files(records_no_urls, output_dir)

if __name__ == "__main__":
    main()

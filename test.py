import zipfile

def unzip_file(zip_path, extract_directory):
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # Get the list of files in the zip archive
            file_list = zip_ref.namelist()

            # Extract each file individually to the specified directory
            for file in file_list:
                zip_ref.extract(file, extract_directory)
        
        print(f"File {zip_path} unzipped at {extract_directory}")
        return True
    except Exception as e:
        print(f"Error during extraction: {e}")
        return False
    
unzip_file()
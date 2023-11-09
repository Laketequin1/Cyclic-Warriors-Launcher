import requests

def get_total_filesize(links):
    total_size = 0
    for link in links:
        try:
            response = requests.head(link)
            if 'content-length' in response.headers:
                total_size += int(response.headers['content-length'])
        except requests.exceptions.RequestException:
            # Handle any network or URL errors here
            pass

    return total_size

# Example usage:
file_links = ['https://example.com/file1.txt', 'https://example.com/file2.pdf']
total_size = get_total_filesize(file_links)
print(f'Total file size: {total_size} bytes')
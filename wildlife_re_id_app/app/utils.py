import requests

def download_file(url, output_path):
    r = requests.get(url, allow_redirects=True)
    r.raise_for_status()
    with open(output_path, "wb") as f:
        f.write(r.content)
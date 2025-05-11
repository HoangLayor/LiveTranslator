import requests
import zipfile
import os

def download_file(url, local_filename):
    # NOTE the stream=True parameter below
    r = requests.get(url, stream=True)
    if r.status_code != 200:
        raise Exception(f"Failed to download file: {url}")
    
    with open(local_filename, 'wb') as f:
        for chunk in r.iter_content(chunk_size=8192):
            if chunk:  # filter out keep-alive new chunks
                f.write(chunk)
    return local_filename

### Test data
data_dir = "./dataset/test_data/OPUS-Tatoeba"
os.makedirs(data_dir, exist_ok=True)
ru_vi_url = "https://object.pouta.csc.fi/OPUS-Tatoeba/v20190709/moses/ru-vi.txt.zip"
test_file_path = f"{data_dir}/ru-vi.txt.zip"
download_file(ru_vi_url, test_file_path) # download the file

# Unzip the downloaded file
with zipfile.ZipFile(test_file_path, 'r') as zip_ref:
    zip_ref.extractall(data_dir)

os.remove(test_file_path) # remove the zip file after extraction

### Train data
data_dir = "./dataset/train_data/OPUS-MultiCCAligned"
os.makedirs(data_dir, exist_ok=True)
ru_vi_url = "https://object.pouta.csc.fi/OPUS-MultiCCAligned/v1.1/moses/ru-vi.txt.zip"

train_file_path = f"{data_dir}/ru-vi.txt.zip"
download_file(ru_vi_url, train_file_path) # download the file

# Unzip the downloaded file
with zipfile.ZipFile(train_file_path, 'r') as zip_ref:
    zip_ref.extractall(data_dir)

os.remove(train_file_path) # remove the zip file after extraction
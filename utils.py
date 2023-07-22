import os
import zipfile

from pathlib import Path


def load_input_folders():
    main = os.getcwd()
    input_dir = './input'
    for folder in os.listdir(input_dir):
        if ".zip" in folder:
            name = folder.split('.')[0]
            input_path = Path(f"{input_dir}/{name}")
            input_path.mkdir(exist_ok=True)
            with zipfile.ZipFile(f'{input_dir}/{folder}', 'r') as f:
                f.extractall(input_path)


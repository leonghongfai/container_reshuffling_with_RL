import os

from utils import *
from data_loader import DataLoader


if __name__ == '__main__':
    load_input_folders()
    input_folders_path = './input'
    for folder in os.listdir(input_folders_path):
        if '.zip' not in folder:
            tgt_folder_path = f"{input_folders_path}/{folder}"
            data = DataLoader(tgt_folder_path)

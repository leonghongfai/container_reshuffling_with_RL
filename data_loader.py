import json
import os
import pandas as pd
import shutil


class DataLoader:

    def __init__(self, folder_path):
        self.model_config = pd.DataFrame()
        self.all_terminals_shuffle_config = pd.DataFrame()
        self.lying_df = pd.DataFrame()
        self.planned_df = pd.DataFrame()
        self.max_height_weight = pd.DataFrame()
        self.unusable_space = pd.DataFrame()
        # self.shuffle_blk = pd.DataFrame()
        self.shuffle_slots = pd.DataFrame()
        self.controls = pd.DataFrame()
        self.dependency_config = pd.DataFrame()
        self.blk_hrly_mvs = pd.DataFrame()
        self.slotTo_hrly_mvs = pd.DataFrame()
        self.blk_nYC = pd.DataFrame()
        self.__get_data(folder_path)

    def __get_data(self, folder_path):
        """
        Populates DataLoader object attributes (Dataframes).
        :param folder_path: path of main input folder
        :return: None
        """
        self.initialise_ppo_config(folder_path)
        self.model_config = self.load_json_file()
        self.all_terminals_shuffle_config = self.load_shuffle_config(f'{folder_path}/config_smartShuffling.xlsx')
        self.lying_df = self.load_lying_data(f"{folder_path}/shuffleSlots.xlsx")
        self.planned_df = self.load_planned_data(f"{folder_path}/planBox_forShuffling_p123.xlsx")
        self.max_height_weight = self.load_max_height_weight(f"{folder_path}/Max_Height_Weight.xlsx")
        self.unusable_space = self.load_unusable_space(f"{folder_path}/unusableSpace.xlsx")

    def load_unusable_space(self, data_path):
        """
        Loads unusable space data into a pd df
        :param data_path: path to unusable space Excel file
        :return: pd.DataFrame
        """
        try:
            unusable_space = pd.read_excel(data_path, sheet_name='uusabeSpace',
                                           engine='openpyxl')  # Sheetname looks weird but that's how its spelt
            return unusable_space
        except Exception as e:
            print(f"Error reading unusable space data: {e}")

    def load_max_height_weight(self, data_path):
        """
        Loads max height and weight data into pd df
        :param data_path: path to max hw Excel file
        :return: pd.DataFrame
        """
        try:
            max_height_weight = pd.read_excel(data_path, sheet_name='Max_Height_Weight', engine='openpyxl')
            return max_height_weight
        except Exception as e:
            print(f"Error reading max hw data: {e}")

    def load_planned_data(self, data_path):
        """
        Loads planned containers into a pd df
        :param data_path: path to Excel sheet containing plan box info
        :return: pd.DataFrame
        """
        try:
            full_df = pd.read_excel(data_path, sheet_name='planBox_for_Shuffling', engine='openpyxl')
            return full_df
        except Exception as e:
            print(f"Error reading planned data: {e}")

    def load_lying_data(self, data_path):
        """
        Loads lying container data into a pd df.
        :param data_path: path to Excel sheet
        :return: pd.DataFrame
        """
        try:
            full_df = pd.read_excel(data_path, sheet_name='shuffleData', engine='openpyxl')
            full_df = full_df[full_df['level'] != 0]
            full_df = full_df[~full_df['CNTR_N'].isna()]
        except Exception as e:
            print(f"Error reading lying data: {e}")
        return full_df

    def initialise_ppo_config(self, folder_path):
        """
        Deletes old config file in folder if it exists, adds the newest config file into folder.
        :param folder_path: input folder file path
        """
        print(folder_path)
        for file in os.listdir(folder_path):
            if "PPO_config.json" in file:
                os.remove(f"{folder_path}/{file}")
                print(f"Del original config json")
                break
        try:
            shutil.copy2("PPO_config.json", folder_path)
            print(f"Copying config json into {folder_path}")
        except FileNotFoundError as e:
            print("Config json file not provided!")

    def load_json_file(self):
        """
        Loads config json file into a pd df.
        :return: pd.DataFrame
        """
        try:
            with open('./PPO_config.json', 'r') as f:
                model_config = json.load(f)
            return model_config
        except Exception as e:
            print(f"Error reading config json: {e}")

    def load_shuffle_config(self, data_path):
        """
        Loads shuffle config into a pd df.
        :param data_path: string path of Excel file to read.
        :return: pd.DataFrame
        """
        try:
            shuffle_config = pd.read_excel(data_path, sheet_name='action', engine='openpyxl')
            shuffle_config.set_index('ct', inplace=True)
            return shuffle_config
        except Exception as e:
            print(f"Error reading shuffle_config data: {e}")

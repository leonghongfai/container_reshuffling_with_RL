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
        self.to_shuffle = {}
        self.__populate_data(folder_path)

    def __populate_data(self, folder_path):
        """
        Populates DataLoader object attributes (Dataframes).
        :param folder_path: path of main input folder
        :return: None
        """
        print("____________________________________________")
        print("Populating DataLoader dfs:")
        self.initialise_ppo_config(folder_path)
        self.model_config = self.load_json_file()
        self.all_terminals_shuffle_config = self.load_shuffle_config(f'{folder_path}/config_smartShuffling.xlsx')
        self.lying_df = self.load_lying_data(f"{folder_path}/shuffleSlots.xlsx")
        self.planned_df = self.load_planned_data(f"{folder_path}/planBox_forShuffling_p123.xlsx")
        self.max_height_weight = self.load_max_height_weight(f"{folder_path}/Max_Height_Weight.xlsx")
        self.unusable_space = self.load_unusable_space(f"{folder_path}/unusableSpace.xlsx")
        self.shuffle_slots = self.load_shuffle_slots(f"{folder_path}/config_smartShuffling.xlsx")
        self.controls = self.load_controls(f"{folder_path}/config_smartShuffling.xlsx")
        self.dependency_config = self.load_max_dependency(f"{folder_path}/config_smartShuffling.xlsx")
        self.blk_hrly_mvs = self.load_blk_hrly_mvs(f"{folder_path}/yard_mvs.xlsx")
        self.slotTo_hrly_mvs = self.load_slotTo_hrly_mvs(f"{folder_path}/yard_mvs.xlsx")
        self.blk_nYC = self.load_nYC(f"{folder_path}/yard_mvs.xlsx")
        self.load_to_shuffle(f"{folder_path}/BlksToRun.xlsx")
        print("____________________________________________")

    def load_to_shuffle(self, data_path):
        """
        Loads blocks to shuffle from blocks_to_run into to_shuffle dictionary
        :param data_path: path to BlksToRun.xlsx
        :return: None
        """
        blocks_to_shuffle = []
        df = self.load_blocks_to_run(data_path)
        for row in df.iterrows():
            ct = str(row[1]["CT"])
            blk = str(row[1]["Blk"])
            slot = row[1]["slot"]
            blocks_to_shuffle.append((ct, blk, slot))
        for i in blocks_to_shuffle:
            # If specified slot number is -ve, then run all available slots for the block.
            slot_num = i[2]
            if slot_num < 0:
                # Get all distinct slots in this block
                block_df = self.lying_df[self.lying_df['blk'] == i[1]]
                distinct_slots = block_df['slotTo'].unique().tolist()
                slots_to_shuffle = distinct_slots  # All slots in the block to be run
            else:
                slot_list = [slot_num]
                slots_to_shuffle = slot_list  # One Slot is run per block
            key = (i[0], i[1])

            if key not in self.to_shuffle:
                self.to_shuffle[key] = slots_to_shuffle
            else:
                self.to_shuffle[key].extend(slots_to_shuffle)

    def load_blocks_to_run(self, data_path):
        """
        Loads BlksToRun.xlsx into pd df
        :param data_path: path to BlksToRun.xlsx
        :return: pd.DataFrame
        """
        try:
            blocks_to_run = pd.read_excel(data_path, engine='openpyxl')
            return blocks_to_run
        except Exception as e:
            print(f"Error reading BlksToRun data: {e}")

    def load_nYC(self, data_path):
        """
        Loads blk_nYC sheet from yard_mvs into pd df
        :param data_path: path to yard_mvs.xlsx
        :return: pd.DataFrame
        """
        try:
            blk_nYC = pd.read_excel(data_path, sheet_name='blk_nYC', engine='openpyxl')
            return blk_nYC
        except Exception as e:
            print(f"Error reading yard_mvs data: {e}")

    def load_slotTo_hrly_mvs(self, data_path):
        """
        Loads slotTo_hrly_mvs sheet from yard_mvs into pd df
        :param data_path: path to yard_mvs.xlsx
        :return: pd.DataFrame
        """
        try:
            slotTo_hrly_mvs = pd.read_excel(data_path, sheet_name='slotTo_hrly_mvs', engine='openpyxl')
            return slotTo_hrly_mvs
        except Exception as e:
            print(f"Error reading yard_mvs data: {e}")

    def load_blk_hrly_mvs(self, data_path):
        """
        Loads blk_hly_mvs sheet from yard_mvs into pd df
        :param data_path: path to yard_mvs.xlsx
        :return: pd.DataFrame
        """
        try:
            blk_hrly_mvs = pd.read_excel(data_path, sheet_name='blk_hly_mvs', engine='openpyxl')
            return blk_hrly_mvs
        except Exception as e:
            print(f"Error reading yard_mvs data: {e}")

    def load_max_dependency(self, data_path):
        """
        Loads MaxDependency sheet from config_smartShuffling into pd df
        :param data_path: path to config_smartShuffling.xlsx
        :return: pd.DataFrame
        """
        try:
            dependency_config = pd.read_excel(data_path, sheet_name='MaxDependency', engine='openpyxl')
            return dependency_config
        except Exception as e:
            print(f"Error reading config_smartShuffling data: {e}")

    def load_controls(self, data_path):
        """
        Loads control sheet from config_smartShuffling into pd df
        :param data_path: path to config_smartShuffling.xlsx
        :return: pd.DataFrame
        """
        try:
            controls = pd.read_excel(data_path, sheet_name='control', engine='openpyxl')
            return controls
        except Exception as e:
            print(f"Error reading config_smartShuffling data: {e}")

    def load_shuffle_blocks(self, data_path):
        """
        Loads shuffleBlk sheet from config_smartShuffling Excel file into pd df
        :param data_path: path to config_smartShuffling.xlsx
        :return: pd.DataFrame
        """
        try:
            origin_shuffle_blks = pd.read_excel(data_path, sheet_name='shuffleBlk', engine='openpyxl')
            return origin_shuffle_blks
        except Exception as e:
            print(f"Error reading shuffleBlk data: {e}")

    def load_shuffle_slots(self, data_path):
        """
        Loads shuffleSlots sheet from config_smartShuffling Excel file into pd df
        :param data_path: path to config_smartShuffling.xlsx
        :return: pd.DataFrame
        """
        origin_shuffle_blks = self.load_shuffle_blocks(data_path)
        origin_shuffle_slots = pd.read_excel(data_path, sheet_name='shuffleSlot', engine='openpyxl')

        shuffle_blks = origin_shuffle_blks[origin_shuffle_blks['isShuffleBlk']
                                           == 1]['blk'].unique()

        shuffle_slots = origin_shuffle_slots[origin_shuffle_slots['blk'].isin(
            shuffle_blks) & (origin_shuffle_slots['isShufleSlot'] == 1)]

        shuffle_slots = shuffle_slots.set_index('blk')

        return shuffle_slots

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

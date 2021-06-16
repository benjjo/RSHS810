import pandas as pd
import os
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import filedialog


class Scoper:
    _version = '2.0'
    root = tk.Tk()
    root.withdraw()

    def __init__(self):
        """Setup"""
        self.all_data = pd.DataFrame()
        self.data = pd.DataFrame()
        self.path = os.getcwd()
        self.files = os.listdir(self.path)
        self.file_path = str()

    def setup_all_data(self):
        self.all_data = pd.read_csv(filedialog.askopenfilename(), skiprows=5)

    def setup_data(self):
        self.all_data.rename(columns={self.all_data.columns[0]: "Record"}, inplace=True)
        self.data['Record'] = self.all_data['Record']
        self.data['Voltage'] = (self.data['Record'] - 128) * 3.8
        self.data.drop('Record', axis=1, inplace=True)
        self.data.insert(0, 'Time', range(1, len(self.data) + 1))
        self.data['Time'] = pd.to_datetime(self.data['Time'], unit='ms').dt.time
        self.data.set_index('Time', inplace=True)
        self.write_voltage_tocsv()

    def write_voltage_tocsv(self):
        self.data.to_csv('Voltage_Final.csv', index=False)

    def plot_voltage(self):
        self.data.plot(kind='line', legend=None)
        plt.xticks(color='C0', rotation='vertical')
        plt.xlabel('Time (mS)', color='C0', size=10)
        plt.yticks(color='C0')
        plt.tight_layout(pad=2)
        plt.title('Recorded Voltage', color='C0')
        plt.ylabel('Voltage (Vpp)', color='C0', size=10)
        plt.grid('on', linestyle='--')
        plt.show()


def main():
    scope = Scoper()
    scope.setup_all_data()
    scope.setup_data()
    scope.write_voltage_tocsv()
    scope.plot_voltage()


if __name__ == "__main__":
    main()

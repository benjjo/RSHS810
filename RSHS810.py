import numpy as np
import pandas as pd
import os
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import filedialog

"""
The RS Components RSHS 810 Oscilloscope does not come with any kind of software to process the logs. 
This is an attempt at creating a log viewer style interface that will allow you to process the data in a smooth 
and easy fashion.  
"""


class Scoper:
    _version = '2.2'
    root = tk.Tk()
    root.withdraw()

    def __init__(self):
        """Setup"""
        self.voltage_sample_data = pd.DataFrame()
        self.information_data = pd.DataFrame()
        self.data = pd.DataFrame()
        self.path = os.getcwd()
        self.files = os.listdir(self.path)
        self.file_path = str()
        self.Coef = float()
        self.zero = int()

    def setup_all_data(self):
        """
        Grab the CSV file that has been created by the RSHS Oscilloscope and create two separate dataframes.
        The first df will hold the coefficient and zero point data. The second will hold the recorded data.
        Scooper.root.destroy() is called to close the invisible Tk window.
        :return: None
        """
        file = filedialog.askopenfilename()
        self.information_data = pd.read_csv(file, nrows=3, usecols=[0, 1], index_col=False)
        self.voltage_sample_data = pd.read_csv(file, skiprows=4, index_col=False)
        Scoper.root.destroy()

    def set_Coef_data(self):
        """
        Filter out the Coefficient data from the information dataFrame.
        :return: None
        """
        self.Coef = float(self.information_data['CH1'].iloc[1].split(':')[-1].split('uv')[0]) * 0.00001

    def set_zero(self):
        """
        Filter out the zero point data. I'm not sure this ever changes from 128 but here it is just in case.
        :return: None
        """
        self.zero = int(self.information_data['CH1'].iloc[2].split(':')[-1])

    def setup_main_DataFrame(self):
        """
        Create the main DataFrame that will be used to display the data.
        :return: None
        """
        self.voltage_sample_data.rename(columns={self.voltage_sample_data.columns[0]: "Record"}, inplace=True)
        self.data['Record'] = self.voltage_sample_data['Record']
        self.data['Vpp'] = (self.data['Record'] - self.zero) * self.Coef
        self.data.drop('Record', axis=1, inplace=True)
        self.data.insert(0, 'Time', range(1, len(self.data) + 1))
        self.data['Time'] = pd.to_datetime(self.data['Time'], unit='ms').dt.time
        self.data.set_index('Time', inplace=True)
        self.data['RMS'] = self.data['Vpp'].rolling(20).max() * (1/np.sqrt(2))  # 20 = 50Hz sample rate
        self.write_voltage_tocsv()

    def second_channel(self) -> bool:
        """
        Checks to see if the second channel exists.
        :return: boolean
        """
        return self.information_data.columns[1] == 'CH2'

    def write_voltage_tocsv(self):
        """
        Helper method for setup_main_DataFrame
        Writes the final DataFrame to a csv file.
        :return: None
        """
        self.data.to_csv('Voltage_Final.csv', index=False)

    def plot_voltage(self):
        """
        Does all the work and displays the main DataFrame using matplotlib.
        :return: None
        """
        ax = self.data['Vpp'].plot(kind='line')
        self.data['RMS'].plot(kind='line', ax=ax)
        plt.xticks(color='C0', rotation='vertical')
        plt.xlabel('Time (mS)', color='C0', size=10)
        plt.yticks(color='C0')
        plt.tight_layout(pad=2)
        plt.title('Recorded Voltage', color='C0')
        plt.ylabel('Voltage', color='C0', size=10)
        plt.grid('on', linestyle='--')
        plt.legend(title='Voltage')
        plt.get_current_fig_manager().canvas.set_window_title('RSHS 810 Logger. V{}'.format(Scoper._version))
        image_name = 'RSHS_810_Log_Record.png'
        plt.savefig(image_name, dpi=300, facecolor='w', edgecolor='w',
                    orientation='landscape', format=None, transparent=False, pad_inches=0.1)
        plt.show()


def main():
    scope = Scoper()
    scope.setup_all_data()
    scope.set_Coef_data()
    scope.set_zero()
    scope.setup_main_DataFrame()
    scope.write_voltage_tocsv()
    scope.plot_voltage()


if __name__ == "__main__":
    main()

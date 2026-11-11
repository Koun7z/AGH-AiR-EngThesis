#!/usr/bin/env python3

from stdatalog_core.HSD.HSDatalog import HSDatalog
from stdatalog_utils import prepare_folder, get_acc_data, get_gyro_data

from pathlib import Path
import shutil
import argparse
import pandas as pd
import numpy as np
import scipy as sp

from matplotlib import pyplot as plt


def preview_datalog(path: str):

    hsd = HSDatalog()
    hsd_version = hsd.validate_hsd_folder(path)
    print(f"HSD Version: {hsd_version}\n")

    hsd_instance = hsd.create_hsd(acquisition_folder=path)

    dat_files = hsd.get_dat_file_list(hsd_instance)
    print(f".dat Files: {dat_files}\n")

    acc_t, acc_data = get_acc_data(path, debug=True)
    gyro_t, gyro_data = get_gyro_data(path, debug=True)

    gyro_data = np.rad2deg(gyro_data)  # Convert to deg/s for display

    plt.figure()
    plt.plot(acc_t, acc_data)
    plt.xlabel("Time [s]")
    plt.ylabel("Acceleration [g]")
    plt.legend(["X", "Y", "Z"])
    plt.grid()

    acc_data = acc_data - np.mean(acc_data, axis=0)
    plt.figure()
    plt.subplot(2, 1, 1)
    plt.plot(acc_t, acc_data)
    plt.xlabel("Time [s]")
    plt.ylabel("Acceleration (AC) [g]")
    plt.legend(["X", "Y", "Z"])
    plt.grid()

    plt.subplot(2, 1, 2)
    plt.plot(acc_t, np.linalg.norm(acc_data, axis=1))
    plt.xlabel("Time [s]")
    plt.ylabel("Acceleration Norm [g]")
    plt.grid()

    acc_v_int = sp.integrate.cumulative_simpson(acc_data * 9.81, x=acc_t, axis=0)
    plt.figure()
    plt.plot(acc_t[1:], acc_v_int)
    plt.xlabel("Time [s]")
    plt.ylabel("Velocity integrated [m/s]")
    plt.legend(["X", "Y", "Z"])
    plt.grid()

    plt.figure()
    plt.plot(gyro_t, gyro_data)
    plt.xlabel("Time [s]")
    plt.ylabel("Angular Velocity [deg/s]")
    plt.legend(["X", "Y", "Z"])
    plt.grid()

    plt.show()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Preview HSDatalog data.")

    parser.add_argument("input_file")

    args = parser.parse_args()

    path = args.input_file

    work_path = prepare_folder(path)

    preview_datalog(work_path)

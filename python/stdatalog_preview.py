#!/usr/bin/env python3

from stdatalog_core.HSD.HSDatalog import HSDatalog
from stdatalog_utils import prepare_folder

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

    components = hsd.get_all_components(hsd_instance)
    for comp in components:
        print(comp.keys())

    df_a = hsd.get_dataframe(hsd_instance, components[0])[0]
    acc_data = df_a.to_numpy()

    df_g = hsd.get_dataframe(hsd_instance, components[1])[0]
    gyro_data = df_g.to_numpy()

    plt.figure()
    plt.plot(acc_data[:, 0], acc_data[:, 1:])
    plt.xlabel("Time [s]")
    plt.ylabel("Acceleration [g]")
    plt.legend(["X", "Y", "Z"])
    plt.grid()

    acc_data[:, 1:] = acc_data[:, 1:] - np.mean(acc_data[:, 1:], axis=0)
    plt.figure()
    plt.subplot(2, 1, 1)
    plt.plot(acc_data[:, 0], acc_data[:, 1:])
    plt.xlabel("Time [s]")
    plt.ylabel("Acceleration (AC) [g]")
    plt.legend(["X", "Y", "Z"])
    plt.grid()

    plt.subplot(2, 1, 2)
    plt.plot(acc_data[:, 0], np.linalg.norm(acc_data[:, 1:], axis=1))
    plt.xlabel("Time [s]")
    plt.ylabel("Acceleration Norm [g]")
    plt.grid()

    acc_v_int = sp.integrate.cumulative_simpson(acc_data[:, 1:] * 9.81, x=acc_data[:, 0], axis=0)
    plt.figure()
    plt.plot(acc_data[1:, 0], acc_v_int)
    plt.xlabel("Time [s]")
    plt.ylabel("Velocity integrated [m/s]")
    plt.legend(["X", "Y", "Z"])
    plt.grid()

    plt.figure()
    plt.plot(gyro_data[:, 0], gyro_data[:, 1:])
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

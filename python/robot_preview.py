import pandas as pd
import numpy as np
import scipy

from matplotlib import pyplot as plt

import argparse


def load_data(file_path):
    df = pd.read_csv(file_path, skiprows=[0, 2])
    return df


def preview_data(df):

    xyz_data = df[["XYZ position(FB) X", "XYZ position(FB) Y", "XYZ position(FB) Z"]].to_numpy().astype(
        np.float64) / 1000  # to meters
    abc_data = df[["XYZ position(FB) A", "XYZ position(FB) B", "XYZ position(FB) C"]].to_numpy().astype(np.float64)
    time_data = df['Time'].to_numpy().astype(np.float64) / 1000  # to seconds

    print("XYZ Position Data: ", xyz_data.shape)

    xyz_data = scipy.signal.savgol_filter(xyz_data, window_length=11, polyorder=3, axis=0)
    abc_data = scipy.signal.savgol_filter(abc_data, window_length=21, polyorder=5, axis=0)

    xyz_vel = np.gradient(xyz_data, time_data, axis=0)
    xyz_acc = np.gradient(xyz_vel, time_data, axis=0)

    plt.figure()
    plt.plot(time_data, df[["XYZ position(FB) X", "XYZ position(FB) Y", "XYZ position(FB) Z"]])
    plt.plot(time_data, xyz_data * 1000, linestyle='--')
    plt.xlabel("Time [s]")
    plt.ylabel("Tool Position [mm]")
    plt.legend(["X", "Y", "Z"])

    plt.figure()
    plt.subplot(3, 1, 1)
    plt.plot(time_data, df["XYZ position(FB) A"])
    plt.plot(time_data, abc_data[:, 0], linestyle='--')
    plt.ylabel("Tool A [deg]")

    plt.subplot(3, 1, 2)
    plt.plot(time_data, df["XYZ position(FB) B"])
    plt.plot(time_data, abc_data[:, 1], linestyle='--')
    plt.ylabel("Tool B [deg]")

    plt.subplot(3, 1, 3)
    plt.plot(time_data, df["XYZ position(FB) C"])
    plt.plot(time_data, abc_data[:, 2], linestyle='--')
    plt.ylabel("Tool C [deg]")

    plt.xlabel("Time [s]")

    plt.figure()
    plt.plot(time_data, xyz_vel)
    plt.xlabel("Time [s]")
    plt.ylabel("Tool Velocity [m/s]")
    plt.legend(["X", "Y", "Z"])

    plt.figure()
    plt.subplot(2, 1, 1)
    plt.plot(time_data, xyz_acc / 9.81)
    plt.ylabel("Tool Acceleration [g]")
    plt.legend(["X", "Y", "Z"])

    plt.subplot(2, 1, 2)
    plt.plot(time_data, np.linalg.norm(xyz_acc, axis=1) / 9.81)
    plt.xlabel("Time [s]")
    plt.ylabel("Tool Acceleration Norm [g]")

    plt.show()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Load and preview data from a CSV file.")

    parser.add_argument("input_file", help="Path to the input CSV file.")
    args = parser.parse_args()

    file_path = args.input_file

    data = load_data(file_path)

    #print(data.describe())

    preview_data(data)

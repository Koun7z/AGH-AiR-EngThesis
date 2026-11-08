from typing import Tuple

from stdatalog_utils import prepare_folder, get_acc_data, get_ref_xyz_data

import matplotlib.pyplot as plt
from matplotlib.widgets import SpanSelector
import numpy as np
import scipy as sp

fs_imu = 833.0
fs_robot = (1000 / 3.35)
fc = 100.0

def prepare_acc_data(t, data) -> tuple[np.ndarray, np.ndarray]:
    
    # low-pass before downsampling
    b,a = sp.signal.butter(2, fc/(fs_imu/2), btype='low')

    data_filtered = sp.signal.filtfilt(b, a, acc_data, axis=0)

    # remove dc component (gravity vector + const bias)
    data_ac_filtered = data_filtered - np.mean(data_filtered, axis=0)

    return (data_filtered, data_ac_filtered)

def prepare_robot_data(t, data) -> tuple[np.ndarray, np.ndarray]:

    vel = sp.signal.savgol_filter(robot_xyz, 11, 3, deriv=1, delta=np.mean(np.diff(robot_t)), axis=0)
    acc = sp.signal.savgol_filter(robot_xyz, 11, 3, deriv=2, delta=np.mean(np.diff(robot_t)), axis=0) / 9.8105

    return (vel, acc)

def display_span_selector(x1, y1, x2, y2) -> Tuple[np.float64, np.float64, np.float64, np.float64]:

    selection_acc = (0,0)
    selection_robot = (0,0)

    def on_select_a(xmin, xmax):
        nonlocal selection_acc
        selection_acc = (xmin, xmax)

    def on_select_b(xmin, xmax):
        nonlocal selection_robot
        selection_robot = (xmin, xmax)

   
    fig, (ax1, ax2) = plt.subplots(2, 1, sharex=False)
    ax1.plot(x1, y1)
    ax1.set_title("Accelerometer Data")
    ax1.set_xlabel("Time [s]")
    ax1.set_ylabel("Acceleration [g]")
    ax1.legend(["X", "Y", "Z"])
    ax1.grid()

    ax2.plot(x2, y2)
    ax2.set_title("Robot Tool Acceleration Data (differentiated from tool xyz data)")
    ax2.set_xlabel("Time [s]")
    ax2.set_ylabel("Tool Acceleration [g]")
    ax2.legend(["X", "Y", "Z"])
    ax2.grid()

    span1 = SpanSelector(
        ax1,
        on_select_a,
        "horizontal",
        interactive=True,
    )

    span2 = SpanSelector(
        ax2,
        on_select_b,
        "horizontal",
        interactive=True,
    )      

    plt.show()

    return (selection_acc[0], selection_acc[1], selection_robot[0], selection_robot[1])

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Sync IMU and Robot data.")
    parser.add_argument("path", type=str, help="Path to the HSDatalog acquisition folder")
    args = parser.parse_args()

    prepared_path = prepare_folder(args.path)

    acc_t, acc_data = get_acc_data(prepared_path)
    acc_data_filtered, acc_data_ac_filtered = prepare_acc_data(acc_t, acc_data)

    robot_t, robot_xyz = get_ref_xyz_data(prepared_path)
    robot_vel, robot_acc = prepare_robot_data(robot_t, robot_xyz)

    acc_start, acc_end, robot_start, robot_end = display_span_selector(acc_t, acc_data_filtered, robot_t, robot_acc)    
    if(acc_start == acc_end or robot_start == robot_end):
        print("No selection made, exiting...")
        exit(1)

    # Resample IMU data to robot time points
    acc_resampled = sp.interpolate.interp1d(acc_t, acc_data_filtered, axis=0, fill_value="extrapolate")(robot_t)
    acc_resampled_normalized = (acc_resampled - np.mean(acc_resampled, axis=0)) / np.std(acc_resampled, axis=0)

    # Get the selected IMU fragment for correlation
    acc_mask = (robot_t >= acc_start) & (robot_t <= acc_end)
    acc_t_frag = robot_t[acc_mask] # get robot time points after resampling
    acc_data_frag = acc_resampled_normalized[acc_mask, :]

    # Get the selected robot data fragment for correlation
    robot_acc_normalized = (robot_acc - np.mean(robot_acc, axis=0)) / np.std(robot_acc, axis=0)
    robot_mask = (robot_t >= robot_start) & (robot_t <= robot_end)
    robot_t_frag = robot_t[robot_mask]
    robot_data_frag = robot_acc_normalized[robot_mask, :]

    # Compute cross-correlation between the selected fragments
    corr = sp.signal.correlate(
        acc_data_frag[:, 2],
        robot_data_frag[:, 2],
        mode="full"
    )

    # Find sample lag corresponding to the maximum correlation
    lags = sp.signal.correlation_lags(
        len(acc_data_frag[:,2]),
        len(robot_data_frag[:,2]),
        mode="full"
    )
    best_lag = lags[np.argmax(corr)]

    # convert sample lag to time offset
    offset_local = best_lag * np.mean(np.diff(robot_t))
    offset_global = offset_local - robot_start + acc_start

    plt.figure()
    plt.subplot(3, 1, 1)
    plt.plot(acc_t_frag, acc_data_frag[:,2])
    plt.plot(robot_t_frag, robot_data_frag[:,2], linestyle="--")
    plt.ylabel("Normalized Acceleration [g]")
    plt.title("Selected Fragments for Correlation")
    plt.grid()
    plt.subplot(3, 1, 2)
    plt.plot(acc_t_frag - offset_global, acc_data_frag[:,2])
    plt.plot(robot_t_frag, robot_data_frag[:,2], linestyle="--")
    plt.ylabel("Normalized Acceleration [g]")
    plt.title("Matched fragments")
    plt.xlabel("Time [s]")
    plt.grid()
    plt.subplot(3, 1, 3)
    plt.plot(np.linspace(-1.0, 1.0, len(corr)), corr / np.std(corr), linestyle=":")
    plt.title("Correlation of Selected Fragments")
    plt.xlabel("Lag")
    plt.ylabel("Normalized Correlation")
    plt.grid()
    plt.show()

    # Plot synced data
    fig, ax = plt.subplots(3, 1, sharex=False)
    ax[0].set_title("X Axis")
    ax[1].set_title("Y Axis")
    ax[2].set_title("Z Axis")
    ax[2].set_xlabel("Time [s]")

    for i in range(3):
        ax[i].plot(robot_t, robot_acc[:, i], label="Robot Acc (dpos/dt^2)", linestyle="--")
        ax[i].plot(acc_t - offset_global, acc_data_ac_filtered[:,i], label="IMU Acc")
        ax[i].set_ylabel("Acceleration [g]")
        ax[i].legend()
        ax[i].grid()        

    plt.show()

    # TODO: Prepare and export synced data to CSV
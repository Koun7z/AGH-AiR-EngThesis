from typing import Tuple

import stdatalog_utils
from stdatalog_utils import prepare_folder, get_acc_data, get_ref_xyz_data, load_sync_selection, save_sync_selection

import matplotlib.pyplot as plt
from matplotlib.widgets import SpanSelector
import numpy as np
import scipy as sp
import dtaidistance
from tqdm import tqdm

Ts_imu = 1.0 / 833.0
fs_imu = 833.0

Ts_robot = stdatalog_utils.ROBOT_TS
fs_robot = 1.0 / Ts_robot

fc = 30.0


def prepare_acc_data(t, data) -> tuple[np.ndarray, np.ndarray]:
    global fs_imu
    global Ts_imu
    Ts_imu = np.mean(np.diff(t))
    fs_imu = 1.0 / Ts_imu

    print(f"IMU Sampling Frequency: {fs_imu} Hz")

    # low-pass before downsampling
    b, a = sp.signal.butter(2, fc / (fs_imu / 2), btype="low")

    data_filtered = sp.signal.filtfilt(b, a, data, axis=0)

    # remove dc component (gravity vector + const bias)
    data_ac_filtered = data_filtered - np.mean(data_filtered, axis=0)

    return (data_filtered, data_ac_filtered)


def prepare_robot_data(t, data) -> tuple[np.ndarray, np.ndarray]:

    vel = sp.signal.savgol_filter(data, 11, 3, deriv=1, delta=Ts_robot, axis=0)
    acc = (sp.signal.savgol_filter(data, 11, 3, deriv=2, delta=Ts_robot, axis=0) / 9.8105)

    return (vel, acc)


def display_span_selector(x1, y1, x2, y2) -> Tuple[np.float64, np.float64, np.float64, np.float64]:

    selection_acc: Tuple[np.float64, np.float64] = (0.0, 0.0)  # type: ignore
    selection_robot: Tuple[np.float64, np.float64] = (0.0, 0.0)  # type: ignore

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

    sel = load_sync_selection(prepared_path)
    if (sel is not None):
        selection_acc = (sel[0], sel[1])
        selection_robot = (sel[2], sel[3])

        ax1.axvspan(selection_acc[0], selection_acc[1], alpha=0.2, color="orange")

        ax2.axvspan(selection_robot[0], selection_robot[1], alpha=0.2, color="orange")

    plt.show()

    if (selection_acc[0] != selection_acc[1] and selection_robot[0] != selection_robot[1]):
        save_sync_selection(prepared_path, selection_acc[0], selection_acc[1], selection_robot[0], selection_robot[1])

    return (selection_acc[0], selection_acc[1], selection_robot[0], selection_robot[1])


def display_correlated_frag(t1, frag1, t2, frag2, corr, offset):
    plt.figure()
    plt.subplot(3, 1, 1)
    plt.plot(t1, frag1)
    plt.plot(t2, frag2, linestyle="--")
    plt.ylabel("Normalized Acceleration [g]")
    plt.title("Selected Fragments for Correlation (Normalized)")
    plt.grid()
    plt.subplot(3, 1, 2)
    plt.plot(t1 - offset, frag1)
    plt.plot(t2, frag2, linestyle="--")
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


def check_xy_alignment(acc_data, robot_acc) -> np.ndarray:
    candidates = [
        np.array([[1, 0], [0, 1]]),
        np.array([[-1, 0], [0, 1]]),
        np.array([[1, 0], [0, -1]]),
        np.array([[-1, 0], [0, -1]]),
        np.array([[0, 1], [1, 0]]),
        np.array([[0, -1], [1, 0]]),
        np.array([[0, 1], [-1, 0]]),
        np.array([[0, -1], [-1, 0]]),
    ]

    best_score = -np.inf

    best_transform = candidates[0]

    corr_len = min(len(acc_data), len(robot_acc))

    imu_xy = acc_data[:corr_len, :2]
    robot_xy = robot_acc[:corr_len, :2]

    for T in candidates:

        imu_test = imu_xy @ T.T

        score_x = np.corrcoef(imu_test[:, 0], robot_xy[:, 0])[0, 1]

        score_y = np.corrcoef(imu_test[:, 1], robot_xy[:, 1])[0, 1]

        score = score_x + score_y

        # print(
        #     f"Transform:\n{T}\nScore: {score:.4f} (X: {score_x:.4f}, Y: {score_y:.4f})"
        # )

        if score > best_score:
            best_score = score
            best_transform = T

    return best_transform


def analyze_dtw_alignment(imu, robot, t):

    x_ds = sp.signal.decimate(imu, 4, axis=0)
    y_ds = sp.signal.decimate(robot, 4, axis=0)

    t_ds = t[::4]

    path = dtaidistance.dtw.warping_path_fast(x_ds, y_ds)
    path = np.asarray(path)

    print(f"DTW path length: {path}")

    imu_idx = path[:, 0]
    robot_idx = path[:, 1]

    delay_samples = robot_idx - imu_idx
    delay_time = delay_samples * Ts_robot

    plt.figure()
    plt.plot(t_ds[imu_idx], delay_time)
    plt.plot(t_ds[imu_idx], delay_samples, linestyle="--")
    plt.xlabel("Time [s]")
    plt.ylabel("Delay [s]")
    plt.grid()
    plt.title("DTW Alignment of IMU and Robot Data")


class SyncResult:

    def __init__(self, offset_t: np.float64, fit_corr: Tuple[np.float64, np.float64, np.float64],
                 transform: np.ndarray):
        self.offset_t: np.float64 = offset_t
        self.fit_corr: Tuple[np.float64, np.float64, np.float64] = fit_corr
        self.transform: np.ndarray = transform


def sync_process(acc_t, acc_data, acc_data_ac, robot_t, robot_acc, plot: bool) -> SyncResult:

    # Resample IMU data to robot time points
    acc_resampled_t = robot_t[robot_t <= acc_t[-1]]  # only resample up to the last IMU time point
    acc_resampled = sp.interpolate.interp1d(acc_t, acc_data_ac, axis=0, fill_value="extrapolate")(acc_resampled_t)

    acc_resampled_normalized = acc_resampled / np.std(acc_resampled, axis=0)

    # Get the selected IMU fragment for correlation
    acc_start_idx = np.searchsorted(acc_resampled_t, acc_start)
    acc_end_idx = np.searchsorted(acc_resampled_t, acc_end)

    acc_t_frag = acc_resampled_t[acc_start_idx:acc_end_idx]
    acc_data_frag = acc_resampled_normalized[acc_start_idx:acc_end_idx, :]

    # Get the selected robot data fragment for correlation
    robot_acc_normalized = (robot_acc - np.mean(robot_acc, axis=0)) / np.std(robot_acc, axis=0)

    robot_start_idx = np.searchsorted(robot_t, robot_start)
    robot_end_idx = np.searchsorted(robot_t, robot_end)

    robot_t_frag = robot_t[robot_start_idx:robot_end_idx]
    robot_data_frag = robot_acc_normalized[robot_start_idx:robot_end_idx, :]

    # Compute cross-correlation between the selected fragments
    corr = sp.signal.correlate(acc_data_frag[:, 2], robot_data_frag[:, 2], mode="full")

    # Find sample lag corresponding to the maximum correlation
    lags = sp.signal.correlation_lags(len(acc_data_frag[:, 2]), len(robot_data_frag[:, 2]), mode="full")
    best_lag = lags[np.argmax(corr)]
    robot_t_sample_offset = best_lag - robot_start_idx + acc_start_idx

    # convert sample lag to time offset
    offset_local = best_lag * Ts_robot
    offset_global = offset_local - robot_start + acc_start

    if (plot):
        display_correlated_frag(
            acc_t_frag,
            acc_data_frag[:, 2],
            robot_t_frag,
            robot_data_frag[:, 2],
            corr,
            offset_global,
        )

    if (robot_t_sample_offset > 0):
        acc_resampled_aligned = acc_resampled[robot_t_sample_offset:, :]
        robot_acc_aligned = robot_acc
    elif (robot_t_sample_offset < 0):
        acc_resampled_aligned = acc_resampled
        robot_acc_aligned = robot_acc[-robot_t_sample_offset:, :]
    else:
        acc_resampled_aligned = acc_resampled
        robot_acc_aligned = robot_acc

    if (plot):
        plt.figure()
        plt.plot(acc_resampled_aligned[:, 2])
        plt.plot(robot_acc_aligned[:, 2], linestyle="--")
        plt.show()

    transform = check_xy_alignment(acc_resampled_aligned, robot_acc_aligned)

    acc_transformed = acc_data_ac_filtered.copy()
    acc_transformed[:, :2] = acc_transformed[:, :2] @ transform.T

    acc_resampled_aligned_transformed = acc_resampled_aligned.copy()
    acc_resampled_aligned_transformed[:, :2] = acc_resampled_aligned_transformed[:, :2] @ transform.T

    acc_t_aligned = acc_t - offset_global

    # Plot synced data
    if (plot):
        fig, ax = plt.subplots(3, 1)
        ax[0].set_title("X Axis")
        ax[1].set_title("Y Axis")
        ax[2].set_title("Z Axis")
        ax[2].set_xlabel("Time [s]")

        for i in range(3):
            ax[i].plot(acc_t_aligned, acc_transformed[:, i], label="IMU Acc")
            ax[i].plot(
                robot_t,
                robot_acc[:, i],
                label="Robot Acc",
                #label="\text{Robot Acc} (\frac{\text{dpos}}{\text{d}t^2})",
                linestyle="--")
            ax[i].set_ylabel("Acceleration [g]")
            ax[i].legend()
            ax[i].grid()

        plt.show()

    # Plot data for correlation analysis
    if (plot):
        fig, ax = plt.subplots(3, 1)
        ax[0].set_title("X Axis")
        ax[1].set_title("Y Axis")
        ax[2].set_title("Z Axis")
        ax[2].set_xlabel("Time [s]")

        for i in range(3):
            ax[i].plot(acc_resampled_aligned_transformed[:, i], label="IMU Acc")
            ax[i].plot(
                robot_acc_aligned[:, i],
                label="Robot Acc",
                #label="\text{Robot Acc} (\frac{\text{dpos}}{\text{d}t^2})",
                linestyle="--")
            ax[i].set_ylabel("Acceleration [g]")
            ax[i].legend()
            ax[i].grid()

        fig.suptitle("Aligned IMU and Robot Acceleration Data for Correlation Analysis")

        plt.show()

    corr_len = min(len(acc_resampled_aligned_transformed), len(robot_acc_aligned))
    sync_corr_x = np.corrcoef(acc_resampled_aligned_transformed[:corr_len, 0], robot_acc_aligned[:corr_len, 0])[0, 1]
    sync_corr_y = np.corrcoef(acc_resampled_aligned_transformed[:corr_len, 1], robot_acc_aligned[:corr_len, 1])[0, 1]
    sync_corr_z = np.corrcoef(acc_resampled_aligned_transformed[:corr_len, 2], robot_acc_aligned[:corr_len, 2])[0, 1]

    return SyncResult(offset_global, (sync_corr_x, sync_corr_y, sync_corr_z), transform)


if __name__ == "__main__":
    import argparse

    #plt.rcParams.update({"text.usetex": True, "font.family": "Helvetica"})

    parser = argparse.ArgumentParser(description="Sync IMU and Robot data.")
    parser.add_argument("path", type=str, help="Path to the HSDatalog acquisition folder")
    parser.add_argument("--find-ts", action="store_true", help="Find best robot sample time")
    args = parser.parse_args()

    prepared_path = prepare_folder(args.path)

    acc_t, acc_data = get_acc_data(prepared_path)
    acc_data_filtered, acc_data_ac_filtered = prepare_acc_data(acc_t, acc_data)

    robot_t, robot_xyz = get_ref_xyz_data(prepared_path)
    robot_vel, robot_acc = prepare_robot_data(robot_t, robot_xyz)

    acc_start, acc_end, robot_start, robot_end = display_span_selector(acc_t, acc_data_filtered, robot_t, robot_acc)
    if acc_start == acc_end or robot_start == robot_end:
        print("No selection made, exiting...")
        exit(1)

    if (not args.find_ts):
        result = sync_process(acc_t, acc_data, acc_data_ac_filtered, robot_t, robot_acc, True)

        print(
            f"Sync Result:\nOffset: {result.offset_t:.6f} s\nCorrelation: X={result.fit_corr[0]:.4f}, Y={result.fit_corr[1]:.4f}, Z={result.fit_corr[2]:.4f}\nTransform:\n{result.transform}"
        )

    else:
        k_scale_min = 0.95
        k_scale_max = 1.05
        k_iter = 10000

        k_range = np.linspace(k_scale_min, k_scale_max, k_iter)

        best_result = None
        best_k = 1.0
        best_corr = -1

        for k in tqdm(k_range, desc="Estimating robot Ts"):
            robot_t_scaled = robot_t * k

            result = sync_process(acc_t, acc_data, acc_data_ac_filtered, robot_t_scaled, robot_acc, False)

            corr = np.sum(result.fit_corr)
            if corr > best_corr:
                best_corr = corr
                best_result = result
                best_k = k

        if best_result is None:
            print("No valid sync result found.")
            exit(1)

        print(
            f"Best Sync Result:\nOffset: {best_result.offset_t:.6f} s\nCorrelation: X={best_result.fit_corr[0]:.4f}, Y={best_result.fit_corr[1]:.4f}, Z={best_result.fit_corr[2]:.4f}\nTransform:\n{best_result.transform}"
        )

        if (abs(best_k - k_scale_min) < 1e-6 or abs(best_k - k_scale_max) < 1e-6):
            print("Warning: Scale factor is out of search bounds, adjust the initial value and try again.")

        print(f"Best scaling factor: {best_k}, Ts({Ts_robot}-->{Ts_robot * best_k})")

    # TODO: Prepare and export synced data to CSV

from pathlib import Path
from typing import Tuple

import stdatalog_utils
from stdatalog_utils import prepare_folder, get_acc_data, get_ref_xyz_data, load_sync_selection, save_sync_selection

import matplotlib.pyplot as plt
from matplotlib.widgets import SpanSelector
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
import scipy as sp
import pandas as pd
from tqdm import tqdm

Ts_imu = 1.0 / 833.0
fs_imu = 833.0

Ts_robot = stdatalog_utils.ROBOT_TS
fs_robot = 1.0 / Ts_robot

fc = 30.0

global pdf


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


def prepare_gyro_data(t, data) -> tuple[np.ndarray, np.ndarray]:
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

    fig, (ax1, ax2) = plt.subplots(2, 1, sharex=False, figsize=(8.27, 11.69))
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

    pdf.savefig(fig, bbox_inches="tight")

    plt.show()

    if (selection_acc[0] != selection_acc[1] and selection_robot[0] != selection_robot[1]):
        save_sync_selection(prepared_path, selection_acc[0], selection_acc[1], selection_robot[0], selection_robot[1])

    return (selection_acc[0], selection_acc[1], selection_robot[0], selection_robot[1])


def display_correlated_frag(t1, frag1, t2, frag2, corr, offset):
    fig, ax = plt.subplots(3, 1, figsize=(8.27, 11.69))

    ax[0].plot(t1, frag1)
    ax[0].plot(t2, frag2, linestyle="--")
    ax[0].set_ylabel("Normalized Acceleration [g]")
    ax[0].set_title("Selected Fragments for Correlation (Normalized)")
    ax[0].grid()

    ax[1].plot(t1 - offset, frag1)
    ax[1].plot(t2, frag2, linestyle="--")
    ax[1].set_ylabel("Normalized Acceleration [g]")
    ax[1].set_title(f"Matched fragments ({offset:0.3f}s offset)")
    ax[1].set_xlabel("Time [s]")
    ax[1].grid()

    ax[2].plot(np.linspace(-1.0, 1.0, len(corr)), corr / np.std(corr), linestyle=":")
    ax[2].set_title("Correlation of Selected Fragments")
    ax[2].set_xlabel("Lag")
    ax[2].set_ylabel("Normalized Correlation")
    ax[2].grid()
    fig.subplots_adjust(hspace=0.4)
    pdf.savefig(fig, bbox_inches="tight")
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


# def analyze_dtw_alignment(imu, robot, t):

#     x_ds = sp.signal.decimate(imu, 4, axis=0)
#     y_ds = sp.signal.decimate(robot, 4, axis=0)

#     t_ds = t[::4]

#     path = dtaidistance.dtw.warping_path_fast(x_ds, y_ds)
#     path = np.asarray(path)

#     print(f"DTW path length: {path}")

#     imu_idx = path[:, 0]
#     robot_idx = path[:, 1]

#     delay_samples = robot_idx - imu_idx
#     delay_time = delay_samples * Ts_robot

#     plt.figure()
#     plt.plot(t_ds[imu_idx], delay_time)
#     plt.plot(t_ds[imu_idx], delay_samples, linestyle="--")
#     plt.xlabel("Time [s]")
#     plt.ylabel("Delay [s]")
#     plt.grid()
#     plt.title("DTW Alignment of IMU and Robot Data")


class SyncResult:

    def __init__(self, offset_t: np.float64, fit_corr: Tuple[np.float64, np.float64, np.float64],
                 xy_transform: np.ndarray):
        self.offset_t: np.float64 = offset_t
        self.fit_corr: Tuple[np.float64, np.float64, np.float64] = fit_corr
        self.xy_transform: np.ndarray = xy_transform


def sync_process(acc_t, acc_data, acc_data_ac, robot_t, robot_acc, plot: bool, verbose: bool = False) -> SyncResult:

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

    if (plot and verbose):
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
        fig, ax = plt.subplots(3, 1, figsize=(8.27, 11.69))
        ax[0].set_title("X Axis")
        ax[1].set_title("Y Axis")
        ax[2].set_title("Z Axis")
        ax[2].set_xlabel("Time [s]")
        fig.suptitle("Final IMU and Robot Acceleration Data Time-aligned")

        for i in range(3):
            ax[i].plot(acc_t_aligned, acc_transformed[:, i], label="IMU Acc (LPF_fc = 30 Hz)")
            ax[i].plot(
                robot_t,
                robot_acc[:, i],
                label="Robot Acc",
                #label="\text{Robot Acc} (\frac{\text{dpos}}{\text{d}t^2})",
                linestyle="--")
            ax[i].set_ylabel("Acceleration [g]")
            ax[i].legend()
            ax[i].grid()

        pdf.savefig(fig, bbox_inches="tight")
        plt.show()

    #Plot data for correlation analysis
    if (plot and verbose):
        fig, ax = plt.subplots(3, 1, figsize=(8.27, 11.69))
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

        pdf.savefig(fig, bbox_inches="tight")
        plt.show()

    corr_len = min(len(acc_resampled_aligned_transformed), len(robot_acc_aligned))
    sync_corr_x = np.corrcoef(acc_resampled_aligned_transformed[:corr_len, 0], robot_acc_aligned[:corr_len, 0])[0, 1]
    sync_corr_y = np.corrcoef(acc_resampled_aligned_transformed[:corr_len, 1], robot_acc_aligned[:corr_len, 1])[0, 1]
    sync_corr_z = np.corrcoef(acc_resampled_aligned_transformed[:corr_len, 2], robot_acc_aligned[:corr_len, 2])[0, 1]

    return SyncResult(offset_global, (sync_corr_x, sync_corr_y, sync_corr_z), transform)


def prepare_synced_data_frame(sync_result: SyncResult, imu_t, raw_acc, raw_gyro, robot_t, robot_acc,
                              robot_abc) -> pd.DataFrame:

    # Remove IMU data that were recorded before the robot data started
    synced_imu_t = imu_t - sync_result.offset_t
    zero_offset = np.searchsorted(synced_imu_t, 0.0)
    print(f"Zero offset index: {zero_offset}, synced_imu_t[zero_offset]: {synced_imu_t[zero_offset]}")

    synced_imu_t = synced_imu_t[zero_offset:]
    raw_acc_sync = raw_acc.copy()[zero_offset:, :]
    raw_acc_sync[:, :2] = raw_acc_sync[:, :2] @ sync_result.xy_transform.T
    raw_gyro_sync = raw_gyro.copy()[zero_offset:, :]
    raw_gyro_sync[:, :2] = raw_gyro_sync[:, :2] @ sync_result.xy_transform.T

    rot = sp.spatial.transform.Rotation.from_euler("zyx", robot_abc, degrees=True)

    robot_rot_slerp = sp.spatial.transform.Slerp(robot_t, rot)

    ref_rot_imu_t = robot_rot_slerp(synced_imu_t)
    ref_quat_imu_t = ref_rot_imu_t.as_quat()

    upsamp_robot_acc = sp.interpolate.interp1d(robot_t, robot_acc, axis=0, fill_value="extrapolate")(synced_imu_t)

    # shift the final time vector to start at 0
    synced_imu_t = synced_imu_t - synced_imu_t[0]

    # Plot synced data
    fig, ax = plt.subplots(3, 1, figsize=(8.27, 11.69))
    ax[0].set_title("X Axis")
    ax[1].set_title("Y Axis")
    ax[2].set_title("Z Axis")
    ax[2].set_xlabel("Sample")
    fig.suptitle("Final Raw IMU and Robot per-sample data alignement")

    for i in range(3):
        ax[i].plot(raw_acc_sync[:, i] - np.mean(raw_acc_sync[:, i]), label="IMU Acc")
        ax[i].plot(
            upsamp_robot_acc[:, i],
            label="Robot Acc",
            #label="\text{Robot Acc} (\frac{\text{dpos}}{\text{d}t^2})",
            linestyle="--")
        ax[i].set_ylabel("Acceleration [g]")
        ax[i].legend()
        ax[i].grid()

    fig.tight_layout()
    pdf.savefig(fig, bbox_inches="tight")
    plt.show()

    df = pd.DataFrame()
    df["Time [s]"] = synced_imu_t
    df["q_w"] = ref_quat_imu_t[:, 3]
    df["q_x"] = ref_quat_imu_t[:, 0]
    df["q_y"] = ref_quat_imu_t[:, 1]
    df["q_z"] = ref_quat_imu_t[:, 2]
    df["Acc_X [g]"] = raw_acc_sync[:, 0]
    df["Acc_Y [g]"] = raw_acc_sync[:, 1]
    df["Acc_Z [g]"] = raw_acc_sync[:, 2]
    df["Gyro_X [rad/s]"] = raw_gyro_sync[:, 0]
    df["Gyro_Y [rad/s]"] = raw_gyro_sync[:, 1]
    df["Gyro_Z [rad/s]"] = raw_gyro_sync[:, 2]
    df["Mag_X [uT]"] = np.array([1.0] * len(df))
    df["Mag_Y [uT]"] = np.array([0.0] * len(df))
    df["Mag_Z [uT]"] = np.array([0.0] * len(df))

    return df


if __name__ == "__main__":
    import argparse

    #plt.rcParams.update({"text.usetex": True, "font.family": "Helvetica"})

    parser = argparse.ArgumentParser(description="Sync IMU and Robot data.")
    parser.add_argument("path", type=str, help="Path to the HSDatalog acquisition folder")
    parser.add_argument("--find-ts", action="store_true", help="Find best robot sample time")
    parser.add_argument("-o", "--output", type=str, help="Output file for sync result")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output")
    parser.add_argument("-s", "--silent", action="store_true", help="Suppress most plots")
    args = parser.parse_args()

    prepared_path = prepare_folder(args.path)

    pdf = PdfPages(Path(prepared_path) / "sync_plots.pdf")

    acc_t, acc_data = get_acc_data(prepared_path)
    acc_data_filtered, acc_data_ac_filtered = prepare_acc_data(acc_t, acc_data)

    robot_t, robot_xyz = get_ref_xyz_data(prepared_path)
    robot_vel, robot_acc = prepare_robot_data(robot_t, robot_xyz)

    acc_start, acc_end, robot_start, robot_end = display_span_selector(acc_t, acc_data_filtered, robot_t, robot_acc)
    if acc_start == acc_end or robot_start == robot_end:
        print("No selection made, exiting...")
        exit(1)

    if (not args.find_ts):
        result = sync_process(acc_t, acc_data_filtered, acc_data_ac_filtered, robot_t, robot_acc, not args.silent,
                              args.verbose)

        print(
            f"Sync Result:\nOffset: {result.offset_t:.6f} s\nCorrelation: X={result.fit_corr[0]:.4f}, Y={result.fit_corr[1]:.4f}, Z={result.fit_corr[2]:.4f}\nTransform:\n{result.xy_transform}"
        )

        if (args.output):
            out_path = Path(args.output)
            if (out_path.is_dir()):
                out_path = out_path / Path(Path(prepared_path).name.lower() + "_synced.csv")

            out_path.parent.mkdir(parents=True, exist_ok=True)

            _, gyro_data = stdatalog_utils.get_gyro_data(prepared_path)
            _, robot_abc = stdatalog_utils.get_ref_abc_data(prepared_path)

            gyro_data_filtered, _ = prepare_gyro_data(acc_t, gyro_data)

            df = prepare_synced_data_frame(result, acc_t, acc_data, gyro_data, robot_t, robot_acc, robot_abc)

            with open(out_path, "w") as f:
                f.write("Time (s);Ref Orientation;;;;IMU Acceleration;;;;IMU Gyroscope;;;;IMU Magnetometer;;;\n")

                f.write(";W;X;Y;Z;X;Y;Z;X;Y;Z;X;Y;Z\n")

                df.to_csv(
                    f,
                    sep=";",
                    index=False,
                    header=False,
                    float_format="%.9g",
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

            result = sync_process(acc_t, acc_data_filtered, acc_data_ac_filtered, robot_t_scaled, robot_acc, False)

            corr = np.sum(result.fit_corr)
            if corr > best_corr:
                best_corr = corr
                best_result = result
                best_k = k

        if best_result is None:
            print("No valid sync result found.")
            exit(1)

        print(
            f"Best Sync Result:\nOffset: {best_result.offset_t:.6f} s\nCorrelation: X={best_result.fit_corr[0]:.4f}, Y={best_result.fit_corr[1]:.4f}, Z={best_result.fit_corr[2]:.4f}\nTransform:\n{best_result.xy_transform}"
        )

        if (abs(best_k - k_scale_min) < 1e-6 or abs(best_k - k_scale_max) < 1e-6):
            print("Warning: Scale factor is out of search bounds, adjust the initial value and try again.")

        print(f"Best scaling factor: {best_k}, Ts({Ts_robot}-->{Ts_robot * best_k})")

    pdf.close()

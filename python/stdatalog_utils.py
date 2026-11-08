from stdatalog_core.HSD.HSDatalog import HSDatalog

import shutil
from pathlib import Path
import numpy as np
import pandas as pd


def prepare_folder(path: str) -> str:
    src = Path(path).resolve()
    dst = Path("./tmp", src.name).resolve()

    stamp_file = dst / ".last_dat_mtime"

    # Find newest .dat file in source
    dat_files = list(src.rglob("*.dat"))
    newest_mtime = max((f.stat().st_mtime for f in dat_files), default=0.0)

    # Check if destination is up to date
    if dst.exists() and stamp_file.exists():
        try:
            saved_mtime = float(stamp_file.read_text().strip())
            if saved_mtime >= newest_mtime:
                return str(dst)
        except (ValueError, OSError):
            pass

    # Rebuild destination
    if dst.exists():
        shutil.rmtree(dst)

    shutil.copytree(src, dst)

    # Rename .dat files to lowercase
    for file in dst.rglob("*.dat"):
        new_path = file.with_name(file.name.lower())
        if file != new_path:
            file.rename(new_path)

    # Save newest source .dat modification time
    stamp_file.write_text(str(newest_mtime))

    return str(dst)


def get_acc_data(path: str, debug: bool = False) -> tuple[np.ndarray, np.ndarray]:
    hsd = HSDatalog()

    hsd_instance = hsd.create_hsd(acquisition_folder=path)

    components = hsd.get_all_components(hsd_instance)
    if(debug):
        for comp in components:
            print(comp.keys())

    df_a = hsd.get_dataframe(hsd_instance, components[0])[0]
    if(debug):
        print(df_a.describe())

    
    acc_data = df_a.to_numpy()
    acc_t = acc_data[:,0] - acc_data[0,0]  # Normalize time to start at 0

    return (acc_t, acc_data[:,1:])

def get_gyro_data(path: str, debug: bool = False) -> tuple[np.ndarray, np.ndarray]:
    hsd = HSDatalog()

    hsd_instance = hsd.create_hsd(acquisition_folder=path)

    components = hsd.get_all_components(hsd_instance)
    if(debug):
        for comp in components:
            print(comp.keys())

    df_a = hsd.get_dataframe(hsd_instance, components[1])[0]
    if(debug):
        print(df_a.describe())

    
    acc_data = df_a.to_numpy()
    acc_t = acc_data[:,0] - acc_data[0,0]  # Normalize time to start at 0

    return (acc_t, acc_data[:,1:])

def get_ref_xyz_data(path: str, debug: bool = False) -> tuple[np.ndarray, np.ndarray]:
    src_df = pd.read_csv(Path(path) / "ref_data.csv", skiprows=[0,2])

    if(debug):
        print(src_df.describe())
        print(src_df.head())

    # resample the data to Ts = 3.55 ms because Mitsubishi can't label their own data properly...
    robot_t = np.arange(len(src_df["Time"])) * (3.55 / 1000)
    robot_xyz = src_df[["XYZ position(FB) X", "XYZ position(FB) Y", "XYZ position(FB) Z"]].to_numpy() / 1000

    return (robot_t, robot_xyz)

def get_ref_abc_data(path: str, debug: bool = False) -> tuple[np.ndarray, np.ndarray]:
    src_df = pd.read_csv(Path(path) / "ref_data.csv", skiprows=[0,2])

    if(debug):
        print(src_df.describe())
        print(src_df.head())

    robot_t = np.arange(len(src_df["Time"])) * (3.55 / 1000)
    robot_xyz = src_df[["XYZ position(FB) A", "XYZ position(FB) B", "XYZ position(FB) C"]].to_numpy() / 1000

    return (robot_t, robot_xyz)

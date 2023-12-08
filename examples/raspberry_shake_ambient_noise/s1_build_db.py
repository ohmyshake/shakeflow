# %%
import sys
import time
from pathlib import Path

sys.path.append("/Users/yinfu/ohmyshake/shakecore")
sys.path.append("/Users/yinfu/ohmyshake/shakeflow")

import shakecore as sc
from shakeflow import file_monitor, get_logger


# watchdog parameters
n_files = 3  # at least 'n_files' to start computing
path = (
    "/Users/yinfu/ohmyshake/shakeflow/examples/raspberry_shake_ambient_noise/download"
)
mode = "from_origin"
suffix = ".h5"

# task parameters
outpath = Path("./database")
logpath = Path("./log")


# %%
def get_to_do_files(total_files, finished_files, n_files):
    to_do_files = sorted(list(set(total_files) - set(finished_files)))[0:n_files]
    return to_do_files


def get_finished_files(to_do_files, finished_files):
    finished_files = finished_files + to_do_files
    return finished_files


def compute_task(files, logpath):
    # 1. set logger
    logger = get_logger(str(logpath / "s1_build_db.log"))

    try:
        # read
        stream = sc.read(
            files,
            format="sc",
            backend="shakecore",
        ).merge(axis="time")

        # write
        out_file = outpath / stream.stats.starttime.strftime(
            f"%Y_%m_%d_%H_%M_%S_%f_EHZ.h5"
        )
        stream.write(str(out_file), format="sc", backend="shakecore")

        # log
        logger.info(f"Success: {files}")
    except Exception:
        logger.exception(f"Error: {files}")


# main function
if __name__ == "__main__":
    # thread-1: file monitor
    observer, event_handler = file_monitor(path, mode=mode, suffix=suffix)
    observer.start()

    # thread-2: compute jobs
    try:
        outpath.mkdir(parents=True, exist_ok=True)
        logpath.mkdir(parents=True, exist_ok=True)
        total_files = event_handler.files
        finished_files = []
        while True:
            time.sleep(1)
            if (len(total_files) - len(finished_files)) >= n_files:
                to_do_files = get_to_do_files(total_files, finished_files, n_files)
                print(f"Start: {to_do_files}")
                compute_task(to_do_files, logpath)
                finished_files = get_finished_files(to_do_files, finished_files)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

# %%

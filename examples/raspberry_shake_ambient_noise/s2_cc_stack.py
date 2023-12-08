# %%
import sys
import time
import numpy as np
from pathlib import Path
from obspy.geodetics import locations2degrees
from obspy.geodetics import degrees2kilometers

sys.path.append("/Users/yinfu/ohmyshake/noisecc")
sys.path.append("/Users/yinfu/ohmyshake/shakecore")
sys.path.append("/Users/yinfu/ohmyshake/shakeflow")

import noisecc as nc
import shakecore as sc
from shakeflow import file_monitor, get_logger


# watchdog parameters
n_files = 2  # at least 'n_files' to start computing
path = (
    "/Users/yinfu/ohmyshake/shakeflow/examples/raspberry_shake_ambient_noise/database"
)
mode = "from_origin"
suffix = ".h5"

# task parameters
jobs = 2
outpath = Path("./results")
logpath = Path("./log")

# preprocess parameters
resampling_rate = 50  # resample rate, in Hz

# chunk parameters
cc_len = 3 * 60  # length of cross-correlation (s)
cc_step = 2 * 60
time_norm = "no"  # no onebit clip smooth
clip_std = 10
smooth_N = 20

# rfft
freq_norm = "smooth_whiten"  # no whiten smooth_whiten
freqmin = 0.5
freqmax = 10
whiten_npad = 50
smoothspect_N = 20

# corr
corr_method = "coherency"  # xcorr, deconv, coherency
maxlag = 20  # lags of cross-correlation to save (s)
smoothspect_N = 20


# stack
stack_method = "pws"  # "linear", "pws", and "robust", maybe add "PCA"
stack_all = True
stack_len = 20  # Int64; number of chuncks to stack;
stack_step = 0
pick = True
median_high = 3  # Float64; max median value (default value)
median_low = 0.5  # Float64; min median value (default value)


# %%
def get_to_do_files(total_files, finished_files, n_files):
    to_do_files = sorted(list(set(total_files) - set(finished_files)))[0:n_files]
    return to_do_files


def get_finished_files(to_do_files, finished_files):
    finished_files = finished_files + to_do_files
    return finished_files


def compute_task(files, logpath, jobs):
    # 1. set logger
    logger = get_logger(str(logpath / "s2_cc_stack.log"))

    try:
        # 2. read
        stream = sc.read(
            files,
            format="sc",
            backend="shakecore",
        ).merge(axis="time")

        # 3. preprocess
        stream.data[np.isnan(stream.data)] = 0
        stream.detrend()
        stream.taper()
        stream.filter(type="bandpass", freqmin=freqmin, freqmax=freqmax)
        stream.resample(sampling_rate=float(resampling_rate))

        # 4. chunk
        ChunkData = nc.chunk(
            data=stream.data,
            starttime=stream.stats.starttime,
            cc_len=cc_len,
            cc_step=cc_step,
            dt=stream.stats.delta,
            time_norm=time_norm,
            clip_std=clip_std,
            smooth_N=smooth_N,
            device="cpu",
            jobs=1,
            flag=False,
        )

        # 5. rfft
        RFFTData = nc.rfft(
            data=ChunkData.data,
            dt=ChunkData.dt,
            cc_len=cc_len,
            cc_step=cc_step,
            starttime=stream.stats.starttime,
            freq_norm=freq_norm,
            freqmin=freqmin,
            freqmax=freqmax,
            whiten_npad=whiten_npad,
            smoothspect_N=smoothspect_N,
            device="cpu",
            jobs=1,
            flag=False,
        )

        # 6. corr-pairs
        channel_num = stream.stats.trace_num
        pairs_num = int((channel_num + 1) * channel_num / 2)
        pairs = np.empty((pairs_num, 2))
        pairs_dist = np.empty(pairs_num)

        count = 0
        for i in range(0, channel_num):
            for j in range(i, channel_num):
                pairs[count] = np.array([i, j])
                lat1 = stream.stats.latitude[i]
                lon1 = stream.stats.longitude[i]
                lat2 = stream.stats.latitude[j]
                lon2 = stream.stats.longitude[j]
                dist = degrees2kilometers(locations2degrees(lat1, lon1, lat2, lon2))
                # print((lat1, lon1, lat2, lon2))
                pairs_dist[count] = dist
                count += 1

        # 7. corr
        CorrData = nc.corr(
            data=RFFTData.data,
            dt=RFFTData.dt,
            cc_len=cc_len,
            cc_step=cc_step,
            starttime=stream.stats.starttime,
            method=corr_method,
            pairs=pairs,
            maxlag=maxlag,
            smoothspect_N=smoothspect_N,
            device="cpu",
            jobs=10,
            flag=False,
        )
        out_file = (
            outpath
            / "cc"
            / stream.stats.starttime.strftime(f"cc_%Y_%m_%d_%H_%M_%S_%f_EHZ")
        )
        CorrData.save(str(out_file))

        # 8. stack
        StackData = nc.stack(
            data=CorrData.data,
            dt=CorrData.dt,
            cc_len=cc_len,
            cc_step=cc_step,
            starttime=stream.stats.starttime,
            pairs=pairs,
            pairs_dist=pairs_dist,
            dist_unit="km",
            pick=pick,
            stack_all=stack_all,
            stack_len=stack_len,
            stack_step=stack_step,
            method=stack_method,
            device="cpu",
            jobs=jobs,
            flag=False,
        )
        out_file = (
            outpath
            / "stack"
            / stream.stats.starttime.strftime(f"stack_%Y_%m_%d_%H_%M_%S_%f_EHZ")
        )
        StackData.save(str(out_file))

        # 9. log
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
        (outpath / "cc").mkdir(parents=True, exist_ok=True)
        (outpath / "stack").mkdir(parents=True, exist_ok=True)
        logpath.mkdir(parents=True, exist_ok=True)
        total_files = event_handler.files
        finished_files = []
        while True:
            time.sleep(1)
            if (len(total_files) - len(finished_files)) >= n_files:
                to_do_files = get_to_do_files(total_files, finished_files, n_files)
                print(f"Start: {to_do_files}")
                compute_task(to_do_files, logpath, jobs)
                finished_files = get_finished_files(to_do_files, finished_files)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

# %%

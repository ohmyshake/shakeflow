# %%
import sys
import time
import numpy as np
from pathlib import Path
from obspy import UTCDateTime
from joblib import Parallel, delayed
from obspy.clients.fdsn import Client

sys.path.append("/Users/yinfu/ohmyshake/shakecore")
sys.path.append("/Users/yinfu/ohmyshake/shakeflow")

from shakecore import Stream
from shakeflow import time_monitor, get_logger


# watchdog parameters
starttime = UTCDateTime() - 24 * 60 * 60  # set the start time to be the current time
time_interval = 60 * 10  # data segment to download as one file, in seconds
time_lagging = 60 * 60  # some lagging time, in seconds


# task parameters
jobs = 3
freqmin = 0.1
freqmax = 49.9
resampling_rate = 100  # resample rate, in Hz
outpath = Path("./download")
logpath = Path("./log")

stations = [
    "RF926",
    "R3CDE",
    "R27ED",
    "RC2BF",
    "R6650",
    "R16DA",
    "R4081",
    "R3978",
    "SB819",
    "R0D0E",
    "RFC36",
    "RF44C",
    "RF395",
    "R1B48",
    "RDCFB",
    "R42D0",
    "RF5C1",
    "R37A5",
    "R0EBF",
]


# %%
def get_to_do_times(total_times, finished_times):
    to_do_times = sorted(list(set(total_times) - set(finished_times)))[0]
    return to_do_times


def get_finished_times(to_do_times, finished_times):
    finished_times = finished_times + [to_do_times]
    return finished_times


def pre_task(stations):
    #  obspy download metadata, would be better to use a local file which is downloaded in advance
    metadata_all = []
    client = Client("RASPISHAKE")
    for i in range(0, len(stations)):
        try:
            metadata = client.get_stations(
                network="AM",
                station=stations[i],
                location="00",
                channel="EHZ",
                level="RESP",
            )
            metadata_all.append(metadata)
        except Exception:
            metadata_all.append("error")

    return metadata_all


def process(trace, metadata, start_time, end_time, freqmin, freqmax, resampling_rate):
    if trace != "error" and metadata != "error":
        # remove response
        trace.remove_response(inventory=metadata, output="VEL")

        # filter
        trace.filter("bandpass", freqmin=freqmin, freqmax=freqmax)

        # resample
        trace.resample(resampling_rate)

        # trim
        trace.trim(start_time, end_time, pad=True, nearest_sample=True, fill_value=0)

        return trace
    else:
        return "error"


def compute_task(
    metadata_all, times, freqmin, freqmax, resampling_rate, time_interval, logpath
):
    # 1. set logger
    logger = get_logger(str(logpath / "s0_download.log"))

    # 2. obspy download data
    client = Client("RASPISHAKE")
    obspy_trace_all = []
    start_time = UTCDateTime(times)
    end_time = start_time + time_interval
    for i in range(0, len(stations)):
        try:
            # get data
            obspy_stream = client.get_waveforms(
                "AM", stations[i], "00", "EHZ", start_time, end_time
            )
            obspy_stream.merge(fill_value=0)

            # append
            obspy_trace_all.append(obspy_stream[0])

            # log
            logger.info(f"Success download: {stations[i]} {start_time}")
        except Exception:
            obspy_trace_all.append("error")
            logger.info(f"Error download: {stations[i]} {start_time}")

    # 3. process
    try:
        if jobs == 1:
            obspy_process_trace_all = []
            for i in range(0, len(obspy_trace_all)):
                tr = process(
                    obspy_trace_all[i],
                    metadata_all[i],
                    start_time,
                    end_time,
                    freqmin,
                    freqmax,
                    resampling_rate,
                )
                obspy_process_trace_all.append(tr)
        elif jobs > 1:
            obspy_process_trace_all = Parallel(n_jobs=jobs, backend="loky")(
                delayed(process)(
                    obspy_trace_all[i],
                    metadata_all[i],
                    start_time,
                    end_time,
                    freqmin,
                    freqmax,
                    resampling_rate,
                )
                for i in range(0, len(obspy_trace_all))
            )
        else:
            raise Exception("jobs must be a positive integer")

        logger.info(f"Success process: {start_time}")
    except Exception:
        obspy_process_trace_all = ["error"] * len(stations)
        logger.exception(f"Error process: {start_time}")

    # 4. convert to shakecore
    try:
        npts = int(time_interval * resampling_rate)
        data = np.zeros((len(stations), npts))
        stream = Stream(
            data,
            header={
                "npts": npts,
                "sampling_rate": float(resampling_rate),
                "station": stations,
                "starttime": start_time,
                "type": "velocity",
            },
        )
        for i in range(0, len(stations)):
            # set data
            if obspy_process_trace_all[i] == "error":
                stream.data[i, :] = np.NaN
            else:
                stream.data[i, :] = obspy_process_trace_all[i].data[0:npts]

            # set stats
            stream.stats.network[i] = "AM"
            stream.stats.channel[i] = "EHZ"
            if metadata_all[i] == "error":
                stream.stats.latitude[i] = np.NaN
                stream.stats.longitude[i] = np.NaN
                stream.stats.elevation[i] = np.NaN
            else:
                stream.stats.latitude[i] = (
                    metadata_all[i].networks[0].stations[0].latitude
                )
                stream.stats.longitude[i] = (
                    metadata_all[i].networks[0].stations[0].longitude
                )
                stream.stats.elevation[i] = (
                    metadata_all[i].networks[0].stations[0].elevation
                )

        #  save stream
        str_time = stream.stats.starttime.strftime(f"%Y_%m_%d_%H_%M_%S_%f")
        out_file = outpath / f"{str_time}_EHZ.h5"
        stream.write(str(out_file), format="sc", backend="shakecore")

        # log
        logger.info(f"Success write: {start_time}")
    except Exception:
        logger.exception(f"Error write: {start_time}")


# main function
if __name__ == "__main__":
    # thread-1: file monitor
    observer, event_handler = time_monitor(starttime, time_interval, time_lagging)
    observer.start()

    # thread-2: compute jobs
    try:
        outpath.mkdir(parents=True, exist_ok=True)
        logpath.mkdir(parents=True, exist_ok=True)
        total_times = event_handler.times
        finished_times = []
        metadata_all = pre_task(stations)
        while True:
            time.sleep(1)
            if len(total_times) > len(finished_times):
                to_do_times = get_to_do_times(total_times, finished_times)
                print(f"Start: {to_do_times}")
                compute_task(
                    metadata_all,
                    to_do_times,
                    freqmin,
                    freqmax,
                    resampling_rate,
                    time_interval,
                    logpath,
                )
                finished_times = get_finished_times(to_do_times, finished_times)

    except KeyboardInterrupt:
        observer.stop()
    observer.join()

# %%

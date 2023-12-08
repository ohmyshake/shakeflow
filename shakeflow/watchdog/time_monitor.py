import time
import threading
from obspy import UTCDateTime


class EventHandler:
    def __init__(self, starttime, time_interval, time_lagging):
        self.starttime = starttime
        self.time_interval = time_interval
        self.time_lagging = time_lagging
        self.times = [str(starttime)]
        self.running = True

    def trigger(self):
        while self.running:
            current_utc_time = UTCDateTime()
            if (
                current_utc_time
                > self.starttime + self.time_interval + self.time_lagging
            ):
                self.times.append(str(self.starttime + self.time_interval))
                self.starttime += self.time_interval
            time.sleep(1)

    def stop(self):
        self.running = False


class TimeMonitor:
    def __init__(self):
        self.thread = None

    def schedule(self, event_handler):
        self.event_handler = event_handler
        self.thread = threading.Thread(target=self.event_handler.trigger)

    def start(self):
        if self.thread:
            self.thread.start()

    def stop(self):
        if self.thread and self.event_handler:
            self.event_handler.stop()

    def join(self):
        if self.thread:
            self.thread.join()


def time_monitor(starttime, time_interval=60 * 60, time_lagging=0):
    """Start monitoring the specified time.

    Parameters
    ----------
    starttime : obspy.UTCDateTime
        The start time to be monitored.
    time_interval : int or float
        The time interval between two time segments, in seconds.
    time_lagging : int or float
        The lagging time between the current time and the last time segment,
        in seconds.

    Returns
    -------
    observer : watchdog.observers.Observer
        The observer.
    event_handler : EventHandler
        The event handler.
    """
    event_handler = EventHandler(starttime, time_interval, time_lagging)
    observer = TimeMonitor()
    observer.schedule(event_handler)

    return observer, event_handler

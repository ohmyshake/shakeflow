import os
import glob
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class FileHandler(FileSystemEventHandler):
    def __init__(self, files, suffix):
        self.suffix = suffix
        self.files = files

    def on_created(self, event):
        if event.is_directory:
            pass
        elif event.src_path.endswith(self.suffix):
            self.files.append(event.src_path)
        else:
            pass


def file_monitor(path, mode="from_origin", suffix=".h5"):
    """
    Start monitoring the specified path.

    Parameters
    ----------
    path : str
        The path to be monitored.
    mode : str
        "from_origin" or "from_now"
    suffix : str
        The suffix of the files to be monitored.
    logger : logging.Logger
        The logger to record the events.

    """
    if mode == "from_origin":
        files = sorted(
            glob.glob(
                os.path.join(path, f"**/*{suffix}"),
                recursive=True,
            )
        )
    elif mode == "from_now":
        files = []
    else:
        raise ValueError("mode must be 'from_origin' or 'from_now'")

    event_handler = FileHandler(files, suffix)
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)

    return observer, event_handler

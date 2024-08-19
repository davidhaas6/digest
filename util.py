import threading
from tqdm import tqdm
import time
from typing import Callable


def progress_bar(estimated_time: float, stop_event: threading.Event) -> None:
    """
    Display a progress bar based on estimated time.
    
    :param estimated_time: Estimated time for the operation in seconds
    :param stop_event: Threading event to signal when to stop the progress bar
    """
    with tqdm(total=100, unit="%") as pbar:
        start_time = time.time()
        while not stop_event.is_set():
            elapsed = time.time() - start_time
            progress = int((elapsed / estimated_time) * 100)
            pbar.n = progress
            pbar.refresh()
            time.sleep(0.1)
        # pbar.n = 100
        pbar.refresh()


def run_with_progress(func: Callable, estimated_time: float, *args, **kwargs):
    """
    Run a function with a progress bar.
    
    :param func: Function to run
    :param estimated_time: Estimated time for the function to complete
    :param args: Positional arguments for the function
    :param kwargs: Keyword arguments for the function
    :return: Result of the function
    """
    stop_event = threading.Event()
    progress_thread = threading.Thread(target=progress_bar, args=(estimated_time, stop_event))
    progress_thread.start()

    try:
        result = func(*args, **kwargs)
    finally:
        stop_event.set()
        progress_thread.join()

    return result


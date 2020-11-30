import logging
import subprocess as sp
import threading
from pathlib import Path
from queue import Queue, Empty
from typing import Union, Optional


class RunProcess(threading.Thread):
    result_timeout = 10

    def __init__(self, arguments: Union[list, str], cwd: Optional[Path] = None,
                 kill_process_event: Optional[threading.Event] = None, global_stdout_queue: Optional[Queue] = None):
        """ Run a process with given args from this thread
            Log process output in another thread and eventually wait for kill event to abort the process.

        :param arguments: Arguments for Popen
        :param cwd: Current working directory
        :param kill_process_event: Event to kill a running process
        :param global_stdout_queue: optional Queue to receive stdout, stderr output
        """
        super(RunProcess, self).__init__()
        self.args = arguments
        self.cwd = cwd
        self.kill_process_event = kill_process_event or threading.Event()

        self.log_thread = None
        self.result_queue = Queue()
        self.global_stdout_queue = global_stdout_queue
        self.event = threading.Event()

    def run(self):
        self._start_process()

        # Wait until process finished or aborted
        self.event.wait()
        self.event.clear()

        try:
            process_exitcode = self.result_queue.get(timeout=self.result_timeout)
        except Empty as e:
            logging.error('Did not receive process result/exitcode: %s', e)
            return

        if process_exitcode != 0:
            logging.error('Process result failed: %s', process_exitcode)
            return

    def _start_process(self):
        # Log STDOUT in own thread to keep parent thread ready for abort signals
        self.log_thread = threading.Thread(target=self._process_loop,
                                           args=(self.args, self.cwd, self.event,
                                                 self.kill_process_event, self.result_queue, self.global_stdout_queue))
        self.log_thread.start()

    @staticmethod
    def _process_loop(args: Union[list, str], cwd: Optional[Path],
                      event: threading.Event, kill_event: threading.Event, result_queue: Queue,
                      global_queue: Optional[Queue]):
        """ Reads and writes process stdout to log until process ends """
        try:
            process = sp.Popen(args, stdout=sp.PIPE, stderr=sp.STDOUT, stdin=sp.PIPE, cwd=cwd)
        except Exception as e:
            logging.error('Error starting process: %s', e)
            event.set()
            return

        # --- Read Stdout output non-blocking in another thread
        stdout_queue = Queue()
        read_stdout_non_blocking = threading.Thread(target=RunProcess.log_subprocess_output,
                                                    args=(process, stdout_queue, event)
                                                    )
        read_stdout_non_blocking.start()
        while True:
            # Loop thru stdout readline
            try:
                stdout_line = stdout_queue.get(timeout=1)
            except Empty:
                pass
            else:
                if global_queue:
                    global_queue.put(stdout_line)
                logging.info(stdout_line)

            # Process ended
            if event.is_set():
                break

            # Kill event received
            if kill_event.is_set():
                logging.info('Terminating process.')
                process.terminate()
                break

        # --- Wait for process to close stdout, stdin pipes
        try:
            logging.info('Process stdout stream ended. Fetching exitcode.')
            out, err = process.communicate(timeout=RunProcess.result_timeout)
        except sp.TimeoutExpired as e:
            logging.error('Error waiting for process to finish: %s', e)

            # Forcefully end non-reacting process
            try:
                logging.info('Attempting to forcefully kill process.')
                process.kill()
                logging.info('Process successfully killed.')
            except Exception as e:
                logging.error(e)

        # --- Read and transmit return code
        logging.info('Process ended with exitcode %s', process.returncode)
        result_queue.put(process.returncode)

        # --- Wake up RunProcess thread
        event.set()

    @staticmethod
    def log_subprocess_output(process, queue, event):
        """ Redirect subprocess output to logging so it appears in console and log file """
        try:
            for line in iter(process.stdout.readline, b''):
                try:
                    line = line.decode(encoding='utf-8')
                    line = line.replace('\n', '')
                except Exception as e:
                    logging.error('Error decoding process output: %s', e)

                if line:
                    queue.put(line)
        except Exception as e:
            logging.error('Error reading stdout: %s', e)

        # Process stdout closed
        event.set()

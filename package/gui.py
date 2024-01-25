"""
Implements a GUI for running the HERON and RAVEN main scripts using tkinter.
"""

import sys
import os
import subprocess
import threading
import time
import datetime
from collections.abc import Callable
from typing import Optional, List

import tkinter as tk
from tkinter import filedialog
from tkinter.messagebox import askokcancel
from tkinter.scrolledtext import ScrolledText


def threadify(func: Callable, daemon: bool = True) -> Callable:
    """
    Wrap a function in a thread.
    @In, func, Callable, the function to wrap
    @Out, wrapper, Callable, the wrapped function
    """
    def wrapper() -> None:
        """
        Run the function in a thread.
        @In, None
        @Out, None
        """
        thread = threading.Thread(target=func)
        thread.daemon = daemon
        thread.start()
    return wrapper


class BasicGUI:
    """ A basic graphical user interface for running FORCE tools. """
    def __init__(self, title: str) -> None:
        """
        Constructor. Builds the GUI.
        @In, title, str, the title of the GUI window
        @Out, None
        """
        # Default window size for different states
        self._window_size_no_output   = '300x100'
        self._window_size_with_output = '550x400'

        # Root window
        self._root = tk.Tk()
        self._root.title(title)
        self._root.geometry(self._window_size_no_output)
        self._root.resizable(width=True, height=True)

        # The window is divided into three frames:
        #   1. File selection
        #   2. Status panel
        #   2. Output text
        #   3. "Show/Hide Output", "Run" and "Cancel" buttons
        self._file_frame = tk.Frame(self._root, height=20)
        self._file_frame.grid(column=0, row=0, sticky=tk.NW)
        status_frame = tk.Frame(self._root, height=40)
        status_frame.grid(column=0, row=1, sticky=tk.NW)
        output_frame = tk.Frame(self._root)
        output_frame.grid(column=0, row=2, sticky=tk.NW)
        buttons_frame = tk.Frame(self._root, height=20)
        buttons_frame.grid(column=0, row=3, sticky=tk.NSEW)
        self._root.grid_columnconfigure(0, weight=1)
        self._root.grid_rowconfigure(2, weight=1)

        # File selection
        self._file_arg = None
        self._file_button = tk.Button(self._file_frame, text='Select File', command=self.get_file_to_run)
        self._file_button.grid(column=0, row=0, sticky=tk.W)
        file_label = tk.Label(self._file_frame, text='File:')
        file_label.grid(column=1, row=0, sticky=tk.W)
        self._file_to_run_label = tk.Label(self._file_frame, text=self._file_arg)
        self._file_to_run_label.grid(column=2, row=0, sticky=tk.W)

        # Status panel
        self._status_label = tk.Label(status_frame, text='Status: No file selected.')
        self._status_label.grid(column=0, row=0, sticky=tk.W)
        self._time_elapsed_label = tk.Label(status_frame, text='Time elapsed:')
        self._time_elapsed_label.grid(column=0, row=1, sticky=tk.W)

        # Script output
        # Text widget for showing script output, hidden by default
        self._text = ScrolledText(output_frame, wrap='char')
        self._text.configure(state=tk.DISABLED)
        self._text.pack_forget()

        # Buttons for showing and hiding the text widget, running the script, and canceling the run
        self._show_output = tk.Button(buttons_frame, text='Show Output', command=self._show_text)
        self._show_output.grid(column=0, row=0, sticky=tk.SW)
        self._cancel_pressed = False
        self._cancel_button = tk.Button(buttons_frame, text='Cancel', command=self._ask_cancel)
        self._cancel_button.grid(column=1, row=0, sticky=tk.SE)
        self._run_button = tk.Button(buttons_frame, text='Run', state=tk.DISABLED)
        self._run_button.grid(column=2, row=0, sticky=tk.SE)
        buttons_frame.grid_rowconfigure(0, weight=1)
        buttons_frame.grid_columnconfigure(0, weight=1)

        # Bind Ctrl+C to the cancel button for convenience
        self._root.bind('<Control-c>', lambda event: self._cancel_button.invoke())

    def _show_text(self) -> None:
        """
        Show the text widget and scrollbar.
        @In, None
        @Out, None
        """
        self._show_output.configure(text='Hide Output', command=self._hide_text)
        self._text.pack(fill=tk.BOTH, expand=tk.YES)
        self._root.geometry(self._window_size_with_output)

    def _hide_text(self) -> None:
        """
        Hide the text widget and scrollbar.
        @In, None
        @Out, None
        """
        self._show_output.configure(text='Show Output', command=self._show_text)
        self._text.pack_forget()
        self._root.geometry(self._window_size_no_output)

    def _ask_cancel(self) -> None:
        """
        Cancel the run by killing the subprocess.
        @In, None
        @Out, None
        """
        response = askokcancel('Cancel', 'Are you sure you want to terminate the running script?')
        if response:
            self._cancel_pressed = True

    def get_file_to_run(self) -> str:
        """
        Get a file to run using a file dialog.
        @In, None
        @Out, None
        """
        filename = filedialog.askopenfilename(title='Select File to Run', filetypes=[('XML files', '*.xml')])
        if filename == '':  # user canceled
            return

        self._file_arg = filename
        self._file_to_run_label.configure(text=os.path.relpath(self._file_arg))
        self._run_button.configure(state=tk.NORMAL)
        self._update_status(status='Ready')

    def _update_status(self, status: Optional[str] = None, time_elapsed: Optional[float] = None) -> None:
        """
        Update the status panel.
        @In, status, str, the status to display
        @In, time_elapsed, str, the time elapsed to display
        @Out, None
        """
        if status is not None:
            self._status_label.configure(text='Status: ' + status)
        if time_elapsed is not None:
            time_elapsed = datetime.timedelta(seconds=round(time_elapsed))
            self._time_elapsed_label.configure(text='Time elapsed: ' + str(time_elapsed))

    def write(self, text: str) -> None:
        """
        Add text to the text widget.
        @In, text, str, the line to write
        @Out, None
        """
        for line in text:
            self._text.configure(state=tk.NORMAL)
            self._text.insert(tk.END, line)
            self._text.update()
            self._text.see(tk.END)  # autoscroll
            self._text.configure(state=tk.DISABLED)

    def write_line(self, line: str) -> None:
        """
        Add a line to the text widget.
        @In, line, str, the line to write
        @Out, None
        """
        self._text.configure(state=tk.NORMAL)
        self._text.insert(tk.END, line)
        self._text.see(tk.END)
        self._text.configure(state=tk.DISABLED)
        self._text.update()

    def _build_script_command(self, filename: str) -> List[str]:
        """
        Build the command to run a python script.
        @In, filename, str, the filename to run
        @Out, cmd, list[str], the command to run the script
        """
        if filename.endswith('.py') or filename.endswith('.pyc'):
            cmd = ['python', '-u', filename]
        elif filename.endswith('.exe'):
            cmd = [filename]
        elif filename.endswith('.sh'):
            cmd = ['bash', filename]
        else:
            raise ValueError(f'File {filename} has an unrecognized extension. Must be .py, .exe, or .sh.')
        if self._file_arg is not None:
            cmd.append(self._file_arg)
        return cmd

    def run_script(self, filename: str, requires_input: bool = True) -> None:
        """
        Run a python script in the GUI.
        @In, filename, str, the filename to run
        @In, requires_input, bool, optional, if True the script requires an input file
        @Out, None
        """
        if not os.path.exists(filename):
            raise FileNotFoundError(f'File {filename} does not exist.')

        # If the script doesn't require an input file, it can be run immediately.
        # In this case, hide the file selection elements.
        if not requires_input:
            self._update_status(status='Ready')
            self._run_button.configure(state=tk.NORMAL)
            self._file_frame.grid_forget()  # hide file selection frame

        # Wrap the script in a function that will run it in a subprocess. Also handles
        # routing script output to the GUI. Then, if we wrap all of this in a thread,
        # we can run the script while keeping the GUI responsive.
        @threadify
        def _run_script() -> None:
            """
            Run the script in filename as a subprocess.
            @In, filename, str, the filename to run
            @Out, None
            """
            self._cancel_pressed = False  # reset cancel button

            # Construct python command to run the script. Assumes that the script takes
            # an XML file as a positional argument. The -u flag is necessary to disable
            # output buffering, allowing the output to be written to the text widget in
            # real time.
            # cmd = ['python', '-u', filename, self._file_arg]
            cmd = self._build_script_command(filename)

            # Update status bar and clear text widget
            self._update_status(status='Running', time_elapsed=0.0)
            start_time = time.time()
            self._text.configure(state=tk.NORMAL)
            self._text.delete('1.0', tk.END)
            self._text.configure(state=tk.DISABLED)

            # Run the script as a subprocess so that the GUI does not freeze while
            # waiting for the script to finish.
            exit_status = 'Done'  # default exit status
            with subprocess.Popen(cmd,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT,
                                bufsize=1,
                                universal_newlines=True) as p:
                # Disable the run button while the script is running and enable the cancel button
                self._run_button.configure(state=tk.DISABLED)
                self._cancel_button.configure(state=tk.NORMAL)
                # Grab the output from the subprocess and write it to the text widget
                for line in p.stdout:
                    self.write_line(line)
                    self._update_status(time_elapsed=time.time() - start_time)
                    # Quit if the cancel button was pressed
                    if self._cancel_pressed:
                        p.terminate()
                        self.write_line('Subprocess terminated.\n')
                        exit_status = 'Halted'
                        break
                if p.poll():
                    exit_status = f'Error ({p.poll()})'
            # Re-enable run button when the script is done
            self._update_status(status=exit_status, time_elapsed=time.time() - start_time)
            self._run_button.configure(state=tk.NORMAL)

        # Set the run button command to run the function
        self._run_button.configure(command=_run_script)

        # Run the GUI
        self._root.mainloop()


# Some test code
if __name__ == '__main__':
    gui = BasicGUI('Test GUI')
    gui.run_script('gui_test_func.py', requires_input=False)

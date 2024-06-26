#!/usr/bin/env python3

import argparse
import datetime
import json
import signal
import sys
import select
import shlex
import subprocess

def handle_sig_hup(_, __):
    """
    Closes the global log file and sets it to None when a SIGHUP signal is received.

    Parameters:
    - _: a placeholder for the first signal parameter (unused)
    - __: a placeholder for the second signal parameter (unused)

    Returns:
    None
    """
    global log_file
    log_file.close()
    log_file = None

def get_args():
    """
    Parses command line arguments and returns the parsed arguments.

    :return: The parsed command line arguments.
    """
    parser = argparse.ArgumentParser(description='Convert Caddy logs to CLF')
    parser.add_argument('-o', '--output-file',
                        help='Output filename')
    parser.add_argument('-i', '--input-pipe',
                        help='Input pipe (default=STDIN)')
    return parser.parse_args()

def process_pipe(command, output_file):
    """
    Opens a pipe to a command and calls process_logs with the stdout of the
    command as an argument.

    :param command: The command to execute.
    :param output_file: The filename to output the CLF to
    """
    with subprocess.Popen(shlex.split(command),
                          stdout=subprocess.PIPE) as input_pipe:
        process_logs(input_pipe.stdout, output_file)

def format_line(logdata):
    """
    Formats a log line into a string in Common Log Format.

    :param logdata: A dictionary containing the log data.
    :type logdata: dict
    :return: A string representing the log line in Common Log Format.
    :rtype: str
    """
    request = '"%s %s %s"' % (logdata['request']['method'], logdata['request']['uri'],
                              logdata['request']['proto'])
    logfields = (logdata['request']['remote_ip'], '-', logdata['user_id'],
                 datetime.datetime.fromtimestamp(logdata['ts']).strftime("%d/%b/%Y:%H:%M:%S %z"),
                 request, str(logdata['status']), str(logdata['size']))
    return ' '.join(('-' if field == '' else field) for field in logfields)

def process_logs(input_pipe, output_file):
    """
    Process logs from an input pipe and write them to an output file.

    :param input_pipe: The input pipe to read logs from.
    :type input_pipe: file object
    :param output_file: The output file to write logs to (if None use stdout)
    :type output_file: str
    """
    global log_file
    log_file = None
    if output_file:
        log_file = open(output_file, "a")
    reading_log = True
    while reading_log:
        if log_file is None and output_file is not None:
            log_file = open(output_file, "a")
        while input_pipe in select.select([input_pipe], [], [], 0)[0]:
            line = input_pipe.readline()
            if input_pipe is not sys.stdin:
                line = line.decode("utf-8")
            if line == '':
                reading_log = False
                break
            elif line[0] != '{':
                continue
            try:
                logdata = json.loads(line)
            except json.decoder.JSONDecodeError:
                continue
            logline = format_line(logdata)
            if log_file is not None:
                log_file.write("%s\n" % logline)
            else:
                print(logline)
    if log_file is not None:
        log_file.close()

def main():
    """
    The main function that serves as the entry point of the program.

    This function performs the following steps:
    1. Sets up a signal handler for the SIGHUP signal by calling the `handle_sig_hup` function.
    2. Parses the command line arguments by calling the `get_args` function and stores the result in the `args` variable.
    3. Checks if the `input_pipe` argument is `None`. If it is `None`, assigns `sys.stdin` to the `input_pipe` variable. Otherwise, calls the `open_pipe` function with the `args.input_pipe` argument and assigns the result to the `input_pipe` variable.
    4. Calls the `process_logs` function with the `input_pipe` and `args.output_file` arguments.

    This function does not have any parameters.

    This function does not return any values.
    """
    signal.signal(signal.SIGHUP, handle_sig_hup)
    args = get_args()
    if args.input_pipe is None:
        process_logs(sys.stdin, args.output_file)
    else:
        process_pipe(args.input_pipe, args.output_file)
        # with subprocess.Popen(shlex.split(args.input_pipe),
        #                     stdout=subprocess.PIPE) as input_pipe:
        #   process_logs(input_pipe.stdout, args.output_file)

if __name__ == '__main__':
    main()


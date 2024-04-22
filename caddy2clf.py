#!/bin/env python3

# caddy2clf - convert caddy json web logs to Common Log Format
# CLF: host ident authuser date request status bytes

import argparse
import datetime
import json
import signal
import sys
import select
import shlex
import subprocess
import time
import typing

hup_received = False

def handler(signum, _) -> None:
	'''handle HUP signals'''
	global hup_received
	signame = signal.Signals(signum).name
	print(f'Signal handler called with signal {signame} ({signum})')
	hup_received = True


def getargs() -> argparse.Namespace:
    '''get CLI args'''
    parser = argparse.ArgumentParser(description='Convert Caddy logs to CLF')
    parser.add_argument('-o', '--outputfilename', help='Output filename')
    parser.add_argument('-i', '--inputpipe', help='Input pipe (default = STDIN)')
    return parser.parse_args()


def open_pipe(cmdline: str) -> typing.TextIO:
	'''return pipe to passed cmdline'''
	cmdargs = shlex.split(cmdline)
	ps = subprocess.Popen(cmdargs, stdout=subprocess.PIPE)
	return ps.stdout


def hyphen_if_empty(field: str) -> str:
	"""replace empty string with hyphen"""
	if field == '':
		return '-'
	return field


def epoch_to_strftime(epoch_time: float) -> str:
	log_ts = datetime.datetime.fromtimestamp(epoch_time)
	return log_ts.strftime("%d/%b/%Y:%H:%M:%S %z")


def buildline(logdata: dict) -> str:
	'''convert caddy dict to CLF str'''
	request = '"%s %s %s"' % (logdata['request']['method'], logdata['request']['uri'],
							  logdata['request']['proto'])
	# set ident to -
	logfields = (logdata['request']['client_ip'], '-', logdata['user_id'],
				 epoch_to_strftime(logdata['ts']),
				 request, str(logdata['status']), str(logdata['size']))
	logfields = (hyphen_if_empty(field) for field in logfields)
	logline = ' '.join(logfields)
	return logline


def process_logs(inputpipe: typing.TextIO, outfilename: str) -> None:
	"""process stdin caddy json logs"""
	global hup_received
	outfile = None
	reading_log = True
	while reading_log:
		if outfilename and outfile is None:
			outfile = open(outfilename, "a")
		while inputpipe in select.select([inputpipe], [], [], 0)[0]:
			line = inputpipe.readline()
			if inputpipe is not sys.stdin:
				line = line.decode("utf-8")
			if line == '':
				# stdin closed, exit
				reading_log = False
				break
			elif line[0] != '{':
				# not caddy JSON, skip
				continue
			try:
				logdata = json.loads(line)
			except json.decoder.JSONDecodeError:
				continue
			logline = buildline(logdata)
			if outfile is not None:
				outfile.write("%s\n" % logline)
			else:
				print(logline)
			if hup_received:
				if outfile is not None:
					# print('closing %s' % outfilename)  # DEBUG
					outfile.close()
					outfile = None
					hup_received = False
				break
		else:
			# waiting on data, sleep & try again
			time.sleep(1)
			# print('something else')   # DEBUG


def main():
	signal.signal(signal.SIGHUP, handler)
	args = getargs()
	if args.inputpipe is None:
		inputpipe = sys.stdin
	else:
		inputpipe = open_pipe(args.inputpipe)
	process_logs(inputpipe, args.outputfilename)


if __name__ == '__main__':
    main()

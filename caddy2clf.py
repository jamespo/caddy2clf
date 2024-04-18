#!/bin/env python3

# caddy2clf - convert caddy json web logs to Common Log Format
# CLF: host ident authuser date request status bytes

import datetime
import json
import signal
import sys
import select
import time

reading_log = True

def handler(signum, frame):
	global reading_log
	signame = signal.Signals(signum).name
	print(f'Signal handler called with signal {signame} ({signum})')
	reading_log = False


def hyphen_if_empty(field):
	"""replace empty string with hyphen"""
	if field == '':
		return '-'
	return field


def epoch_to_strftime(epoch_time):
	log_ts = datetime.datetime.fromtimestamp(epoch_time)
	return log_ts.strftime("%d/%b/%Y:%H:%M:%S %z")


def buildline(logdata):
	request = '"%s %s %s"' % (logdata['request']['method'], logdata['request']['uri'], logdata['request']['proto'])
	# set ident to -
	logfields = (logdata['request']['client_ip'], '-', logdata['user_id'], epoch_to_strftime(logdata['ts']),
				 request, str(logdata['status']), str(logdata['size']))
	logfields = (hyphen_if_empty(field) for field in logfields)
	logline = ' '.join(logfields)
	return logline


def process_logs(outfilename: str):
	"""process stdin caddy json logs"""
	global reading_log
	outfile = None
	while reading_log:
		if outfilename and outfile is None:
			outfile = open(outfilename, "a")
		while sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
			line = sys.stdin.readline()
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
			if not reading_log:
				# HUP received
				break
		else:
			# waiting on data, sleep & try again
			time.sleep(1)
			print('something else')   # DEBUG
			if not reading_log and outfile is not None:
				# close output file
				print('closing %s' % outfilename)  # DEBUG
				outfile.close()
				outfile = None


def main():
	signal.signal(signal.SIGHUP, handler)
	try:
		outfilename = sys.argv[1]
	except IndexError:
		outfilename = None
	process_logs(outfilename)


if __name__ == '__main__':
    main()

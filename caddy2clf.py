#!/bin/env python3

# caddy2clf - convert caddy json web logs to Common Log Format
# CLF: host ident authuser date request status bytes

import datetime
import json
import sys


def hyphen_if_empty(field):
	"""replace empty string with hyphen"""
	if field == '':
		return '-'
	return field

def epoch_to_strftime(epoch_time):
	log_ts = datetime.datetime.fromtimestamp(epoch_time)
	return log_ts.strftime("%d/%b/%Y:%H:%M:%S %z")

def main():
	"""process stdin caddy json logs"""
	for line in sys.stdin.readlines():
		if line[0] != '{':
			continue
		try:
			logdata = json.loads(line)
		except json.decoder.JSONDecodeError:
			continue
		request = '"%s %s %s"' % (logdata['request']['method'], logdata['request']['uri'], logdata['request']['proto'])
		# set ident to -
		logfields = (logdata['request']['client_ip'], '-', logdata['user_id'], epoch_to_strftime(logdata['ts']),
					 request, str(logdata['status']), str(logdata['size']))
		logfields = (hyphen_if_empty(field) for field in logfields)
		print(' '.join(logfields))


if __name__ == '__main__':
    main()

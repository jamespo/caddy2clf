caddy2clf
=========

Convert Caddy webserver JSON log files to Common Log Format 

Usage
=====

    tail -100 logs/access.log | caddy2clf.py
    tail -100 logs/access.log | caddy2clf.py -o '/var/logs/caddy2clf/caddy.clf'
    tail -f logs/access.log | caddy2clf.py
    tail -F logs/access1.log logs/access2.log logs/access3.log | caddy2clf.py
    caddy2clf.py -i 'tail -f caddy.log' -o '/var/logs/caddy2clf/caddy.clf'


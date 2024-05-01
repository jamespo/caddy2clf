#!/bin/env python3

import tempfile
import unittest
from unittest.mock import patch, mock_open
from io import StringIO
from caddy2clf import process_logs, open_pipe, format_line
import os

class TestCaddy2Clf(unittest.TestCase):

    def setUp(self):
        self.outfile = tempfile.NamedTemporaryFile(mode='w', delete=False)
        self.outfile.close()
        self.infile = tempfile.NamedTemporaryFile(mode='w', delete=False)
        self.infile.write('{"level":"info","ts":1713985562.6151454,"logger":"http.log.access.log0","msg":"handled request","request":{"remote_ip":"120.77.35.242","remote_port":"50538","client_ip":"120.77.35.242","proto":"HTTP/1.1","method":"GET","host":"armyman.fancydan.co.uk","uri":"/wp-login.php","headers":{"User-Agent":["Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:94.0) Gecko/20100101 Firefox/95.0"],"Accept-Encoding":["gzip"],"Connection":["close"]}},"bytes_read":0,"user_id":"","duration":0.0000418,"size":0,"status":308,"resp_headers":{"Server":["Caddy"],"Connection":["close"],"Location":["https://www.bbc.co.uk/"],"Content-Type":[]}}\n')
        self.infile.close()

    def tearDown(self):
        #self.outfile.close()
        #self.infile.close()
        try:
            os.remove(self.outfile.name)
            os.remove(self.infile.name)
        except:
            pass

    def test_process_logs_pipe(self):
        input_pipe = open_pipe('cat %s' % self.infile.name)
        process_logs(input_pipe.stdout, self.outfile.name)
                        

if __name__ == '__main__':
    unittest.main()

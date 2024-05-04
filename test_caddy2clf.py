#!/bin/env python3

import tempfile
import unittest
from unittest.mock import patch
from io import StringIO
from caddy2clf import process_pipe
import os

class TestCaddy2Clf(unittest.TestCase):

    def setUp(self):
        self.infile = tempfile.NamedTemporaryFile(mode='w', delete=False)
        self.infile.write('{"level":"info","ts":1713985562.6151454,"logger":"http.log.access.log0","msg":"handled request","request":{"remote_ip":"120.77.35.242","remote_port":"50538","client_ip":"120.77.35.242","proto":"HTTP/1.1","method":"GET","host":"www.bbc.co.uk","uri":"/wp-login.php","headers":{"User-Agent":["Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:94.0) Gecko/20100101 Firefox/95.0"],"Accept-Encoding":["gzip"],"Connection":["close"]}},"bytes_read":0,"user_id":"","duration":0.0000418,"size":0,"status":308,"resp_headers":{"Server":["Caddy"],"Connection":["close"],"Location":["https://www.bbc.co.uk/"],"Content-Type":[]}}\n')
        self.infile.close()

    def tearDown(self):
        try:
            os.remove(self.infile.name)
        except:
            pass

    @patch('sys.stdout', new_callable=StringIO)
    def test_process_logs_pipe(self, mock_stdout):
        process_pipe('cat %s' % self.infile.name, None)
        self.assertEqual(mock_stdout.getvalue(), '120.77.35.242 - - 24/Apr/2024:20:06:02  "GET /wp-login.php HTTP/1.1" 308 0\n')



if __name__ == '__main__':
    unittest.main()

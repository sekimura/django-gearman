# -*- encoding: utf-8 -*-
import os, sys, time, signal

from gearman import GearmanClient, Task

from django.core.management import call_command
from django.conf import settings
from django.test import TestCase

class DjangoGearmanTestCase(TestCase):
    """
    Test case
    """
    server_pid = 0
    worker_pid = 0
    def start_server(self, port=9050):
        loc = [
            '/usr/bin/gearmand',
            '/usr/sbin/gearmand',
        ]
        server_path = [x for x in loc if os.path.exists(x)][0]

        pid = os.fork()
        if pid:
            self.server_pid = pid
        else:
            os.system(" ".join([server_path, '--port=%d' % port]))
            os._exit(0)
        return pid

    def setUp(self, **kwargs):
        self.start_server()
        pid = os.fork()
        if pid:
            self.worker_pid = pid
        else:
            call_command('gearman_worker')
            os._exit(0)

    def tearDown(self, **kwargs):
        os.kill(self.server_pid, signal.SIGTERM)
        os.kill(self.worker_pid, signal.SIGTERM)

    def test_reverse(self, **kwargs):
        client = GearmanClient(settings.GEARMAN_SERVERS)
        sentence = 'The quick brown fox jumps over the lazy dog'
        res = client.do_task(Task("testapp.reverse", sentence))
        self.assertEqual(res, 'god yzal eht revo spmuj xof nworb kciuq ehT')

    def test_background_counting(self, **kwargs):
        client = GearmanClient(settings.GEARMAN_SERVERS)
        res = client.do_task(Task("testapp.background_counting", None))
        self.assertFalse(res)


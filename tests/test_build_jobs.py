#!/usr/bin/env python3
import os
import sys
import unittest
from unittest.mock import patch

# Add repository root to sys.path to import build.py
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import build


class TestBuildJobs(unittest.TestCase):

    def test_get_total_ram_gb(self):
        ram_gb = build.get_total_ram_gb()
        if ram_gb is not None:
            self.assertIsInstance(ram_gb, float)
            self.assertGreater(ram_gb, 0)

    @patch('multiprocessing.cpu_count', return_value=16)
    @patch('build.get_total_ram_gb', return_value=8.0)
    def test_get_default_jobs_capped_by_ram(self, mock_ram, mock_cpu):
        # 8 GB RAM with 2 GB per job -> max 4 jobs even with 16 CPUs
        jobs = build.get_default_jobs(ram_per_job_gb=2.0)
        self.assertEqual(jobs, 4)

    @patch('multiprocessing.cpu_count', return_value=4)
    @patch('build.get_total_ram_gb', return_value=16.0)
    def test_get_default_jobs_capped_by_cpu(self, mock_ram, mock_cpu):
        # 16 GB RAM with 2 GB per job allows 8 jobs, but only 4 CPUs exist
        jobs = build.get_default_jobs(ram_per_job_gb=2.0)
        self.assertEqual(jobs, 4)

    @patch('multiprocessing.cpu_count', return_value=16)
    @patch('build.get_total_ram_gb', return_value=1.0)
    def test_get_default_jobs_minimum_one(self, mock_ram, mock_cpu):
        # Low RAM should still return at least 1 job
        jobs = build.get_default_jobs(ram_per_job_gb=2.0)
        self.assertEqual(jobs, 1)

    def test_parse_args_jobs_option(self):
        with patch.object(sys, 'argv', ['build.py', '--install', '-j', '2']):
            args = build.parse_args()
            self.assertEqual(args.jobs, 2)

        with patch.object(sys, 'argv', ['build.py', '--install', '--jobs', '3']):
            args = build.parse_args()
            self.assertEqual(args.jobs, 3)

        with patch.object(sys, 'argv', ['build.py', '--install', '-p', '1']):
            args = build.parse_args()
            self.assertEqual(args.jobs, 1)


if __name__ == '__main__':
    unittest.main()

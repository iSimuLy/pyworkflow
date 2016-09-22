"""
py_scheduler.py: Controls the job submission and result transfer
"""


import subprocess as sub


class Scheduler:

    def __init__(self):
        self.job_queue = []

    def add_job(self, job):
        self.job_queue.append(job)
        sub.Popen(job.run(), shell=True, stdout=sub.PIPE)

    def check_job_status(self, job):
        pass
# end Scheduler

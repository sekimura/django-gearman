from django.conf import settings
from gearman import GearmanClient, GearmanWorker, Task, Taskset


class DjangoGearmanClient(GearmanClient):
    """gearman client, automatically connecting to server"""

    def __call__(self, func, arg, uniq=None, **kwargs):
        raise NotImplementedError('Use do_task() or dispatch_background'\
                                  '_task() instead')

    def __init__(self, **kwargs):
        """instantiate Gearman client with servers from settings file"""
        return super(DjangoGearmanClient, self).__init__(
                settings.GEARMAN_SERVERS, **kwargs)

    def dispatch_background_task(self, func, arg, uniq=None, high_priority=False):
        """Submit a background task and return its handle."""
        task = DjangoGearmanTask(func, arg, uniq=uniq, background=True,
                                 high_priority=high_priority)
        taskset = Taskset([task])
        self.do_taskset(taskset)
        return task.handle

class DjangoGearmanWorker(GearmanWorker):
    """
    gearman worker, automatically connecting to server and discovering
    available jobs
    """

    def __init__(self, **kwargs):
        """instantiate Gearman worker with servers from settings file"""
        return super(DjangoGearmanWorker, self).__init__(
                settings.GEARMAN_SERVERS, **kwargs)

class DjangoGearmanTask(Task):
    """Gearman Task, namespacing jobs according to config file"""

    def __init__(self, func, arg, **kwargs):
        # get app and job name from function call, namespace as configured,
        # then execute
        parts = func.partition('.')
        if parts[2]:
            app = parts[0]
            job = parts[2]
        else:
            app = ''
            job = parts[0]

        try:
            func = settings.GEARMAN_JOB_NAME % {'app': app, 'job': job}
        except NameError:
            pass

        return super(DjangoGearmanTask, self).__init__(func, arg, **kwargs)


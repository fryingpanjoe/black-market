from random import uniform


class Timer(object):
    def __init__(self, duration, do_reset=True):
        if isinstance(duration, (list, tuple)):
            self.min_duration = duration[0]
            self.max_duration = duration[1]
        else:
            self.min_duration = duration
            self.max_duration = None

        self.time_left = 0

        if do_reset:
            self.reset()

    def update(self, delta_time):
        self.time_left -= delta_time

    def is_expired(self):
        return self.time_left <= 0

    def reset(self, time_left=None):
        if time_left:
            self.time_left = time_left
        else:
            if self.max_duration:
                self.time_left = uniform(self.min_duration, self.max_duration)
            else:
                self.time_left = self.min_duration

    def fforward(self):
        self.time_left = 0


class Scheduler(object):
    def __init__(self):
        self.jobs = []

    def post(self, func, duration):
        self.jobs.append((Timer(duration), func, False))

    def periodic(self, func, duration):
        self.jobs.append((Timer(duration, False), func, True))

    def update(self, delta_time):
        for (timer, func, is_periodic) in self.jobs:
            timer.update(delta_time)
            if timer.is_expired():
                timer.reset()
                func()
                if not is_periodic:
                    self.jobs.remove((timer, func, is_periodic))

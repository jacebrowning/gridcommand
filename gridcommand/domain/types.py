import time


class Widget:

    def __init__(self, number, name):
        self.number = number
        self.name = name
        self.inspections = []

    def inspect(self, status=True):
        inspection = Inspection(status=status)
        self.inspections.append(inspection)
        return inspection


class Inspection:

    def __init__(self, status, stamp=None):
        self.status = status
        self.stamp = stamp or int(time.time())

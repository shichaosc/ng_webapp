class Occurrence(object):

    def __init__(self, event_id, start, end, student, status=0, class_type=None):
        self.event_id = event_id
        self.start = start
        self.end = end
        self.student = student  # 班长
        self.status = status
        self.class_type = class_type

    def __eq__(self, other):
        return self.event_id == other.event_id

    def __hash__(self):
        return hash(('event_id', self.event_id))

    def __str__(self):
        return 'event id: {} {} {} status{} student{}'.format(
            self.event_id, self.start, self.end, self.status, self.student)

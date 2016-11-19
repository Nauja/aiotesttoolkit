# Dict acting like a class
class ClassDict(dict):
    def __init__(self):
        super(ClassDict, self).__init__()
        
    def __getattr__(self, attr):
        return self[attr]
    
    def __setattr__(self, attr, value):
        self[attr] = value
        
# Get the last value of an iterable object
def last(values, default = None):
    result = default
    for result in values:
        pass
    return result

def discard(values):
    for _ in values:
        pass
    
def next_if_has_next(generator):
    try:
        next(generator)
        return True
    except StopIteration:
        return False
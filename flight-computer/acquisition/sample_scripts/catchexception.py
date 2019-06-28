import sys
import traceback

def catchex(method):
    def wrapper(*args, **kwargs):
        rc = -1
        try:
            rc = method(*args, **kwargs)
        except:
            print >> sys.stderr, traceback.format_exc()
        return rc
    return wrapper


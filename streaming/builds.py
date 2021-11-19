import datetime
import time

##################################################
# Streaming API
##################################################

def readline_streams(fp):
    """Stream the lines content of a filepath"""
    with open(fp) as fd:
        while True:
            line = fd.readline()
            if not line:
                return
            yield line

def to_stream(iterable):
    """Convert an iterable to stream

    >>> to_stream("Hello")
    <generator object to_stream at 0x7f7d011fe9e0>
    """
    for elem in iterable:
        yield elem

def drop(count, stream):
    """Drop the first count elements from a stream

    >>> list(drop(2, to_stream([1, 2, 3, 4])))
    [3, 4]
    """
    if count > 0:
        for elem in stream:
            count -= 1
            if count == 0:
                break
    return stream

def take(count, stream):
    """Take the first count elements from a stream

    >>> list(take(2, to_stream([1, 2, 3, 4])))
    [1, 2]
    """
    if count > 0:
        for elem in stream:
            yield elem
            count -= 1
            if count == 0:
                break

def head(stream):
    """Return the first element of a stream

    >>> head(to_stream("Hello"))
    'H'
    """
    for elem in stream:
        return elem

def chunks(count, stream):
    """Group stream elements

    >>> list(chunks(3, to_stream("Hello world")))
    [['H', 'e', 'l'], ['l', 'o', ' '], ['w', 'o', 'r'], ['l', 'd']]
    """
    while True:
        chunk = list(take(count, stream))
        if not chunk:
            break
        yield chunk


##################################################
# Example usage for the ci-log-processing
##################################################

def build_monotonic():
    """Generate a continuous list of builds:

    >>> list(take(3, build_monotonic()))
    ['2021-11-12', '2021-11-11', '2021-11-10']
    """
    now = datetime.datetime.now()
    age = 0
    while True:
        time.sleep(0.01)
        yield datetime.datetime.strftime(
            now + datetime.timedelta(days=-age),
            "%Y-%m-%d")
        age += 1

def get_builds_page(skip, limit):
    """A fake builds endpoint that takes a skip/limit argument

    >>> list(get_builds_page(3, 2))
    ['2021-11-09', '2021-11-08']
    """
    return take(limit, drop(skip, build_monotonic()))

def get_builds():
    """A helper function to scan the builds page

    >>> list(take(2, get_builds()))
    ['2021-11-12', '2021-11-11']
    """
    (pos, size) = (0, 10)
    known_build = set()
    while True:
        for build in get_builds_page(pos, size):
            if build not in known_build:
                yield build
            known_build.add(build)
        pos += size

def get_recent_builds(since):
    """A helper function to collect build until a previously known since date"""
    for build in get_builds():
        if build == since:
            break
        yield build

def get_logfiles(build):
    """TODO: fetch zuul-manifest then yield each logfile url"""
    yield ("%s log1" % build)
    yield ("%s log2" % build)

def get_loglines(logfile):
    """TODO: fetch url and yield each line"""
    for x in range(0, 200):
        yield ("%s content %d" % (logfile, x))

def get_recent_loglines(since):
    """The main logic to collect build logs"""
    for build in get_recent_builds(since):
        for logfile in get_logfiles(build):
            for logline in get_loglines(logfile):
                yield dict(build=build, logfile=logfile, logline=logline)

def index_log_lines(chunk):
    """TODO: bulk upload the loglines"""
    print("Indexing %d lines" % len(chunk))

def main():
    since = head(get_builds())
    # let's use an older that for demo purpose
    since = '2021-08-11'
    for lines in chunks(500, get_recent_loglines(since)):
        index_log_lines(lines)

#!/usr/bin/env python
# -*- coding: utf8 -*-

                         ##############################
                        #  ____    ___   ____  ______  #
                        # |    \  /  _] /    T|      T #
                        # |  o  )/  [_ Y  o  ||      | #
                        # |   _/Y    _]|     |l_j  l_j #
                        # |  |  |   [_ |  _  |  |  |   #
                        # |  |  |     T|  |  |  |  |   #
                        # l__j  l_____jl__j__j  l__j   #
                        #                              #
                         #####                    #####
                              # Repeat commands! #
                               ##################

import errno, os, subprocess, sys, time
from optparse import OptionParser


interval = 1.0
command = 'true'
clear = True
get_paths = lambda: set()
verbose = True
dynamic = False
paths_command = None

USAGE = """\
usage: %prog [options] COMMAND

COMMAND should be given as a single argument using a shell string.

A list of paths to watch should be piped in on standard input.

For example:

    find . | peat './test.sh'
    find . -name '*.py' | peat 'rm *.pyc'
    find . -name '*.py' -print0 | peat -0 'rm *.pyc'

If --dynamic is given, a command to generate the list should be piped in
on standard input instead.  It will be used to generate the list of files
to check before each run.

This command must be quoted properly, and this can be tricky.  Make sure
you know what you're doing.

For example:

    echo find . | peat --dynamic './test.sh'
    echo find . -name '*.py' | peat --dynamic 'rm *.pyc'
"""


def log(s):
    if verbose:
        print(s)

def die(s):
    sys.stderr.write('ERROR: ' + s + '\n')
    sys.exit(1)

def check(paths):
    cutoff = int(time.time() - interval)
    for p in paths:
        try:
            if os.stat(p).st_mtime >= cutoff:
                return True
        except OSError as e:
            # If the file has been deleted since we started watching, don't
            # worry about it.
            if e.errno == errno.ENOENT:
                pass
            else:
                raise
    return False

def run():
    log("running: " + command)
    subprocess.call(command, shell=True)

def build_option_parser():
    p = OptionParser(USAGE)

    # Main options
    p.add_option('-i', '--interval', default=None,
                 help='interval between checks in milliseconds',
                 metavar='N')
    p.add_option('-I', '--smart-interval', dest='interval',
                 action='store_const', const=None,
                 help='determine the interval based on number of files watched (default)')
    p.add_option('-d', '--dynamic', default=False,
                 action='store_true',
                 help='take a command on standard input to generate the list of files to watch')
    p.add_option('-D', '--no-dynamic', dest='dynamic',
                 action='store_false',
                 help='take a list of files to watch on standard in (default)')
    p.add_option('-c', '--clear', default=True,
                 action='store_true', dest='clear',
                 help='clear screen before runs (default)')
    p.add_option('-C', '--no-clear',
                 action='store_false', dest='clear',
                 help="don't clear screen before runs")
    p.add_option('-v', '--verbose', default=True,
                 action='store_true', dest='verbose',
                 help='show extra logging output (default)')
    p.add_option('-q', '--quiet',
                 action='store_false', dest='verbose',
                 help="don't show extra logging output")
    p.add_option('-w', '--whitespace', default=None,
                 action='store_const', dest='sep', const=None,
                 help="assume paths on stdin are separated by whitespace (default)")
    p.add_option('-n', '--newlines',
                 action='store_const', dest='sep', const='\n',
                 help="assume paths on stdin are separated by newlines")
    p.add_option('-s', '--spaces',
                 action='store_const', dest='sep', const=' ',
                 help="assume paths on stdin are separated by spaces")
    p.add_option('-0', '--zero',
                 action='store_const', dest='sep', const='\0',
                 help="assume paths on stdin are separated by null bytes")

    return p


def _main():
    if dynamic:
        log("Running the following command to generate watch list:")
        log('  ' + paths_command)
        log('')

    log("Watching the following paths:")
    for p in get_paths():
        log('  ' + p)
    log('')
    log('Checking for changes every %d milliseconds.' % int(interval * 1000))
    log('')

    run()

    while True:
        time.sleep(interval)
        if check(get_paths()):
            if clear:
                subprocess.check_call('clear')
            run()

def smart_interval(count):
    """Return the smart interval to use in milliseconds."""
    if count >= 50:
        return 1000
    else:
        sq = lambda n: n * n
        return int(1000 * (1 - (sq(50.0 - count) / sq(50))))

def _parse_interval(options):
    global get_paths
    if options.interval:
        i = int(options.interval)
    elif options.dynamic:
        i = 1000
    else:
        i = smart_interval(len(get_paths()))

    return i / 1000.0

def _parse_paths(sep, data):
    if not sep:
        paths = data.split()
    else:
        paths = data.split(sep)

    paths = [p.rstrip('\n') for p in paths if p]
    paths = map(os.path.abspath, paths)
    paths = set(paths)

    return paths

def main():
    global interval, command, clear, get_paths, verbose, dynamic, paths_command

    (options, args) = build_option_parser().parse_args()

    if len(args) != 1:
        die("exactly one command must be given")

    command = args[0]
    clear = options.clear
    verbose = options.verbose
    sep = options.sep
    dynamic = options.dynamic

    if dynamic:
        paths_command = sys.stdin.read().rstrip()

        if not paths_command:
            die("no command to generate watch list was given on standard input")

        def _get_paths():
            data = subprocess.check_output(paths_command, shell=True)
            return _parse_paths(sep, data)

        get_paths = _get_paths
    else:
        data = sys.stdin.read()
        paths = _parse_paths(sep, data)

        if not paths:
            die("no paths to watch were given on standard input")

        for path in paths:
            if not os.path.exists(path):
                die('path to watch does not exist: ' + repr(path))

        get_paths = lambda: paths

    interval = _parse_interval(options)

    _main()


def entry_point():
    import signal
    def sigint_handler(signal, frame):
        sys.stdout.write('\n')
        sys.exit(130)
    signal.signal(signal.SIGINT, sigint_handler)
    main()

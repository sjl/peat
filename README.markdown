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

`peat` repeats commands.

It's kind of like [Kicker][] except:

* It doesn't use inotify or OS X FSEvents, so it'll run anywhere.
* It doesn't require external libraries, so it'll run anywhere with Python.
* It won't eat your CPU (unless you try to watch too much).
* It takes paths to watch on standard input so you can use something like
  find(1) or [friendly-find][] to specify what to watch.

[Kicker]: https://github.com/alloy/kicker
[friendly-find]: https://github.com/sjl/friendly-find

**Table of Contents**

[TOC]

Installation
------------

Get the `peat` script on your machine and into your `$PATH` somehow.  Copy and
paste it, `curl` it, or clone the repository.  Make sure it's executable.
That's it.

Usage
-----

Generate a list of files you want to watch for changes, separated by whitespace.
echo(1), find(1) or [friendly-find][] are good for this:

    $ ffind '.*.py$'
    ./foo.py
    ./bar.py

    $ echo *.py
    foo.py bar.py

Now pipe that to `peat`, and specify the command you want to run whenever one of
those files changes:

    $ ffind '.*.py$' | peat 'echo "A file changed!"'

Use `Ctrl-C` to stop.

The command to run needs to be specified as a single argument to `peat`.  You
can do this with a shell string as seen above.  Using a single-quoted string
like this will preserve wildcards and such:

    $ ffind '.*.py$' | peat 'rm *.pyc'

This will delete all `.pyc` files in the current directory when a Python file is
modified.  Google around for "shell quoting" if you don't understand what's
happening here.

### Dynamic File Listing

If you want to build the file list fresh each time (so that `peat` will pick up
newly created files without having to restart it) you can use the `--dynamic`
option.

Instead of piping in the list of files to watch, you'll specify a *command* that
`peat` will run to generate the list before every check (as well as the actual
command to run, of course).  For example:

    $ ffind ".markdown$"
    ./foo.markdown
    ./bar/baz.markdown

    $ peat --dynamic 'ffind ".markdown$"' 'echo "A file changed!"'

### Tips & Tricks

Watch all the files Mercurial is tracking (instead of hand-crafting a `find`
command to output that list) and run `make` on changes:

    $ hg files | peat make

### Full Usage

Here's the full usage:

    Usage: peat [options] COMMAND

    COMMAND should be given as a single argument using a shell string.

    A list of paths to watch should be piped in on standard input.

    For example:

        find . | peat './test.sh'
        find . -name '*.py' | peat 'rm *.pyc'
        find . -name '*.py' -print0 | peat -0 'rm *.pyc'

    If --dynamic is used, the given command will be run each time to generate the
    list of files to check:

        peat --dynamic 'find .' './test.sh'
        peat --dynamic 'find . -name '\''*.py'\''' 'rm *.pyc'


    Options:
      -h, --help            show this help message and exit
      -i N, --interval=N    interval between checks in milliseconds
      -I, --smart-interval  determine the interval based on number of files
                            watched (default)
      -d COMMAND, --dynamic=COMMAND
                            run COMMAND before each run to generate the list of
                            files to check
      -D, --no-dynamic      take a list of files to watch on standard in (default)
      -c, --clear           clear screen before runs (default)
      -C, --no-clear        don't clear screen before runs
      -v, --verbose         show extra logging output (default)
      -q, --quiet           don't show extra logging output
      -w, --whitespace      assume paths are separated by whitespace (default)
      -n, --newlines        assume paths are separated by newlines
      -s, --spaces          assume paths are separated by spaces
      -0, --zero            assume paths are separated by null bytes

License
-------

Copyright 2016 Steve Losh and contributors.

Licensed under [version 3 of the GPL][gpl].

Remember that you can use GPL'ed software through their command line interfaces
without any license-related restrictions.  `peat`'s command line interface is
the only stable one, so it's the only one you should ever be using anyway.  The
license doesn't affect you unless you're:

* Trying to copy the code and release a non-GPL'ed version of `peat`.
* Trying to use it as a Python module from other Python code (for your own
  sanity I urge you to not do this) and release the result under a non-GPL
  license.

[gpl]: http://www.gnu.org/copyleft/gpl.html

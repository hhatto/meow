#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    ___ ___      __    ___   __  __  __
  /' __` __`\  /'__`\ / __`\/\ \/\ \/\ \\
  /\ \/\ \/\ \/\  __//\ \L\ \ \ \_/ \_/ \\
  \ \_\ \_\ \_\ \____\ \____/\ \___x___/'
   \/_/\/_/\/_/\/____/\/___/  \/__//__/

  Editor-agnostic markdown live preview server.

Usage: meow [options] FILE

Options:
  -q, --quiet             Quiet mode.
  -p port, --port=port    Server port. [default: 7777]
  -o file, --output=file  Export to HTML mode.
  -t type, --filetype=type  Force specify file type.
  --debug                 Output verbose debug logs.

"""

import logging
import os
import sys
from docopt import docopt
from ._version import __version__
from .meow import quickstart, export_html, Markup, SUPPORT_FILETYPE


def open_local_url(port):
    import webbrowser
    logging.debug('opening web browser...')
    # from ipdb import set_trace; set_trace()
    local_url = 'http://127.0.0.1:%d' % port
    webbrowser.open(local_url)


def main():
    args = docopt(__doc__, version=__version__)

    markdown_file = os.path.abspath(args['FILE'])
    output_file = args['--output']
    if output_file is not None:
        output_file = os.path.abspath(output_file)

    # export HTML mode
    if output_file is not None:
        export_html(markdown_file, output_file)
        return

    # shut-your-mouth-up mode
    if args['--quiet']:
        logging_level = logging.ERROR
    # logging configs
    if args['--debug']:
        logging_level = logging.DEBUG
        use_debug = True
    else:
        logging_level = logging.INFO
        use_debug = False

    logging.basicConfig(level=logging_level,
                        format='%(asctime)s %(levelname)-8s %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')

    try:
        port = int(args['--port'])
    except:
        sys.stderr.write('Invalid port number\n')
        sys.exit(-1)

    # check filetype
    try:
        Markup.ftdetect(markdown_file)
    except ValueError as e:
        if e.message == "unsupported markup":
            _, ext = os.path.splitext(markdown_file)
            print('"%s" is unsupported markup type.' % ext)
            print('\n[SUPPORT FILETYPE]')
            for k, v in SUPPORT_FILETYPE.items():
                print('  %s: %s' % (k, v))
            return
        raise e

    # try open browser
    try:
        open_local_url(port)
    except:
        pass
    print('Preview on http://127.0.0.1:%d' % port)
    print('Hit Ctrl-C to quit.')

    # start server
    quickstart(markdown_file, port=port, debug=use_debug, filetype=args['--filetype'])

if __name__ == '__main__':
    main()

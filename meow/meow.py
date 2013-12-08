"""
Copyright (c) 2013 Hideo Hattori
Copyright (c) 2013 metaphysiks

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
of the Software, and to permit persons to whom the Software is furnished to do
so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import bottle
import logging
import os
import re
from bottle import Bottle
try:
    from .markdown import to_html as markdown_to_html
except ImportError:
    mdmod_is_not_installed = True
try:
    from .txtile import to_html as textile_to_html
except ImportError:
    txlmod_is_not_installed = True
from .rst import to_html as rst_to_html
from .server import StoppableCherryPyServer

__all__ = ['build_app', 'quickstart', 'export_html']
__file__ = os.path.normpath(os.path.abspath(__file__))
__path__ = os.path.dirname(__file__)

# for Python3.x
if not hasattr(__builtins__, 'long'):
    long = int

# Fix default template path
DEFAULT_TEMPLATE_DIR = os.path.normpath(os.path.join(__path__, 'templates'))
bottle.TEMPLATE_PATH = [DEFAULT_TEMPLATE_DIR, './']

# Fix default static file path
DEFAULT_STATIC_FILES_DIR = os.path.normpath(os.path.join(__path__, 'static'))

SUPPORT_FILETYPE = {
    'markdown': {'prefix': 'markdown|md|mdown|mkd|mkdn', 'module': 'hoedown'},
    'textile': {'prefix': 'textile|txtile', 'module': 'python-textile'},
    'rst': {'prefix': 'rst|rest', 'module': 'docutils'},
}


def build_app(filename, port, debug, quiet, filetype):
    app = Bottle()
    server = StoppableCherryPyServer(port=port, debug=debug, quiet=quiet)
    root, ext = os.path.splitext(filename)
    markup = Markup(filename, filetype)
    dirname, basename = os.path.split(markup.filename)
    title = '%s - %s' % (basename, dirname)

    @app.get('/')
    @bottle.view('github')
    def handle_index():
        html_part = markup.html
        return {
            'html_part': html_part,
            'title': title,
            'timestamp': markup.timestamp
        }

    @app.delete('/')
    def handle_shutdown():
        server.shutdown()

    @app.post('/update')
    def handle_update():
        try:
            obj = bottle.request.json
            timestamp = long(obj['timestamp'])
        except Exception as e:
            logging.debug(e.message)
            bottle.response.status = '400 Malformed JSON'
            return
        try:
            file_timestamp = markup.timestamp
        except OSError as e:
            logging.critical('%s: %s', markup.filename, e.strerror)
            raise e

        if file_timestamp == timestamp:     # Keep old entry
            return {
                'title': title,
                'timestamp': file_timestamp,
                'html_part': None
            }
        else:
            logging.info('detected file change')
            return {
                'title': title,
                'timestamp': file_timestamp,
                'html_part': markup.html
            }

    @app.route('/static/<filename>')
    def handle_static(filename):
        return bottle.static_file(filename, root=DEFAULT_STATIC_FILES_DIR)

    def run_app():
        try:
            server.run(app)
        except KeyboardInterrupt:
            server.shutdown()

    return run_app


class Markup(object):
    _markup_detect = {}
    _markup_render = {}

    @classmethod
    def add_markup(cls, markup, ftdetect, render_func):
        markup = str(markup)
        cls._markup_detect[markup] = ftdetect
        cls._markup_render[markup] = render_func

    def __init__(self, filename, filetype=None):
        filename = os.path.abspath(os.path.expanduser(filename))
        if not os.path.exists(filename) or not os.path.isfile(filename):
            raise ValueError('invalid filename')
        self._filename = filename
        self._basename = os.path.basename(filename)
        self._dirname = os.path.dirname(filename)
        _filename = filename
        if filetype:
            _filename = "dummy.%s" % filetype
        self._filetype = self.ftdetect(_filename)

    @classmethod
    def ftdetect(self, filename):
        # Markup._markup_detect
        for ft, detect in Markup._markup_detect.items():
            if re.search(detect, filename) is not None:
                return ft
        raise ValueError('unsupported markup')

    @classmethod
    def has_filetype_module(self, filetype):
        print self._markup_detect
        if filetype in self._markup_detect:
            return True
        return False

    def filename():
        doc = "The filename property."
        def fget(self):
            return self._filename
        return locals()
    filename = property(**filename())

    def timestamp():
        doc = "Source file timestamp."
        def fget(self):
            ts = long(os.stat(self.filename).st_mtime)
            logging.debug('markup file timestamp %s', str(ts))
            return ts
        return locals()
    timestamp = property(**timestamp())

    def html():
        doc = "Rendered html."
        def fget(self):
            render_func = Markup._markup_render[self._filetype]
            return render_func(self._filename)
        return locals()
    html = property(**html())

if 'mdmod_is_not_installed' not in locals():
    Markup.add_markup('markdown', r'\.(%s)$' % SUPPORT_FILETYPE['markdown']['prefix'], markdown_to_html)
if 'txlmod_is_not_installed' not in locals():
    Markup.add_markup('txtile', r'\.(%s)$' % SUPPORT_FILETYPE['textile']['prefix'], textile_to_html)
Markup.add_markup('rst', r'\.(%s)$' % SUPPORT_FILETYPE['rst']['prefix'], rst_to_html)


def quickstart(markdown_file, port, debug=False, quiet=True, filetype=None):
    app = build_app(filename=markdown_file, port=port,
                    debug=debug, quiet=quiet, filetype=filetype)
    logging.debug('starting server at port %d', port)
    app()


def export_html(markdown_file, export_file):
    markup = Markup(markdown_file)
    dirname, basename = os.path.split(markup.filename)
    title = '%s - %s' % (basename, dirname)
    html_part = markup.html

    export_data = {
        'html_part': html_part,
        'title': title,
        'timestamp': markup.timestamp
    }
    logging.debug('rendering exported html...')
    exported_html = bottle.template('github-export', export_data)
    try:
        with open(export_file, 'w') as export_file:
            export_file.write(exported_html.encode('utf-8'))
    except IOError as e:
        logging.error(e.strerror)

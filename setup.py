"""
    meow
    ~~~~

    Meow is a markdown and reStructuredText preview server that provides
    preview of markdown (and reST) files. It automatically reload rendered
    HTML in your broswer when file changes, which makes it suitable to preview
    markdown in editors that does not provide this feature. Plugins can
    be easily written to interface with it.

    :copyright: Copyright 2013 by Hideo Hattori.
    :copyright: Copyright 2012-2013 by metaphysiks.
    :license: MIT
"""

from setuptools import setup

setup(
	name='meow',
	version='0.1.1',
	description="meow is an editor-agnostic markdown/reST live preview server.",
	long_description=open('README.rst').read(),
    author="Hideo Hattori",
    author_email="hhatto.jp@gmail.com",
    keywords=("markdown", "reStructuredText", "pygments", "preview",
              "bottle", "github"),
    url = "https://github.com/hhatto/meow",
	packages=['meow'],
	include_package_data=True,
	zip_safe=False,
    platforms = 'any',
	install_requires=['misaka', 'docutils', 'bottle', 'pygments',
                      'docopt', 'cherrypy'],
    license='MIT',
	entry_points={
        'console_scripts': ['meow = meow.cmdline:main'],
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Topic :: Utilities'
    ]
)


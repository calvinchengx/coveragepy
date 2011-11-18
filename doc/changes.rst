.. _changes:

====================================
Major change history for coverage.py
====================================

:history: 20090524T134300, brand new docs.
:history: 20090613T164000, final touches for 3.0
:history: 20090706T205000, changes for 3.0.1
:history: 20091004T170700, changes for 3.1
:history: 20091128T072200, changes for 3.2
:history: 20091205T161525, 3.2 final
:history: 20100221T151900, changes for 3.3
:history: 20100306T181400, changes for 3.3.1
:history: 20100725T211700, updated for 3.4.
:history: 20100820T151500, updated for 3.4b1
:history: 20100906T133800, updated for 3.4b2
:history: 20100919T163400, updated for 3.4 release.
:history: 20110604T214100, updated for 3.5b1
:history: 20110629T082200, updated for 3.5
:history: 20110923T081600, updated for 3.5.1


These are the major changes for coverage.py.  For a more complete change
history, see the `CHANGES.txt`_ file in the source tree.

.. _CHANGES.txt: http://bitbucket.org/ned/coveragepy/src/tip/CHANGES.txt


Version 3.5.1 --- 23 September 2011
-----------------------------------

- When combining data files from parallel runs, you can now instruct coverage
  about which directories are equivalent on different machines.  A ``[paths]``
  section in the configuration file lists paths that are to be considered
  equivalent.  Finishes `issue 17`_.

- for-else constructs are understood better, and don't cause erroneous partial
  branch warnings.  Fixes `issue 122`_.

- Branch coverage for ``with`` statements is improved, fixing `issue 128`_.

- The number of partial branches reported on the HTML summary page was
  different than the number reported on the individual file pages.  This is
  now fixed.

- An explicit include directive to measure files in the Python installation
  wouldn't work because of the standard library exclusion.  Now the include
  directive takes precendence, and the files will be measured.  Fixes
  `issue 138`_.

- The HTML report now handles Unicode characters in Python source files
  properly.  This fixes `issue 124`_ and `issue 144`_. Thanks, Devin
  Jeanpierre.

- In order to help the core developers measure the test coverage of the
  standard library, Brandon Rhodes devised an aggressive hack to trick Python
  into running some coverage code before anything else in the process.
  See the coverage/fullcoverage directory if you are interested.

.. _issue 17: http://bitbucket.org/ned/coveragepy/issue/17/support-combining-coverage-data-from
.. _issue 122: http://bitbucket.org/ned/coveragepy/issue/122/for-else-always-reports-missing-branch
.. _issue 124: http://bitbucket.org/ned/coveragepy/issue/124/no-arbitrary-unicode-in-html-reports-in
.. _issue 128: http://bitbucket.org/ned/coveragepy/issue/128/branch-coverage-of-with-statement-in-27
.. _issue 138: http://bitbucket.org/ned/coveragepy/issue/138/include-should-take-precedence-over-is
.. _issue 144: http://bitbucket.org/ned/coveragepy/issue/144/failure-generating-html-output-for


Version 3.5 --- 29 June 2011
----------------------------

HTML reporting:

- The HTML report now has hotkeys.  Try ``n``, ``s``, ``m``, ``x``, ``b``,
  ``p``, and ``c`` on the overview page to change the column sorting.
  On a file page, ``r``, ``m``, ``x``, and ``p`` toggle the run, missing,
  excluded, and partial line markings.  You can navigate the highlighted
  sections of code by using the ``j`` and ``k`` keys for next and previous.
  The ``1`` (one) key jumps to the first highlighted section in the file,
  and ``0`` (zero) scrolls to the top of the file.

- HTML reporting is now incremental: a record is kept of the data that
  produced the HTML reports, and only files whose data has changed will
  be generated.  This should make most HTML reporting faster.


Running Python files

- Modules can now be run directly using ``coverage run -m modulename``, to
  mirror Python's ``-m`` flag.  Closes `issue 95`_, thanks, Brandon Rhodes.

- ``coverage run`` didn't emulate Python accurately in one detail: the
  current directory inserted into ``sys.path`` was relative rather than
  absolute. This is now fixed.

- Pathological code execution could disable the trace function behind our
  backs, leading to incorrect code measurement.  Now if this happens,
  coverage.py will issue a warning, at least alerting you to the problem.
  Closes `issue 93`_.  Thanks to Marius Gedminas for the idea.

- The C-based trace function now behaves properly when saved and restored
  with ``sys.gettrace()`` and ``sys.settrace()``.  This fixes `issue 125`_
  and `issue 123`_.  Thanks, Devin Jeanpierre.

- Coverage.py can now be run directly from a working tree by specifying
  the directory name to python:  ``python coverage_py_working_dir run ...``.
  Thanks, Brett Cannon.

- A little bit of Jython support: `coverage run` can now measure Jython
  execution by adapting when $py.class files are traced. Thanks, Adi Roiban.


Reporting

- Partial branch warnings can now be pragma'd away.  The configuration option
  ``partial_branches`` is a list of regular expressions.  Lines matching any of
  those expressions will never be marked as a partial branch.  In addition,
  there's a built-in list of regular expressions marking statements which should
  never be marked as partial.  This list includes ``while True:``, ``while 1:``,
  ``if 1:``, and ``if 0:``.

- The ``--omit`` and ``--include`` switches now interpret their values more
  usefully.  If the value starts with a wildcard character, it is used as-is.
  If it does not, it is interpreted relative to the current directory.
  Closes `issue 121`_.

- Syntax errors in supposed Python files can now be ignored during reporting
  with the ``-i`` switch just like other source errors.  Closes `issue 115`_.

.. _issue 93: http://bitbucket.org/ned/coveragepy/issue/93/copying-a-mock-object-breaks-coverage
.. _issue 95: https://bitbucket.org/ned/coveragepy/issue/95/run-subcommand-should-take-a-module-name
.. _issue 115: https://bitbucket.org/ned/coveragepy/issue/115/fail-gracefully-when-reporting-on-file
.. _issue 121: https://bitbucket.org/ned/coveragepy/issue/121/filename-patterns-are-applied-stupidly
.. _issue 123: https://bitbucket.org/ned/coveragepy/issue/123/pyeval_settrace-used-in-way-that-breaks
.. _issue 125: https://bitbucket.org/ned/coveragepy/issue/125/coverage-removes-decoratortoolss-tracing


Version 3.4 --- 19 September 2010
---------------------------------

Controlling source:

- BACKWARD INCOMPATIBILITY: the ``--omit`` and ``--include`` switches now take
  file patterns rather than file prefixes, closing `issue 34`_ and `issue 36`_.

- BACKWARD INCOMPATIBILITY: the `omit_prefixes` argument is gone throughout
  coverage.py, replaced with `omit`, a list of filename patterns suitable for
  `fnmatch`.  A parallel argument `include` controls what files are included.

- The run command now has a ``--source`` switch, a list of directories or
  module names.  If provided, coverage.py will only measure execution in those
  source files.  The run command also now supports ``--include`` and ``--omit``
  to control what modules it measures.  This can speed execution and reduce the
  amount of data during reporting. Thanks Zooko.

- The reporting commands (report, annotate, html, and xml) now have an
  ``--include`` switch to restrict reporting to modules matching those file
  patterns, similar to the existing ``--omit`` switch. Thanks, Zooko.

Reporting:

- Completely unexecuted files can now be included in coverage results, reported
  as 0% covered.  This only happens if the --source option is specified, since
  coverage.py needs guidance about where to look for source files.

- Python files with no statements, for example, empty ``__init__.py`` files,
  are now reported as having zero statements instead of one.  Fixes `issue 1`_.

- Reports now have a column of missed line counts rather than executed line
  counts, since developers should focus on reducing the missed lines to zero,
  rather than increasing the executed lines to varying targets.  Once
  suggested, this seemed blindingly obvious.

- Coverage percentages are now displayed uniformly across reporting methods.
  Previously, different reports could round percentages differently.  Also,
  percentages are only reported as 0% or 100% if they are truly 0 or 100, and
  are rounded otherwise.  Fixes `issue 41`_ and `issue 70`_.

- The XML report output now properly includes a percentage for branch coverage,
  fixing `issue 65`_ and `issue 81`_, and the report is sorted by package
  name, fixing `issue 88`_.

- The XML report is now sorted by package name, fixing `issue 88`_.

- The precision of reported coverage percentages can be set with the
  ``[report] precision`` config file setting.  Completes `issue 16`_.

- Line numbers in HTML source pages are clickable, linking directly to that
  line, which is highlighted on arrival.  Added a link back to the index page
  at the bottom of each HTML page.

Execution and measurement:

- Various warnings are printed to stderr for problems encountered during data
  measurement: if a ``--source`` module has no Python source to measure, or is
  never encountered at all, or if no data is collected.

- Doctest text files are no longer recorded in the coverage data, since they
  can't be reported anyway.  Fixes `issue 52`_ and `issue 61`_.

- Threads derived from ``threading.Thread`` with an overridden `run` method
  would report no coverage for the `run` method.  This is now fixed, closing
  `issue 85`_.

- Programs that exited with ``sys.exit()`` with no argument weren't handled
  properly, producing a coverage.py stack trace.  This is now fixed.

- Programs that call ``os.fork`` will properly collect data from both the child
  and parent processes.  Use ``coverage run -p`` to get two data files that can
  be combined with ``coverage combine``.  Fixes `issue 56`_.

- When measuring code running in a virtualenv, most of the system library was
  being measured when it shouldn't have been.  This is now fixed.

- Coverage can now be run as a module: ``python -m coverage``.  Thanks,
  Brett Cannon.

.. _issue 1:  http://bitbucket.org/ned/coveragepy/issue/1/empty-__init__py-files-are-reported-as-1-executable
.. _issue 16: http://bitbucket.org/ned/coveragepy/issue/16/allow-configuration-of-accuracy-of-percentage-totals
.. _issue 34: http://bitbucket.org/ned/coveragepy/issue/34/enhanced-omit-globbing-handling
.. _issue 36: http://bitbucket.org/ned/coveragepy/issue/36/provide-regex-style-omit
.. _issue 41: http://bitbucket.org/ned/coveragepy/issue/41/report-says-100-when-it-isnt-quite-there
.. _issue 52: http://bitbucket.org/ned/coveragepy/issue/52/doctesttestfile-confuses-source-detection
.. _issue 56: http://bitbucket.org/ned/coveragepy/issue/56/coveragepy-cant-trace-child-processes-of-a
.. _issue 61: http://bitbucket.org/ned/coveragepy/issue/61/annotate-i-doesnt-work
.. _issue 65: http://bitbucket.org/ned/coveragepy/issue/65/branch-option-not-reported-in-cobertura
.. _issue 70: http://bitbucket.org/ned/coveragepy/issue/70/text-report-and-html-report-disagree-on-coverage
.. _issue 81: http://bitbucket.org/ned/coveragepy/issue/81/xml-report-does-not-have-condition-coverage-attribute-for-lines-with-a
.. _issue 85: http://bitbucket.org/ned/coveragepy/issue/85/threadrun-isnt-measured
.. _issue 88: http://bitbucket.org/ned/coveragepy/issue/88/xml-report-lists-packages-in-random-order


Version 3.3.1 --- 6 March 2010
------------------------------

- Using ``parallel=True`` in a .coveragerc file prevented reporting, but now
  does not, fixing `issue 49`_.

- When running your code with ``coverage run``, if you call ``sys.exit()``,
  coverage.py will exit with that status code, fixing `issue 50`_.

.. _issue 49: http://bitbucket.org/ned/coveragepy/issue/49
.. _issue 50: http://bitbucket.org/ned/coveragepy/issue/50


Version 3.3 --- 24 February 2010
--------------------------------

- Settings are now read from a .coveragerc file.  A specific file can be
  specified on the command line with ``--rcfile=FILE``.  The name of the file
  can be programmatically set with the ``config_file`` argument to the
  coverage() constructor, or reading a config file can be disabled with
  ``config_file=False``.

- Added coverage.process_start to enable coverage measurement when Python
  starts.

- Parallel data file names now have a random number appended to them in
  addition to the machine name and process id. Also, parallel data files
  combined with ``coverage combine`` are deleted after they're combined, to
  clean up unneeded files. Fixes `issue 40`_.

- Exceptions thrown from product code run with ``coverage run`` are now
  displayed without internal coverage.py frames, so the output is the same as
  when the code is run without coverage.py.

- Fixed `issue 39`_ and `issue 47`_.

.. _issue 39: http://bitbucket.org/ned/coveragepy/issue/39
.. _issue 40: http://bitbucket.org/ned/coveragepy/issue/40
.. _issue 47: http://bitbucket.org/ned/coveragepy/issue/47


Version 3.2 --- 5 December 2009
-------------------------------

- Branch coverage: coverage.py can tell you which branches didn't have both (or
  all) choices executed, even where the choice doesn't affect which lines were
  executed.  See :ref:`branch` for more details.

- The table of contents in the HTML report is now sortable: click the headers
  on any column.  The sorting is persisted so that subsequent reports are
  sorted as you wish.  Thanks, `Chris Adams`_.

- XML reporting has file paths that let Cobertura find the source code, fixing
  `issue 21`_.

- The ``--omit`` option now works much better than before, fixing `issue 14`_
  and `issue 33`_.  Thanks, Danek Duvall.

- Added a ``--version`` option on the command line.

- Program execution under coverage is a few percent faster.

- Some exceptions reported by the command line interface have been cleaned up
  so that tracebacks inside coverage.py aren't shown.  Fixes `issue 23`_.

- Fixed some problems syntax coloring sources with line continuations and
  source with tabs: `issue 30`_ and `issue 31`_.

.. _Chris Adams: http://improbable.org/chris/
.. _issue 21: http://bitbucket.org/ned/coveragepy/issue/21
.. _issue 23: http://bitbucket.org/ned/coveragepy/issue/23
.. _issue 14: http://bitbucket.org/ned/coveragepy/issue/14
.. _issue 30: http://bitbucket.org/ned/coveragepy/issue/30
.. _issue 31: http://bitbucket.org/ned/coveragepy/issue/31
.. _issue 33: http://bitbucket.org/ned/coveragepy/issue/33


Version 3.1 --- 4 October 2009
------------------------------

- Python 3.1 is now supported.

- Coverage.py has a new command line syntax with sub-commands.  This expands
  the possibilities for adding features and options in the future.  The old
  syntax is still supported.  Try ``coverage help`` to see the new commands.
  Thanks to Ben Finney for early help.

- Added an experimental ``coverage xml`` command for producing coverage reports
  in a Cobertura-compatible XML format.  Thanks, Bill Hart.

- Added the ``--timid`` option to enable a simpler slower trace function that
  works for DecoratorTools projects, including TurboGears.  Fixed `issue 12`_
  and `issue 13`_.

- HTML reports now display syntax-colored Python source.

- Added a ``coverage debug`` command for getting diagnostic information about
  the coverage.py installation.

- Source code can now be read from eggs.  Thanks, `Ross Lawley`_.  Fixes
  `issue 25`_.

.. _Ross Lawley: http://agileweb.org/
.. _issue 25: http://bitbucket.org/ned/coveragepy/issue/25
.. _issue 12: http://bitbucket.org/ned/coveragepy/issue/12
.. _issue 13: http://bitbucket.org/ned/coveragepy/issue/13


Version 3.0.1 --- 7 July 2009
-----------------------------

- Removed the recursion limit in the tracer function.  Previously, code that
  ran more than 500 frames deep would crash.

- Fixed a bizarre problem involving pyexpat, whereby lines following XML parser
  invocations could be overlooked.

- On Python 2.3, coverage.py could mis-measure code with exceptions being
  raised.  This is now fixed.

- The coverage.py code itself will now not be measured by coverage.py, and no
  coverage modules will be mentioned in the nose ``--with-cover`` plugin.

- When running source files, coverage.py now opens them in universal newline
  mode just like Python does.  This lets it run Windows files on Mac, for
  example.


Version 3.0 --- 13 June 2009
----------------------------

- Coverage is now a package rather than a module.  Functionality has been split
  into classes.

- HTML reports and annotation of source files: use the new ``-b`` (browser)
  switch.  Thanks to George Song for code, inspiration and guidance.

- The trace function is implemented in C for speed.  Coverage runs are now
  much faster.  Thanks to David Christian for productive micro-sprints and
  other encouragement.

- The minimum supported Python version is 2.3.

- When using the object api (that is, constructing a coverage() object), data
  is no longer saved automatically on process exit.  You can re-enable it with
  the ``auto_data=True`` parameter on the coverage() constructor.
  The module-level interface still uses automatic saving.

- Code in the Python standard library is not measured by default.  If you need
  to measure standard library code, use the ``-L`` command-line switch during
  execution, or the ``cover_pylib=True`` argument to the coverage()
  constructor.

- API changes:

  - Added parameters to coverage.__init__ for options that had been set on
    the coverage object itself.

  - Added clear_exclude() and get_exclude_list() methods for programmatic
    manipulation of the exclude regexes.

  - Added coverage.load() to read previously-saved data from the data file.

  - coverage.annotate_file is no longer available.

  - Removed the undocumented cache_file argument to coverage.usecache().

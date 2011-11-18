"""Coverage-test Coverage.py itself.

Run as:

    $ python test/meta_coverage.py run [NOSE_ARGS]

to run and collect coverage, then:

    $ python test/meta_coverage.py report

to put the HTML report into the htmlcov directory.

"""

import os, shutil, sys
import nose

HTML_DIR = "htmlcov"

def run_tests_with_coverage():
    """Run the test suite with coverage measuring itself."""
    import coverage

    tracer = os.environ.get('COVERAGE_TEST_TRACER', 'c')
    version = "%s%s" % sys.version_info[:2]
    suffix = "%s_%s" % (version, tracer)

    cov = coverage.coverage(config_file="metacov.ini", data_suffix=suffix)
    # Cheap trick: the coverage code itself is excluded from measurement, but
    # if we clobber the cover_prefix in the coverage object, we can defeat the
    # self-detection.
    cov.cover_prefix = "Please measure coverage.py!"
    cov.erase()
    cov.start()

    # Re-import coverage to get it coverage tested!  I don't understand all the
    # mechanics here, but if I don't carry over the imported modules (in
    # covmods), then things go haywire (os == None, eventually).
    covmods = {}
    covdir = os.path.split(coverage.__file__)[0]
    # We have to make a list since we'll be deleting in the loop.
    modules = list(sys.modules.items())
    for name, mod in modules:
        if name.startswith('coverage'):
            if hasattr(mod, '__file__') and mod.__file__.startswith(covdir):
                covmods[name] = mod
                del sys.modules[name]
    import coverage     # don't warn about re-import: pylint: disable=W0404
    #sys.modules.update(covmods)

    # Run nosetests, with the arguments from our command line.
    print(":: Running nosetests %s" % " ".join(sys.argv[1:]))
    try:
        nose.run()
    except SystemExit:
        # nose3 seems to raise SystemExit, not sure why?
        pass

    cov.stop()
    print(":: Saving .coverage%s" % suffix)
    cov.save()

def report_on_combined_files():
    """Combine all the .coverage files and make an HTML report."""
    if os.path.exists(HTML_DIR):
        shutil.rmtree(HTML_DIR)

    print(":: Writing HTML report to %s/index.html" % HTML_DIR)
    import coverage
    cov = coverage.coverage(config_file="metacov.ini")
    cov.combine()
    cov.save()
    cov.html_report(directory=HTML_DIR)


try:
    cmd = sys.argv[1]
except IndexError:
    cmd = ''

if cmd == 'run':
    # Ugly hack: nose.run reads sys.argv directly, so here I delete my command
    # argument so that sys.argv is left as just nose arguments.
    del sys.argv[1]
    run_tests_with_coverage()
elif cmd == 'report':
    report_on_combined_files()
else:
    print("Need 'run' or 'report'")

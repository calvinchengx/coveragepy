#!/usr/bin/env bash
#
# To run the tests on many Pythons, create a series of virtualenvs in a 
# sibling directory called "ve".  Give the directories there names like
# "26" for Python 2.6.  
#
# All the Python installs have a .pth pointing to the egg file created by
# 2.6, so install the testdata in 2.6
ve=${COVERAGE_VE:-../ve}
echo "Testing in $ve"
source $ve/26/bin/activate
make --quiet testdata

for v in 23 24 25 26 27 31 32
do 
    source $ve/$v/bin/activate
    python setup.py -q develop
    python -c "import platform, sys; print('=== Python %s with C tracer (%s) ===' % (platform.python_version(), sys.executable))"
    COVERAGE_TEST_TRACER=c nosetests $@
    python -c "import platform, sys; print('=== Python %s with Python tracer (%s) ===' % (platform.python_version(), sys.executable))"
    rm coverage/tracer*.so
    COVERAGE_TEST_TRACER=py nosetests $@
done

make --quiet clean

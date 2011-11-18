@echo off
@rem all the Python installs have a .pth pointing to the egg file created by
@rem 2.6, so install the testdata in 2.5
call switchpy c:\vpy\coverage\26 quiet
make --quiet testdata

for %%v in (24 25 26 27 31 32) do (
    call switchpy c:\vpy\coverage\%%v
    python setup.py -q develop
    set COVERAGE_TEST_TRACER=c
    nosetests %1 %2 %3 %4 %5 %6 %7 %8 %9
    del coverage\tracer.pyd
    set COVERAGE_TEST_TRACER=py
    nosetests %1 %2 %3 %4 %5 %6 %7 %8 %9
    )

make --quiet clean

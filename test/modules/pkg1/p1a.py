import os, sys

# Invoke functions in os and sys so we can see if we measure code there.
x = sys.getcheckinterval()
y = os.getcwd()

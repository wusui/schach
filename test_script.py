# Copyright (C) 2025 Warren Usui, MIT License
"""
Test script.  Read puzzle setups (one per line) and run solver on each.
"""
import time
from schach import schach

start = time.time()
with open("testcases.test", 'r', encoding='utf-8') as testlines:
    testv = testlines.read()
    for tst in testv.split('\n'):
        print(schach(tst))
        print('-----------------------------------------')

print(f'Elapsed Time: {time.time() - start}')

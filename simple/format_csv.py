# !/usr/bin/env python
"""
Save as format.py, then run "python format.py".

Input file : temp.csv
Output file: t2m_20000801.csv
"""
with open('input.csv', 'r') as f_in, open('output.csv', 'w') as f_out:
    f_out.write(next(f_in))
    [f_out.write(','.join(line.split()) + '\n') for line in f_in]
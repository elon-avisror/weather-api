with open('input.csv', 'r') as f_in, open('output.csv', 'w') as f_out:
    f_out.write(next(f_in))
    [f_out.write(','.join(line.split()) + '\n') for line in f_in]
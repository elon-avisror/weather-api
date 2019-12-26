from datetime import timedelta, date


def date_range(start_date, end_date):
    for n in range(int((end_date - start_date).days) + 1):
        yield start_date + timedelta(n)


start_date = date(day=30, month=8, year=1990)
end_date = date(day=1, month=9, year=1990)
for single_date in date_range(start_date, end_date):
    print(single_date.strftime("%d/%m/%Y"))

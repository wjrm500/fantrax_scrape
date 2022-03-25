from time import strftime, strptime

def convert_date(match_date: str, season: str) -> str:
    match_time_sans_year = strptime(match_date, '%b %d')
    month = match_time_sans_year.tm_mon
    [start_year, end_year] = list(map(int, season.split('-')))
    year = start_year if month >= 8 else end_year
    return strftime(f'{year}-%m-%d', match_time_sans_year)
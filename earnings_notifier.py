from colored import fg, attr
from datetime import datetime, timedelta
import calendar
import json
import re
import urllib.request

def fetch_from_yahoo():
    """Batch fetch and process future earnings announcements from Yahoo."""
    base = "http://biz.yahoo.com/research/earncal/"
    n = datetime.now()
    date = n
    dt = timedelta(days=1)
    database = {}
    tries = 0

    print("Loading...\n")

    while date < datetime(n.year, n.month+1, n.day):
        date_str = date2str(date)
        query = "{0}{1}.html".format(base, date_str)
        try:
            response = urllib.request.urlopen(query)
            data = response.read()
        except urllib.error.HTTPError:
            tries += 1
            if tries > 5:
                print("Note: Couldn't load reports on {0}.".format(date_str_dashes(date)))
                date += dt
                tries = 0
            continue
        text = data.decode('utf-8')
        reg_ex = '.*<a href="http://finance\.yahoo\.com/q\?s=.*">(.*)</a>.*\n.*\n.*<small>(.*)</small>.*'
        stocks = re.findall(reg_ex, text, re.M)
        if stocks:
            day_data = {}
            for s in stocks:
                day_data[s[0]] = s[1]
            database[date_str] = day_data
        date += dt
    return database
   
def fetch_watchlist():
    """Return a list of ticker symbols for the user's watched stocks."""
    stock_list = json.load(open('stock_list3.txt'))
    return [stock['symbol'] for stock in stock_list]

def str2date(string):
    """Convert a string formatted like 20150721 to a datetime object."""
    return datetime.strptime(string, "%Y%m%d")

def date_str_dashes(d):
    """Convert a datetime or a string like 20150721 to 2015-07-21 format."""
    if type(d) == datetime:
        d = date2str(d)
    year = d[0:4]
    month = d[4:6]
    day = d[6:8]
    return "{0}-{1}-{2}".format(year, month, day)

def date2str(date):
    """Convert a datetime object into a string formatted like 20150721."""
    return date.strftime("%Y%m%d")

def trim_database(database, watchlist):
    """Replace the aggregate database with one with only the user's stocks."""
    trimmed = {}
    for date in database:
        trimmed[date] = {}
        for stock in database[date]:
            if stock in watchlist:
                trimmed[date][stock] = database[date][stock]
    return trimmed

def print_all_days(database):
    """Prints out a list of earnings announcements for the user's stocks."""
    print("\nReporting dates for your tracked stocks:")
    color = fg(11)
    reset = attr('reset')
    for date in sorted(database.items()):
        d = date[0]
        header = datetime.strptime(date[0], "%Y%m%d").strftime("%A, %Y-%m-%d")
        header = "{0}{1}{2}".format(color, header, reset)
        date_str = "{0}{1}{2}".format(color, date_str_dashes(d), reset)
        print("\n{0}:".format(header))
        if len(database[d]) == 0:
            print("  (none)")
        for stock in database[d]:
            print("  {:10s} [{:5s}]".format(stock, database[d][stock]))

def print_month_cals():
    """Print a calendar of the current and next month for the user."""
    print()
    c = calendar.TextCalendar(calendar.SUNDAY)
    n = datetime.now()
    c.prmonth(n.year, n.month)
    print()
    c.prmonth(n.year, n.month + 1)
    print()

def main():
    print_month_cals()
    database = fetch_from_yahoo()
    database = trim_database(database, fetch_watchlist())
    print_all_days(database)

main()

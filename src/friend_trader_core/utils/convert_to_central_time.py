import datetime
import pytz


def convert_to_central_time(eth_timestamp):
    utc_time = datetime.datetime.utcfromtimestamp(eth_timestamp)
    utc_time = pytz.utc.localize(utc_time)
    central_time = utc_time.astimezone(pytz.timezone('US/Central'))
    central_time = central_time.strftime('%Y-%m-%dT%H:%M:%S')
    return eth_timestamp
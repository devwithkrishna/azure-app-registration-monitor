import pytz
from datetime import datetime
from dateutil import parser

def convert_to_ist(utc_dt):
    # Define UTC timezone
    utc = pytz.timezone('UTC')

    # Define IST timezone
    ist = pytz.timezone('Asia/Kolkata')

    # Convert UTC datetime to IST
    ist_dt = utc_dt.astimezone(ist)

    # Format the DateTime object
    formatted_dt = ist_dt.strftime('%d-%B-%Y %H:%M:%S')

    # Get the time zone abbreviation
    tz_abbr = ist_dt.strftime('%Z')

    # Construct the final string with time zone
    final_str = f"{formatted_dt} {tz_abbr}"

    return final_str

def date_time():
    """return current date time formatted"""
    now = datetime.now()
    formatted_datetime = now.strftime("%d-%B-%Y %H:%M")
    return formatted_datetime
    # print(formatted_datetime)


def compare_dates(expiry_date_str):
    # Get the current date and time in UTC in the same format
    current_date_str = datetime.utcnow().isoformat() + 'Z'

    # Parse the date strings into datetime objects
    current_date = parser.isoparse(current_date_str)
    expiry_date = parser.isoparse(expiry_date_str)

    # Find the difference between the dates
    time_difference = expiry_date - current_date
    days = time_difference.days
    # Return the results
    return days


def main():
    # to test the code #
    # Sample DateTime object in UTC
    utc_dt = datetime(2024, 7, 25, 18, 51, 25, 764458, tzinfo=pytz.utc)

    # Convert to IST
    ist_str = convert_to_ist(utc_dt)
    print(ist_str)

if __name__ == "__main__":
    main()

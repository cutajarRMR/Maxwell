import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
from langchain.tools import tool
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
import smtplib
from email.mime.text import MIMEText
load_dotenv()


@tool
def will_rain_openmeteo(lat, lon, forecast_days, range_start, range_end):
    """
    Determines the expected precipitation (in mm) for a given location and time range
    using the Open-Meteo API.

    Args:
        lat (float): Latitude of the location.
        lon (float): Longitude of the location.
        forecast_days (int): Number of days ahead to forecast (1 = tomorrow).
        range_start (int): Start of the time range in 24-hour format (e.g., 17 for 5pm).
        range_end (int): End of the time range in 24-hour format (e.g., 19 for 7pm).

    Returns:
        float: Total precipitation (mm) expected in the given time window.
               Returns 0 if no precipitation is expected.

    Example:
        >>> will_rain_openmeteo(-37.713, 144.927, 1, 17, 19)
        0.2

    Notes:
        - Uses the Open-Meteo public API (no API key required).
        - Timezone is set to Australia/Sydney for accurate local times.
    """
    # Calculate target date
    now = datetime.now()
    target_date = (now + timedelta(days=forecast_days)).date()

    # Build Open-Meteo API URL
    url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={lat}&longitude={lon}"
        f"&hourly=precipitation"
        f"&timezone=Australia/Sydney"
    )

    # Call API
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()

    # Extract hourly data
    times = data.get("hourly", {}).get("time", [])
    precipitation = data.get("hourly", {}).get("precipitation", [])

    # Sum precipitation in the desired window
    total_precip = 0.0
    for time_str, precip in zip(times, precipitation):
        dt = datetime.fromisoformat(time_str)
        if dt.date() == target_date and range_start <= dt.hour < range_end:
            total_precip += precip

    return total_precip

@tool
def worm_max():
    """
    Returns True if Maxwell needs to be wormed (between 26th and end of month).
    """
    def is_end_of_month(date: datetime) -> bool:
        """
        Returns True if the date is between the 26th and the last day of the month (inclusive).
        """
        last_day = 31
        return 26 <= date.day <= last_day
    
    if is_end_of_month(datetime.today()):
        return True
    else:
        return False

@tool
def send_user_email(body :str):
    """
    Docstring for send_user_email
    
    :param body: Information to include in the email body
    
    Sends an email with the provided body content to a predefined recipient.
    """
    # Email details
    sender = os.environ["GMAIL_USERNAME"]
    receiver = ["anthony.j.cutajar@gmail.com"]  # or another recipient
    password = os.environ["GMAIL_PASSWORD"]  # or GMAIL_APP_PASSWORD

    msg = MIMEText(body)
    msg["Subject"] = "Maxwell Summary"
    msg["From"] = sender
    msg["To"] = ", ".join(receiver)

    # Send email
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender, password)
        server.sendmail(sender, receiver, msg.as_string())


if __name__ == "__main__":

    tools = [will_rain_openmeteo, worm_max, send_user_email]

    agent_max = create_agent(ChatOpenAI(model="gpt-4o",api_key =os.environ["OPENAI_API_KEY"]), 
                tools=tools,
                system_prompt="""You are a helpful assistant for caring for my dog Maxwell.
    Use the available tools to provide accurate information about whether Maxwell needs to be wormed this month and whether it will rain during his walk time.
    If it will rain in Glenroy Victoria Australia tomorrow between 5pm and 7pm, suggest alternative walk times. Options are tomorrow morning between 6am and 7am, or the following day (2 days way) between 6am and 7am.
    If an alternative time is suggested or Maxwell needs to be warmed, use the send_user_email tool to email me the details.
    Do not send an email if no action is needed.""")


    walkplan = agent_max.invoke(
                {"messages": [{"role": "user"  , "content": "Perform Maxwell's daily care check"}]}
            )
    #print(walkplan)
    #for step in walkplan['messages']:
    #    print(step)
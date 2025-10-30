import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
from langchain.tools import tool
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
load_dotenv()


#os.getenv("OpenAI_API_KEY")


llm = ChatOpenAI(
    model="gpt-4o",
    api_key =os.environ["OPENAI_API_KEY"])

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


#will_rain_openmeteo(lat=-37.713, lon=144.927, forecast_days=1, range_start=17, range_end=19)

class maxwell:
    
    from datetime import datetime
    
    def __init__(self, name):
        self.name = name
        self.dob = None
        self.llm = ChatOpenAI(model="gpt-4o",api_key =os.getenv("OpenAI_API_KEY"))
    
    def worm_max(self):
        
        def is_end_of_month(date: datetime) -> bool:
            """
            Returns True if the date is between the 26th and the last day of the month (inclusive).
            """
            last_day = 31
            return 26 <= date.day <= last_day
        
        if is_end_of_month(datetime.today()):
            return "Maxwell needs to be wormed."
        else:
            return None
        
    def walk_max(self):
        agent = create_agent(self.llm, tools=[will_rain_openmeteo])
        walkplan = agent.invoke(
            {"messages": [{"role": "system", "content": "You are a helpful assistant that provides weather advice based on precipitation forecasts for when I should walk my dog Maxwell. Just reutrn the final answer without any additional commentary."}
                         ,{"role": "user"  , "content": "Will it rain in Glenroy tomorrow between 5pm and 7pm? If so, suggest an alternative time to walk Maxwell. Options are tomorrow morning between 6am and 7am, or the following day (2 days way) between 6am and 7am."}]}
        )
        
        return walkplan['messages'][-1].content
    
    
def maxwell_summary():
    max = maxwell("Maxwell")
    file = f"""{max.name}:
    {max.worm_max()}

    {max.walk_max()}
    """
    return file

if __name__ == "__main__":
    file = maxwell_summary()
    
    with open("result.txt", "w") as f:

        f.write(file)

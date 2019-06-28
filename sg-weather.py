import requests as req
import json
from collections import defaultdict
from datetime import datetime

sggovurl="https://api.data.gov.sg/v1/environment/24-hour-weather-forecast"
customheader={"accept": "application/json"}

response = req.get(sggovurl,headers=customheader)
response.raise_for_status()
weatherData = json.loads(response.text)

output=defaultdict(list)

timepattern="%I:%M %p of %Y-%m-%d"

print()
print(" ".join(">>> 24 hour weather forecast for Singapore <<<").upper())

for period in weatherData["items"][0]["periods"]:
    for region in period["regions"].keys():
        output[region].append({"start":period["time"]["start"],"end":period["time"]["end"],"weather":period["regions"][region]});

for regionname, regiondata in output.items():
    print()
    print("Forecast for {} region of Singapore:".format(regionname.upper()))
    for period in regiondata:
        starttime=datetime.strptime(period["start"].replace('+08:00','+0800'), "%Y-%m-%dT%H:%M:%S%z").strftime(timepattern)
        endtime=datetime.strptime(period["end"].replace('+08:00','+0800'), "%Y-%m-%dT%H:%M:%S%z").strftime(timepattern)
        
        print("From {} to {} >>> {} <<<.".format(starttime,endtime,period["weather"]))
        
    
                         


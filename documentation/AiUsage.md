# AI Usage
AI tools were used throughout this assignment to help me brainstorm and parse out the data received from each provider. However, the responses provided required additional prompting and edits for the finalized version of this project.

One main way I used AI was to help me understand Docker and creating a Postgres Database as I have limited working experience with these tools. AI helped me create a yml file to set up the database, and also provided me with instructions on how to connect to the database using the Postgres extension. I updated the yml file slightly to ensure that if the container was stopped, it would restart.

I further used AI to learn how to connect to the database in Python. While AI created the connection logic for me, I adapted it to make it a global variable so I did not have to pass it through each function. This can be further updated to be more secure.

Another main way I used AI was to set up the launch.json and task.json files. I prompted AI that I wanted a way to run and debug the code at the same time. I additionally directed AI to create a task.json file that would create the Docker container on startup. I further added creating the virtual environment and installing the requirements.

AI was also used to learn more about BeautifulSoup and how to extract data from Cheap Airport Parking, as I have never used this library before.

For instance, AI gave me the following snippet for how to extract information from HTML:
```
import json
from bs4 import BeautifulSoup

def parse(onclick):
    a = [x.strip().strip("'") for x in onclick[onclick.find("(")+1:onclick.rfind(")")].split(",")]
    return {"id": int(a[1]), "name": a[4], "latitude": float(a[2]), "longitude": float(a[3])}

soup = BeautifulSoup(response.text, "html.parser")

data = [parse(btn["onclick"]) for btn in soup.select("[onclick*='gotoMap']")]

print(json.dumps(data, indent=2))
```
I customized the code and simplified it to:

```
soup = BeautifulSoup(response.text, 'html.parser')

parking_data = []

for listing in soup.select("div.my_but[onclick*='gotoMap']"):
    data = listing["onclick"]
    args = [x.strip().strip("'") for x in data[data.find("(")+1:data.rfind(")")].split(",")]

```
Another way in which I used AI was to help with the matching algorithm. I prompted AI to match and produce a JSON based on latitude and longitude. AI produced this result:
```
def find_nearby_duplicates(data, tolerance=0.001):  # ~100 meter tolerance
    results = []
    
    for i, item1 in enumerate(data):
        for item2 in data[i+1:]:
            lat_diff = abs(item1["latitude"] - item2["latitude"])
            lng_diff = abs(item1["longitude"] - item2["longitude"])
            
            if lat_diff < tolerance and lng_diff < tolerance:
                results.append((item1["name"], item2["name"]))
    
    return results
```

After further prompting to clean up and simplify the code, I was prompted with this solution: 

```
matches = {}

for item in listings:
    key = (item["latitude"], item["longitude"])
    matches.setdefault(key, []).append(item)
```

I changed to slightly to the following, so I did not have to use setdefault and added rounding/precision to the matching algorithm:

```
matches = defaultdict(list)

for item in parking_data:
    key = (round(item.get("latitude"), 4), round(item.get("longitude"), 4))
    matches[key].append(item)
```

Overall, AI helped me throughout this assignment to parse results and match data. The foundation of the AI response was helpful, but needed revision to be applicable for each vendor integration.

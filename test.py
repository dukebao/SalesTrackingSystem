import requests 

url = "https://api.congress.gov/v3/treaty/116/123/committees?format=asf"

header = {'accept': 'application/xml'}
response = requests.get(url, headers=header)
print(response.text)
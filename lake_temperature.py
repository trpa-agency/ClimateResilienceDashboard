import requests
from bs4 import BeautifulSoup

url  = "https://tahoe.ucdavis.edu/real-time-conditions"
url2 = "https://ecs-193a-red-phoenix.github.io/isolated/real-time"

response = requests.get(url)

if response.status_code == 200:
    soup = BeautifulSoup(response.text, 'html.parser')
    # Use BeautifulSoup to navigate and extract the data you need
    # For example, if the data is in a table, you might do something like:
    table_data = soup.find('table').find_all('td')
    for td in table_data:
        print(td.text)
else:
    print("Failed to retrieve the webpage. Status code:", response.status_code)

You can use Python along with the `requests` and `BeautifulSoup` libraries to fetch and parse the data from the "Тенденции" section. Here's an example:

```python
import requests
from bs4 import BeautifulSoup

# URL of the target website
url = "https://www.moex.com/"

# Sending a GET request to the URL
response = requests.get(url)

if response.status_code == 200:  # Checking if the request was successful
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Finding the Тенденции section
    trends_section = soup.find('section', class_='trend-section')  # Update the class or tag based on actual HTML
    
    if trends_section:
        trends = trends_section.get_text(strip=True)
        print("Тенденции Data:")
        print(trends)
    else:
        print("Couldn't find the Тенденции section. Check the HTML structure.")
else:
    print(f"Failed to fetch the page. HTTP Status Code: {response.status_code}")
```

### Notes:
1. Replace `'section', class_='trend-section'` with the correct HTML tags and classes from the source's actual structure. Use browser developer tools (F12) to inspect the HTML and locate the "Тенденции" section.
2. Ensure the website allows web scraping by reviewing its `robots.txt` and terms of service.
3. You might need to use headers or handle cookies if the website has scraping protection mechanisms.

Let me know if you want help adapting this code further!
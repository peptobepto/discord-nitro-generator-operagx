import requests
import time
from concurrent.futures import ThreadPoolExecutor
from requests.auth import HTTPProxyAuth
from scrapy.downloadermiddlewares.httpproxy import HttpProxyMiddleware
from scrapy.downloadermiddlewares.useragent import UserAgentMiddleware
from scrapy import signals
from twisted.internet.error import TimeoutError, TCPTimedOutError
import concurrent.futures

# Define rotating proxy middleware
class RotateUserAgentMiddleware(UserAgentMiddleware):
    def __init__(self, user_agent=""):
        super().__init__(user_agent)
        self.user_agent = user_agent

    def process_request(self, request, spider):
        ua = self.user_agent
        if ua:
            request.headers.setdefault("User-Agent", ua)


class RotateProxyMiddleware(HttpProxyMiddleware):
    def __init__(self, proxy_list, user_agent=""):
        self.proxies = proxy_list
        self.user_agent = user_agent
        self.proxy_index = 0

    def process_request(self, request, spider):
        request.meta["proxy"] = self.proxies[self.proxy_index % len(self.proxies)]
        self.proxy_index += 1

    def process_exception(self, request, exception, spider):
        if isinstance(exception, (TimeoutError, TCPTimedOutError)):
            spider.log("Timeout exception. Retrying with the next proxy.")
            return self._retry(request, exception, spider)
        return None

# Replace 'YOUR_PROXY_URL' with the actual URL providing the list of proxies
proxy_url = 'https://proxylist.geonode.com/api/proxy-list?limit=500&page=1&sort_by=lastChecked&sort_type=desc'
response = requests.get(proxy_url)

# Extract proxy list from the response
proxy_list = response.text.splitlines()

# Post request headers and URL
url = 'https://api.discord.gx.games/v1/direct-fulfillment'
headers = {
    'authority': 'api.discord.gx.games',
    'accept': '*/*',
    'accept-language': 'en-US,en;q=0.9',
    'content-type': 'application/json',
    'origin': 'https://www.opera.com',
    'referer': 'https://www.opera.com/',
    'sec-ch-ua': '"Opera GX";v="105", "Chromium";v="119", "Not?A_Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'cross-site',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 OPR/105.0.0.0'
}

data = {
    'partnerUserId': '649b934ca495991b7852b855'
}

filepath = "keys.txt"

# Initialize Scrapy settings with rotating proxy middleware
SETTINGS = {
    "DOWNLOADER_MIDDLEWARES": {
        "scrapy_rotating_proxies.middlewares.RotatingProxyMiddleware": 610,
        "scrapy_rotating_proxies.middlewares.BanDetectionMiddleware": 620,
        "your_project_name.RotateUserAgentMiddleware": 400,
        "your_project_name.RotateProxyMiddleware": 750,
    },
    "ROTATING_PROXY_LIST": proxy_list,
    "ROTATING_PROXY_PAGE_RETRY_TIMES": 5,
    "USER_AGENT": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36 OPR/87.0.651.93",
}

# actual post request below
keyNumber = input("How many keys do you want?: ")

# Define the number of requests per second and delay between requests
requests_per_second = 15  # Change this to your desired value
delay_between_requests = 2 / requests_per_second

def fetch_request(_):
    response = requests.post(url, headers=headers, json=data)
    final = response.json()
    print(final)  # If the response is in JSON format
    token = final.get('token', '')

    # Format the token as desired
    formatted_token = token.strip('\"')

    # Append the formatted token to the URL
    final_url = f'https://discord.com/billing/partner-promotions/1180231712274387115/{formatted_token}'

    print(final_url)

    with open(filepath, 'a') as file:
        file.write(final_url + '\n \n')

# Use ThreadPoolExecutor to parallelize the requests
with ThreadPoolExecutor(max_workers=int(keyNumber)) as executor:
  # Start the fetch_request tasks and store the futures in a list to track their completion
  futures = [executor.submit(fetch_request, _) for _ in range(int(keyNumber))]

  # Wait for all tasks to complete
  for future in concurrent.futures.as_completed(futures):
      # Get the result of the completed task to handle any potential exceptions
      try:
          result = future.result()
      except Exception as exc:
          print(f'Task generated an exception: {exc}')
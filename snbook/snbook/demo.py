import re

base_url = '/1-503109-0-0-0-0-0-0-0-4.html'

base_url = re.findall('/1-(\d+)-(\d+)-0-0-0-0-(\d+)-0-4.html',base_url)[0][0]
print(base_url)
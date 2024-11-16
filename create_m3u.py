import csv
import requests

NAME = 0
URL = 1
LOGO = 2
GROUP = 3

output = []


def add_header(row):
    return f'#EXTINF:-1 tvg-id="{row[NAME]}" tvg-logo="{row[LOGO]}" group-title="{row[GROUP]}",{row[NAME]}'


def add_line(row):
    url = f'{row[URL]}'
    response = requests.get(url)
    print(url, response.code, response.status_code)
    response = response.text
    if '.m3u8' in response:
        end = response.find('.m3u8') + 5
        tuner = 100
        while True:
            if 'https://' in response[end-tuner: end]:
                link = response[end-tuner:end]
                start = link.find('https://')
                end = link.find('.m3u8') + 5
                break
            else:
                tuner += 5
        return f"{link[start:end]}"
    else:
        print(f"No m3u8 in response for {url}", response.find('.m3u8'))
        return None


with open("input/youtube.csv") as infile:
    reader = csv.reader(infile)
    for row in reader:
        print(row)
        header = add_header(row)
        line = add_line(row)
        print(header,line)
        if line is not None:
            output.append(header)
            output.append(line)

with open("input/others.m3u") as others:
    for row in others:
        output.append(row.strip())

with open("output/list.m3u", 'w') as outfile:
    print('#EXTM3U', file=outfile)
    for row in output:
        print(row, file=outfile)

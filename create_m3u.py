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
    print(url)
    response = requests.get(url).text
    end = response.find('.m3u8') + 5
    tuner = 100
    if '.m3u8' in response:
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
        return None


with open("input/youtube.csv") as infile:
    reader = csv.reader(infile)
    for row in reader:
        header = add_header(row)
        line = add_line(row)
        if line is not None:
            output.append(header)
            output.append(line)

with open("input/others.m3u") as others:
    for row in others:
        output.append(row)

with open("output/youtube.m3u", 'w') as outfile:
    print('#EXTM3U', file=outfile)
    for row in output:
        print(row, file=outfile)
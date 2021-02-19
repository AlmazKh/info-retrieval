import codecs

from bs4 import BeautifulSoup

pages_html = codecs.open("pages_html/541080.html", 'r', 'utf-8')
html = pages_html.read()
# print(html)

soup = BeautifulSoup(html, features='html.parser')

# kill all script, style, meta, links, span, a, time, button, li, dt, h2, h3, legend elements
for script in soup(
        ["script", "style", "meta", "link", "span", "a", "time", "button", "li", "dt", "h2", "h3", "legend"]):
    script.extract()  # rip it out

# get text
text = soup.get_text()

# break into lines and remove leading and trailing space on each
lines = (line.strip() for line in text.splitlines())

# break multi-headlines into a line each
chunks = (phrase.strip() for line in lines for phrase in line.split("  "))

# drop blank lines
text = '\n'.join(chunk for chunk in chunks if chunk)

# split to words. Тут пока со знаками препинания.
split_text = text.split()

print(split_text)

with open("words_list.txt", "w") as file:
    for elem in split_text:
        file.write(elem + '\n')

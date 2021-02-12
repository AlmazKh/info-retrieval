import scrapy

class BlogSpider(scrapy.Spider):
    name = 'spider'

    def start_requests(self):
        with open("links.txt") as file:
            urls = [row.strip() for row in file]
        print("URLS ----------------", urls)
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        page = response.url.split("/")[-1]
        filename = f'wiki-{page}.html'
        with open(filename, 'wb') as f:
            f.write(response.body)
        self.log(f'Saved file {filename}')
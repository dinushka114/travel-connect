from scraper import TravelConnectScraper

def main():
    url = "https://dinushka114.github.io/travel-connect/"
    
    scraper = TravelConnectScraper(url)
    scraper.run()


if __name__ == "__main__":
    main()
from pcpartpicker import API as pcpartpickerAPI
from pcpartscraper.scraper import Part, Query
from amazon_buddy import Product, AmazonBuddy, Category, SortType
import pprint


def part_picker_main():
    # method 1:
    part_picker_api = pcpartpickerAPI('us')
    # print(part_picker_api.supported_parts)
    cpu_data = part_picker_api.retrieve("cpu")
    pprint.pprint(len(cpu_data.get('cpu', [])))
    # print(cpu_data.get('cpu')[200])
    cpu = cpu_data.get('cpu')[200]
    pprint.pprint(dir(cpu))

    # amazon
    # ab = AmazonBuddy(debug=True, user_agent='ADD_USER_AGENT')
    # products = ab.search_products(
    #     'ryzen cpu',
    #     sort_type=SortType.PRICE_HIGH_TO_LOW,
    #     min_price=0,
    #     category=Category.BEAUTY_AND_PERSONAL_CARE,
    #     max_results=20
    # )
    # print(len(products))


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    part_picker_main()

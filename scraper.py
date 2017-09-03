
from selenium import webdriver
from bs4 import BeautifulSoup
from time import sleep

ROUTES_URL = "https://www.bt4u.org/routes-and-schedules/"
DETAILS_URL = "https://www.bt4u.org/route-details/"


def get_page(sel_browser, url):
    """ Gets a BeautifulSoup object representing a page.
    :param sel_browser A selenium browser to fetch the page with
    :param url The URL of the page to access
    :return A BeautifulSoup object representing the page at the given url"""

    # Fetch the page
    sel_browser.get(url)
    # Wait for the JS to load
    sleep(5)
    # Get the updated HTML from the page
    inner_html = browser.execute_script("return document.body.innerHTML")
    # Return a soup object with the HTML
    return BeautifulSoup(inner_html, "html.parser")


def is_route(tag):
    """ Checks if an HTML tag is a bus route.
    :param tag A BeautifulSoup tag
    :return True if the tag has a "data-routes" attribute, False otherwise"""
    return tag.has_attr("data-routes")


def is_stop(tag):
    """ Checks if an HTML tag is a stop
    :param tag A BeautifulSoup tag
    :return True if the tag is a link to a "displayBusStopDetails" page, False otherwise"""
    return tag.has_attr("href") and tag["href"].startswith("/displayBusStopDetails?")

if __name__ == "__main__":

    # Create a selenium browser
    # TODO make this customizable by CLAs
    browser = webdriver.Chrome()

    # Get a list of routes from the routes page
    routes_soup = get_page(browser, ROUTES_URL)
    route_elems = routes_soup.find_all(is_route)

    # Parse the route data from the list elements
    routes = []
    for route in route_elems:
        names = route["data-routes"].split("|")
        if len(names) != 3:
            raise RuntimeError("The route name format is not as expected: " + route["data-routes"])
        routes.append({"abbr": names[0], "name": names[1], "id": names[2], "stops": []})

    # Fetch the stops from each route
    for route in routes:
        query = "?routeId=" + route["abbr"]
        route_soup = get_page(browser, DETAILS_URL + query)

        stop_elems = route_soup.find_all(is_stop)
        for stop in stop_elems:
            stop_text = stop.text.strip()
            # Excpected format: "<name> (#<id>)Next: <time>, <time>, <time> ..."
            # For now this is very brittle, it expects this *exact* format
            stop_name = stop_text.split("(")[0].strip()
            stop_id = stop_text.split("(")[1][1:].split(")")[0].strip()
            stop_times = [x.strip() for x in stop_text.split(")")[1][5:].split(",")]
            route["stops"].append({"name": stop_name, "id": stop_id, "times": stop_times})

# At this point, routes contains a complete snapshot of the data available on the website.

# TODO Determine the day of the week the stops are on based on current local time

# TODO Insert times into database to maintain persistent schedule

# TODO Figure out how to detect changes in the schedule - dump that day's schedule and repopulate if different

# TODO Host database remotely

import os
import copy
import pickle
import re
import itertools
import requests
from bs4 import BeautifulSoup
import pandas as pd

os.chdir("C:/Users/User/Documents/DATA SCIENCE FOLDER/PROJECT FOLDER/Data" +
         " Engineering ETL/HOLIDAYETL APP/HolidayETL/holiday-newsletter/" +
         "newsletter/jobs")


# wikip countries and confirm nager supports
wiki_isos = requests.get(
    "https://en.wikipedia.org/wiki/List_of_ISO_3166_country_codes").text
soup = BeautifulSoup(wiki_isos, "html.parser")

# full country names
html_table = soup.find("table", class_="wikitable sortable")

# full name
html_table = soup.find("table", class_="wikitable sortable")
td_anchors = [td.find_all("a", href=True)
              for td in html_table.find_all("td")]
unlisted = list(itertools.chain.from_iterable(td_anchors))
countries_full_raw = [i.attrs["href"] for i in unlisted]
re_str1 = "wiki.([A-Z]{1}.[a-z_[^a-z]+[A-z]+)"
p = re.compile(re_str1)
one_str = " ".join(countries_full_raw)
countries_full_provisional = sorted(set(p.findall(one_str)))

# clean by removing hyphens
countries_full_provisional = [i.strip("_")
                              for i in countries_full_provisional]
countries_full_provisional = [i.replace("_", " ")
                              for i in countries_full_provisional]

# short name
spans = soup.find_all("span", class_="monospaced")
spans = [*spans]
spans = [*map(str, spans)]
spans = [item.replace('"', "") for item in spans]
re_str2 = "monospaced>([A-Z]{2})[^A-Z]"
p = re.compile(re_str2)
one_str = " ".join(spans)
countries_short_provisional = p.findall(one_str)

# remove missing data and rematch
cf = pd.Series(copy.deepcopy(countries_full_provisional))
cf_inds = [
    1, 9, 15, 16, 20, 39, 48, 49, 55, 56, 57, 58, 59, 60, 61, 63, 68, 73,
    77, 85, 92, 109, 114, 118, 120, 123, 125, 127, 129, 131, 135, 136,
    147, 148, 149, 150, 162, 164, 165, 166, 167, 168, 169, 172, 173, 176,
    179, 180, 181, 182, 183, 184, 185, 186, 187, 188, 191, 204, 205, 206,
    210, 211, 212, 213, 214, 215, 216, 217, 219, 221, 227, 228, 233, 234,
    237, 240, 244, 249, 250, 252, 266, 267, 270, 271, 274, 275, 276, 277,
    278, 279, 280
    ]
cs = pd.Series(copy.deepcopy(countries_short_provisional))
cs_inds = [
    1, 47, 49, 50, 51, 52, 53, 54, 81, 92, 94, 107, 108, 115, 118, 119,
    131, 132, 133, 134, 145, 146, 147, 148, 149, 150, 155, 158, 161, 162,
    163, 164, 165, 166, 167, 170, 182, 186, 187, 188, 189, 190, 191, 192,
    194, 195, 202, 208, 216, 221, 235, 239, 246, 247, 248
    ]
cf = list(cf.drop(cf_inds))
cs = list(cs.drop(cs_inds))
codes = pd.Series([*zip(cf, cs)])

# reduce according to api support
unsupported_inds = [
    0, 2, 3, 5, 6, 7, 8, 10, 11, 12, 14, 15, 16, 17, 23, 24, 26, 27, 29,
    30, 31, 32, 33, 34, 35, 36, 37, 39, 40, 41, 44, 45, 48, 52, 53, 58,
    59, 61, 62, 63, 65, 68, 69, 70, 72, 74, 79, 80, 82, 85, 86, 88, 89,
    91, 93, 94, 95, 100, 101, 102, 103, 104, 105, 107, 110, 114, 115, 116,
    118, 119, 120, 121, 122, 123, 126, 128, 132, 133, 138, 139, 143, 144,
    145, 146, 147, 148, 149, 150, 151, 151, 152, 153, 154, 155, 156, 158,
    160, 161, 166, 167, 168, 169, 170, 171, 172, 173, 176, 177, 178, 179,
    181, 185
    ]
codes = list(codes.drop(unsupported_inds))  # 79 countries

# add extras
to_add = [
    ("Australia", "AU"), ("Aland Islands", "AX"), ("Bahamas", "BS"),
    ("Gambia", "GM"), ("Guernsey", "GG"), ("Iceland", "IS"),
    ("Isle of Man", "IM"), ("Madagascar", "MG"), ("Mozambique", "MZ"),
    ("Madagascar", "MG"), ("Morocco", "MA"), ("Montserrat", "MS"),
    ("Monaco", "MC"), ("Montenegro", "ME"), ("Norway", "NO"),
    ("North Macedonia", "MK"), ("Niger", "NE"), ("Ireland", "IE"),
    ("Romania", "RO"), ("Russia", "RU"), ("San Marino", "SM"),
    ("Serbia", "RS"), ("Slovakia", "SK"), ("Slovenia", "SI"),
    ("South Korea", "KR"), ("Vatican City", "VA")
    ]
country_list = codes + to_add
country_list.sort()
country_dict = dict(country_list)

# remove unsupported: Cameroon, Chad, Cura, Dominica, Eritrea,
# Falkland Islands, Fiji, French Southern Territories, Georgia, Ghana,
# Guam, Guinea, India, Israel, Laos, Lebanon, Libya, Mali, Myanmar, Nepal,
# Palau, Pitcairn Islands, Solomon Islands, Sri Lanka, Sudan,
# Trinidad and Tobago, Tristan da Cunha, Tuvalu, United Arab Emirates,
# Uzbekistan
del country_dict["Cameroon"]
del country_dict["Chad"]
del country_dict["Cura"]
del country_dict["Dominica"]
del country_dict["Eritrea"]
del country_dict["Falkland Islands"]
del country_dict["Fiji"]
del country_dict["French Southern Territories"]
del country_dict["Georgia"]
del country_dict["Ghana"]
del country_dict["Guam"]
del country_dict["Guinea"]
del country_dict["India"]
del country_dict["Israel"]
del country_dict["Laos"]
del country_dict["Lebanon"]
del country_dict["Libya"]
del country_dict["Mali"]
del country_dict["Myanmar"]
del country_dict["Nepal"]
del country_dict["Palau"]
del country_dict["Pitcairn Islands"]
del country_dict["Solomon Islands"]
del country_dict["Sri Lanka"]
del country_dict["Sudan"]
del country_dict["Trinidad and Tobago"]
del country_dict["Tristan da Cunha"]
del country_dict["Tuvalu"]
del country_dict["United Arab Emirates"]
del country_dict["Uzbekistan"]


def save_obj(country_dict, name):
    with open("country_dict/" + name + ".pkl", "wb") as f:
        pickle.dump(country_dict, f, pickle.HIGHEST_PROTOCOL)


# save dict
save_obj(country_dict, "country_dict")

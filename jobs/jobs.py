import os
import sys
import datetime
import json
import itertools
import pickle
import requests
import pandas as pd
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)
os.chdir(currentdir)
from core.models import Newsletter


def get_subj_and_content():
    """
    Get content for auto_send here: ('subject' and 'content').
    """
    parse_dates = ["Date"]
    holidays_df = pd.read_csv("data/holidays.csv",
                              parse_dates=parse_dates)
    today_str = datetime.datetime.today().strftime("%Y-%m-%d")
    sub_df = holidays_df.loc[holidays_df["Date"] == datetime.datetime(
                                                        int(today_str[0:4]),
                                                        int(today_str[5:7]),
                                                        int(today_str[8:10]))]
    # test w/ known holiday Christmas Day
    # sub_df = holidays_df.loc[holidays_df["Date"] == datetime.datetime(
    #                                                       2021, 12, 25)]

    countrs = list(sub_df.iloc[:, 2].unique())
    if len(countrs) == 0:
        content = """No supported international public holidays \
    detected for today."""

    else:
        my_dict = dict(zip(countrs, [list() for i in range(len(countrs))]))
        for i, r in sub_df.iterrows():
            my_dict[r["Country"]].append(r["Day"])

        # # temp file to store email content
        with open("logs/content.txt", "w", encoding="utf-8") as file:
            file.write("<pre>")
            for k, v in my_dict.items():
                file.write((str(k) + ":\n" + "\n".join(v) + "\n\n"))
            file.write("</pre>")

        # read content for email from temp file
        with open("logs/content.txt", "r") as file:
            content = file.read()

    date = datetime.datetime.today().strftime("%Y-%m-%d")
    subject = "International Holidays for " + date

    return (subject, content)


def schedule_email():  # schedule to run daily
    def update_data():
        """
        Saves new df for current year to data/ folder.
        Need to start Docker for function to run correctly.
        Run 2x Docker commands below before 9am NYD.
        """
        def load_obj(name):
            with open("country_dict/" + name + ".pkl", "rb") as f:

                return pickle.load(f)

        country_dict = load_obj("country_dict")
        reverse_dict = dict(zip(country_dict.values(), country_dict.keys()))

        def get_response(country, year=datetime.datetime.now().year,
                         reverse_dict=reverse_dict):
            api_endpoint = \
                "http://host.docker.internal/api/v3/PublicHolidays/" + \
                str(year)+"/"+str(country)
            days = json.loads(requests.get(api_endpoint).text)

            return [(datetime.datetime.strptime(d["date"], "%Y-%m-%d").date(),
                     reverse_dict[d["countryCode"]], d["name"]) for d in days]

        def get_subsets(countries, year=datetime.datetime.now().year):
            responses = [get_response(c) for c in countries]

            return responses

        # supports 74 countries / 968 public holidays
        # dict ready to use, connect to api via Docker and pull data
        # api_url e.g. "https://date.nager.at/api/v3/PublicHolidays/2021/ZA"
        # format: "https://date.nager.at/api/v3/PublicHolidays/YEAR/CODE"
        # format above for api_url: also includes year and code seperated by /
        # open nager/nager-date image as container with: (externally start
        # Docker and run two commands below for update_data() to
        # work correctly.)
        # --> docker load -i nager-date.tar (in .tar dir)
        # then
        # --> docker run -e "EnableCors=true" -e "EnableIpRateLimiting=false"
        # -e "EnableSwaggerMode=true" -p 80:80 nager/nager-date
        # can visit UI via: http://localhost/index.html
        # sample response
        # response = requests.get\
        #     ("http://host.docker.internal/api/v3/PublicHolidays/2021/ZA").text
        mydata_nested = get_subsets(countries=[*country_dict.values()])
        # create df
        mydata = list(itertools.chain(*mydata_nested))
        dates, countries, days = [tup[0] for tup in mydata], \
            [tup[1] for tup in mydata], [tup[2] for tup in mydata]
        holidays_df = pd.DataFrame.from_dict({"Date": dates,
                                              "Country": countries,
                                              "Day": days})

        # save df
        # holidays_df.to_csv("data/holidays_updatetest.csv")
        holidays_df.to_csv("data/holidays.csv")

    def send_email(subject, content):
        """
        Send email message to all subscribers.
        """        
        Newsletter.auto_send(subject, content)
        print("Email successfully delivered to all subscribers.")

    if (datetime.date.today()) == (datetime.date(datetime.datetime.now().year,
                                                 1,
                                                 1)):
        update_data()  # update data on New Year's  Day

    subject, content = get_subj_and_content()
    send_email(subject, content)

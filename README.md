# HolidayETL

Production-ready email scheduler for international public holidays.

Calendar-based Application Programming Interfaces (APIs) are used extensively in industries such as travel, banking, finance and supply chain.  
Looking to familiarise myself with the ETL (Extract Transform Load) process, these APIs inspired me to create an app for automation of extraction and delivery of calendar data to end-users.  
With automated information retrieval from the API service, the tedious process of working with the API directly is avoided.  
Django and APScheduler were primarily used to schedule emails from the nager.date open-source API.  
The app is configured to alert subscribers of public holidays at 9:00 daily (host time zone). The Django admin user interface also allows customised newsletter-type alerts to be sent to subscribers.  

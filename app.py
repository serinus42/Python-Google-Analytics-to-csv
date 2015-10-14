"""A simple example of how to access the Google Analytics API."""

import argparse

from apiclient.discovery import build
from oauth2client.client import SignedJwtAssertionCredentials


import httplib2
from oauth2client import client
from oauth2client import file
from oauth2client import tools
import operator
import time 
import datetime
import csv
from operator import itemgetter



companies = [
    {
        "name" : "ING",
        "slug" : "storing/ing",
        "indicator" : "ing-9"
    },
    {
        "name" : "Rabobank",
        "slug" : "storing/rabobank",
        "indicator" : "rabobank-13"
    },
    {
        "name" : "SNS Bank",
        "slug" : "storing/sns-bank",
        "indicator" : "sns-bank-10019"
    },
    {
        "name" : "ABN Amro",
        "slug" : "storing/abn-amro",
        "indicator" : "abn-amro-29"
    }]


def get_service(api_name, api_version, scope, key_file_location,
                service_account_email):
  """Get a service that communicates to a Google API.

  Args:
    api_name: The name of the api to connect to.
    api_version: The api version to connect to.
    scope: A list auth scopes to authorize for the application.
    key_file_location: The path to a valid service account p12 key file.
    service_account_email: The service account email address.

  Returns:
    A service that is connected to the specified API.
  """

  f = open(key_file_location, 'rb')
  key = f.read()
  f.close()

  credentials = SignedJwtAssertionCredentials(service_account_email, key,
    scope=scope)

  http = credentials.authorize(httplib2.Http())

  # Build the service object.
  service = build(api_name, api_version, http=http)

  return service


def get_first_profile_id(service):
  # Use the Analytics service object to get the first profile id.

  # Get a list of all Google Analytics accounts for this user
  accounts = service.management().accounts().list().execute()

  if accounts.get('items'):
    # Get the first Google Analytics account.
    account = accounts.get('items')[0].get('id')

    # Get a list of all the properties for the first account.
    properties = service.management().webproperties().list(
        accountId=account).execute()

    if properties.get('items'):
      # Get the first property id.
      property = properties.get('items')[0].get('id')

      # Get a list of all views (profiles) for the first property.
      profiles = service.management().profiles().list(
          accountId=account,
          webPropertyId=property).execute()

      if profiles.get('items'):
        # return the first view (profile) id.
        return profiles.get('items')[0].get('id')

  return None


def pagehits(service,company_slug):
#collect page hits for all companies
  #start_date='2014-10-23'
  #end_date='2014-10-23'
  start_date='2014-01-01'
  end_date='2015-10-12'
#add company_filter as function var
  return service.data().ga().get(
      ids='ga:' + str(56043106),
      start_date=start_date,
      end_date=end_date,
      metrics='ga:sessions',
      dimensions='ga:date',
      filters='ga:medium==organic;ga:landingPagePath=~' + company_slug,
      output='json').execute()
  #,samplingLevel='HIGHER_PRECISION'


def events(service,company_indicator,date):
# collect event with the highest count
  return service.data().ga().get(
      ids='ga:' + str(72566635),
      start_date=date,
      end_date=date,
      metrics='ga:uniqueEvents',
      dimensions='ga:eventLabel',
      filters='ga:eventCategory==indicator;ga:eventAction==' + company_indicator,
      output='json').execute()
    #,samplingLevel='HIGHER_PRECISION'

def pagehit_results(results):
  if results:
    data = {}
    rows = results.get('rows')
    for row in rows:
      date = row[0]
      date = str(datetime.datetime.strptime(date, "%Y%m%d").date())
      value = row[1]
      data[date] = value
    return data
  else:
    print 'No results found'

def events_results(results):
    if results:
        rows = results.get('rows')
        if rows == None:
          highest = None
        else:
          highest = None
          proper_rows = []
          for row in rows:
            proper_rows.append([row[0],int(row[1])])
          proper_rows = sorted(proper_rows, key=itemgetter(1), reverse=True)
          if proper_rows[0][1] and int(proper_rows[0][1]) > 14:
            highest = proper_rows[0][0]
        return highest

def main():
  # Define the auth scopes to request.
  scope = ['https://www.googleapis.com/auth/analytics.readonly']

  # Use the developer console and replace the values with your
  # service account email and relative location of your key file.
  service_account_email = '*****'
  key_file_location = 'client_secrets.p12'

  # Authenticate and construct service.
  service = get_service('analytics', 'v3', scope, key_file_location,
    service_account_email)
  #profile = get_first_profile_id(service)
  with open('data.csv', 'wb') as csvfile:
    mydata = csv.writer(csvfile, delimiter=',',
                        quotechar='|', quoting=csv.QUOTE_MINIMAL)
    csv_header = ('Company','Date','Reports','Most_reported')
    mydata.writerow(csv_header)
    for company in companies:
      company_name = company['name']
      company_slug = company['slug']
      company_indicator = company['indicator']
      
      views = pagehit_results(pagehits(service,company_slug))
      for view in views:
        date = view
        view_count = views[view] 
        most_reported = events_results(
          events(service,company_indicator,date))
        csv_row = company_name,date,view_count,most_reported
        print csv_row
        mydata.writerow(csv_row)

if __name__ == '__main__':
  main()

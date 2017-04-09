# Copyright 2017 Laurent Picard
# Licensed under the Apache License, Version 2.0
# http://www.apache.org/licenses/LICENSE-2.0
# 
# What it does:
# 1. Retrieval of DJU monthly data for a range of years
# 2. Creation of CSV with monthly data

import sys
import datetime
import urllib
import os
import re
import csv

# File info
DATA_ROOT = './data/'
HTML_DIR = DATA_ROOT + 'infoclimat/'
CSV_DIR = DATA_ROOT + 'dju/'
CSV_FILE = 'dju.csv'
# Data source web site
INFOCLIMAT_URL_FMT = 'http://www.infoclimat.fr/climatologie/annee/%d/paris-montsouris/valeurs/07156.html'
# Years to process
YEAR_FIRST = 2012
YEAR_NOW = datetime.datetime.now().year

def check_make_dir(dir):
  if not os.path.isdir(dir):
    os.makedirs(dir)

def localize_floats(row):
  return [
    str(el).replace('.', ',') 
    for el in row
  ]

def get_dju_data():
  check_make_dir(DATA_ROOT)
  check_make_dir(HTML_DIR)
  check_make_dir(CSV_DIR)

  # List of rows: [YEAR, DJU1,... DJUn] with n <= 12
  rows_data = []

  for year in range(YEAR_FIRST, YEAR_NOW+1):
    print "<", year, ">"
    htmlfilename = '%s%d.html' % (HTML_DIR, year)

    if not os.path.isfile(htmlfilename):
      print 'Retrieving %s' % (htmlfilename)
      url = INFOCLIMAT_URL_FMT % year
      urllib.urlretrieve(url, htmlfilename)

    # Current year is likely to be incomplete
    # whereas previous years have complete data
    row_complete = False
 
    with open(htmlfilename, 'r') as htmlfile:
      print "Parsing..."
      text = htmlfile.read()

      # Expected float data can be found in JS code
      # "DJU chauffagiste","type":"line","data":[jan_float,...dec_float] 
      search = re.search(r'"DJU chauffagiste","type":"line","data":\[(.*?)\]', text)
      if not search:
        print 'Could not find DJU data'
        break

      month_data_line = search.group(1)
      #print 'Found[%s]' % (month_data_line)
      month_data = re.findall("\d+\.\d+|\d+", month_data_line)
      
      monthcount = len(month_data)
      row_complete = (monthcount == 12)
 
      row_data = [year] + month_data
      rows_data.append(row_data)

    if not row_complete:
      print "Removing incomplete file..."
      os.remove(htmlfilename) # File will be retrieved again next time

  #print "rows_data", rows_data

  #"""
  csvfilename = '%s%s' % (CSV_DIR, CSV_FILE)
  with open(csvfilename, 'w') as csvfile:
    print "Writing %s..." % (csvfilename)
    writer = csv.writer(csvfile, delimiter=';', lineterminator='\n')
    headers = ['year'] + ['m'+str(i+1) for i in range(12)]
    writer.writerow(headers)
    for row in rows_data:
      writer.writerow(localize_floats(row))
  #"""
    
def main():
  get_dju_data()
  
if __name__ == "__main__":
  main()

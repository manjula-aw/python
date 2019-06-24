import socket
import requests as req

# Note: Replace following value with your domain name (e.g. if you want to check for a domain for 'myblog' with any TLD, put myblog
domainprefix='myblog'

outputfilepath="unregistereddomains-for-{}.txt".format(domainprefix);
resp = req.get("https://data.iana.org/TLD/tlds-alpha-by-domain.txt")

# Clears the content of output file.
open(outputfilepath, 'w').close()

for tld in resp.iter_lines():    
   tld=tld.decode().lower().strip();
   
   if (len(tld) <= 3 and not tld.startswith('#') and not tld.startswith('xn--')):       
       domainname = "{}.{}".format(domainprefix,tld);
       try:
           socket.gethostbyname_ex(domainname);
       except:
               print("{} is available.".format(domainname))
               fout=open(outputfilepath,'a');
               fout.write("{} is available.\n".format(domainname))
               fout.close();
                 

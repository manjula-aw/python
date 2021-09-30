import ipaddress
import struct
import socket
import json
import requests

inputfile_badIps="ip-list.txt"
outputfile="extracted-bad-ips-from-aws.txt"

# to read from aws region json
# netmasks
networks = []

data = json.loads(requests.get("https://ip-ranges.amazonaws.com/ip-ranges.json").text)

original_netmasks = []

for i in data['prefixes']:
    original_netmasks.append(i["ip_prefix"])

uniqe_netmasks = set(original_netmasks)


for i in uniqe_netmasks:
    
    n = ipaddress.ip_network(i)
    netw = int(n.network_address)
    mask = int(n.netmask)

    networks.append({"netw":netw, "mask":mask})



# Ip addresses
ip_list = []

# read from file and loop
with open(inputfile_badIps) as fp:
    for current_ip in fp:
        current_ip = current_ip.strip();
        
        a = int(ipaddress.ip_address(current_ip))
        a = struct.unpack('!I', socket.inet_pton(socket.AF_INET, current_ip))[0]
        a = struct.unpack('!I', socket.inet_aton(current_ip))[0]  
        ip_list.append({"numberic":a,"standard":current_ip})

with open(outputfile, 'w') as f:
    for thisnet in networks:
        for i, thisip in enumerate(ip_list):
            in_network = (thisip["numberic"] & thisnet["mask"]) == thisnet["netw"]
            if in_network:
                f.write("{}\n".format(thisip["standard"]))
                #ip_list[i]  = None

print("=======")

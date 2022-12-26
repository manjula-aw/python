from scapy.all import *
import os
import urllib.request
import geoip2.database
import ipaddress
import folium
from folium.vector_layers import PolyLine
import webbrowser
import branca
from math import atan
from math import atan2
from math import cos
from math import sin


target_host = "example.com"

# GeoLiteCity database file URL
url = "https://github.com/P3TERX/GeoLite.mmdb/raw/download/GeoLite2-City.mmdb"
destination_path = "GeoLite2-City.mmdb"

ipdetails_of_the_route = []
legend_html_pre = '''
{% macro html(this, kwargs) %}
<div style="position: fixed;
text-align: center;
top:10px;
left: 50%;
transform: translate(-50%, 0);
z-index:9999;
font-size:16px;
font-weight: bold;
margin:20px;
padding:10px;
border: 1px solid black;
background-color:#ffffff;
opacity:0.7;">
Traceroute to
'''
legend_html_pre = legend_html_pre + target_host
legend_html_pre = legend_html_pre + '''</div>
<div style="
    position: fixed; 
    top: 50px;
    left: 50px;
    z-index:9999;
    font-size:12px;
    ">
    <table style="background-color:#ffffff;opacity:0.7;border-collapse:collapse;border:1px solid;margin:20px;padding:10px">
    '''

legend_html_post = '''
    </table>
    </div>
    {% endmacro %}
    '''
legend_html_mid = '<tr style="color:#000000;margin-left:20px;margin-right:20px;padding:10px"><th>&emsp;Current Hop#</th><th>&emsp;IP Address</th><th>&emsp;Country Name</th></tr>'

def traceroute(host):
    # Set the maximum number of hops to 30
    max_hops = 30
    # Set the timeout value for each hop to 2 seconds
    timeout = 2
    # Set the base sequence number for the ICMP packets
    seq_number = 1
    # Set the starting hop value to 1
    current_hop = 1
    # Set the flag to indicate whether the host has been reached
    reached_host = False
    

    print("Tracing route to {} over a maximum of {} hops:".format(host, max_hops))

    # Loop through the maximum number of hops
    while current_hop <= max_hops and not reached_host:
        # Send an ICMP echo request packet to the host with the current hop value as the ttl (time-to-live)
        response_packet = sr1(IP(dst=host, ttl=current_hop) / ICMP(id=seq_number, seq=seq_number), timeout=timeout, verbose=0)

        # If a response packet was received
        if response_packet is not None:
            # If the response packet is an ICMP time exceeded packet
            if response_packet.haslayer(ICMP) and response_packet[ICMP].type == 11:
                print("{}\t{} ({})".format(current_hop, response_packet.src, response_packet[IP].src))
                geoipdetails(response_packet[IP].src, current_hop)

                seq_number += 1
                current_hop += 1
            # If the response packet is an ICMP echo reply packet
            elif response_packet.haslayer(ICMP) and response_packet[ICMP].type == 0:
                print("{}\t{} ({})".format(current_hop, response_packet.src, response_packet[IP].src))
                geoipdetails(response_packet[IP].src, current_hop)
                reached_host = True
        # If no response packet was received
        else:
            # Print a "*" to indicate a timeout
            print("{}\t*".format(current_hop))

            current_hop += 1

def geoipdetails(ip, current_hop):
    global legend_html_mid
    address = ipaddress.ip_address(ip)
    if address.is_global:
        reader = geoip2.database.Reader(destination_path)
        location = reader.city(ip)
        ipdetails_of_the_route.append({"Country":location.country.name,"Latitude":location.location.latitude,"Longitude":location.location.longitude,"IP":ip})
        legend_html_mid = legend_html_mid + '<tr style="color:#000000;margin:5px;padding:5px"><td>&emsp;' + str(current_hop) + '</td><td>&emsp;' + ip + '</td><td>&emsp;' + location.country.name + '</td></tr>'
        
    else:
        # Private IP address
        legend_html_mid = legend_html_mid + '<tr style="color:#000000;margin:5px;padding:5px"><td>&emsp;' + str(current_hop) + '</td><td>&emsp;' + ip + '</td><td>&emsp;Private IP</td></tr>'
                
        if len(ipdetails_of_the_route) > 0:
            last_ip_details = ipdetails_of_the_route[-1]
        else:
            last_ip_details = {"Country":"Private IP","Latitude":0,"Longitude":0}
            
        ipdetails_of_the_route.append({"Country":"Private IP","Latitude":last_ip_details["Latitude"],"Longitude":last_ip_details["Longitude"],"IP":ip})


# Download the GeoLiteCity database, only if it does not exists or more than 1 day old
if not os.path.exists(destination_path) or (time.time() - os.path.getmtime(destination_path) > 86400):
    print("Downloading GeoLiteCity database file...")
    try:
        urllib.request.urlretrieve(url, destination_path)
        print("Done.")
    except Exception as e:
        print("An error occurred while downloading GeoLiteCity database file.", e)
else:
    print("GeoLiteCity database file already exists and is up to date.")

# Run the trace route
traceroute(target_host)

# show IP locations in a map
f = folium.Figure(width=1000, height=500)
m = folium.Map(max_bounds=True, zoom_start=2.2, location=[0, 0]).add_to(f)

# Add a marker for each hop location
current_ip_latitude = 0
current_ip_longitude = 0
first_loc = True
for ip_location in ipdetails_of_the_route:
    if ip_location["Country"] != "Private IP":
        prev_ip_latitude = current_ip_latitude
        prev_ip_longitude = current_ip_longitude
        current_ip_latitude = ip_location["Latitude"]
        current_ip_longitude = ip_location["Longitude"]
        folium.Marker(location=[current_ip_latitude, current_ip_longitude],tooltip=str(ip_location["Country"]+ " " + ip_location["IP"])).add_to(m)
        if first_loc:
            first_loc = False
        else:
            PolyLine([[prev_ip_latitude, prev_ip_longitude], [current_ip_latitude, current_ip_longitude]], color='red', weight=2, opacity=1, arrow_style='fancy', arrow_size=40).add_to(m)

            latitude_difference = current_ip_latitude - prev_ip_latitude
            longitude_difference = current_ip_longitude - prev_ip_longitude
            
            if longitude_difference != 0:
                arrow_loc_lat = (current_ip_latitude + prev_ip_latitude)/2
                arrow_loc_lon = (current_ip_longitude + prev_ip_longitude)/2
                rotate = atan2(sin(longitude_difference)*cos(current_ip_latitude),cos(prev_ip_latitude)*sin(current_ip_latitude)-sin(prev_ip_latitude)*cos(current_ip_latitude)
                                *cos(longitude_difference))
                folium.RegularPolygonMarker(location=(arrow_loc_lat, arrow_loc_lon), fill_color='red', number_of_sides=3, radius=4, rotation=rotate, fill=True, color='red').add_to(m)



# Add traceroute hops as a legend to the map
legend_html = legend_html_pre + legend_html_mid + legend_html_post
legend = branca.element.MacroElement()
legend._template = branca.element.Template(legend_html)

folium.LayerControl().add_to(m)
m.get_root().add_child(legend)

# Display the map
f.save("map.html")
webbrowser.open("map.html")

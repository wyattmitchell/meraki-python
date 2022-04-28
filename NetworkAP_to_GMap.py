""" Copyright (c) 2022 Cisco and/or its affiliates.
This software is licensed to you under the terms of the Cisco Sample
Code License, Version 1.1 (the "License"). You may obtain a copy of the
License at
           https://developer.cisco.com/docs/licenses
All use of the material herein must be in accordance with the terms of
the License. All rights not expressly granted by the License are
reserved. Unless required by applicable law or agreed to separately in
writing, software distributed under the License is distributed on an "AS
IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied. 
"""

import meraki
import json
import csv

# Instructions:
# Make sure to set your APIKEY in environment variable MERAKI_DASHBOARD_API_KEY.
# 
# Script will prompt to select Org, Network and Floorplan then create a CSV file for all APs in that floorplan.
# This CSV can be imported into Google Maps to visualize lat/lng per device.
#
# Set verbose_console to True for more console logging.

# Variables:
verbose_console = False

# Connect to Dashboard
dashboard = meraki.DashboardAPI(suppress_logging=not verbose_console)

def printj(ugly_json_object):

    # The json.dumps() method converts a JSON object into human-friendly formatted text
    pretty_json_string = json.dumps(ugly_json_object, indent = 2, sort_keys = False)
    return print(pretty_json_string)

def getBssid(serial):

    # Get all SSID info
    wireless_status_all = dashboard.wireless.getDeviceWirelessStatus(serial)
   
    if verbose_console == True:
        ## Print all SSIDs for AP
        print("This is the wireless status for AP: " + serial)
        printj(wireless_status_all)

    # Get only active SSIDs
    wireless_status = [i for i in wireless_status_all['basicServiceSets'] if i['enabled'] == True ]
    wireless24_status = wireless_status[0]
    wireless5_status = wireless_status[1]

    if verbose_console == True:
        ## Print all active SSIDs for APs
        print("These are the active SSIDs for AP: " + serial)
        printj(wireless24_status)
        printj(wireless5_status)

    return wireless24_status, wireless5_status

def getLldp(serial):

    # Get LLDP/CDP info
    device_lldps_info = dashboard.devices.getDeviceLldpCdp(serial)

    if verbose_console == True:
        ## Print LLDP/CDP info
        print("This the LLDP/CDP info for AP: " + serial)
        printj(device_lldps_info)

    # Check if info is empty (LLDP/CDP disabled upstream) and return NA
    if device_lldps_info == {}:
        # print("Nothing for AP serial: " + serial)
        return {'systemName': 'NA','portId': 'NA'}
        
    return device_lldps_info['ports']['wired0']['lldp']

def select_org(dashboard):
    # Fetch and select the organization
    print('\n\nFetching organizations...\n')
    organizations = dashboard.organizations.getOrganizations()
    organizations.sort(key=lambda x: x['name'])
    counter = 0
    print('Select organization:')
    for organization in organizations:
        orgName = organization['name']
        print(f'{counter} - {orgName}')
        counter+=1
    isDone = False
    while isDone == False:
        selected = input('\nSelect the organization ID you would like to query: ')
        try:
            if int(selected) in range(0,counter):
                isDone = True
            else:
                print('\tInvalid Organization Number\n')
        except:
            print('\tInvalid Organization Number\n')
    return(organizations[int(selected)]['id'], organizations[int(selected)]['name'])

def select_net(dashboard, orgId):
    # Fetch and select the network
    print('\n\nFetching networks...\n')
    networks = dashboard.organizations.getOrganizationNetworks(orgId)
    networks.sort(key=lambda x: x['name'])
    counter = 0
    print('Select organization:')
    for net in networks:
        netName = net['name']
        print(f'{counter} - {netName}')
        counter+=1
    isDone = False
    while isDone == False:
        selected = input('\nSelect the network ID you would like to query: ')
        try:
            if int(selected) in range(0,counter):
                isDone = True
            else:
                print('\tInvalid Network Number\n')
        except:
            print('\tInvalid Network Number\n')
    return(networks[int(selected)]['id'], networks[int(selected)]['name'])

def select_floorplan(netId):
    # Fetch and select the floorplan
    print('\n\nFetching floorplans...\n')
    try:
        plans = dashboard.networks.getNetworkFloorPlans(networkId=netId)
    except:
        print('\nCould not gather floorplans.')
        exit()
    plans.sort(key=lambda x: x['name'])
    counter = 0
    print('Select floorplan:')
    for plan in plans:
        planName = plan['name']
        print(f'{counter} - {planName}')
        counter+=1
    isDone = False
    while isDone == False:
        selected = input('\nSelect the floorplan you would like to query: ')
        try:
            if int(selected) in range(0,counter):
                isDone = True
            else:
                print('\tInvalid floorplan Number\n')
        except:
            print('\tInvalid floorplan Number\n')
    return dashboard.networks.getNetworkFloorPlan(networkId=netId, floorPlanId=plans[int(selected)]['floorPlanId'])

orgId, orgName = select_org(dashboard)
netId, netName = select_net(dashboard, orgId)
floorplan = select_floorplan(netId)

# Extract devices on floorplan
devices = floorplan['devices']

# Get all MR's
fp_aps = [i for i in devices if 'MR' in i['model']]

if verbose_console == True:
    ## Print all AP detail
    print('These are the APs:')
    printj(fp_aps)

# Write CSV per organization with row per active SSID & Band for every AP
csvname = str(floorplan['name'] + '_AP_GMAP.csv')
csvname = csvname.replace("\"", "")
print(f'Writing CSV file {csvname}')
with open(csvname, 'w', encoding='utf-8', newline='') as f:
    csvheader = ['lat', 'long', 'AP_NAME,SSID_Channel,Power']
    writer = csv.writer(f)
    writer.writerow(csvheader)
    for i in fp_aps:
        bssid_info24, bssid_info5 = getBssid(i['serial'])
        apdata = i['name'] + ", " + str(bssid_info5['channel']) + ", " + str(bssid_info5['power'])
        data = [i['lat'], i['lng'], apdata]
        writer.writerow(data)
print(f'{csvname} complete. Continuing...')
print('Script finished.')
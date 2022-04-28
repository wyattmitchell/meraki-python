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
import csv

# Instructions:
# Make sure to set your APIKEY in environment variable MERAKI_DASHBOARD_API_KEY.
# Script will display and prompt you to select OrgId and NetworkId then ask for a string to match device type.
# Partial matches allowed for device type. Example 'MR' will capture all AP models. 'MR4' will match MR44, MR46, etc.
# To ignore specific devices, create ignorelist.csv in the same path as the script. One name or serial number per line in a single column.
#
# Recommended: Perform a test run with the final line commented to see what will be rebooted and what will be skipped.
# When ready, uncomment last line to enable the rebootDevice API call.
#
# IMPORTANT: Devices will not reboot until the last line is uncommented.

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

dashboard = meraki.DashboardAPI(suppress_logging=True)

# Read ignorelist.csv for device names or serials to skip.
ignorelist = []
try:
    with open('ignorelist.csv', 'r') as file:
        ignorelist = [row[0] for row in csv.reader(file)]
    print('\nignorelist.csv found and imported.\n')
except:
    print('\nignorelist.csv could not be found or read. Continuing...\n')

# Select org and network
orgId, orgName = select_org(dashboard)
netId, netName = select_net(dashboard, orgId)

# Get all devices in Net
devices = dashboard.networks.getNetworkDevices(networkId=netId)

# Define type of device you want to reboot.
# Partial matches allowed. 'MR' will capture all AP models. 'MR4' will match MR44, MR46, etc.
print('\nEnter device type to reboot. ')
print('Partial matches allowed. "MR" will capture all AP models. "MR4" will match MR44, MR46, etc.')
devicetype = input('Enter device type: ')

# Get all device types specified in devicetype variable
devices_selected = [i for i in devices if devicetype in i['model']]

print(f'\nListing all devices matching "{devicetype}" in selected network:')

for dev in devices_selected:
    devName = dev['name']
    print(f'{devName}')

reboot = input('\nContinue? (Y/N): ')

if reboot == 'Y' or 'y':
    # Reboot all devices, ignoring any name or serial in ignorelist variable
    for i in devices_selected:
        if i['name'] in ignorelist:
            print("Skipping " + i["name"] + " " + i['model'] + " " + i['serial'] + ". Name is in ignorelist.")
            continue
        if i['serial'] in ignorelist:
            print("Skipping " + i["name"] + " " + i['model'] + " " + i['serial'] + ". Serial is in ignorelist.")
            continue
        print("Rebooting " + i["name"] + " " + i['model'] + " " + i['serial'])
        # dashboard.devices.rebootDevice(serial=i['serial'])
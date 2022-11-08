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
import os

# Instructions:
# Set your APIKEY in environment variable MERAKI_DASHBOARD_API_KEY.

# ---- Begin Script Functions ----

def select_org(dashboard):
    # Fetch, sort by name and select organization
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
    # Fetch and select network
    networks = dashboard.organizations.getOrganizationNetworks(orgId)

    # Prompt search for network name to filter for shorter list.
    searchName = input('Enter search string or leave blank for all networks: ')

    netList = []
    while netList == []:
        if searchName == '':
            # Return all networks for blank search string.
            netList = networks
        else:   
            # Return networks matching searchName.
            for net in networks:
                if searchName in net["name"]:
                    netList.append(net)
        # Validate at least 1 network is returned and prompt for new search string if empty.
        if netList == []:
            print(f'No networks found matching {searchName}.')
            searchName = input('Enter search string or leave blank for all networks: ')
    
    netList.sort(key=lambda x: x['name'])
    counter = 0

    print('Networks:')
    for net in netList:
        netName = net['name']
        print(f'{counter} - {netName}')
        counter+=1
    isDone = False
    while isDone == False:
        selected = input('\nSelect the network ID you would like to use: ')
        try:
            if int(selected) in range(0,counter):
                isDone = True
            else:
                print('\tInvalid Network Number\n')
        except:
            print('\tInvalid Network Number\n')
    return(netList[int(selected)]['id'], netList[int(selected)]['name'])

def get_network_device_list(dashboard, netId, devString):
    # Fetch all network devices
    devices = dashboard.networks.getNetworkDevices(netId)
    
    if consoleDebug == True: print(f'{devices}')

    deviceList = []
    
    # Filter networks
    for device in devices:
        if devString in device["model"]:
            deviceList.append(device)

    if consoleDebug == True:
        print(deviceList)

    return deviceList

def select_device(deviceList):
    # Sort and select from input devices list.
    deviceList.sort(key=lambda x: x['name'])
    counter = 0
    for dev in deviceList:
        devName = dev['name']
        print(f'{counter} - {devName}')
        counter+=1
    isDone = False
    while isDone == False:
        selected = input('\nSelect the device you would like to migrate: ')
        try:
            if int(selected) in range(0,counter):
                isDone = True
            else:
                print('\tInvalid Device Number\n')
        except:
            print('\tInvalid Device Number\n')
    return(deviceList[int(selected)]['serial'], deviceList[int(selected)]['name'])

def get_yn_response(question):
    # Prompt for user Y/N response to input question.
    while True:
        resp = input(question).strip()
        if resp.lower() in ['y','n']:
            return resp.lower()
        print('Invalid response. Please enter Y or N.\n')


# ---- Begin Script Main ----

# Debug options
### Additional logging to Console
consoleDebug = False
### Log Meraki SDK activity to file
logDebug = False

# Connect to dashboard, select org and network
dashboard = meraki.DashboardAPI(suppress_logging=not logDebug)
orgId, orgName = select_org(dashboard)

print('\n\nSelect source network...\n')
srcNetId, srcNetName = select_net(dashboard, orgId)

print('\n\nSelect destination network...\n')
dstNetId, dstNetName = select_net(dashboard, orgId)

confirm = get_yn_response(f'\nSource network {srcNetName} and destination network {dstNetName} selected. Continue? (Y/N): ')

if confirm == 'n':
    exit()

# Get list of network devices
devString = 'MR'
deviceList = get_network_device_list(dashboard, srcNetId, devString)
if deviceList == []:
    print('No matching devices found in network. Exiting...')

if consoleDebug == True: print(deviceList)

# Get source and destination floorplans.
src_floorplans = dashboard.networks.getNetworkFloorPlans(srcNetId)
dst_floorplans = dashboard.networks.getNetworkFloorPlans(dstNetId)

for ap in deviceList:
    serial = ap['serial']
    try:
        name = ap['name']
    except:
        name = ap['mac']
    tags = ap['tags']
    lat = ap['lat']
    lng = ap['lng']
    address = ap['address']

    # Get source floorplan name.
    srcFloorplan = ''
    for fp in src_floorplans:
        if ap['floorPlanId'] == fp['floorPlanId']:
            srcFloorplan = fp['name']
            break
            
    print(f'Source floorplan is {srcFloorplan}.')

    # Match source FP name to destination name.
    dstFound = False
    for fp in dst_floorplans:
        if srcFloorplan == fp['name']:
            dstFloorplan = fp['floorPlanId']
            print('Destination floorplan match found.\n')
            dstFound = True
            break
    
    if dstFound == False:
        print(f'No matching destination floor plan found for {name}. Continuing...')

    print(f'\nRemoving {name} from source network...')
    dashboard.networks.removeNetworkDevices(srcNetId, serial)
    claimSerial = [serial]
    print(f'Adding {name} to destination network...')
    dashboard.networks.claimNetworkDevices(dstNetId, claimSerial)            

    if dstFound == True:
        try:
            dashboard.devices.updateDevice(
                serial = serial,
                name = name,
                tags = tags,
                lat = lat,
                lng = lng,
                address = address,
                floorPlanId=dstFloorplan
            )
        except:
            print(f'Could not configure {name}.')
    else:
        try:
            dashboard.devices.updateDevice(
                serial = serial,
                name = name,
                tags = tags,
                lat = lat,
                lng = lng,
                address = address
            )
        except:
            print(f'Could not configure {name}.')
                
print('Complete')
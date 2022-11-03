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
    networks = dashboard.organizations.getOrganizationNetworks(orgId)

    # Prompt search for network name to filter for shorter list.
    search_name = input('Enter search string: ')
    netList = []
    # Filter only MS devices
    for net in networks:
        if search_name in net["name"]:
            netList.append(net)
    
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
    isDone = False
    while isDone == False:
        resp = input(question)
        try:
            if resp == 'Y' or 'y' or 'N' or 'n':
                isDone = True
            else:
                print('\tInvalid response. Please enter Y or N.\n')
        except:
            print('\tInvalid response.\n')
    return resp.lower()

def clear():
     os.system('cls' if os.name=='nt' else 'clear')
     return("   ")
# ---- Begin Script Execution ----

consoleDebug = False
logDebug = False

# Connect to dashboard, select org and network
dashboard = meraki.DashboardAPI(suppress_logging=not logDebug)
selected_org, orgName = select_org(dashboard)

print('\n\nSelect source network...\n')
src_net, src_netName = select_net(dashboard, selected_org)

print('\n\nSelect destination network...\n')
dst_net, dst_netName = select_net(dashboard, selected_org)

print(f'\nSource network {src_netName} and destination network {dst_netName} selected. Continuing...')

# Get list of network devices
devString = 'MR'
deviceList = get_network_device_list(dashboard, src_net, devString)
if deviceList == []:
    print('No matching devices found in network. Exiting...')

if consoleDebug == True: print(deviceList)

# Get source and destination floorplans.
src_floorplans = dashboard.networks.getNetworkFloorPlans(src_net)
dst_floorplans = dashboard.networks.getNetworkFloorPlans(dst_net)

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
    dashboard.networks.removeNetworkDevices(src_net, serial)
    claimSerial = [serial]
    print(f'Adding {name} to destination network...')
    dashboard.networks.claimNetworkDevices(dst_net, claimSerial)            

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
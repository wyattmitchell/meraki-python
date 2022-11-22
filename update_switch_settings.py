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
# Set your APIKEY in environment variable MERAKI_DASHBOARD_API_KEY.
# Input CSV must have columns as: XXXXX_____NEED TO UPDATE_____XXXXX

# ---- Begin Script ----

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

consoleDebug = False
logDebug = False

# Connect to dashboard, select org and network
dashboard = meraki.DashboardAPI(suppress_logging=not logDebug)
selected_org, orgName = select_org(dashboard)
selected_net, netName = select_net(dashboard, selected_org)

# Prompt for input file
in_path = input('Enter CSV file name: ')

with open(in_path, 'r') as infile:
    rows = []
    try:
        csvreader = csv.reader(infile)
        csvheader = next(csvreader)
        for row in csvreader:
            rows.append(row)
        print(f'\n{in_path} imported. Continuing...\n')
    except:
        print(f'\nCould not open or read {in_path}. Exiting script.\n')

for row in rows:
    if consoleDebug == True: print(row)
    if row[0] == "ignore":
        pass
    elif row[0] == "switch":
        rowPurpose, sName, sSerial, sAddress, *rest = row 
        try:
            response = dashboard.devices.updateDevice(serial=sSerial, name=sName, address=sAddress)
            print(f'\n{sSerial} updated to {sName} at {sAddress}')
        except Exception as error:
            print(str(error))
    elif row[0] == "port":
        rowPurpose, pName, pID, pEnable, pPOE, pType, pVlan, pVoice, pAllowed, pSTPenable, pSTPguard = row
        if pVoice == '0':
            pVoice = None
        try: 
            if pType == "access":
                response = dashboard.switch.updateDeviceSwitchPort(serial=sSerial, portId=pID, name=pName, enabled=pEnable, poeEnabled=pPOE, type=pType, vlan=pVlan, voiceVlan=pVoice, rstpEnabled=pSTPenable, stpGuard=pSTPguard)
                print(f'Port {pID} configured as {pType} with data vlan {pVlan} and voice vlan {pVoice}.')
            elif pType == "trunk":
                response = dashboard.switch.updateDeviceSwitchPort(serial=sSerial, portId=pID, name=pName, enabled=pEnable, poeEnabled=pPOE, type=pType, vlan=pVlan, allowedVlans=pAllowed, rstpEnabled=pSTPenable, stpGuard=pSTPguard)
                print(f'Port {pID} configured as {pType} with native vlan {pVlan} and allowed vlans {pVoice}.')
        except Exception as error:
            print(str(error))
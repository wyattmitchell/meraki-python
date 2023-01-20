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

def select_ssid(dashboard, netId):
    # Fetch and select network
    items = dashboard.wireless.getNetworkWirelessSsids(netId)

    # Prompt search for string to filter for shorter list.
    searchStr = input('Enter search string or leave blank for all: ')

    list = []
    while not list:
        if searchStr == '':
            # Return all for blank search string.
            list = items
        else:   
            # Return networks matching searchStr.
            for item in items:
                if searchStr in item["name"]:
                    list.append(item)
        # Validate at least 1 network is returned and prompt for new search string if empty.
        if not list:
            print(f'No matches found for {searchStr}.')
            searchStr = input('Enter search string or leave blank for all: ')
    
    list.sort(key=lambda x: x['name'])
    counter = 0

    print('SSIDs:')
    for item in list:
        name = item['name']
        print(f'{counter} - {name}')
        counter+=1
    isDone = False
    while isDone == False:
        selected = input('\nSelect the SSID you would like to use: ')
        try:
            if int(selected) in range(0,counter):
                isDone = True
            else:
                print('\tInvalid SSID Number\n')
        except:
            print('\tInvalid SSID Number\n')
    return(list[int(selected)]['number'], list[int(selected)]['name'])

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
consoleDebug = True
### Log Meraki SDK activity to file
logDebug = False

# Connect to dashboard, select org and networks
dashboard = meraki.DashboardAPI(suppress_logging=not logDebug)
orgId, orgName = select_org(dashboard)

print('Select network:')
netId, netName = select_net(dashboard, orgId)

print('Select SSID to filter clients:')
ssidNum, ssidName = select_ssid(dashboard, netId)

isDone = 'n'
while isDone == 'n':
    appName = input('Enter search string to match with application: ')
    isDone = get_yn_response(f'{appName} entered for search. Is that correct? (Y/N): ')

clientList = dashboard.networks.getNetworkClients(netId, timespan=604800)

# Filter client list to only those matching selected SSID
filteredClientList = []
filteredClientKey = ''
for client in clientList:
    if client['ssid'] == ssidName:
        filteredClientList.append(client)
        filteredClientKey = filteredClientKey + client['id'] + ','
if consoleDebug == True: print(f'Client keys: {filteredClientKey}')
if consoleDebug == True: print(f'Client list: {filteredClientList}')


# Get application usage for all selected clients
appUsageAll = dashboard.networks.getNetworkClientsApplicationUsage(networkId=netId, clients=filteredClientKey, timespan=604800)

# Filter appUsage list to only those clients matching application search string
appUsers = []
for client in appUsageAll:
    apps = client['applicationUsage']
    for app in apps:
        if appName in app['application']:
            if consoleDebug == True:
                matchedApp = app['application']
                print(f'Matched app {matchedApp}.')
            appUsers.append(client['clientId'])
if consoleDebug == True: print(f'App users list: {appUsers}')

# Collect final list of clients that used the selected SSID & the matched application
finalClientList = []
for client in filteredClientList:
    if client['id'] in appUsers:
        finalClientList.append(client)

# Do some output or export
print('\nThe following clients match this search:\n')
for client in finalClientList:
    desc = client['description']
    mac = client['mac']
    ip = client['ip']
    recentDevice = client['recentDeviceName']
    print(f'Client {desc} with IP: {ip}, MAC {mac}, and last connected on {recentDevice}.')
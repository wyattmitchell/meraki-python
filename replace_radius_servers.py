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
import tabulate

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

def select_net_search(dashboard, orgId):
    # Fetch and select network
    networks = dashboard.organizations.getOrganizationNetworks(orgId)

    # Prompt search for network name to filter for shorter list.
    print('Proceeding to network selection.')
    searchName = input('Enter search string or leave blank to display all networks: ')

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
            searchName = input('Enter search string or leave blank to display all networks: ')
    
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

def replace_ssid_radius(dashboard, netId, radiusUpdate, replaceAll, filterName, ssidNum, ssidName):
    
    ssidConfig = []
    if replaceAll == 'y':
        # Get all SSIDs for the network
        ssidConfig = dashboard.wireless.getNetworkWirelessSsids(netId)
    elif replaceAll == 'n':
        # Get single SSID to update
        response = dashboard.wireless.getNetworkWirelessSsid(netId, number=ssidNum)
        ssidConfig.append(response)

    if filterName == 'y':
        filteredSsid = []
        for ssid in ssidConfig:
            if ssid['name'] == ssidName:
                filteredSsid.append(ssid)
        ssidConfig = filteredSsid

    # Iterate through SSIDs to configure.
    for ssid in ssidConfig:
        # Grab each configured radius server, check if replacement needed and update host, port, secret.
        ssidNumber = ssid['number']
        ssidName = ssid['name']
        pendingRadius = False
        pendingAcct = False
        if 'radiusServers' in ssid:
            radiusServers = ssid['radiusServers']
            for server in radiusServers:
                for line in radiusUpdate:
                    if line[0] == 'radius':
                        if line[1] == server['host']:
                            pendingRadius = True
                            server['host'] = line[2]
                            server['port'] = line[3]
                            server['secret'] = line[4]
                            break

        # Repeat for radius accounting server.
        if 'radiusAccountingServers' in ssid:
            radiusAcctServers = ssid['radiusAccountingServers']
            for server in radiusAcctServers:
                for line in radiusUpdate:
                    if line[0] == 'accounting':
                        if line[1] == server['host']:
                            pendingAcct = True
                            server['host'] = line[2]
                            server['port'] = line[3]
                            server['secret'] = line[4]
                            break
        
        # if consoleDebug == True:
        print(f'Processing {ssidName}...')

        if pendingRadius == True:
            if consoleDebug == True:
                print(radiusServers)
            # Push updated RADIUS info
            dashboard.wireless.updateNetworkWirelessSsid(networkId=netId, number=ssidNumber, radiusServers=radiusServers)
        
        if pendingAcct == True:
            if consoleDebug == True:
                print(radiusAcctServers)
            # Push updated Accounting info                    
            dashboard.wireless.updateNetworkWirelessSsid(networkId=netId, number=ssidNumber, radiusAccountingServers=radiusAcctServers)

    return

def select_ssid(dashboard, netId):
    # Fetch and select the SSIDs
    print('\n\nFetching SSIDs...\n')
    ssidList = dashboard.wireless.getNetworkWirelessSsids(networkId=netId)
    counter = 0
    print('Select SSID:')
    for ssid in ssidList:
        ssidName = ssid['name']
        print(f'{counter} - {ssidName}')
        counter+=1
    isDone = False
    while isDone == False:
        selected = input('\nSelect the SSID number you would like to update: ')
        try:
            if int(selected) in range(0,counter):
                isDone = True
            else:
                print('\tInvalid SSID Number\n')
        except:
            print('\tInvalid SSID Number\n')
    return(ssidList[int(selected)]['number'], ssidList[int(selected)]['name'])

def get_yn_response(question):
    # Prompt for user Y/N response to input question.
    while True:
        resp = input(question).strip()
        if resp.lower() in ['y','n']:
            return resp.lower()
        print('Invalid response. Please enter Y or N.\n')

def import_csv():
    rows = []
    try:
        with open('radius_update.csv', 'r') as file:
            csvreader = csv.reader(file)
            csvheader = next(csvreader)
            for row in csvreader:
                rows.append(row)
        print('\n\nSuccessfully imported the following data:\n')
        print(tabulate.tabulate(rows, headers=csvheader))
    except:
        print(f'\nCould not open or read {csvname}. Exiting script.\n')
        exit()
    return rows

def prompt_import_csv(question):
    # Prompt for CSV to import with question.
    while True:
        filename = input(question).strip()
        rows = []
        try:
            with open(filename, 'r') as file:
                csvreader = csv.reader(file)
                csvheader = next(csvreader)
                for row in csvreader:
                    rows.append(row)
            print('\n\nSuccessfully imported the following data:\n')
            print(tabulate.tabulate(rows, headers=csvheader))
            cont = get_yn_response('Do you want to continue with this data? Y/N: ')
            if cont == 'y':
                return rows
            else:
                continue
        except:
            print(f'\nCould not open or read {filename}. Exiting script.\n')

# ---- Begin Script ----

consoleDebug = True
logDebug = False

# Import RADIUS server csv for replacements.
radiusUpdate = prompt_import_csv('Enter filename for RADIUS server update list: ')

netListImport = get_yn_response('Would you like to import a csv of networks to update? Y/N: ')
if netListImport == 'y':
    netImport = prompt_import_csv('Enter filename with networks to update: ')
    netList = []
    for net in netImport:
        netList.append(net[0])
    allNets = 'y'
else:
    print('Continuing to network selection...')
    allNets = get_yn_response('Update RADIUS info in all networks? Y/N: ')

# cont = get_yn_response('\nDo you want to continue with the above RADIUS replacements? Y/N: ')

# if cont == 'n':
#     print('Exiting...')
#     exit()
# else:
#     print('Continuing...\n')

# Connect to dashboard, select org and network
dashboard = meraki.DashboardAPI(suppress_logging=not logDebug)
orgId, orgName = select_org(dashboard)

if allNets == 'n':

    # Get network to migrate
    netId, netName = select_net_search(dashboard, orgId)

    allSsid = get_yn_response('Do you want to process RADIUS updates for all SSIDs? Y/N: ')

    if allSsid == 'n':
        ssidId, ssidName = select_ssid(dashboard, netId)
        replace_ssid_radius(dashboard, netId=netId, radiusUpdate=radiusUpdate, replaceAll='n', filterName='n', ssidNum=ssidId, ssidName='')

    elif allSsid == 'y':
        replace_ssid_radius(dashboard, netId=netId, radiusUpdate=radiusUpdate, replaceAll='y', filterName='n', ssidNum='', ssidName='')

elif allNets == 'y':

    # Get all networks
    networks = dashboard.organizations.getOrganizationNetworks(orgId)
    
    # Check for imported network list and filter accordingly.
    if netListImport == 'y':
        filteredNets = []
        for network in networks:
            if network['id'] in netList:
                filteredNets.append(network)
        if consoleDebug == True:
                print('\n\nImported network list to process.\n\n')
                print(filteredNets)
        networks = filteredNets
    else:
        print('All networks are selected. Continuing...')

    # Remove template bound and non-wireless networks from the network list to update.
    # SSID updates can only apply to wireless networks not bound to a template.
    filteredNets = []
    for network in networks:
        if network['isBoundToConfigTemplate'] == False and 'wireless' in network['productTypes']:
            filteredNets.append(network)
    if consoleDebug == True:
        print('\n\nNetwork list to process.\n\n')
        print(filteredNets)
    networks = filteredNets

    allSsid = get_yn_response('Do you want to replace RADIUS for all SSIDs in all networks? Y/N: ')

    if allSsid == 'y':
        print('All SSIDs are selected. Continuing...')
        finalCheck = get_yn_response('!!CONFIRMING!! - All networks and all SSIDs will be checked for matching RADIUS config and updated. Are you sure you want to continue? Y/N: ')
        if finalCheck == 'y':
            # Iterate over all networks to replace RADIUS
            for network in networks:
                netId, netName = network['id'], network['name']
                print(f'\nUpdating {netName} SSIDs...')
                replace_ssid_radius(dashboard, netId=netId, radiusUpdate=radiusUpdate, replaceAll='y', filterName='n', ssidNum='', ssidName='')
        elif finalCheck == 'n':
            print('Exiting...')
            exit()

    elif allSsid == 'n':
        print('Matching SSID by name...')
        # Get SSID name to update (all matching SSIDs will be updated).
        chooseSsid = True
        while chooseSsid == True:
            ssidName = input('Enter exact SSID name to match: ')
            cont = get_yn_response(f'All SSIDs with name "{ssidName}" will be updated. Is this name correct? Y/N: ')
            if cont == 'y':
                chooseSsid = False
            elif cont == 'n':
               print('Ignoring prior selection...')
        
        (f'\nProceeding to update SSID named "{ssidName}" in each network.')
        finalCheck = get_yn_response(f'!!CONFIRMING!! - All SSIDs with name "{ssidName}" in these networks will be checked for matching RADIUS config and updated. Are you sure you want to continue? Y/N: ')
        if finalCheck == 'y':
            for network in networks:
                netId, netName = network['id'], network['name']
                print(f'Updating {netName} SSIDs...')
                replace_ssid_radius(dashboard, netId=netId, radiusUpdate=radiusUpdate, replaceAll='y', filterName='y', ssidNum='', ssidName=ssidName)
        elif finalCheck == 'n':
            print('Exiting...')
            exit()

print('\nComplete')
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

def select_org(dashboard):
    # Fetch and select the organization
    print('\n\nFetching organizations...\n')
    organizations = dashboard.organizations.getOrganizations()
    organizations.sort(key=lambda x: x['name'])
    counter = 0
    print('Select org to query:')
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

# ---- Begin Script ----

# Connect to dashboard, select org
dashboard = meraki.DashboardAPI(output_log=True, log_path="./logs/MerakiSDK", log_file_prefix=os.path.basename(__file__), print_console=False)
orgId, orgName = select_org(dashboard)

outPath = orgName + '_DeviceExport.csv'

searchString = input('Enter string to match on device model or blank for all: ')
orgDevices = dashboard.organizations.getOrganizationDevices(orgId)
orgNets = dashboard.organizations.getOrganizationNetworks(orgId)

if not searchString == '':
    devList = []
    for dev in orgDevices:
        if searchString in dev['model']:
            devList.append(dev)
    orgDevices = devList

with open(outPath, 'w') as file:
    export_string = 'name,lat,lng,address,networkId,networkname,serial,model,mac,lanIp,firmware,productType'
    file.write(export_string + '\n')
    for dev in orgDevices:
        for net in orgNets:
            if dev['networkId'] == net['id']:
                netName = net['name']
                break
        try:
            devName = dev['name']
        except:
            devName = dev['mac']
        devLat = str(dev['lat'])
        devLng = str(dev['lng'])
        devAddress = ''.join(str(dev['address']).splitlines()).replace(',','')
        devNet = dev['networkId']
        devSerial = dev['serial']
        devModel = dev['model']
        devMac = dev['mac']
        if 'lanIp' in dev:
            if dev['lanIp'] == None:
                devIp = 'None'
            else:
                devIp = dev['lanIp']
        else:
            devIp = 'NA'
        devFirmware = dev['firmware']
        devType = dev['productType']
        export_string = devName + ',' + devLat + ',' + devLng  + ',' + devAddress + ',' + devNet + ',' + netName + ',' + devSerial + ',' + devModel + ',' + devMac + ',' + devIp + ',' + devFirmware + ',' + devType 
        file.write(export_string + '\n')
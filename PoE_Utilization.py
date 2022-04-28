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

# Connect to dashboard
dashboard = meraki.DashboardAPI(suppress_logging=True)

# Select organization
orgId, orgName = select_org(dashboard)

# Get networks and devices
networks = dashboard.organizations.getOrganizationNetworks(organizationId=orgId)
devices = dashboard.organizations.getOrganizationDevicesStatuses(organizationId=orgId)
# Filter to only MS devices
devices_selected = [i for i in devices if 'MS' in i['model']]

# Write CSV per network with row per switch
csvname = str(orgName + '_MS_POWER_DRAW.csv')
csvname = csvname.replace("\"", "")
with open(csvname, 'w', encoding='utf-8', newline='') as f:
    
    csvheader = ['Network', 'Switch', 'PoE Consumption in Watts', 'PSU1', 'PSU2']
    writer = csv.writer(f)
    writer.writerow(csvheader)

    for net in networks:
        # Extract devices from org device list.
        net_devices = [i for i in devices_selected if net['id'] in i['networkId']]
        for dev in net_devices:
            infoname = 'Unnamed'
            powerdraw = 0
            try:
                infoname = dev['name']
            except:
                continue
            ports = dashboard.switch.getDeviceSwitchPortsStatuses(serial=dev['serial'], timespan=3600)
            for port in ports:               
                try:
                    infoport = port['portId']
                    infopower = port['powerUsageInWh']
                    print(f'Switch {infoname} port {infoport} has draw of {infopower}Wh')
                    powerdraw = powerdraw + port['powerUsageInWh']
                except:
                    continue
            # Get PSU Info
            try:
                psu1 = dev['components']['powerSupplies'][0]['model']
                psu2 = dev['components']['powerSupplies'][1]['model']
                data = [net['name'], dev['name'], powerdraw, psu1, psu2]
            except:
                data = [net['name'], dev['name'], powerdraw]
            writer.writerow(data)

print(f'{csvname} complete. Continuing...')
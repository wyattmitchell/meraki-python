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

# Instructions:
# Set your APIKEY in environment variable MERAKI_DASHBOARD_API_KEY.
#
# Use:
# Script will prompt for org selection and total all PoE Usage over the past day.
# Then prompt for # hours expected to disable PoE and give a rough estimate of energy savings.

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

# Vars
powerdraw = 0


# ---- Begin Script ----


# Connect to dashboard, select org and get networks
dashboard = meraki.DashboardAPI(suppress_logging=True)
selected_org, orgName = select_org(dashboard)
networks = dashboard.organizations.getOrganizationNetworks(organizationId=selected_org)

# Iterate over all switches in all networks to collect PoE Usage
for net in networks:
    devices = dashboard.networks.getNetworkDevices(networkId=net['id'])
    # Get all MS devices
    devices_selected = [i for i in devices if 'MS' in i['model']]
    for dev in devices_selected:
        infoname = 'none'
        try:
            infoname = dev['name']
        except:
            continue
        ports = dashboard.switch.getDeviceSwitchPortsStatuses(serial=dev['serial'])
        for port in ports:                
            try:
                infoport = port['portId']
                infopower = port['powerUsageInWh']
                print(f'Switch {infoname} port {infoport} has draw of {infopower}Wh')
                powerdraw = powerdraw + port['powerUsageInWh']
            except:
                powerdraw

# Convert to estimated monthly power draw
powerdraw = round(powerdraw, 2)
pwrMonth = round(((powerdraw * 30) / 1000), 2)
print(f'\nTotal power draw of all selected ports over the last day is {powerdraw}Wh.')
print(f'That equates to roughly {pwrMonth}KWh for a 30 day month.\n')

# Prompt for hours to shutdown ports
hoursDisabled = int(input('How many hours per day do you anticipate PoE ports to be disabled?\n'))

# Calc and display results
prcntActive = (24 - hoursDisabled)/24
prcntInactive = round((1 - prcntActive)*100, 2)
activeMonth = round((pwrMonth * prcntActive), 2)
savingsMonth = round((pwrMonth - activeMonth), 2)
print(f'\nBased on that number of hours disabled you would save {savingsMonth}KWh or {prcntInactive}% of the power draw and use {activeMonth}KWh per month.\n')
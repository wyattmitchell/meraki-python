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
# Set APIKEY in environment variable MERAKI_DASHBOARD_API_KEY.

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

# ---- Begin Variables ----
debugLog = False
csvOutSuffix = '_DeviceStatus.csv'

# ---- Begin Script ----

# Connect to dashboard, select org
dashboard = meraki.DashboardAPI(output_log=debugLog, log_path="./logs/", log_file_prefix=os.path.basename(__file__), print_console=False)
selected_org, orgName = select_org(dashboard)
print(f"[+] Organization ID: {selected_org}")

print("[+] Grabbing Network Device List")
devices = dashboard.organizations.getOrganizationDevicesAvailabilities(organizationId=selected_org)

outPath = orgName + csvOutSuffix
with open(outPath, 'w') as file:
    export_string = 'Status,MAC,DeviceName,NetId'
    file.write(export_string + '\n')
    for a in devices:
        if (a['status'] == 'alerting' or a['status'] == 'dormant' or a['status'] == 'offline'):
            print("Status: %s MAC: %s Name: %s Network ID: %s" % (a['status'], a['mac'], a['name'], a['network']['id']))
            export_string = a['status'] +','+ a['mac'] +','+ a['name'] +','+ a['network']['id']
            file.write(export_string + '\n')
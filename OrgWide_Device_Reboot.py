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
# Set devicetype variable below.
# To ignore specific devices, create ignorelist.csv in the same path as the script. One name or serial number per line in a single column.
#
# Recommended: Perform a test run with the final line commented to see what will be rebooted and what will be skipped.
# When ready, uncomment last line to enable the rebootDevice API call.
#
# IMPORTANT: Devices will not reboot until the last line is uncommented.

dashboard = meraki.DashboardAPI(suppress_logging=True)

# Define type of device you want to reboot.
# Partial matches allowed. 'MR' will capture all AP models. 'MR4' will match MR44, MR46, etc.
devicetype = 'MR'

# Read ignorelist.csv for device names or serials to skip.
ignorelist = []
try:
    with open('ignorelist.csv', 'r') as file:
        ignorelist = [row[0] for row in csv.reader(file)]
    print('\nignorelist.csv found and imported.\n')
except:
    print('\nignorelist.csv could not be found or read. Continuing...\n')

# Gather all organizations
organizations = dashboard.organizations.getOrganizations()

for org in organizations:
    orgId = org['id']
    orgName = org['name']
    print('')
    print(f'The selected OrganizationId is {orgId} named {orgName}.')

    # Get all devices in Org
    devices = dashboard.organizations.getOrganizationDevices(organizationId=orgId)

    # Get all device types specified in devicetype variable
    devices_selected = [i for i in devices if devicetype in i['model']]

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
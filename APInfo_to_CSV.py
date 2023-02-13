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
import csv

# Instructions:
# Make sure to set your APIKEY in environment variable MERAKI_DASHBOARD_API_KEY.
# 
# Script will write a separate CSV file for every organization.
#
# Set verbose_console to True for more console logging.

# Variables:
verbose_console = False

dashboard = meraki.DashboardAPI(suppress_logging=not verbose_console)

def printj(ugly_json_object):

    # The json.dumps() method converts a JSON object into human-friendly formatted text
    pretty_json_string = json.dumps(ugly_json_object, indent = 2, sort_keys = False)
    return print(pretty_json_string)

def getBssid(serial):

    # Get all SSID info
    wireless_status_all = dashboard.wireless.getDeviceWirelessStatus(serial)
   
    if verbose_console == True:
        ## Print all SSIDs for AP
        print("This is the wireless status for AP: " + serial)
        printj(wireless_status_all)

    # Get only active SSIDs
    wireless_status = [i for i in wireless_status_all['basicServiceSets'] if i['enabled'] == True]

    if verbose_console == True:
        ## Print all active SSIDs for APs
        print("These are the active SSIDs for AP: " + serial)
        printj(wireless_status)

    return wireless_status

def getLldp(serial):

    device_lldps_info = {}

    try:    
        # Get LLDP/CDP info
        device_lldps_info = dashboard.devices.getDeviceLldpCdp(serial)
    except:
        pass

    if verbose_console == True:
        ## Print LLDP/CDP info
        print("This the LLDP/CDP info for AP: " + serial)
        printj(device_lldps_info)

    # Check if info is empty (LLDP/CDP disabled upstream) and return NA
    if device_lldps_info == {}:
        # print("Nothing for AP serial: " + serial)
        return {'systemName': 'NA','portId': 'NA', 'deviceId': 'NA', 'cdpPort': 'NA'}

    deviceId = ""
    systemName = ""
    portId = ""
    cdpPort = ""
    
    deviceId = device_lldps_info['ports']['wired0'].get('cdp', 'None').get('deviceId', 'None')
    systemName = device_lldps_info['ports']['wired0'].get('lldp', 'None').get('systemName', 'None')
    portId = device_lldps_info['ports']['wired0'].get('lldp', 'None').get('portId', 'None')
    cdpPort = device_lldps_info['ports']['wired0'].get('cdp', 'None').get('portId', 'None')

    return_data = {'systemName': systemName,'portId': portId, 'deviceId': deviceId, 'cdpPort': cdpPort}

    return return_data

# Gather all organizations
organizations = dashboard.organizations.getOrganizations()

if verbose_console == True:
    ## Print complete org list
    print('Organizations:')
    printj(organizations)

for org in organizations:
    orgId = org['id']
    orgName = org['name']
    print('')
    print(f'Found Organization with ID {orgId} named {orgName}. Querying for devices...')

    # Get all MR S/N's
    networks = dashboard.organizations.getOrganizationNetworks(organizationId=orgId)

    # Write CSV per organization with row per active SSID & Band for every AP
    csvname = str(orgName + '_AP_BSSID.csv')
    csvname = csvname.replace("\"", "")
    print(f'Writing CSV file {csvname}')
    with open(csvname, 'w', encoding='utf-8', newline='') as f:
        csvheader = ['Network', 'AP', 'LLDP_Name', 'LLDP_Port', 'CDP_Device', 'CDP_Port', 'SSID_Name', 'SSID_Band', 'SSID_Channel', 'SSID_ChannelWidth', 'BSSID']
        writer = csv.writer(f)
        writer.writerow(csvheader)

        for net in networks:
            netId = net['id']
            netName = net['name']
            devices = dashboard.networks.getNetworkDevices(networkId=netId)

            # Get all MR's
            devices_aps = [i for i in devices if any(m in i['model'] for m in ('MR','CW'))]

            if verbose_console == True:
                ## Print all AP detail
                print('These are the APs:')
                printj(devices_aps)
            
            network_info = dashboard.networks.getNetwork(networkId=netId)
            for i in devices_aps:
                lldp_info = getLldp(i['serial'])
                bssid_info = getBssid(i['serial'])
                for item in bssid_info:
                    data = [network_info['name'], i['name'], lldp_info['systemName'], lldp_info['portId'], lldp_info['deviceId'], lldp_info['cdpPort'], item['ssidName'], item['band'], item['channel'], item['channelWidth'], item['bssid']]
                    writer.writerow(data)
            print(f'{netName} complete. Continuing...')
print('Script finished.')
    
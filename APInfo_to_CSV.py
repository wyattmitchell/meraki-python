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

    # Get LLDP/CDP info
    device_lldps_info = dashboard.devices.getDeviceLldpCdp(serial)

    if verbose_console == True:
        ## Print LLDP/CDP info
        print("This the LLDP/CDP info for AP: " + serial)
        printj(device_lldps_info)

    # Check if info is empty (LLDP/CDP disabled upstream) and return NA
    if device_lldps_info == {}:
        # print("Nothing for AP serial: " + serial)
        return {'systemName': 'NA','portId': 'NA'}
        
    return device_lldps_info['ports']['wired0']['lldp']

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
    devices = dashboard.organizations.getOrganizationDevices(organizationId=orgId)
    devices_statuses = dashboard.organizations.getOrganizationDevicesStatuses(organizationId=orgId)

    # Get all MR's
    devices_aps = [i for i in devices if 'MR' in i['model']]

    if verbose_console == True:
        ## Print all AP detail
        print('These are the APs:')
        printj(devices_aps)

    # Write CSV per organization with row per active SSID & Band for every AP
    csvname = str(orgName + '_AP_BSSID.csv')
    csvname = csvname.replace("\"", "")
    print(f'Writing CSV file {csvname}')
    with open(csvname, 'w', encoding='utf-8', newline='') as f:
        csvheader = ['Network', 'AP', 'LLDP_Name', 'LLDP_Port', 'SSID_Name', 'SSID_Band', 'SSID_Channel', 'SSID_ChannelWidth', 'BSSID']
        writer = csv.writer(f)
        writer.writerow(csvheader)
        for i in devices_aps:
            network_info = dashboard.networks.getNetwork(networkId=i['networkId'])
            lldp_info = getLldp(i['serial'])
            bssid_info = getBssid(i['serial'])
            for item in bssid_info:
                data = [network_info['name'], i['name'], lldp_info['systemName'], lldp_info['portId'], item['ssidName'], item['band'], item['channel'], item['channelWidth'], item['bssid']]
                writer.writerow(data)
    print(f'{csvname} complete. Continuing...')
print('Script finished.')
    
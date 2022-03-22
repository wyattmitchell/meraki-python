import meraki
import json
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
    print('')
    print('ignorelist.csv found and imported.')
    print('')
except:
    print('')
    print('ignorelist.csv could not be found or read. Continuing...')
    print('')

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
        print('')
        if i['name'] in ignorelist:
            print("Skipping " + i["name"] + " " + i['model'] + " " + i['serial'] + ". Name is in ignorelist.")
            continue
        if i['serial'] in ignorelist:
            print("Skipping " + i["name"] + " " + i['model'] + " " + i['serial'] + ". Serial is in ignorelist.")
            continue
        print("Rebooting " + i["name"] + " " + i['model'] + " " + i['serial'])
        # dashboard.devices.rebootDevice(serial=i['serial'])
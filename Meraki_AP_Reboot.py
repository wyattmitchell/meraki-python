import meraki
import json

# IMPORTANT: Devices will not reboot until the last line is uncommented.
# Modify variables below and do a test run to see what will be rebooted and what will be skipped.
# Uncomment last line to enable the rebootDevice API call.

# Change APIKEY below to your Meraki Dashboard API key.
dashboard = meraki.DashboardAPI('APIKEY')

# Define type of device you want to reboot.
# Partial matches allowed. 'MR' will capture all AP models. 'MR4' will match MR44, MR46, etc.
devicetype = 'MR'

# Add any specific device names or serials you do NOT want to reboot.
ignorelist = [
    'IGNORE_MY_NAME',
    'IGNORE_MY_SERIAL',
    'MYAP',
    'ETC'
]

# Gather all organizations
organizations = dashboard.organizations.getOrganizations()

for org in organizations:
    orgId = org['id']
    orgName = org['name']
    print('')
    print(f'The OrganizationId is {orgId}, and its name is {orgName}.')

    # Get all devices in Org
    devices = dashboard.organizations.getOrganizationDevices(organizationId=orgId)

    # Get all device types specified in devicetype variable
    devices_selected = [i for i in devices if devicetype in i['model']]

    # Reboot all devices, ignoring any name or serial in ignorelist variable
    for i in devices_selected:
        print('')
        if i['name'] in ignorelist:
            print("Name is ignored.")
            print("Skipping " + i["name"] + " " + i['model'] + " " + i['serial'])
            continue
        if i['serial'] in ignorelist:
            print("Serial is ignored.")
            print("Skipping " + i["name"] + " " + i['model'] + " " + i['serial'])
            continue
        print("Rebooting " + i["name"] + " " + i['model'] + " " + i['serial'])
        # dashboard.devices.rebootDevice(serial=i['serial'])
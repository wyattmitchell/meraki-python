import meraki
import json

# IMPORTANT: Devices will not reboot until the last line is uncommented.
# Modify variables below and do a test run to see what will be rebooted and what will be skipped.
# Uncomment last line to enable the rebootDevice API call.

# Change APIKEY below to your Meraki Dashboard API key.
dashboard = meraki.DashboardAPI('APIKEY')

# Add any specific device names or serials you do NOT want to reboot.
ignorelist = [
    'IGNORE_MY_NAME',
    'IGNORE_MY_SERIAL',
    'MYAP',
    'ETC'
]

# Gather all organizations
organizations = dashboard.organizations.getOrganizations()

print('')
print('Listing all organizations:')

for org in organizations:
    orgId = org['id']
    orgName = org['name']
    print(f'The OrganizationId is {orgId}, and its name is {orgName}.')

print('Enter selected OrganizationId: ')
selected_org = input()

# Get networks in selected org
networks = dashboard.organizations.getOrganizationNetworks(organizationId=selected_org)

print('')
print('Listing all networks in selected Organization:')

for net in networks:
    netId = net['id']
    netName = net['name']
    print(f'The NetworkId is {netId}, and its name is {netName}.')

print('')
print('Enter selected NetworkId: ')
selected_net = input()

# Get all devices in Net
devices = dashboard.networks.getNetworkDevices(networkId=selected_net)

# Define type of device you want to reboot.
# Partial matches allowed. 'MR' will capture all AP models. 'MR4' will match MR44, MR46, etc.
print('')
print('Select device type to reboot. ')
print('Partial matches allowed. "MR" will capture all AP models. "MR4" will match MR44, MR46, etc.')
print('Enter device type: ')
devicetype = input()

# Get all device types specified in devicetype variable
devices_selected = [i for i in devices if devicetype in i['model']]

print('')
print('Listing all devices matched in selected network:')

for dev in devices_selected:
    devName = dev['name']
    print(f'{devName}')

print('')
print('Continue? (Y/N): ')
reboot = input()

if reboot == 'Y':
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
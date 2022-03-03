import meraki
import json

dashboard = meraki.DashboardAPI('APIKEY')

def printj(ugly_json_object):

    # The json.dumps() method converts a JSON object into human-friendly formatted text
    pretty_json_string = json.dumps(ugly_json_object, indent = 2, sort_keys = False)
    return print(pretty_json_string)

# Gather all organizations
organizations = dashboard.organizations.getOrganizations()

## Print complete org list
# print('Organizations:')
# printj(organizations)

for org in organizations:
    orgId = org['id']
    orgName = org['name']
    print('')
    print(f'The OrganizationId is {orgId}, and its name is {orgName}.')

    # Get all MR S/N's
    devices = dashboard.organizations.getOrganizationDevices(organizationId=orgId)

    # Get all MR's
    devices_aps = [i for i in devices if 'MR' in i['model']]

    ## Print all AP detail
    # print('These are the APs:')
    # printj(devices_aps)

    # Write CSV per organization with row per active SSID & Band for every AP
    for i in devices_aps:
        print('')
        print("Rebooting " + i["name"] + " " + i['model'] + " " + i['serial'])
        dashboard.devices.rebootDevice(serial=i['serial'])
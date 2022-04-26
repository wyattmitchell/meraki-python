import meraki
import csv

# Instructions:
# Make sure to set your APIKEY in environment variable MERAKI_DASHBOARD_API_KEY.

dashboard = meraki.DashboardAPI(suppress_logging=True)

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
orgGood = 0
while orgGood == 0:
    try:
        networks = dashboard.organizations.getOrganizationNetworks(organizationId=selected_org)
        orgGood = 1
    except:
        print('')
        print('Selected org does not exist for the provided APIKEY.')

# Write CSV per network with row per switch
csvname = str('MS_POWER_DRAW.csv')
csvname = csvname.replace("\"", "")
with open(csvname, 'w', encoding='utf-8', newline='') as f:
    
    csvheader = ['Network', 'Switch', 'PoE Consumption in Watts']
    writer = csv.writer(f)
    writer.writerow(csvheader)

    for net in networks:
            devices = dashboard.networks.getNetworkDevices(networkId=net['id'])
            # Get all MS devices
            devices_selected = [i for i in devices if 'MS' in i['model']]
            for dev in devices_selected:
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
                data = [net['name'], dev['name'], powerdraw]
                writer.writerow(data)

print(f'{csvname} complete. Continuing...')
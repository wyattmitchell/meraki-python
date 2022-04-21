import meraki
import json
import csv

# Instructions:
# Make sure to set your APIKEY in environment variable MERAKI_DASHBOARD_API_KEY.

powerdraw = 0
sampleScope = 1
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
try:
    networks = dashboard.organizations.getOrganizationNetworks(organizationId=selected_org)
except:
    print('')
    print('Selected org does not exist for the provided APIKEY.')
    exit()

if sampleScope == 1:
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

powerdraw = round(powerdraw, 2)
pwrMonth = round(((powerdraw * 30) / 1000), 2)
print(f'Total power draw of all selected ports over the last day is {powerdraw}Wh.')
print(f'That equates to roughly {pwrMonth}KWh for a 30 day month.\n')
print('How many hours per day do you anticipate PoE ports to be disabled?')
hoursDisabled = int(input())
prcntActive = (24 - hoursDisabled)/24
prcntInactive = round((1 - prcntActive)*100, 2)
activeMonth = round((pwrMonth * prcntActive), 2)
savingsMonth = round((pwrMonth - activeMonth), 2)

print(f'Based on that number of hours disabled you would save {savingsMonth}KWh or {prcntInactive}% of the power draw and use {activeMonth}KWh per month.')
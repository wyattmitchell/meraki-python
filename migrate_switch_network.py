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
import datetime
import json

# Instructions:
# Set your APIKEY in environment variable MERAKI_DASHBOARD_API_KEY.

# ToDo:
# Maybe STP config migration (preserve STP priority for switches / stacks).
# Maybe powerExceptions (getnetworkswitchsettings) (MS350/355 only so leaving for later.)
# For ports that rely on network wide settings like access policies maybe tag interfaces with policy name for easy manual config after migration.

# ---- Begin Script Functions ----


def select_org(dashboard):
    # Fetch, sort by name and select organization
    print('\n\nFetching organizations...\n')
    organizations = dashboard.organizations.getOrganizations()
    organizations.sort(key=lambda x: x['name'])
    counter = 0
    print('Select organization:')
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

def select_net(dashboard, orgId):
    # Fetch and select network
    networks = dashboard.organizations.getOrganizationNetworks(orgId)

    # Prompt search for network name to filter for shorter list.
    searchName = input('Enter search string or leave blank for all networks: ')

    netList = []
    while netList == []:
        if searchName == '':
            # Return all networks for blank search string.
            netList = networks
        else:   
            # Return networks matching searchName.
            for net in networks:
                if searchName in net["name"]:
                    netList.append(net)
        # Validate at least 1 network is returned and prompt for new search string if empty.
        if netList == []:
            print(f'No networks found matching {searchName}.')
            searchName = input('Enter search string or leave blank for all networks: ')
    
    netList.sort(key=lambda x: x['name'])
    counter = 0

    print('Networks:')
    for net in netList:
        netName = net['name']
        print(f'{counter} - {netName}')
        counter+=1
    isDone = False
    while isDone == False:
        selected = input('\nSelect the network ID you would like to use: ')
        try:
            if int(selected) in range(0,counter):
                isDone = True
            else:
                print('\tInvalid Network Number\n')
        except:
            print('\tInvalid Network Number\n')
    return(netList[int(selected)]['id'], netList[int(selected)]['name'])

def get_network_device_list(dashboard, netId, devString):
    # Fetch all network devices
    devices = dashboard.networks.getNetworkDevices(netId)
    
    if consoleDebug == True: print(f'{devices}')

    deviceList = []
    
    # Filter networks
    for device in devices:
        if devString in device["model"]:
            deviceList.append(device)

    if consoleDebug == True: print(deviceList)

    return deviceList

def select_device(deviceList):
    # Sort and select from input devices list.
    deviceList.sort(key=lambda x: x.setdefault('name', x['mac']))
    counter = 0
    for dev in deviceList:
        devName = dev.setdefault('name', dev['mac'])
        print(f'{counter} - {devName}')
        counter+=1
    isDone = False
    while isDone == False:
        selected = input('\nSelect the device you would like to migrate: ')
        try:
            if int(selected) in range(0,counter):
                isDone = True
            else:
                print('\tInvalid Device Number\n')
        except:
            print('\tInvalid Device Number\n')
    return(deviceList[int(selected)]['serial'], deviceList[int(selected)]['name'])

def get_yn_response(question):
    # Prompt for user Y/N response to input question.
    while True:
        resp = input(question).strip()
        if resp.lower() in ['y','n']:
            return resp.lower()
        print('Invalid response. Please enter Y or N.\n')

def migrate_switch(dashboard, swSerial):
    # Get switch port config then remove/add from src to dst and finally re-apply port configs.
    print('\nGetting switch port settings...')
    swConfig = dashboard.switch.getDeviceSwitchPorts(swSerial)
    if consoleDebug == True:
        print(swConfig)

    try:
        print('\nRemoving switch from source network...')
        dashboard.networks.removeNetworkDevices(srcNetId, swSerial)
        claimSerial = [swSerial]

        print('\nAdding switch to destination network...')
        dashboard.networks.claimNetworkDevices(dstNetId, claimSerial)

        # Read each port config then apply as access or trunk.
        print('\nApplying port configuration...')
        for port in swConfig:
            # Extract settings
            pID = port['portId']
            pName = port['name']
            pTags =  port['tags']
            pEnable =  port['enabled']
            pPOE =  port['poeEnabled']
            pType =  port['type']
            pVlan =  port['vlan']
            pVoice =  port['voiceVlan']
            pAllowed =  port['allowedVlans']
            pIsolate = port['isolationEnabled']
            pSTPenable =  port['rstpEnabled']
            pSTPguard = port['stpGuard']
            pLink = port['linkNegotiation']
            pSchedule = port['portScheduleId']
            pUdld = port['udld']
            pPolicy = port['accessPolicyType']
            
            if pVoice == '0':
                pVoice = None
            try: 
                if pType == "access":
                    response = dashboard.switch.updateDeviceSwitchPort(serial=swSerial, portId=pID, name=pName, enabled=pEnable, poeEnabled=pPOE, type=pType, vlan=pVlan, voiceVlan=pVoice, rstpEnabled=pSTPenable, stpGuard=pSTPguard, tags=pTags, linkNegotiation=pLink, isolationEnabled=pIsolate, udld=pUdld)
                    print(f'\nPort {pID} configured as {pType} with data vlan {pVlan} and voice vlan {pVoice}.')
                elif pType == "trunk":
                    response = dashboard.switch.updateDeviceSwitchPort(serial=swSerial, portId=pID, name=pName, enabled=pEnable, poeEnabled=pPOE, type=pType, vlan=pVlan, allowedVlans=pAllowed, rstpEnabled=pSTPenable, stpGuard=pSTPguard, tags=pTags, linkNegotiation=pLink, isolationEnabled=pIsolate, udld=pUdld)
                    print(f'\nPort {pID} configured as {pType} with native vlan {pVlan} and allowed vlans {pVoice}.')
            except Exception as error:
                print(str(error))
    except:
        # If move or port config fails, write out log with serial number and port config JSON for manual review.
        with open('logs/' + 'migrate_log.txt', 'a') as outfile:
            outfile.write(f'{datetime.datetime.now()} - switch migration error. Switch serial {swSerial}. Writing switch config. Validate switch remove and claim then validate config from string below.\n')
            outfile.write(json.dumps(swConfig))
            outfile.write('\n\n')
        print('Errors encountered. See error log.')
    return


# ---- Begin Script Main ----

# Debug options
### Additional logging to Console
consoleDebug = False
### Log Meraki SDK activity to file
logDebug = False

# Connect to dashboard, select org and networks
dashboard = meraki.DashboardAPI(suppress_logging=not logDebug)
orgId, orgName = select_org(dashboard)

print('Select source network:')
srcNetId, srcNetName = select_net(dashboard, orgId)

print('Select destination network:')
dstNetId, dstNetName = select_net(dashboard, orgId)

print(f'\nSource network {srcNetName} and destination network {dstNetName} selected. Continuing...')

# Get scope of change
scopeAll = get_yn_response('\nMigrate all switches in network? (Y/N): ')

# Set MS as device type for device list
devString = 'MS'

# Process individual switch/stack migrations
if scopeAll == 'n':
    # moveSwitch is prompted after each migration. Allows additional migrations or end of script.
    moveSwitch = 'y'
    while moveSwitch == 'y':
        # Get list of network switches
        swList = get_network_device_list(dashboard, srcNetId, devString)   
        if swList == []:
            print('No switches found in network. Exiting...')
            break
        # Get list of network stacks
        stackList = dashboard.switch.getNetworkSwitchStacks(srcNetId)

        if consoleDebug == True: print(swList)
        
        # Prompt for switch to migrate
        swSerial, swName = select_device(swList)

        # --- Begin stack check and stack migration section. ---
        # Check if selected serial is a stack member and prompt to move full stack if found.
        # If serial is not a stack member moveStack is empty and will skip past moveStack sections.

        moveStack = ''
        for stack in stackList:
            if swSerial in stack['serials']:
                stackId = stack['id']
                stackName = stack['name']
                stackSerials = stack['serials']
                moveStack = get_yn_response(f'{swName} is part of a stack with name {stackName}. Would you like to move the entire stack? (Y/N): ')
                break

        if moveStack == 'n':
            print('Skipping switch and stack. Please select a new switch to migrate.\n')
            continue
        
        if moveStack == 'y':
            print('Preparing to migrate stack...\n')
            print('Listing all stack members...\n')
            for serial in stackSerials:
                switch = dashboard.devices.getDevice(serial)
                switchName = switch['name']
                switchSerial = switch['serial']
                print(f'{switchName} with serial {switchSerial} is a member of this stack.\n')
            
            proceed = get_yn_response('\nWould you like to proceed with stack migration? (Y/N): ')

            if proceed == 'y':
                print(f'\nDeleting stack from {srcNetName}...')
                dashboard.switch.deleteNetworkSwitchStack(srcNetId, stackId)
                print(f'\nMigrating switches to {dstNetName}...')
                for serial in stackSerials:
                    migrate_switch(dashboard, serial)
                print(f'Creating {stackName} stack in {dstNetName}...')
                dashboard.switch.createNetworkSwitchStack(dstNetId, stackName, stackSerials)
                continue
            
            if proceed == 'n':
                print('Skipping switch and stack. Please select a new switch to migrate.\n')
                continue
        # --- End stack migration section. ---

        # --- Begin non-stack switch section. ---
        # Prompt to confirm migration.
        resp = get_yn_response(f'Migrating {swName} with serial {swSerial} from {srcNetName} to {dstNetName}. Continue? (Y/N): ')
        if resp == 'y':
            migrate_switch(dashboard, swSerial)
        else:
            print('Migration cancelled...\n')

        # Prompt if another switch to migrate.
        moveSwitch = get_yn_response('Migrate another switch between these networks? (Y/N): ')

# --- Begin section to migrate all switches in network. ---
# Functions as above without prompts for each device.
# All stacks are migrated first, then switch list is fetched for any remaining to be migrated.
elif scopeAll == 'y':
    while True:
        # Get list of network switches
        swList = get_network_device_list(dashboard, srcNetId, devString)
        if swList == []:
            print('No switches found in network. Exiting...')
            break

        # Get list of network stacks
        stackList = dashboard.switch.getNetworkSwitchStacks(srcNetId)
        
        # Migrate all stacks.
        # For each stack - delete stack, migrate switches, create stack in new network.
        for stack in stackList:
            stackId = stack['id']
            stackName = stack['name']
            stackSerials = stack['serials']
            print(f'\nPreparing to migrate stack {stackName}...')
            
            for serial in stackSerials:
                switch = dashboard.devices.getDevice(serial)
                switchName = switch['name']
                switchSerial = switch['serial']
                print(f'{switchName} with serial {switchSerial} is a member of this stack.')
            
            print(f'\nDeleting stack from {srcNetName}...')
            dashboard.switch.deleteNetworkSwitchStack(srcNetId, stackId)
            print(f'\nMigrating all switches to {dstNetName}...')
            for serial in stackSerials:
                migrate_switch(dashboard, serial)
            print(f'Creating {stackName} stack in {dstNetName}...')
            dashboard.switch.createNetworkSwitchStack(dstNetId, stackName, stackSerials)
            break

        # Refresh list of network switches (after stacks have moved)
        swList = get_network_device_list(dashboard, srcNetId, devString)
        if swList == []:
            print('No standalone switches found in network. Exiting...')
            break

        # Migrate remaining switches
        for sw in swList:
            swSerial = sw['serial']
            migrate_switch(dashboard, swSerial)

print('Complete')
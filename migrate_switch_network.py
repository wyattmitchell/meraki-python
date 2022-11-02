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
# Maybe powerExceptions (getnetworkswitchsettings)
# Finalize additional port configs that can move over. 
# For those that rely on network wide settings like access policies maybe tag interfaces with policy name for easy manual config after migration?

# ---- Begin Script ----

def select_org(dashboard):
    # Fetch and select the organization
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
    # Fetch and select the network
    networks = dashboard.organizations.getOrganizationNetworks(orgId)

    # Prompt search for network name to filter for shorter list.
    search_name = input('Enter search string: ')

    netList = []
    if search_name == '':
        netList = networks
    else:
        # Filter only MS devices
        for net in networks:
            if search_name in net["name"]:
                netList.append(net)
    
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

def get_network_switch_list(dashboard, netId):
    # Fetch all network devices
    devices = dashboard.networks.getNetworkDevices(netId)
    msList = []
    
    # Filter networks
    for device in devices:
        if 'MS' in device["model"]:
            msList.append(device)
    return msList

def select_sw(msList):
    msList.sort(key=lambda x: x['name'])
    counter = 0
    print('Select switch to migrate.')
    for sw in msList:
        swName = sw['name']
        print(f'{counter} - {swName}')
        counter+=1
    isDone = False
    while isDone == False:
        selected = input('\nSelect the switch you would like to migrate: ')
        try:
            if int(selected) in range(0,counter):
                isDone = True
            else:
                print('\tInvalid Switch Number\n')
        except:
            print('\tInvalid Switch Number\n')
    return(msList[int(selected)]['serial'], msList[int(selected)]['name'])

def get_response(question):
    isDone = False
    while isDone == False:
        resp = input(question)
        try:
            if resp == 'Y' or 'y' or 'N' or 'n':
                isDone = True
            else:
                print('\tInvalid response. Please enter Y or N.\n')
        except:
            print('\tInvalid response.\n')
    return resp.lower()

def migrate_switch(dashboard, swSerial):
    print('\nGetting switch port settings...')
    swConfig = dashboard.switch.getDeviceSwitchPorts(swSerial)
    if consoleDebug == True:
        print(swConfig)
    try:
        print('\nRemoving switch from source network...')
        dashboard.networks.removeNetworkDevices(src_net, swSerial)
        claimSerial = [swSerial]
        print('\nAdding switch to destination network...')
        dashboard.networks.claimNetworkDevices(dst_net, claimSerial)
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
        with open('logs/' + 'migrate_log.txt', 'a') as outfile:
            outfile.write(f'{datetime.datetime.now()} - switch migration error. Writing switch config. Validate switch remove and claim then validate config from string below.\n')
            outfile.write(json.dumps(swConfig))
            outfile.write('\n\n')
        print('Errors encountered. See error log.')
    return

def set_STP(dashboard, stpInfo, dst_net, serial):
    dashboard.switch.updateNetworkSwitchStp(dst_net)

consoleDebug = False
logDebug = False
setSTP = True

# Connect to dashboard, select org and network
dashboard = meraki.DashboardAPI(suppress_logging=not logDebug)
selected_org, orgName = select_org(dashboard)

print('Select source network:')
src_net, src_netName = select_net(dashboard, selected_org)

print('Select destination network:')
dst_net, dst_netName = select_net(dashboard, selected_org)

print(f'\nSource network {src_netName} and destination network {dst_netName} selected. Continuing...')

# Get scope of change
scope_all = get_response('\nMigrate all switches in network? (Y/N): ')

# Process switch migrations
if scope_all == 'n':
    moveSwitch = 'y'
    while moveSwitch == 'y':
        # Get list of network switches
        swList = get_network_switch_list(dashboard, src_net)   
        if swList == []:
            print('No switches found in network. Exiting...')
            break
        # Get list of network stacks
        stackList = dashboard.switch.getNetworkSwitchStacks(src_net)

        # Prompt for switch to migrate
        swSerial, swName = select_sw(swList)

        # Check if selected serial is a stack member and prompt to move full stack if found.
        moveStack = ''
        for stack in stackList:
            if swSerial in stack['serials']:
                stackId = stack['id']
                stackName = stack['name']
                stackSerials = stack['serials']
                moveStack = get_response(f'{swName} is part of a stack with name {stackName}. Would you like to move the entire stack? (Y/N): ')
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
            proceed = get_response('\nWould you like to proceed with stack migration? (Y/N): ')

            if proceed == 'y':
                print(f'\nDeleting stack from {src_netName}...')
                dashboard.switch.deleteNetworkSwitchStack(src_net, stackId)
                print(f'\nMigrating switches to {dst_netName}...')
                for serial in stackSerials:
                    migrate_switch(dashboard, serial)
                print(f'Creating {stackName} stack in {dst_netName}...')
                dashboard.switch.createNetworkSwitchStack(dst_net, stackName, stackSerials)
                continue
            
            if proceed == 'n':
                print('Skipping switch and stack. Please select a new switch to migrate.\n')
                continue
            
        # Confirm move
        resp = get_response(f'Migrating {swName} with serial {swSerial} from {src_netName} to {dst_netName}. Continue? (Y/N): ')
        if resp == 'y':
            migrate_switch(dashboard, swSerial)
        else:
            print('Migration cancelled...\n')
        moveSwitch = get_response('Migrate another switch between these networks? (Y/N): ')

elif scope_all == 'y':
    while True:
        # Get list of network switches
        swList = get_network_switch_list(dashboard, src_net)
        if swList == []:
            print('No switches found in network. Exiting...')
            break
        # Get list of network stacks
        stackList = dashboard.switch.getNetworkSwitchStacks(src_net)
        
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
            
            print(f'\nDeleting stack from {src_netName}...')
            dashboard.switch.deleteNetworkSwitchStack(src_net, stackId)
            print(f'\nMigrating all switches to {dst_netName}...')
            for serial in stackSerials:
                migrate_switch(dashboard, serial)
            print(f'Creating {stackName} stack in {dst_netName}...')
            dashboard.switch.createNetworkSwitchStack(dst_net, stackName, stackSerials)
            break

        # Refresh list of network switches (after stacks have moved)
        swList = get_network_switch_list(dashboard, src_net)
        if swList == []:
            print('No standalone switches found in network. Exiting...')
            break

        for sw in swList:
            swSerial = sw['serial']
            swName = sw['name']
                                
            # Migrate single switch
            migrate_switch(dashboard, swSerial)

print('Complete')
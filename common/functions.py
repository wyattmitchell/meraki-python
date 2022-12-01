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
    print('\n\nFetching networks...\n')
    networks = dashboard.organizations.getOrganizationNetworks(orgId)
    networks.sort(key=lambda x: x['name'])
    counter = 0
    print('Select organization:')
    for net in networks:
        netName = net['name']
        print(f'{counter} - {netName}')
        counter+=1
    isDone = False
    while isDone == False:
        selected = input('\nSelect the network ID you would like to query: ')
        try:
            if int(selected) in range(0,counter):
                isDone = True
            else:
                print('\tInvalid Network Number\n')
        except:
            print('\tInvalid Network Number\n')
    return(networks[int(selected)]['id'], networks[int(selected)]['name'])

def select_net_search(dashboard, orgId):
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
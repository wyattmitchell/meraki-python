# Meraki Python Scripts

## Description
A collection of standalone scripts used to automate tasks within a Meraki network.

## Other Resources
- Meraki API Docs - https://developer.cisco.com/meraki/

## Usage
Set your Meraki API key to an environment variable:
- export MERAKI_DASHBOARD_API_KEY=XXXXXX
Some scripts read or write CSV files. Example files and notes on usage will be referenced in the instructions section of each script.

#### Script descriptions:
- AP_Replacement.py - Used to copy AP attributes (name, tags, location, address, floorplan) to a new serial for replacement or upgrade. Reads a CSV to match existing/new serial numbers.
- APInfo_to_CSV.py - Used to gather a set of AP BSSID and CDP/LLDP information for all organizations and networks. Output is a set of CSV files with AP data.
- device_status.py - List all offline, alerting and dormant devices. Write to CSV.
- Energy_Savings_Calc.py - Gather MS PoE usage for the past day, estimate monthly use and calculate potential savings through port scheduling.
- Export_Org_Networks.py - Exports to CSV a list of all networks within a selected organization. CSV can then be modified and used as an input for other scripts.
- migrate_all_aps.py - CLI driven tool used to migrate all APs from one dashboard network to another while preserving AP data such as name, lat/lng, address, floorplan if it exists in the target network, etc.
- migrate_switch_network.py - CLI driven tool to migrate MS switch devices from a source network to a destination along with port configurations on the device.
- migrate_switch_network_ab.py - CLI driven tool to migrate MS switch devices from a source network to a destination along with port configurations on the device. (Same as migrate_switch_network.py but leverages Action Batches to reduce total API calls.)
- Modify_FIPS.py - Imports a CSV with network list and desired FIPS setting to apply FIPS enabled/disabled setting to the network.
- NetworkAP_to_GMap.py - Select network floorplan, gather AP location, name, power and 5Ghz channel info. Write to CSV which can be used to overlay on Google Maps.
- NetworkWide_Device_Reboot.py - A CLI driven tool to reboot all devices of a selected type within a selected Org and Network. Reads a CSV for names/serial numbers of devices to skip.
- OrgWide_Device_Reboot.py - Used to reboot all devices of a certain type across all organizations and networks available. Reads a CSV for names/serial numbers of devices to skip.
- PoE_Utilization.py - Gathers current MS PoE usage and PSUs and writes summary info to CSV.
- replace_radius_servers.py - Interactive CLI to push updated RADIUS server lists to SSIDs. Options for single network, all networks, CSV import of network list as well as targetting all SSIDs or match SSID by name.
- Schedule_Net_Upgrades.py - Schedules network upgrades based on CSV input file.
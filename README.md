# Meraki Python Scripts

## Description
A collection of standalone scripts used to automate tasks within a Meraki network.

## Other Resources
- Meraki API Docs - https://developer.cisco.com/meraki/

## Usage
Set your Meraki API key to an environment variable:
- export MERAKI_DASHBOARD_API_KEY=XXXXXX
Some scripts read or write CSV files. Example files included and notes on usage will be in the instructions section of each script.

#### Script descriptions:
- AP_Replacement.py - Used to copy AP attributes (name, tags, location, address, floorplan) to a new serial for replacement or upgrade. Reads a CSV to match existing/new serial numbers.
- APInfo_to_CSV.py - Used to gather a set of AP BSSID and LLDP information for all organizations and networks. Output is a set of CSV files with AP data.
- OrgWide_Device_Reboot.py - Used to reboot all devices of a certain type across all organizations and networks available. Reads a CSV for names/serial numbers of devices to skip.
- NetworkWide_Device_Reboot.py - A CLI driven tool to reboot all devices of a selected type within a user selected Org and Network. Reads a CSV for names/serial numbers of devices to skip.
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
- APInfo_to_CSV.py - Used to gather a set of AP BSSID and LLDP information for all organizations and networks. Output is a set of CSV files with AP data.
- AP_Replacement.py - Used to copy AP attributes (name, tags, location, address, floorplan) to a new serial for replacement or upgrade. Reads a CSV to match existing/new serial numbers.
- Energy_Savings_Calc.py - Gather MS PoE usage for the past day, estimate monthly use and calculate potential savings through port scheduling.
- NetworkAP_to_GMap.py - Select network floorplan, gather AP location, name, power and 5Ghz channel info. Write to CSV which can be used to overlay on Google Maps.
- NetworkWide_Device_Reboot.py - A CLI driven tool to reboot all devices of a selected type within a selected Org and Network. Reads a CSV for names/serial numbers of devices to skip.
- OrgWide_Device_Reboot.py - Used to reboot all devices of a certain type across all organizations and networks available. Reads a CSV for names/serial numbers of devices to skip.
- PoE_Utilization.py - Gathers current MS PoE usage and PSUs and writes summary info to CSV.
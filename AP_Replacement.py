import meraki
import csv

# Instructions:
# Make sure to set your APIKEY in environment variable MERAKI_DASHBOARD_API_KEY.
# Script will read device_update.csv from the same path the script resides.
# Any errors will be written to AP_Replacement_Errors.csv
#
# Set verbose_console to True for more console logging.

# Variables
verbose_console = False

dashboard = meraki.DashboardAPI(suppress_logging=not verbose_console)

rows = []
try:
    with open('device_update.csv', 'r') as file:
        csvreader = csv.reader(file)
        csvheader = next(csvreader)
        for row in csvreader:
            rows.append(row)

    if verbose_console == True:
        print('Imported list.')
        print(rows)

    print('')
    print('device_update.csv imported. Continuing...')
    print('')

except:
    print('')
    print('Could not open or read device_update.csv. Exiting script.')
    print('')

errors = 0
errors_list = []
for row in rows:
    try:
        device_base = dashboard.devices.getDevice(serial=row[1])
        dashboard.devices.updateDevice(
            row[0],
            name=device_base['name'],
            tags=device_base['tags'],
            lat=device_base['lat'],
            lng=device_base['lng'],
            address=device_base['address'],
            floorPlanId=device_base['floorPlanId']
        )
    except:
        errors_list.append(row)
        errors = errors + 1

csvname = str('AP_Replacement_Errors.csv')
with open(csvname, 'w', encoding='utf-8', newline='') as f:
    csvheader = ['serial_new','serial_old']
    writer = csv.writer(f)
    writer.writerow(csvheader)
    for row in errors_list:
            writer.writerow(row)

print(f'Script completed with {errors} errors.\n')
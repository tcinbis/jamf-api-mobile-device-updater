# JAMF Mobile Device Updater
This script will communicate with a JAMF server of your choice and
update the mobile device name based on an extension attribute stored on the JAMF
server.

## Usage
```
python mobiledevices.py -h
usage: mobiledevices.py [-h] [-n] [-s SERIALS [SERIALS ...]]
                        [--update-all UPDATE_ALL]

optional arguments:
  -h, --help            show this help message and exit
  -n, --dry-run         If set the dry run option is enabled and no changes
                        are made.
  -s SERIALS [SERIALS ...], --serial-numbers SERIALS [SERIALS ...]
                        Space seperated list of serial numbers to look for and
                        update. By default it will be set to None and an
                        information will be printed to the console.
  --update-all UPDATE_ALL
                        Will update all devices registered at the JAMF server.
```

## Installation
First install the dependencies you need by using pip. Note that we are 
suggesting to use Python 3.7 or higher in combination with a virtualenv.

```
git clone https://github.com/tcinbis/jamf-api-mobile-device-updater.git
cd jamf-api-mobile-device-updater
virtualenv -p python3.7 venv
source venv/bin/activate
pip install -r requirements.txt
```

Next you need to supply some information about your JAMF instance like base url,
JAMF server certificate, API username and API password. Simply add these
information as environment variables to your environment. The expected names of
these variables are as following.

```
JAMF_API_USER
JAMF_API_PASSWORD
JAMF_SERVER_BASE_URL
JAMF_SERVER_CERT_FILE
```
Alternatively you can also modify the contents of `mobiledevices.py` and replace
the values which say something similar to `INSERT YOUR XY`.

To obtain your certificate file you can open e.g. Firefox and navigate to your
JAMF server website. Once there, click on the green lock icon to display
additional information and then click on *More Information* in the Site 
Security section. In the next window you can click *View Certificate* and then
under the tab *Details* you can finally export and save the certificate.

![Information][info]

![More Information][more-info]

![View Certificate][view-cert]

![Details][details-cert]

![Export Certificate][export-cert]


[info]: images/https-info.png
[more-info]: images/more-info.png
[view-cert]: images/view-cert.png
[details-cert]: images/details.png
[export-cert]: images/export.png
import argparse
import os
from typing import List

import requests
from dicttoxml import dicttoxml
from requests.auth import HTTPBasicAuth

from logger import get_logger

# NOTE: the specified user must have at least READ and UPDATE permissions
API_USER = os.getenv("JAMF_API_USER", "INSERT YOUR USERNAME")
API_PASSWORD = os.getenv("JAMF_API_PASSWORD", "INSERT YOUR PASSWORD")
SERVER_BASE_URL = os.getenv("JAMF_SERVER_BASE_URL", "https://your-jamf-server.com:8443")
SERVER_CERT_FILE = os.getenv("JAMF_SERVER_CERT_FILE", "your-jamf-server.crt")

logger = get_logger(__name__)


class SetMobileDeviceNames:
    def __init__(self, dry_run: bool = False):
        session = requests.Session()
        session.auth = HTTPBasicAuth(API_USER, API_PASSWORD)
        session.headers = {
            "Accept": "application/json",
            "Content-Type": "application/xml",
        }
        session.verify = SERVER_CERT_FILE
        self.session = session
        self.dry_run = dry_run
        if dry_run:
            logger.warning("Dry run option enabled. No changes will be applied.")

    def get_mobile_devices(self) -> List:
        """
        Get all mobile devices registered in Jamf and return devices as list.
        :return: List containing dicts where each dict represents a mobile device.
        """
        r = self.session.get(f"{SERVER_BASE_URL}/JSSResource/mobiledevices")

        json_response = r.json()  # type: dict

        if r.status_code == 200 and "mobile_devices" in json_response.keys():
            device_list = json_response.get("mobile_devices")
            return device_list
        else:
            logger.error(
                f"JAMF request failed with code {r.status_code}. Failed to get mobile devices."
            )

    def get_extension_attribute(self, device_id: int) -> str:
        """
        Get all extension attributes for a given device. Then try to find the attribute with id 1 and
        name "GivenIOSShortname".
        :return: name of the device provided by the extension attribute in Jamf
        """
        r = self.session.get(
            f"{SERVER_BASE_URL}/JSSResource/mobiledevices/id/{device_id}/subset/extension_attributes"
        )
        json_response = r.json()  # type: dict

        if r.status_code == 200:
            if "mobile_device" in json_response.keys():
                if "extension_attributes" in json_response.get("mobile_device").keys():
                    extension_attributes = json_response.get("mobile_device").get(
                        "extension_attributes"
                    )
                    for extension_attribute in extension_attributes:
                        if (
                            extension_attribute.get("id") == 1
                            and extension_attribute.get("name") == "GivenIOSShortname"
                        ):
                            name = extension_attribute.get("value")
                            return name
                        else:
                            logger.warning(
                                f"Device wit id {device_id} has missing GivenIOSShortname attribute"
                            )
        else:
            logger.error(
                f"Failed to get extension_attribute for device with id {device_id}. Status code was {r.status_code}."
            )

    def update_mobile_device(self, device_name: str, device_id: str, serial: str):
        """
        Updated the mobile device in Jamf by sending a PUT request. The display_name, device_name and name attribute
        will be changed to device_name provided by the caller method. The data is first structured as a dict and then
        converted to a xml by using the dicttoxml package.
        """
        logger.info(f"Updating device with serial {serial} and name {device_name}")
        data = {
            "mobile_device": {
                "general": {
                    "display_name": device_name,
                    "device_name": device_name,
                    "name": device_name,
                }
            }
        }
        p = self.session.put(
            f"{SERVER_BASE_URL}/JSSResource/mobiledevices/id/{device_id}",
            data=dicttoxml(data, attr_type=False, root=False),
        )

        logger.info(f"Update put status code: {p.status_code}")
        if p.status_code != 201:
            logger.error(p.text)

    def send_mdm_command(self, device_name: str, device_id: int):
        """
        Send a MDM command to the given device with corresponding name and id.
        """
        logger.info(f"Sending MDM command to {device_name}.")
        p = self.session.post(
            f"{SERVER_BASE_URL}/JSSResource/mobiledevicecommands/command/DeviceName/{device_name}/id/{device_id}"
        )
        logger.info(f"MDM post status code: {p.status_code}")

        if p.status_code != 201:
            logger.error(p.text)

    def run(self, device_serials: List = None):
        """
        Start the update process for mobile devices. First get all mobile devices and then check whether we want to
        update them. If the serial number of a device is not contained in device_serials we will skip it. Finally update
        Jamf data and send a MDM command.
        :param device_serials: list of serial numbers we want to update. In case the list is empty we will update all
        mobile devices we find. If it is None we will inform the user and return.
        :return:
        """

        if device_serials is None:
            logger.error(
                "Please read the documentation of the SetMobileDeviceNames.run() method and provide a correct "
                "device_serials list."
            )
            logger.info("Exiting")
            return
        elif len(device_serials) == 0:
            logger.warning(
                "Received empty list for device serial numbers. Therefore updating all devices which will be found."
            )

        for device in self.get_mobile_devices():
            id = device.get("id")
            serial = device.get("serial_number")

            if serial in device_serials or len(device_serials) == 0:
                device_given_shortname = self.get_extension_attribute(id)

                if device_given_shortname:
                    if not self.dry_run:
                        self.update_mobile_device(device_given_shortname, id, serial)
                        self.send_mdm_command(device_given_shortname, id)
                else:
                    logger.warning(f"Given shortname for serial {serial} empty.")


def setup_argparse():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-n",
        "--dry-run",
        action="store_true",
        dest="DRY_RUN",
        help="If set the dry run option is enabled and no changes are made.",
    )

    parser.add_argument(
        "-s",
        "--serial-numbers",
        nargs="+",
        default=None,
        dest="SERIALS",
        help="Space seperated list of serial numbers to look for and update. "
        "By default it will be set to None and an information will be "
        "printed to the console.",
    )

    parser.add_argument(
        "--update-all",
        dest="UPDATE_ALL",
        help="Will update all devices registered at the JAMF server.",
    )

    return parser


if __name__ == "__main__":
    args = setup_argparse().parse_args()
    mobile_tool = SetMobileDeviceNames(dry_run=args.DRY_RUN)
    if args.UPDATE_ALL:
        # update every mobile device found on the JAMF server
        mobile_tool.run([])
    else:
        mobile_tool.run(args.SERIALS)

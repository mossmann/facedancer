#!/usr/bin/env python3
# pylint: disable=unused-wildcard-import, wildcard-import
#
# This file is part of Facedancer.
#

import logging

from facedancer import main
from facedancer import *
from usb_protocol.emitters.descriptors.microsoft10  import MicrosoftOS10DescriptorCollection
from usb_protocol.types.descriptors.microsoft10 import RegistryTypes

vendor_code        = 0xee
msft_string_number = 0xee

class WCIDDevice(USBDevice):
    """USB Device For testing WCID descriptors."""

    def __init__(self):
        super().__init__(
            vendor_id            = 0x1209,
            product_id           = 0x0006,
            device_revision      = 0x0000,
            device_class         = 0,
            product_string       = "WCID Test Device",
            manufacturer_string  = "Facedancer",
            serial_number_string = "AAAA",
        )

        configuration = USBConfiguration()
        self.add_configuration(configuration)

        # Device class 0 indicates that this is a composite device and that the
        # host should look in the interface descriptors for class information.
        # We have two interfaces which Windows should present to the user as two
        # separate devices.
        interface0 = USBInterface(
            number           = 0,
            class_number     = 255, # vendor-specific
            interface_string = "WCID Test Interface 0",
        )   
        configuration.add_interface(interface0)
        interface1 = USBInterface(
            number           = 1,
            class_number     = 255, # vendor-specific
            interface_string = "WCID Test Interface 1",
        )   
        configuration.add_interface(interface1)

        # OS String Descriptor tells Windows the vendor request number needed
        # to retrieve the OS Feature Descriptors.
        self.strings.add_string("MSFT100" + chr(vendor_code), index=msft_string_number)

        # OS Feature Descriptors.
        self.msft_descriptors = MicrosoftOS10DescriptorCollection()

        # Extended Compat ID OS Feature Descriptor indicates that the
        # interfaces are compatible with WinUSB.
        with self.msft_descriptors.ExtendedCompatIDDescriptor() as c:
            with c.Function() as f:
                f.bFirstInterfaceNumber = 0
                f.compatibleID          = 'WINUSB'
            with c.Function() as f:
                f.bFirstInterfaceNumber = 1
                f.compatibleID          = 'WINUSB'

        # Extended Properties OS Feature Descriptor contains the GUID for the
        # WinUSB driver.
        with self.msft_descriptors.ExtendedPropertiesDescriptor() as d:
            with d.Property() as p:
                p.dwPropertyDataType = RegistryTypes.REG_SZ
                p.PropertyName       = "DeviceInterfaceGUID"
                p.PropertyData       = "{88bae032-5a81-49f0-bc3d-a4ff138216d6}"

    @vendor_request_handler(number=vendor_code, direction=USBDirection.IN)
    def handle_feature_request(self, request):
        """Handle requests for OS Feature Descriptors"""

        wIndex_list = [x[0] for x in list(self.msft_descriptors)]
        if request.index in wIndex_list:
            location = wIndex_list.index(request.index)
            request.reply(list(list(self.msft_descriptors)[location][1]))
        else:
            request.stall()

main(WCIDDevice())

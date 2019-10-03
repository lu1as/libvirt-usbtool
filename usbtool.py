#!/usr/bin/env python3

import sys
import os
import argparse
import usb.core
from jinja2 import Template

XML="""
<hostdev mode='subsystem' type='usb'>
  <source>
    <vendor id='{{vendor_id}}'/>
    <product id='{{product_id}}'/>
  </source>
</hostdev>
"""

file = "/tmp/usb_dev.xml"
devices = usb.core.find(find_all=True)

def list_devices():
  for i, d in enumerate(devices):
    if is_valid(d):
      print("{}:{} {} {}".format(hex(d.idVendor).lstrip("0x").zfill(4), hex(d.idProduct).lstrip("0x").zfill(4), d.manufacturer, d.product))

def is_valid(dev):
  if dev.manufacturer is None or "Linux" in dev.manufacturer:
    return False
  return True

def create_xml(vendorID, productID, bus=None, deviceID=None):
  t = Template(XML)
  f = open(file, "w")
  f.write(t.render(vendor_id=vendorID, product_id=productID, bus=bus, device_id=deviceID))
  f.close()

def delete_xml():
  os.remove(file)

def attatch(vm):
  os.system("virsh attach-device {} {}".format(vm, file))

def detach(vm):
  os.system("virsh detach-device {} {}".format(vm, file))

p = argparse.ArgumentParser()
p.add_argument("cmd", help="list, attach, detach")
p.add_argument("--vm", help="virtual machine name")
p.add_argument("--vendor", help="usb vendor id")
p.add_argument("--device", help="usb device id")
args = p.parse_args()

if args.cmd == "list":
  list_devices()
  sys.exit(0)
elif args.cmd == "attach" or args.cmd == "detach":
  if args.vendor != "" and args.device != "":
    create_xml("0x" + args.vendor, "0x" + args.device)
    if args.cmd == "attach":
      attatch(args.vm)
    elif args.cmd == "detach":
      detach(args.vm)
    delete_xml()
    sys.exit(0)

sys.exit("command not defined")

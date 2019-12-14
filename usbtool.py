#!/usr/bin/env python3

import sys
import os
import argparse
import usb.core
import libvirt
import libvirt_helpers as helpers

def list_devices():
  devices = usb.core.find(find_all=True)
  for i, d in enumerate(devices):
    if is_valid(d):
      print("{}:{} {} {}".format(hex(d.idVendor).lstrip('0x').zfill(4), hex(d.idProduct).lstrip('0x').zfill(4), d.manufacturer, d.product))

def is_valid(dev):
  if dev.manufacturer is None or 'Linux' in dev.manufacturer:
    return False
  return True

p = argparse.ArgumentParser(description='Manage usb devices of libvirt domains')
p.add_argument('command', help='list, attach or detach')
p.add_argument('--connect', default='qemu:///system', help='libvirt connection url (default: qemu:///system)')
p.add_argument('--domain', type=str, help='domain name')
p.add_argument('--vendor', type=str, help='vendor id of usb device')
p.add_argument('--device', type=str, help='device id of usb device')
args = p.parse_args()

if args.command == 'list':
  list_devices()
  sys.exit(0)
elif args.command == 'attach' or args.command == 'detach':
  conn = libvirt.open(args.connect)
  if conn == None:
    print('Failed to open connection to the hypervisor')
    sys.exit(1)

  dom = conn.lookupByName(args.domain)
  if dom == None:
    print('domain does not exist')
    sys.exit(1)

  helpers.get_usb_hostdev_xml('0x' + args.vendor, '0x' + args.device)
  if args.command == 'attach':
    dom.attachDevice(helpers.get_usb_hostdev_xml(args.vendor, args.device))
  elif args.command == 'detach':
    dom.detachDevice(helpers.get_usb_hostdev_xml(args.vendor, args.device))
  sys.exit(0)

sys.exit('no command given')

import sys
import libvirt
import libvirt_helpers as helpers
from flask import Flask
from flask_restful import Api, reqparse
from flask_httpauth import HTTPTokenAuth
from usbtool import get_usb_hostdev_xml

import config

app = Flask(__name__)
api = Api(app)
auth = HTTPTokenAuth(scheme='Bearer')

qemu = libvirt.open(config.libvirt_url)
if qemu == None:
    print('Failed to open connection to the hypervisor')
    sys.exit(1)

def wrap_message(msg):
  return {
    "message": msg
  }

def wrap_error(msg):
  return {
    "error": msg
  }

@auth.verify_token
def verify_token(token):
    if token in config.tokens:
        return True
    return False

@app.route('/')
def index():
  return wrap_message('Welcome to libvirt-usbtool REST API')

@app.route('/api/domains/<string:name>', methods=['GET'])
@auth.login_required
def show_domain(name):
  try:
    domain = qemu.lookupByName(name)
  except:
    return wrap_error('domain not found'), 404

  return {
    "name": domain.name(),
    "uuid": domain.UUIDString(),
    "active": bool(domain.isActive()),
    "usb_devices": helpers.get_usb_devices(domain),
  }, 200

@app.route('/api/domains/<string:name>/attach', methods=['PUT'])
@auth.login_required
def attach_to_domain(name):
  try:
    domain = qemu.lookupByName(name)
  except:
    return wrap_error('domain not found'), 404

  parser = reqparse.RequestParser()
  parser.add_argument("vendor_id")
  parser.add_argument("product_id")
  args = parser.parse_args()

  try:
    domain.attachDevice(get_usb_hostdev_xml(args['vendor_id'], args['product_id']))
  except libvirt.libvirtError as e:
    return wrap_error('attach device failed: ' + e.get_error_message()), 400

  return wrap_message('device attached'), 200


@app.route('/api/domains/<string:name>/detach', methods=['PUT'])
@auth.login_required
def detach_from_domain(name):
  try:
    domain = qemu.lookupByName(name)
  except:
    return wrap_error('domain not found'), 404

  parser = reqparse.RequestParser()
  parser.add_argument("vendor_id")
  parser.add_argument("product_id")
  args = parser.parse_args()

  try:
    domain.detachDevice(get_usb_hostdev_xml(args['vendor_id'], args['product_id']))
  except libvirt.libvirtError as e:
    return wrap_error('detach device failed: ' + e.get_error_message()), 400
  return  wrap_message('device detached'), 200

app.run(debug=False)
qemu.close()

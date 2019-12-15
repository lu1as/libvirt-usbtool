import sys
import libvirt
import libvirt_helpers as helpers
from flask import Flask
from flask_restful import Api, reqparse
from flask_httpauth import HTTPTokenAuth

import config

app = Flask(__name__)
api = Api(app)
auth = HTTPTokenAuth(scheme='Bearer')

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
  conn = libvirt.open(config.libvirt_url)
  if conn == None:
    return wrap_error('failed to open connecton to the hypervisor'), 500

  try:
    domain = conn.lookupByName(name)
  except:
    conn.close()
    return wrap_error('domain not found'), 404

  conn.close()
  return {
    "name": domain.name(),
    "uuid": domain.UUIDString(),
    "active": bool(domain.isActive()),
    "usb_devices": helpers.get_usb_devices(domain),
  }, 200

@app.route('/api/domains/<string:name>/start', methods=['POST'])
@auth.login_required
def start_domain(name):
  conn = libvirt.open(config.libvirt_url)
  if conn == None:
    return wrap_error('failed to open connecton to the hypervisor'), 500

  try:
    domain = conn.lookupByName(name)
  except:
    conn.close()
    return wrap_error('domain not found'), 404

  try:
    domain.create()
  except libvirt.libvirtError as e:
    conn.close()
    return wrap_error('start domain failed: ' + e.get_error_message()), 400

  conn.close()
  return wrap_message('domain started'), 200

@app.route('/api/domains/<string:name>/attach', methods=['PUT'])
@auth.login_required
def attach_to_domain(name):
  conn = libvirt.open(config.libvirt_url)
  if conn == None:
    return wrap_error('failed to open connecton to the hypervisor'), 500

  try:
    domain = conn.lookupByName(name)
  except:
    conn.close()
    return wrap_error('domain not found'), 404

  parser = reqparse.RequestParser()
  parser.add_argument("vendor_id")
  parser.add_argument("product_id")
  args = parser.parse_args()

  try:
    domain.attachDevice(helpers.get_usb_hostdev_xml(args['vendor_id'], args['product_id']))
  except libvirt.libvirtError as e:
    conn.close()
    return wrap_error('attach device failed: ' + e.get_error_message()), 400

  conn.close()
  return wrap_message('device attached'), 200


@app.route('/api/domains/<string:name>/detach', methods=['PUT'])
@auth.login_required
def detach_from_domain(name):
  conn = libvirt.open(config.libvirt_url)
  if conn == None:
    return wrap_error('failed to open connecton to the hypervisor'), 500

  try:
    domain = conn.lookupByName(name)
  except:
    conn.close()
    return wrap_error('domain not found'), 404

  parser = reqparse.RequestParser()
  parser.add_argument("vendor_id")
  parser.add_argument("product_id")
  args = parser.parse_args()

  try:
    domain.detachDevice(helpers.get_usb_hostdev_xml(args['vendor_id'], args['product_id']))
  except libvirt.libvirtError as e:
    conn.close()
    return wrap_error('detach device failed: ' + e.get_error_message()), 400
  
  conn.close()
  return  wrap_message('device detached'), 200


if __name__ == "__main__":
  app.run(debug=False)

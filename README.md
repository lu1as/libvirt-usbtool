# libvirt-usbtool

## Installation

install dependencies (CentOS)
```sh
yum install python36-pyusb python36-jinja2
pip3.6 install libvirt-python
```

install dependencies (Fedora)
```sh
dnf install python3-pyusb python3-jinja2 python3-libvirt
```

copy `usbtool.py` to `/usr/local/bin`
```sh
cp usbtool.py /usr/local/bin/usbtool
```

## Help

run `usbtool --help` to print help
```
usage: usbtool.py [-h] [--connect CONNECT] command [--domain DOMAIN] [--vendor VENDOR] [--device DEVICE]

Manage usb devices of libvirt domains

positional arguments:
  command            list, attach or detach

optional arguments:
  -h, --help         show this help message and exit
  --connect CONNECT  libvirt connection url (default: qemu:///system)
  --domain DOMAIN    domain name
  --vendor VENDOR    vendor id of usb device
  --device DEVICE    device id of usb device
```

## REST API

Copy the file `config.sample.py` to `config.py` and replace the default token with a random string.

Then install the required packages and run the app:

```sh
pip install -r requirements.txt
export FLASK_APP=app.py
flask run --host=127.0.0.1
```

API is now available at: `http://127.0.0.1:5000/`
All requests should contain a Bearer Authorization header with the valid token.
To get device information of a domain request path `/api/domains/<name>`:

```sh
curl -X PUT http://127.0.0.1:5000/api/domains/ubuntu -H 'Authorization: Bearer mysecrettoken'
```

For attach or detach devices call path `/api/domains/<name>/attach` or  `/api/domains/<name>/detach` with vendor and product ids in the request body:

```sh
curl -X PUT http://127.0.0.1:5000/api/domains/ubuntu/attach -H 'Authorization: Bearer mysecrettoken' \
  -H 'Content-Type: application/json' -d '{"vendor_id":"0x0000","product_id":"0x1111"}'
```

## Add usb devices automatally to virtual machine

First look up vendor and product id of your usb device with `lsusb`. For example:
```
Bus 003 Device 060: ID 12d1:1c51 Huawei Technologies Co., Ltd.
```

Then create udev rules file at `/etc/udev/rules.d/90-libvirt-usb.rules`.
```
ACTION=="add", SUBSYSTEM=="usb", ATTRS{idVendor}=="12d1", ATTRS{idProduct}=="1f0a", RUN+="/usr/local/bin/usbtool attach --domain=ubuntu --vendor=12d1 --device=1f0a"
ACTION=="remove", SUBSYSTEM=="usb", ENV{ID_VENDOR_ID}=="12d1", ENV{ID_MODEL_ID}=="1f0a", RUN+="/usr/local/bin/usbtool detach --domain=ubuntu --vendor=12d1 --device=1f0a"
```

Finally reload udev rules
```sh
sudo udevadm control --reload
```

# qemu-usbtool

## Installation

install dependencies (CentOS)
```sh
yum install python36-pyusb python36-jinja2
```

install dependencies (Fedora)
```sh
yum install python3-pyusb python3-jinja2
```

copy `usbtool.py` to `/usr/local/bin`
```sh
cp usbtool.py /usr/local/bin/usbtool
chmod +x /usr/local/bin/usbtool
```

## Help

run `usbtool --help` to print help
```
usage: usbtool [-h] [--vm VM] [--vendor VENDOR] [--device DEVICE] cmd

positional arguments:
  cmd              list, attach, detach

optional arguments:
  -h, --help       show this help message and exit
  --vm VM          virtual machine name
  --vendor VENDOR  usb vendor id
  --device DEVICE  usb device id
```

## Add usb devices automatally to virtual machine

First look up vendor and product id of your usb device with `lsusb`. For example:
```
Bus 003 Device 060: ID 12d1:1c51 Huawei Technologies Co., Ltd.
```

Then create udev rules file at `/etc/udev/rules.d/90-libvirt-usb.rules`.
```
ACTION=="add", SUBSYSTEM=="usb", ATTRS{idVendor}=="12d1", ATTRS{idProduct}=="1f0a", RUN+="/usr/local/bin/usbtool attach --vm=ubuntu --vendor=12d1 --device=1f0a"
ACTION=="remove", SUBSYSTEM=="usb", ENV{ID_VENDOR_ID}=="12d1", ENV{ID_MODEL_ID}=="1f0a", RUN+="/usr/local/bin/usbtool detach --vm=ubuntu --vendor=12d1 --device=1f0a"
```

Finally reload udev rules
```sh
sudo udevadm control --reload
```

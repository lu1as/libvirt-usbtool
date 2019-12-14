from xml.dom import minidom

def get_usb_devices(dom):
  xml = minidom.parseString(dom.XMLDesc(0))
  hostDevices = xml.getElementsByTagName('hostdev')
  usb = []
  for d in hostDevices:
    if d.getAttribute('type') == 'usb':
      source = d.getElementsByTagName("source")[0]
      usb.append({
        "vendor_id": source.getElementsByTagName("vendor")[0].getAttribute("id"),
        "product_id": source.getElementsByTagName("product")[0].getAttribute("id")
      })
  return usb

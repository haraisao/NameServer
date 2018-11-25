#
#
from xmlrpc import NameServer
import traceback

import uuid
import OpenRTM_aist, RTC, OpenRTM, SDOPackage, RTM, omniORB
import CosNaming

##############################
#  for RTM
#
def resolve_rtc(path):
    name_server = NameServer()
    try:
      if name_server:
        obj = name_server.root_context.resolve_str(path)
      return  obj
    except:
      pass
    return None 
#
#
def get_rtc_ec(path):
    try:
      rtc = resolve_rtc(path)
      if rtc :
        return rtc, rtc.get_owned_contexts()
    except:
      pass
    return None
#
#
def activate_rtc(path):
    try:
      rtc, ecs = get_rtc_ec(path)
      if ecs[0] :
        return ecs[0].activate_component(rtc)
    except:
      pass
    return False
#
# 
def deactivate_rtc(path):
    try:
      rtc, ecs = get_rtc_ec(path)
      if ecs[0] :
        return ecs[0].deactivate_component(rtc)
    except:
      pass
    return False
#
# 
def reset_rtc(path):
    try:
      rtc, ecs = get_rtc_ec(path)
      if ecs[0] :
        return ecs[0].reset_component(rtc)
    except:
      pass
    return False
#
# 
def exit_rtc(path):
    try:
      rtc = resolve_rtc(path)
      if rtc :
        return rtc.exit()
    except:
      pass
    return False
#
# 
def list(val=''):
    if type(val) == type("") :
        return list_one(val)
    if type(val) == type([]) :
        res = []
        for x in val:
          res.append( list(x) )
        return res
    return ""
#
#
def list_one(val=''):
    name_server = NameServer()
    try:
      root_context = name_server.root_context
      cxt = root_context
      cxt_str = val.split('/')
      for x in cxt_str:
          if x :
              if type(cxt.object_table[x][0]) == type(root_context) :
                  cxt = cxt.object_table[ x ][0]
              else:
                  return ""
      ll = cxt.object_table
      res = []
      for x in ll:
        if ll[x][1] == CosNaming.ncontext : res.append(val+x+"/")
        else: res.append(val+x)
      return res

    except:
      return ""
#
#
def get_rtc_ports(path):
  res = []
  try:
    rtc = resolve_rtc(path)
    ports = rtc.get_ports()
    for p in ports:
      prof = p.get_port_profile()
      res.append(prof.name.split('.')[-1]) 
  except:
    pass
  return res
#
#
def check_connection(outp, inp):
    opp = outp.get_port_profile()
    in_name = inp.get_port_profile().name
    for prof in opp.connector_profiles:
        ports = prof.ports
        if len(ports) == 2 :
            #print (outp._is_equivalent(ports[0]) )
            pname1=ports[0].get_port_profile().name
            pname2=ports[1].get_port_profile().name
            if pname1 == in_name or pname2 == in_name:
                #print prof.connector_id
                return prof.connector_id
    return None
#
#
def get_port_property(port, name):
    prof=port.get_port_profile()
    for x in prof.properties:
        if x.name == name:
            return x.value.value()
    return None

def dataTypeOfPort(port):
    return get_port_property(port, 'dataport.data_type')

def str2nv(name, value):
    return SDOPackage.NameValue(name, omniORB.any.to_any(value))

def connect_ports(outp, inp,
        subscription="flush", dataflow="Push",bufferlength=1,
        rate=1000, pushpolicy="new", interfaceType="corba_cdr"):

    if check_connection(outp, inp):
        print(' %s and %s are already connected' %  (out.get_port_profile().name, inp.get_port_profile().name))
        return True

    if dataTypeOfPort(outp) != dataTypeOfPort(inp):
        print(' %s and %s have different data types' % (outp.get_port_profile().name, inp.get_port_profile().name))
        return False

    nv1 = str2nv("dataport.interface_type", interfaceType)
    nv2 = str2nv("dataport.dataflow_type", dataflow)
    nv3 = str2nv("dataport.subscription_type", subscription)
    nv4 = str2nv("dataport.buffer.length", str(bufferlength))
    nv5 = str2nv("dataport.publisher.push_rate", str(rate))
    nv6 = str2nv("dataport.publisher.push_policy", pushpolicy)
    nv7 = str2nv("dataport.data_type", dataTypeOfPort(outp))

    con_prof = RTC.ConnectorProfile(str(uuid.uuid1()), "", [outp, inp], [nv1, nv2, nv3, nv4, nv5, nv6, nv7])

    ret, prof = outp.connect(con_prof)
    if ret != RTC.RTC_OK:
        print("failed to connect")
        return False

    if not check_connection(outp, inp):
        print("connet() returned RTC_OK, but not connected")
        return False
    return True

def disconnect_ports(outp, inp):
    cid = check_connection(outp, inp)
    if cid :
      outp.disconnect(cid)
      return True
    return False

def get_rtc_port(path, pname):
  try:
    rtc = resolve_rtc(path)
    ports = rtc.get_ports()
    for p in ports:
      prof = p.get_port_profile()
      if prof.name.split('.')[-1] == pname:
          return p
  except:
    pass
  return None
 
def get_connection_id(path1, path2):
  try:
    rtc1, pname1 = path1.split(':')
    rtc2, pname2 = path2.split(':')

    p1 = get_rtc_port(rtc1, pname1)
    p2 = get_rtc_port(rtc2, pname2)
    res = check_connection(p1, p2)
    return res
  except:
    pass
  return ''
    
def connect(path1, path2):
  try:
    rtc1, pname1 = path1.split(':')
    rtc2, pname2 = path2.split(':')
    p1 = get_rtc_port(rtc1, pname1)
    p2 = get_rtc_port(rtc2, pname2)
    res = connect_ports(p1, p2)
    return res
  except:
    pass
  return None

def disconnect(path1, path2):
  try:
    rtc1, pname1 = path1.split(':')
    rtc2, pname2 = path2.split(':')
    p1 = get_rtc_port(rtc1, pname1)
    p2 = get_rtc_port(rtc2, pname2)
    res = disconnect_ports(p1, p2)
    return res
  except:
    pass
  return None

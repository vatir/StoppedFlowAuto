#!/usr/bin/python
"""opdump - scan for operations on a given DCERPC interface

Usage: opdump.py hostname port interface version

This binds to the given hostname:port and DCERPC interface. Then, it tries to
call each of the first 256 operation numbers in turn and reports the outcome
of each call.

This will generate a burst of TCP connections to the given host:port!

Example:
$ ./opdump.py 10.0.0.30 135 99FCFEC4-5260-101B-BBCB-00AA0021347A 0.0
op 0 (0x00): rpc_x_bad_stub_data
op 1 (0x01): rpc_x_bad_stub_data
op 2 (0x02): rpc_x_bad_stub_data
op 3 (0x03): success
op 4 (0x04): rpc_x_bad_stub_data
ops 5-255: nca_s_op_rng_error

rpc_x_bad_stub_data, rpc_s_access_denied, and success generally means there's an
operation at that number.

Author: Catalin Patulea <cat@vv.carleton.ca>
"""
def chunks(l, n):
		""" Yield successive n-sized chunks from l.
		"""
		for i in xrange(0, len(l), n):
				yield l[i:i+n]
				
def bind(trans):
	interface = "bf679c30-705a-11d5-b0e1-525400dfee2f"
	iid = uuid.uuidtup_to_bin((interface, "1.0"))
	dce = trans.get_dce_rpc()
	dce.connect()
	dce.bind(iid)
	return dce

def send_op(dce, opnum, data=''):
	print "i: %i" % opnum
	
	dce.call(opnum, data)
	try:
			resp = dce.recv()
			print "Got something back: %i" % opnum
			#print resp.encode('hex')
	except dcerpc.Exception, e:
			result = str(e)
			print "Didn't get anything: %i" % opnum
			resp = ''
	else:
			result = "success"

	#print result
	#print "op %d (0x%02x): %s" % (opnum, opnum, result)

	return resp, result

def FindPort(Host):
		from impacket import uuid
		#from impacket.dcerpc.v5 import transport, epm
		from impacket.dcerpc import epm, transport, dcerpc
		#from impacket.dcerpc import epm as epmold
		host, port, interface, version = Host,	135, "e1af8308-5d1f-11c9-91a4-08002b14a0fa", "3.0"
	
		#epm.
		#print epm.hept_map(host, objectUUID=interface)
		stringbinding = "ncacn_ip_tcp:%s" % host

		trans = transport.DCERPCTransportFactory(stringbinding)
		trans.set_dport(port)
		dce = trans.get_dce_rpc()
		dce.connect()
		dce.bind(epm.MSRPC_UUID_PORTMAP)
		#epm.ept_map()
		rpcepm = epm.DCERPCEpm(dce)
	
		rpcepm.lookup(rpcepm, ObjectUUID="bf679c30705a11d5b0e1525400dfee2f")
		portmapreturn = rpcepm.portmap_dump()
		temp = portmapreturn.get_entry()._entries[0]
		temp2 = temp.get_tower().get_floors()
		targetport = int(temp2[3]._rhs.encode('hex'),16)
		return targetport


import sys
from impacket import uuid
#from impacket.dcerpc.v5 import transport, epm
from impacket.dcerpc import epm, transport, dcerpc
#from impacket.dcerpc import epm as epmold

host, port, interface, version = "129.237.98.75",	0, "e1af8308-5d1f-11c9-91a4-08002b14a0fa", "3.0"
targetport = FindPort(host)
print "Target Port: %i" % targetport
stringbinding = "ncacn_ip_tcp:%s" % host

trans = transport.DCERPCTransportFactory(stringbinding)
trans.set_dport(targetport)
#dce = trans.get_dce_rpc()
#dce.connect()
#dce.bind(epm.MSRPC_UUID_PORTMAP)
##epm.ept_map()
#rpcepm = epm.DCERPCEpm(dce)
	
#rpcepm.lookup(rpcepm, ObjectUUID="bf679c30705a11d5b0e1525400dfee2f")
#portmapreturn = rpcepm.portmap_dump()
#temp = portmapreturn.get_entry()._entries[0]
#temp2 = temp.get_tower().get_floors()
#targetport = int(temp2[3]._rhs.encode('hex'),16)
#print targetport

	
"""
targetport = 2579
trans2 = transport.DCERPCTransportFactory(stringbinding)
trans2 = transport.TCPTransport("129.237.98.75", targetport)
dce2 = trans2.get_dce_rpc()
dce2.connect()
temp5 = dce2.bind(iid)
"""

#diid = uuid.uuidtup_to_bin(("8a885d04-1ceb-11c9-9fe8-08002b104860", "2.0"))
#temp = epm.hept_map(host, iid, dataRepresentation=diid,protocol='ncacn_ip_tcp', objectUUID=iid ,port=1655, host=host)
#print temp


#hept_map

#temp3 = temp.get_tower().get_floors()
#temp2 = rpcepm.lookup(interface)
#print epm.EPMLookup(portmapreturn)
	
#print rpcepm.doRequest(3)
#print epm.EPMLookup(portmapreturn)
#print epm.doRequest(portmapreturn)
	
	
#iid = uuid.uuidtup_to_bin((interface, version))
#print str(epm.MSRPC_UUID_PORTMAP).encode('hex')

#print dce.bind(iid).fields["pduData"].encode('hex')
	
#000000000499499f65985f4bad3c78f9dcff77b6

#RequestCode = 0x00000000b932d4a701808a44b600173a02cdcf11
#RequestCode =''
#dce.DCERPC_RawCall(RequestCode)

#resp = dce.call(4, RequestCode)
#print resp

#000000003f14d4f98619bb449e51c706751504cd01

#RequestCode = 0x00000000b88004583ebdd54e9066bd7bacf265b5
#RequestCode = 0x00000000b932d4a701808a44b600173a02cdcf11
results = []
#for i in range(1,7):
"""
Pattern:
Get Port from ms rpc (port 135 with uuid lookup)

Bind target port

opnum: 2 with data: 00000000fa000000 (check if collecting)
if collecting: opnum: 0 with no data
responce: id for current data collection with a 01 at the end

opnum: 1 with data (1050 byte length starting with id and 00 04 then padded with zeroes)
responce: current filename name

possibly needs a opnum 2 with 0300000000000000 between commands

opnum: 3 with data: responce from opnum 0
returns current filename specs


"""
"""
# Opnum 2 working (returns 00 : Not Collecting 01: Collecting)
# If 00000000fa000000 is sent then 00 : Not Collecting 01: Collecting
# If 0300000000000000 is sent then 00 : Collecting 01: Not Collecting

i = 2
dce = trans.get_dce_rpc()
dce.connect()
		
dce.bind(iid)
print "i: %i" % i
	
dce.call(i, "00000000fa000000".decode('hex'))
try:
		resp = dce.recv()
		print "Got something back: %i" % i
		print resp.encode('hex')
except dcerpc.Exception, e:
		result = str(e)
		print "Didn't get anything: %i" % i
else:
		result = "success"

dce.disconnect()

print result
results.append(result)
"""
	
dce = bind(trans)
send_op(dce,2 ,"00000000fa000000".decode('hex'))

# Last round (not sure what this is for) may be involved in clearing last dataset (often causes timeouts)
#send_op(dce,2 ,"02000000ffffffff".decode('hex'))

try:
    # These are involved in closing out the previous dataset/link (but they cause timeouts if used at the wrong time)

    #send_op(dce,2 ,"02000000ffffffff".decode('hex'))
    send_op(dce,6 ,LastobjectID)
    pass
except:
    pass

temp = send_op(dce, 0)

objectID = temp[0][:-1]
senddata = (temp[0].encode('hex')[:-2]+"0004"+"0"*(1006+1050)).decode('hex')


send_op(dce,2 ,"0300000000000000".decode('hex'))
send_op(dce, 1, senddata)
	
send_op(dce,2 ,"0300000000000000".decode('hex'))
	
temp3 = send_op(dce, 3, temp[0])
send_op(dce,2 ,"0300000000000000".decode('hex'))
temp4 = send_op(dce, 4, objectID)

send_op(dce,2 ,"00000000fa000000".decode('hex'))


temp5 = send_op(dce,6 ,objectID)
send_op(dce,2 ,"00000000fa000000".decode('hex'))

LastobjectID = objectID 

# Last round (not sure what this is for)
#send_op(dce,2 ,"02000000ffffffff".decode('hex'))

#send_op(dce,2 ,"0300000000000000".decode('hex'))
#temp5 = send_op(dce, 4, objectID)

dce.disconnect()
	
# "0x"+temp4[0].encode('hex')
import struct
#print "Code 3:"
#for i in chunks(temp3[0].encode('hex'),8):
#    i = i[-2:] + i[-4:-2] + i[2:4] + i[:2]
#
#
#    #i = "0x" + str(i)
#    try:
#        #print i
#        p = struct.unpack('!f', i.decode('hex'))[0]
#
#        if (p > -1.0) and (p < 10.0) and (p !=0.0): print p
#        #if (p > -1.0) and (p < -0.0000005) and (p !=0.0): print p
#    except:
#        pass
#print "Code 3:"
#from math import log10
#for i in chunks(temp3[0][::].encode('hex'),8):
#    i = i[-2:] + i[-4:-2] + i[2:4] + i[:2]
#
#
#    #i = "0x" + str(i)
#    try:
#        #print i
#        p = struct.unpack('!f', i.decode('hex'))[0]
#
#        #if (p > -1.0) and (p < 10.0) and (p !=0.0): print p
#        if (p == 2.0): print p
#        if (log10(abs(p)) > -10.0) and (p > -1.0) and (p < -0.0000005) and (p !=0.0): print p
#    except:
#        pass
print "Code 4:"
from math import log10
for x, i in enumerate(chunks(temp4[0][::].encode('hex'),8)):
    i = i[-2:] + i[-4:-2] + i[2:4] + i[:2]


    #i = "0x" + str(i)
    try:
        #print i
    
        p = struct.unpack('!f', i.decode('hex'))[0]

        #if (p > -1.0) and (p < 10.0) and (p !=0.0): print p
        if (p == 2.0): print p
        if (log10(abs(p)) > -10.0) and (p > -1.0) and (p < -0.0000005) and (p !=0.0): print "%i: %f" % (x,p)
    except:
        pass

'''
i = 0
dce = trans.get_dce_rpc()
dce.connect()
		
dce.bind(iid)
print "i: %i" % i
	
dce.call(i, "")
try:
		resp = dce.recv()
		print "Got something back: %i" % i
		print resp.encode('hex')
except dcerpc.Exception, e:
		result = str(e)
		print "Didn't get anything: %i" % i
else:
		result = "success"

dce.disconnect()

print result
results.append(result)

i = 4
dce = trans.get_dce_rpc()
dce.connect()
		
dce.bind(iid)
print "i: %i" % i
	
dce.call(i, resp)
try:
		resp = dce.recv()
		print "Got something back: %i" % i
		print resp.encode('hex')
except dcerpc.Exception, e:
		result = str(e)
		print "Didn't get anything: %i" % i
else:
		result = "success"

dce.disconnect()

print result
results.append(result)


#for i in [4,]:
#	dce = trans.get_dce_rpc()
#	dce.connect()
		
#	dce.bind(iid)
#	print "i: %i" % i
#	dce.call(i, 0x000000000499499f65985f4bad3c78f9dcff77b6)
#	try:
#		resp = dce.recv()
#		print "Got something back: %i" % i
#		print resp.encode('hex')
#	except dcerpc.Exception, e:
#		result = str(e)
#		print "Didn't get anything: %i" % i
#	else:
#		result = "success"

#	dce.disconnect()

	#results.append(result)

# trim duplicate suffixes from the back
suffix = results[-1]
while results and results[-1] == suffix:
	results.pop()

for i, result in enumerate(results):
	print "op %d (0x%02x): %s" % (i, i, result)

print "ops %d-%d: %s" % (len(results), 255, suffix)
'''

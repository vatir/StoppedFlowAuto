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
import struct

host, port, interface, version = "129.237.98.75",	0, "e1af8308-5d1f-11c9-91a4-08002b14a0fa", "3.0"
targetport = FindPort(host)
print "Target Port: %i" % targetport
stringbinding = "ncacn_ip_tcp:%s" % host

trans = transport.DCERPCTransportFactory(stringbinding)
trans.set_dport(targetport)
dce = bind(trans)

Op0 = send_op(dce, 0)
objectID = Op0[0][:-1]
objectIDPlus = Op0[0]
print "objectID: %s" % objectID.encode('hex')

senddata = (Op0[0].encode('hex')[:-2]+"00040000").ljust(2100,'0').decode('hex')
getfilename = send_op(dce, 1, senddata)
filename = getfilename[0].encode('hex').decode('hex')[4:-2].strip("\x00")
print "Filename: %s" % filename
"""
print send_op(dce, 3, objectIDPlus)[1]
print send_op(dce, 4, objectID)[1]

Op0Old = Op0
Op0 = send_op(dce, 0)
objectID = Op0[0][:-1]
objectIDPlus = Op0[0]
print "objectID: %s" % objectID.encode('hex')

print send_op(dce, 4, objectID)[1]
print send_op(dce, 6, senddata)

senddata = ((Op0Old[0].encode('hex')[:-2]+"00040000").decode('hex')+filename).ljust(1050,'\x00')
getfilename = send_op(dce, 1, senddata)
print getfilename[1]


filename = getfilename[0].encode('hex').decode('hex')[4:-2].strip("\x00")
print "Filename: %s" % filename
"""
#print send_op(dce, 6, senddata)


#send_op(dce,2 ,"02000000ffffffff".decode('hex'))

#send_op(dce,2 ,"0300000000000000".decode('hex'))
#send_op(dce,2 ,"02000000ffffffff".decode('hex'))
#send_op(dce,2 ,"00000000fa000000".decode('hex'))

#print send_op(dce, 3, objectIDPlus)[1]
#print send_op(dce, 3, objectIDPlus)[1]
#print send_op(dce, 4, objectID)[1]
#print send_op(dce, 5, objectIDPlus)[1]

#temp4 = send_op(dce, 3, objectIDPlus)
#temp4 = send_op(dce, 4, objectID)
#temp4 = send_op(dce, 3, objectIDPlus)
#print send_op(dce, 3, objectIDPlus)[1]
'''
print send_op(dce, 4, objectID)[1]
print send_op(dce,6 ,objectID)
senddata = (Op0[0].encode('hex')[:-2]+"00040000"+filename.encode('hex')).ljust(2100,'0').decode('hex')
getfilename = send_op(dce, 1, senddata)
filename = getfilename[0].encode('hex').decode('hex')[4:-2].strip("\x00")
'''
temp4 = send_op(dce, 3, objectIDPlus)
#temp4 = send_op(dce, 4, objectID)

#print send_op(dce, 3, objectIDPlus)[1]

#temp4 = send_op(dce, 3, objectIDPlus)

#temp4 = send_op(dce, 4, objectIDPlus)
#temp3 = send_op(dce, 4, objectID)

#temp6 = send_op(dce,6 ,objectID)
print "Code 4:"
from math import log10
results = []
k = 0
for x, i in enumerate(chunks(temp4[0][::].encode('hex'),16)):  # chunks might need to be 4 or 8
    #i = i[-2:] + i[-4:-2] + i[2:4] + i[:2]
    z = i[8:]    
    z = z[6:8] + z[4:6] + z[2:4] + z[0:2]
    
    i = i[6:8] + i[4:6] + i[2:4] + i[0:2]
    
    
    
    
    #i = "0x" + str(i)
    try:
        #print i
    
        p = struct.unpack('!f', i.decode('hex'))[0]
        n = struct.unpack('!f', z.decode('hex'))[0]

        #if (p > -1.0) and (p < 10.0) and (p !=0.0): print p
        #if (p == 2.0): print p

        #if (log10(abs(p)) > -10.0) and (p > -1.0) and (p < -0.0000005) and (p !=0.0):

        if (log10(abs(p)) > -10.0) and (p > -1.0) and (p < 10.0) and (p !=0.0):
            k += 1
            print p
            results.append((k,x,p, int(z)))
    except:
        results.append((k,x,p,0))
    try:
        if (log10(abs(n)) > -10.0) and (n > -1.0) and (n < 10.0) and (n !=0.0):
            k += 1
            print n
            results.append((k,x,n, int(z)))
    except:
        results.append((k,x,n,0))
        #print "Error %i" % x

print "Results Length: %i" % len(results)
print "%i: %i: %f: %i" % (results[0][0],results[0][1],results[0][2],results[0][3])
print "%i: %i: %f: %i" % (results[-2][0],results[-2][1],results[-2][2],results[-2][3])

#for i in results[-100:-90]:
#    print i
dce.disconnect()


# -*- coding: utf-8 -*-
"""
Created on Mon Apr 21 17:16:51 2014

@author: Koan
"""
def reversebyte(spun, chunksize = 2):
    holder = []
    for x in chunks(spun, chunksize):
        holder.append(x)
    holder.reverse()
    try:
        unspun = reduce(lambda x, y: x+y, holder)
    except:
        return []
    return unspun

"""
print "Code 4:"
from math import log10
results = []
k = 0
for x, i in enumerate(chunks(temp4[0][0::].encode('hex'),32)):  # chunks might need to be 4 or 8
    #i = i[-2:] + i[-4:-2] + i[2:4] + i[:2]

    #print "%i: %s" % (x, i)

    OrigValue = i[:]
    
    print OrigValue
    #z = i[8:]
    
    z = OrigValue[24:]
    try:
        z = reversebyte(z)
    except:
        pass
    #z = z[6:8] + z[4:6] + z[2:4] + z[0:2]
    try:
        i = reversebyte(i)
    except:
        pass
    
    #i = i[6:8] + i[4:6] + i[2:4] + i[0:2]
    
    
    holder = []
    for value in chunks(OrigValue, 8):
        holder.append(struct.unpack('!i',reversebyte(value).decode('hex'))[0])
    print holder

    holder = []
    for value in chunks(OrigValue, 8):
        holder.append(struct.unpack('!f',reversebyte(value).decode('hex'))[0])
    print holder
    
    
    #i = "0x" + str(i)
    try:
        #print i
    
        p = struct.unpack('!f', i.decode('hex'))[0]
        n = struct.unpack('!f', z.decode('hex'))[0]
            
        #v1 = struct.unpack('!i',i.decode('hex'))[0]  # Int version

        #if (p > -1.0) and (p < 10.0) and (p !=0.0): print p
        #if (p == 2.0): print p

        #if (log10(abs(p)) > -10.0) and (p > -1.0) and (p < -0.0000005) and (p !=0.0):

        if (log10(abs(p)) > -10.0) and (p > -1.0) and (p < 10.0) and (p !=0.0):
            k += 1
            print OrigValue
            print "p: %f" % (p)
            results.append((k,x,p, int(z)))
    except:
        results.append((k,x,p,0))
    try:
        if (log10(abs(n)) > -10.0) and (n > -1.0) and (n < 10.0) and (n !=0.0):
            k += 1
            print OrigValue
            print "n: %f" % n
            results.append((k,x,n, int(z)))
    except:
        results.append((k,x,n,0))
        #print "Error %i" % x
"""
#print "Results Length: %i" % len(results)
#print "%i: %i: %f: %i" % (results[0][0],results[0][1],results[0][2],results[0][3])
#print "%i: %i: %f: %i" % (results[-2][0],results[-2][1],results[-2][2],results[-2][3])


print "Code 4:"
from math import log10
results = []
k = 0
for x, OrigValue in enumerate(chunks(temp4[0][::].encode('hex'),12*8)):  # chunks might need to be 4 or 8
    #print OrigValue
    holder = []
    fholder = []
    iholder = []
    for value in chunks(OrigValue, 8):
        try:
            holder.append(value)
            fholder.append(struct.unpack('!f',reversebyte(value).decode('hex'))[0])
            iholder.append(struct.unpack('!i',reversebyte(value).decode('hex'))[0])
        except:
            print "Exception!!!"
            print e
        
    chartemp = str(OrigValue.strip("\x00"))
    print "-------------------------------------------------------------"
    print "%i: %s" % (x, chartemp)
    
    TargetStr = ""
    for value in holder:
        TargetStr = TargetStr + str(value).rjust(10) + " : "
    print TargetStr[:-3]

    TargetStr = ""
    for value in iholder:
        TargetStr = TargetStr + str(value).rjust(10) + " : "
    print TargetStr[:-3]

    TargetStr = ""
    for value in fholder:
        TargetStr = TargetStr + "{:.4e}".format(value).rjust(10) + " : "
    print TargetStr[:-3]
    """
    try:
        v1 = struct.unpack('!i',reversebyte(holder[0]).decode('hex'))[0]
        v2 = struct.unpack('!i',reversebyte(holder[1]).decode('hex'))[0]
        v3 = struct.unpack('!i',reversebyte(holder[2]).decode('hex'))[0]
        v4 = struct.unpack('!i',reversebyte(holder[3]).decode('hex'))[0]
        print "%i : %i : %i : %i" % (v1,v2,v3,v4)
        v1 = struct.unpack('!f',reversebyte(holder[0]).decode('hex'))[0]
        v2 = struct.unpack('!f',reversebyte(holder[1]).decode('hex'))[0]
        v3 = struct.unpack('!f',reversebyte(holder[2]).decode('hex'))[0]
        v4 = struct.unpack('!f',reversebyte(holder[3]).decode('hex'))[0]
        print "%f : %f : %f : %f" % (v1,v2,v3,v4)

    except:
        print "Exception!!"
    """
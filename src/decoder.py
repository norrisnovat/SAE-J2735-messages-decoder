#!/usr/bin/env python
from binascii import unhexlify
import J2735_201603_combined_mobility
import sys
import csv
import numpy
import datetime

def extract_values(obj, key):
    """Pull all values of specified key from nested JSON."""
    arr = []

    def extract(obj, arr, key):
        """Recursively search for values of key in JSON tree."""
        if isinstance(obj, dict):
            for k, v in obj.items():
                if isinstance(v, (dict, list)):
                    extract(v, arr, key)
                elif k == key:
                    arr.append(v)
        elif isinstance(obj, list):
            for item in obj:
                extract(item, arr, key)
        return arr

    results = extract(obj, arr, key)
    return results

def convID(id, length):
    id = id.hex()
    i = 0
    if (length == 8):
        while(i<21):
            id = id[:i+2] + " " + id[i+2:]
            i += 3
    else:
        while(i<45):
            id = id[:i+2] + " " + id[i+2:]
            i += 3

    id = list(id.split(" "))

    for x in range(len(id)):
        inted = int(id[x], 16)
        id[x] = inted

    return id

def writeSpatHeader(instersectionPhaseArray):
    columnHeaderString="packetTimestamp,intersectionID"
    for headerPhase in range(1,instersectionPhaseArray):
        columnHeaderString = columnHeaderString + ",phase" + str(headerPhase) + "_eventState"
    columnHeaderString = columnHeaderString + ",hex\n"
    fout.write(columnHeaderString)


if (len(sys.argv) < 4) :
    print("Incomplete Arguments")
    exit(1)


fp1 = open(sys.argv[1],'r')
fout = open(sys.argv[2],'w')
msgType = sys.argv[3].strip(' \n')
msgid = sys.argv[4]


if (msgType == "BSM") :
    fout.write("packetTimestamp,bsm_id,secMark,latency,latitude,longitude,speed(m/s),heading,elevation(m),accel_long(m/s^2),hex\n")
elif (msgType=="MAP"):
    fout.write("packetTimestamp,intersectionID,hex\n")  
elif (msgType=="Mobility Request"):
    fout.write("packetTimestamp,hostStaticId,hostBSMId,planId,strategy,planType,urgency,strategyParams,trajectoryStart,trajectory,expiration\n")
elif (msgType=="Mobility Response") : 
    fout.write("packetTimestamp,hostStaticId,hostBSMId,planId,urgency,isAccepted\n")
elif (msgType=="Mobility Path") : 
    fout.write("packetTimestamp,hostStaticId,hostBSMId,planId,location,trajectory\n")
elif (msgType=="Mobility Operation") : 
    fout.write("packetTimestamp,hostStaticId,hostBSMId,planId,strategy,operationParams:\n")
elif (msgType=="Traffic Control Request") :
    fout.write("packetTimestamp,reqid,reqseq,scale,bounds:\n")
elif (msgType=="Traffic Control Message") : 
    fout.write("packetTimestamp,reqid,reqseq,msgtot,msgnum,id,updated,label,tcID,vclasses...,schedule...,detail...,geometry...\n")


fp = csv.reader(fp1,delimiter=',')
list1 = list(fp)

latency_array = []
prevSpatTimestamp = 0


for dt in list1:

    if (dt[1][0:4]==msgid):
        msg = J2735_201603_combined_mobility.DSRC.MessageFrame
        #print("hex: " + dt[1] + " byte length: " + str(len(dt[1])))
        try:
            msg.from_uper(unhexlify(dt[1]))
        except:
            continue

        
        if (msgid == "0013") :
            intersectionID = msg()['value'][1]['intersections'][0]['id']['id']
            instersectionPhaseArray = msg()['value'][1]['intersections'][0]['states']

            numPhases = len(instersectionPhaseArray)+1
            spatPhaseArray = [""] * numPhases
            writeSpatHeader(numPhases - 1)

            for phase in range(len(instersectionPhaseArray)):
                currentPhase = msg()['value'][1]['intersections'][0]['states'][phase].get('signalGroup')
                currentState = msg()['value'][1]['intersections'][0]['states'][phase]['state-time-speed'][0]['eventState']
                spatPhaseArray[currentPhase] = currentState
            
            spatString = str(dt[0]) + "," + str(intersectionID)
            
            for printPhase in range(1,len(instersectionPhaseArray)):
                spatString = spatString + "," + spatPhaseArray[printPhase]
            spatString = spatString + ',' + str(dt[1]) + "\n"
            
            fout.write(spatString)

        elif (msgid == "0012") :
            intersectionID = msg()['value'][1]['intersections'][0]['id']['id']
            #if intersectionID == intersection:
            lat = msg()['value'][1]['intersections'][0]['refPoint']['lat']
            longstr = msg()['value'][1]['intersections'][0]['refPoint']['long']
            laneWidth = msg()['value'][1]['intersections'][0]['laneWidth']
            fout.write(str(dt[0])+','+str(intersectionID)+','+str(lat/10000000.0)+','+str(longstr/10000000.0)+','+str(laneWidth)+','+str(dt[1])+'\n')

        elif (msgid == "0014") : # if bsm , look for lat, long, speed along with time
            bsmId = msg()['value'][1]['coreData']['id']
            lat= msg()['value'][1]['coreData']['lat']
            longstr = msg()['value'][1]['coreData']['long']
            speed = msg()['value'][1]['coreData']['speed']
            elevation = msg()['value'][1]['coreData']['elev']
            secMark = msg()['value'][1]['coreData']['secMark']
            heading = msg()['value'][1]['coreData']['heading']
            speed_converted = speed*0.02 #m/s
            accel_long = msg()['value'][1]['coreData']['accelSet']['long']
            accel_long_converted = accel_long*0.01 #m^s^2
            
            packet_timestamp = datetime.datetime.fromtimestamp(int(float(dt[0])))
            roundDownMinTime = datetime.datetime(packet_timestamp.year,packet_timestamp.month,packet_timestamp.day,packet_timestamp.hour,packet_timestamp.minute).timestamp()
            packetSecondsAfterMin = (float(dt[0]) - roundDownMinTime)
            latency = packetSecondsAfterMin*1000 - secMark
            if (latency < 0) :
                #print("[!!!] Minute mismatch")
                latency = latency + 60000
            #print("latency: " + str(latency))
            
            latency_array.append(latency)
            
            fout.write(str(dt[0])+','+str(bsmId.hex())+','+str(secMark)+','+str(latency)+','+str(lat/10000000.0)+','+str(longstr/10000000.0)+','+str(speed_converted)+','+str(heading)+','+str(accel_long_converted)+','+ str(elevation)+','+str(dt[1])+'\n')

        elif (msgid == "00f0") :
            hostStaticId = msg()['value'][1]['header']['hostStaticId']
            hostBSMId = msg()['value'][1]['header']['hostBSMId']
            planId = msg()['value'][1]['header']['planId']
            strategy = msg()['value'][1]['body']['strategy']
            planType = msg()['value'][1]['body']['planType']
            urgency = msg()['value'][1]['body']['urgency']
            strategyParams = msg()['value'][1]['body']['strategyParams']
            trajectoryStart = msg()['value'][1]['body']['trajectoryStart']
            trajectory = msg()['value'][1]['body']['trajectory']
            expiration = msg()['value'][1]['body']['expiration']

            fout.write(str(dt[0])+','+str(hostStaticId)+','+str(hostBSMId)+','+str(planId)+','+str(strategy)+','+str(planType)+','+str(urgency)+''+str(strategyParams)+''+str(trajectoryStart)+''+str(trajectory)+''+str(expiration)+''+'\n')

        elif (msgid == "00f1") :
            hostStaticId = msg()['value'][1]['header']['hostStaticId']
            hostBSMId = msg()['value'][1]['header']['hostBSMId']
            planId = msg()['value'][1]['header']['planId']
            urgency = msg()['value'][1]['body']['urgency']
            isAccepted = msg()['value'][1]['body']['isAccepted']

            fout.write(str(dt[0])+','+str(hostStaticId)+','+str(hostBSMId)+','+str(planId)+','+str(urgency)+','+str(isAccepted)+'\n')

        elif (msgid == "00f2") :
            hostStaticId = msg()['value'][1]['header']['hostStaticId']
            hostBSMId = msg()['value'][1]['header']['hostBSMId']
            planId = msg()['value'][1]['header']['planId']
            location = msg()['value'][1]['body']['location']
            trajectory = msg()['value'][1]['body']['trajectory']

            fout.write(str(dt[0])+','+str(hostStaticId)+','+str(hostBSMId)+','+str(planId)+','+str(location)+','+str(trajectory)+'\n')

        elif (msgid == "00f3") :
            hostStaticId = msg()['value'][1]['header']['hostStaticId']
            hostBSMId = msg()['value'][1]['header']['hostBSMId']
            planId = msg()['value'][1]['header']['planId']
            strategy = msg()['value'][1]['body']['strategy']
            operationParams = msg()['value'][1]['body']['operationParams']
            
            fout.write(str(dt[0])+','+str(hostStaticId)+','+str(hostBSMId)+','+str(planId)+','+str(strategy)+','+str(operationParams)+'\n')

        elif (msgid == "00f4") :
            reqid = msg()['value'][1]['body'][1]['reqid']
            reqseq = msg()['value'][1]['body'][1]['reqseq']
            scale = msg()['value'][1]['body'][1]['scale']
            bounds = msg()['value'][1]['body'][1]['bounds']

            newReqId = str(convID(reqid, 8)).replace(",", " ")

            fout.write(str(dt[0])+','+newReqId+','+str(reqseq)+','+str(scale)+','+str(bounds)+','+str(dt[1])+'\n')
        
        elif (msgid == "00f5") :
            reqid = msg()['value'][1]['body'][1]['reqid']
            reqseq = msg()['value'][1]['body'][1]['reqseq']
            msgtot = msg()['value'][1]['body'][1]['msgtot']
            msgnum = msg()['value'][1]['body'][1]['msgnum']
            tcmId = msg()['value'][1]['body'][1]['id']
            updated = msg()['value'][1]['body'][1]['updated']
            label = msg()['value'][1]['body'][1]['package']['label']
            tcId = msg()['value'][1]['body'][1]['package']['tcids'][0]
            vclasses = msg()['value'][1]['body'][1]['params']['vclasses']
            schedule = msg()['value'][1]['body'][1]['params']['schedule']
            detail = msg()['value'][1]['body'][1]['params']['detail']
            geometry = msg()['value'][1]['body'][1]['geometry']

            newReqId = str(convID(reqid, 8)).replace(",", " ")
            newTcmId = str(convID(tcmId, 16)).replace(",", " ")
            newtcId = str(convID(tcId, 16)).replace(",", " ")

            fout.write(str(dt[0])+','+newReqId+','+str(reqseq)+','+str(msgtot)+','+str(msgnum)+','+newTcmId+','+str(updated)+','+str(label)+','+newtcId+','+str(vclasses)+','+str(schedule)+','+str(detail)+','+str(geometry)+','+str(dt[1])+'\n')
    
        else:
            sys.exit("Invalid message type\n")


if (msgid == "0014") : 
    print("")
    print("---------- Performance Metrics ----------")
    latency_avg = numpy.average(latency_array)
    print("Latency Average: " + str(latency_avg))
    latency_std = numpy.std(latency_array)
    print("Latency Standard Deviation (Jitter): " + str(latency_std))

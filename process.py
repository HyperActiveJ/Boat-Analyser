import socket
import dash
from dash import dcc, html
import dash_daq as daq
from dash.dependencies import Input, Output
import threading
import random
import time
import sys
from prettytable import PrettyTable
import os
import numpy as np
import plotly.express as px
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime,timedelta
import cProfile




class filtert:   
    def __init__(self):
        self.filterTaps = 10  
        self.filterLoop = 0   
        self.rpmt = np.zeros(self.filterTaps).tolist()
    
    def filtered(self):
        r = 0
        for t in self.rpmt:
            r += t
        return r/self.filterTaps
        
    def setVal(self, x):
        self.filterLoop = (self.filterLoop + 1) % self.filterTaps
        self.rpmt[self.filterLoop] = x
        
    def latestVal(self):
        return self.rpmt[self.filterLoop]
    

class engine:
    def __init__(self):
        self.rpm = filtert()
        self.ff = 0
        self.trimRaw = 0
        self.trimCalibrated = 0
        self.op = 0 #oil Pressure
        self.ot = 0 #oil temp
        self.ct = 0 #coolant temp
        self.cp = 0 #coolant pressure
        self.v = 0  #voltage 
        self.d1 = 0 #discreets1
        self.d2 = 0 #discreets2
        self.load = 0 #never observed
        self.torq = 0 #never observed
    


class data:
    count = 0 #Number of received Messages
    firstrun = 1
    lasttime =0
    running = False
    tengine = 0 #tracks the engine currnetly sending data
    
    engines = [engine(), engine()] 
    
    time_string = "2023-12-25 10:30:00"
    format_string = "%Y-%m-%d %H:%M:%S"
    time = datetime.strptime(time_string, format_string)

    
    excluded = 0
    
    latesttext = ""
    
    heading = 0
    variation = 0
    cog =  0
    sog = 0
    
    yaw = 0
    pitch = 0
    roll = 0

    rpmd = 0 #delta rpm
    rpmr = 0 #ratio of rpms

    
    trimd = 0 #delta trim in degrees calibrated
    trimr = 0 #ratio of trims
    
    tff = 0  #total Fuel Flow
    ffrc = 0 #fuel flow ratio corrected for engine HP

    
    mpg = 0 # miles per gallon
    filter = 0
    
    df2  = []

d = data()


def s16(value):
    return -(value & 0x8000) | (value & 0x7fff)


def decode(line, d, count):  
    d.count += 1
    
    if d.count % 10000 == 1:
       
       print(d.count*100/count)
    
    
    words = line.split(" ")
    updateCalcs = False
    

    if len(words) > 2:
        format_string = "%H:%M:%S.%f"
        time =  datetime.strptime(words[0], format_string)      
        if time < (d.time - timedelta(seconds=1.5)):
            print("ERROR" + str(time) + "  " + str(d.time) + " " + str(d.time - time))       
        d.time = time


        if words[2] == "1DF11A04":
            d.variation = s16(int(words[8]+words[7],16))*0.0001*57.2958          
            #updateCalcs = True
            trigger = "Variation"          
        if words[2] == "09F11200":
            d.heading = s16(int(words[5]+words[4],16))*0.0001*57.2958     
            d.headingc = d.heading + d.variation
            #updateCalcs = True
            trigger = "Heading"  
        if words[2] == "09F80203":
            cog = s16(int(words[6]+words[5],16))*0.0001*57.2958
            if abs(d.cog - cog) > 2:
                #print("COG " + str(abs(d.cog - cog) ))
                d.filter += 1    
            d.cog = cog
            sog = s16(int(words[8]+words[7],16))*0.01*2.23694
            if abs(d.sog - sog) > 0.3:
                #print("SOG " + str(abs(d.sog - sog) ))
                d.filter += 1     
            d.sog = sog
            updateCalcs = True
            trigger = "SOG"
        if words[2] == "0DF11900":
            d.yaw = s16(int(words[5]+words[4],16))*0.0001*57.2958
            d.pitch = s16(int(words[7]+words[6],16))*0.0001*57.2958
            d.roll = s16(int(words[9]+words[8],16))*0.0001*57.2958
            #updateCalcs = True
            trigger = "PYR"
        if words[2] == "09F20001":
            engine = int(words[3],16)
            d.engines[engine].rpm.setVal((int(words[5]+words[4],16))/4)
            d.engines[engine].trimRaw = int(words[8],16)
            if engine == 0:
                d.engines[engine].trimCalibrated = d.engines[engine].trimRaw * 0.26 - 3.5 #todo 
            else:
                d.engines[engine].trimCalibrated = d.engines[engine].trimRaw * 0.602 - 4.89 #todo
            updateCalcs = True
            trigger = "RPM/TRIM"
        if words[2] == "09F20101":    
            word3 = int(words[3],16) % 4
            if word3 == 0:
                d.tengine = int(words[5],16)
                d.engines[d.tengine].op = (int(words[7]+words[6],16))*100*0.000145038
                d.engines[d.tengine].ot = ((((int(words[9]+words[8],16)))*0.1)-273.15)*9/5+32
                d.engines[d.tengine].cta = int(words[10],16)
            if word3 == 1:
                d.engines[d.tengine].ct =  ((((d.engines[d.tengine].cta)+(int(words[4],16)<<8))*0.01)-273.15)*9/5+32
                d.engines[d.tengine].v = (int(words[6]+words[5],16))*0.01
                d.engines[d.tengine].ff = (int(words[8]+words[7],16))*0.1*0.2642
                if d.lasttime != d.tengine:
                    updateCalcs = True
                    trigger = "FF"
                d.lasttime = d.tengine
            if word3 == 2:
                d.engines[d.tengine].cp = 0
            if word3 == 3:
                d.engines[d.tengine].d1 = s16(int(words[5]+words[4],16))
                d.engines[d.tengine].d2 = s16(int(words[7]+words[6],16))
                d.engines[d.tengine].load = int(words[8],16)
                d.engines[d.tengine].torq = int(words[9],16)
                if (d.engines[d.tengine].load != 127) or (d.engines[d.tengine].torq != 127) or (d.engines[d.tengine].d1 != 0) or (d.engines[d.tengine].d2 != 0) :
                    print(d.tengine)
                    print(d.engines[d.tengine].d1)
                    print(d.engines[d.tengine].d2)
                    print(d.engines[d.tengine].load)
                    print(d.engines[d.tengine].torq)
                    
    if updateCalcs:
        

        
        #update the RPM Ratio of the port engine as a percentage of the starboard engine
        rpmd = d.engines[1].rpm.latestVal() - d.engines[0].rpm.latestVal()       
        if abs(d.rpmd - rpmd) > 200:
            d.filter += 1       
        d.rpmd = rpmd
        
        rpmr = 1
        if (d.engines[1].rpm.latestVal()) >0:
            rpmr  = (d.rpmd / float(d.engines[1].rpm.latestVal())) *100   
        if abs(d.rpmr - rpmr) > 5:
            #print("rpmr " + str(abs(d.rpmr - rpmr) ))
            d.filter += 1       
        d.rpmr = rpmr
    
    
        #update the RPM Ratio of the port engine as a percentage of the starboard engine
        d.rpmdf = d.engines[1].rpm.filtered() - d.engines[0].rpm.filtered()
        d.rpmrf = 1
        if (d.engines[1].rpm.filtered()) >0:
            d.rpmrf  = (d.rpmdf / float(d.engines[1].rpm.filtered())) *100
   
        #total fuel flow
        tff = d.engines[0].ff + d.engines[1].ff  
        if abs(d.tff - tff) > 0.2:
            #print("tff " + str(abs(d.tff - tff) ))
            d.filter += 1      
        d.tff = tff
    
        
        #Ratio of fuel flows, accounting for difference in horsepower
        ffrc = 1
        if (d.tff) >0:
            ffrc = (((d.engines[1].ff/d.tff)/(200/(115+200)))-1)*100
        if abs(d.ffrc - ffrc) > 5:
            #print("ffrc " + str(abs(d.ffrc - ffrc) ))
            d.filter += 1      
        d.ffrc = ffrc     

        
        #MPG
        mpg = 0
        if d.tff >0:
          mpg = d.sog/d.tff
        if abs(d.mpg - mpg) > 0.2:
            #print("mpg " + str(abs(d.mpg - mpg) ))
            d.filter += 1      
        d.mpg = mpg
        
        d.trimd = d.engines[1].trimCalibrated  - d.engines[0].trimCalibrated
        
 
        #Build Test Point Datbase 
        df2 = pd.DataFrame({\
                'time': [d.time],\
                'RPMp': [d.engines[0].rpm.latestVal()],\
                'RPMs': [d.engines[1].rpm.latestVal()],\
                'RPMpf': [d.engines[0].rpm.filtered()],\
                'RPMsf': [d.engines[1].rpm.filtered()],\
                'ffp': [d.engines[0].ff],\
                'ffs': [d.engines[1].ff],\
                'trimRawp': [d.engines[0].trimRaw],\
                'trimRaws': [d.engines[1].trimRaw],\
                'trimCalibratedp': [d.engines[0].trimCalibrated],\
                'trimCalibrateds': [d.engines[1].trimCalibrated],\
                'opp': [d.engines[0].op],\
                'ops': [d.engines[1].op],\
                'ctp': [d.engines[0].ct],\
                'cts': [d.engines[1].ct],\
                'otp': [d.engines[0].ot],\
                'ots': [d.engines[1].ot],\
                'vp': [d.engines[0].v],\
                'vs': [d.engines[1].v],\
                'MPG': [d.mpg],\
                'SOG': [d.sog],\
                'COG': [d.cog],\
                'Heading': [d.heading],\
                'HeadingC': [d.headingc],\
                'COG_Heading_d': [d.headingc - d.cog],\
                'yaw': [d.yaw],\
                'pitch': [d.pitch],\
                'roll': [d.roll],\
                'rpmd': [d.rpmd],\
                'rpmr': [d.rpmr],\
                'trimd': [d.trimd],\
                'tff': [d.tff],\
                'ffrc': [d.ffrc],\
                'trigger': [trigger],\
                'filterx': [d.filter],\
                })      
        
        d.filter -= 2
        if d.filter < 0:
            d.filter = 0
        
        d.df2.append(df2)
        #d.df = pd.concat([d.df, df2], ignore_index=True)
        #d.df = d.df.append(df2)

def postProcess():
    d.running += 1
    directory_path = os.getcwd() + "\\TestData"
    for filename in os.listdir( directory_path):
        file_path = os.path.join(directory_path, filename)
        if os.path.isfile(file_path):
            print(file_path)
            with open(file_path, 'r') as file:
                Lines = file.readlines()
                for line in Lines:
                    decode(line, d, len(Lines))

    d.df = pd.concat(d.df2)
    d.df.to_csv('processed'+str(time.time()), sep=',', header=True)

cProfile.run('postProcess()')
quit()

# TCP server function
def tcp_server():
    print("HERE")
    if(not os.path.isfile("lock")):
            print("2 copies")
            f2 = open('lock','a')
            return     
    
    HOST = '192.168.4.1'  # The server's hostname or IP address
    PORT = 1456        # The port used by the server
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))
    sockFile = sock.makefile(mode='r')
    f1 = open('raw'+str(time.time()), 'a')
  
    while True:
        line = sockFile.readline()
        f1.write(line+"\n")
        f1.flush()
        #decode(line,d)  

# Start TCP server in a separate thread
server_thread = threading.Thread(target=tcp_server)
server_thread.daemon = True
server_thread.start()

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

load_figure_template("darkly")

# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])


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
    cog =  0
    sog = 0
    
    yaw = 0
    pitch = 0
    roll = 0

    rpmd = 0 #delta rpm
    rpmr = 0 #ratio of rpms

    rpmdf = 0 #delta rpm
    rpmrf = 0 #ratio of rpms
    
    trimd = 0 #delta trim in degrees calibrated
    trimr = 0 #ratio of trims
    
    tff = 0  #total Fuel Flow
    ffrc = 0 #fuel flow ratio corrected for engine HP

    
    mpg = 0 # miles per gallon
    
    
    df =  pd.DataFrame({\
                'RPMp': [0],\
                'RPMs': [0],\
                'RPMpf': [0],\
                'RPMsf': [0],\
                'ffp': [0],\
                'ffs': [0],\
                'trimRawp': [0],\
                'trimRaws': [0],\
                'trimCalibratedp': [0],\
                'trimCalibrateds': [0],\
                'opp': [0],\
                'ops': [0],\
                'ctp': [0],\
                'cts': [0],\
                'otp': [0],\
                'ots': [0],\
                'vp': [0],\
                'vs': [0],\
                'MPG': [0],\
                'SOG': [0],\
                'COG': [0],\
                'yaw': [0],\
                'pitch': [0],\
                'roll': [0],\
                'rpmd': [0],\
                'rpmr': [0],\
                'rpmdf': [0],\
                'rpmrf': [0],\
                'trimd': [0],\
                'trimr': [0],\
                'tff': [0],\
                'ffrc': [0]\
                })         
    
d = data()

    
tab1_content = dbc.Card(
    dbc.CardBody([                
        html.Div([
            html.Div([                                     
                     dcc.Slider(
                        id='trimP',
                        value = 0,
                        min=-5,
                        max=5,
                        #step=0.5,
                        vertical=True,
                        marks=None,
                        tooltip={"placement": "top", "always_visible": True},
                    ),
                     dcc.Slider(
                        id='trimS',
                        value = 0,
                        min=-5,
                        max=5,
                        #step=0.5,
                        vertical=True,
                        marks=None,
                        tooltip={"placement": "top", "always_visible": True},
                    ),
                    dcc.Slider(
                        id='rpmp',
                        value = 0,
                        min=0,
                        max=6000,
                        #step=250,
                        vertical=True,
                        marks=None,
                        tooltip={"placement": "top", "always_visible": True},
                    ),
                    dcc.Slider(
                        id='rpms',
                        value = 0,
                        min=0,
                        max=6000,
                        #step=250,
                        vertical=True,
                        marks=None,#marks={i: '{}'.format(i) for i in range(0,6000,250)},
                        tooltip={"placement": "top", "always_visible": True},
                    ),
                    dcc.Slider(
                        id='sog',
                        value = 0,
                        min=0,
                        max=31,
                        #step=250,
                        vertical=True,
                        marks=None,#marks={i: '{}'.format(i) for i in range(0,6000,250)},
                        tooltip={"placement": "top", "always_visible": True},
                    ),
                    dcc.Slider(
                        id='mpg',
                        value = 0,
                        min=0,
                        max=3,
                        #step=250,
                        vertical=True,
                        marks=None,#marks={i: '{}'.format(i) for i in range(0,6000,250)},
                        tooltip={"placement": "top", "always_visible": True},
                    ),             
                ], style={'display': 'flex', 'justify-content': 'left', 'padding': '0px 0px 0px 0px'}),
                dcc.Slider(
                    id='rpmr',
                    value = 0,
                    min=-15,
                    max=15,
                    marks=None,
                    tooltip={"placement": "top", "always_visible": True},
                ),
            ], style={'marginTop': 0, 'justify-content': 'center'}),
            dcc.Graph(id = "tdmph"),
            dcc.Graph(id = "tdp"),
            dcc.Graph(id = "tdmpg"),
    ], style={'display': 'flex', 'justify-content': 'left'}),
    
    className="mt-3",
)

tab2_content = dbc.Card(
    dbc.CardBody( [
        html.Div([
            dcc.Slider(
                id='opp',
                value = 0,
                max=60+20,
                min=60-20,
                #step=1,
                marks=None,
                vertical=True,      
                tooltip={"placement": "top", "always_visible": True},                        
            ),
             dcc.Slider(
                id='ops',
                value = 0,
                max=93+20,
                min=93-20,
                #step=1,
                marks=None,
                vertical=True,
                tooltip={"placement": "top", "always_visible": True},
            ), 
            dcc.Slider(
                id='ctp',
                value = 0,
                max=133+20,
                min=133-20,
                #step=1,
                marks=None,
                vertical=True,
                tooltip={"placement": "top", "always_visible": True},
            ),
             dcc.Slider(
                id='cts',
                value = 0,
                max=133+20,
                min=133-20,
                #step=1,
                marks=None,
                vertical=True,
                tooltip={"placement": "top", "always_visible": True},
            ),
            dcc.Slider(
                id='ots',
                value = 0,
                max=150,
                min=80,
                #step=1,
                marks=None,
                vertical=True,
                tooltip={"placement": "top", "always_visible": True},
            ),
        ], style={'display': 'flex', 'justify-content': 'center'}),    
        html.Div([    
            daq.Gauge(
                id='RPMp',
                label='RPM Port',
                units="RPM",
                value=d.rpmr,
                min=0,
                max=6000,
                showCurrentValue = True,
                #color={"gradient":False,"ranges":{"#FF0001":[-15,1],"#00FF00":[1,11],"#0000FF":[11,15]}},
                size = 200,
            ),    
            daq.Gauge(
                id='RPMs',
                label='RPM Starboard',
                units="RPM",
                value=d.rpmr,
                min=0,
                max=6000,
                showCurrentValue = True,
                #color={"gradient":False,"ranges":{"#FF0001":[-15,1],"#00FF00":[1,11],"#0000FF":[11,15]}},
                size = 200,
            ),         
        ], style={'display': 'flex', 'justify-content': 'center'}),
            html.Div([
            daq.Gauge(
                id='CTp',
                label='Coolant Temp Port',
                units="f",
                min=0,
                max=150,
                showCurrentValue = True,
                #color={"gradient":False,"ranges":{"#FF0001":[-15,1],"#00FF00":[1,11],"#0000FF":[11,15]}},
                size = 200,
            ),    
            daq.Gauge(
                id='CTs',
                label='Collant Temp Starboard',
                units="f",
                min=0,
                max=150,
                #scale={'start': 130-30, 'interval': 5, 'labelInterval': 2},
                showCurrentValue = True,
                #color={"gradient":False,"ranges":{"#FF0001":[-15,1],"#00FF00":[1,11],"#0000FF":[11,15]}},
                size = 200,
            ),         
        ], style={'display': 'flex', 'justify-content': 'center'}),
            html.Div([
            daq.Gauge(
                id='OPp',
                label='Oil Pressure Port',
                units="psi",
                min=0,
                max=80,
                showCurrentValue = True,
                #color={"gradient":False,"ranges":{"#FF0001":[-15,1],"#00FF00":[1,11],"#0000FF":[11,15]}},
                size = 200,
            ),    
            daq.Gauge(
                id='OPs',
                label='Oil Presure Starboard',
                units="psi",
                min=0,
                max=120,
                showCurrentValue = True,
                #color={"gradient":False,"ranges":{"#FF0001":[-15,1],"#00FF00":[1,11],"#0000FF":[11,15]}},
                size = 200,
            ),         
        ], style={'display': 'flex', 'justify-content': 'center'}),
    ]),
    className="mt-3",
)

tabs = dbc.Tabs(
    [
        dbc.Tab(tab1_content, label="Data Collection"),
        dbc.Tab(tab2_content, label="Live Data"),
    ]
)

# Set up the layout of the Dash app
app.layout = html.Div([
    dcc.Interval(id='interval-component', interval=250, n_intervals=0),
    dcc.Markdown(id='text-output', style={"white-space": "pre", "font": "monospace", 'fontSize': 12, 'textAlign': 'center', 'marginTop': 0}),
    tabs,
])

# Callback to update the gauge
@app.callback(
    Output('sog', 'value'),
    Output('mpg', 'value'),
    Output('opp', 'value'),
    Output('ops', 'value'),
    Output('ctp', 'value'),
    Output('cts', 'value'),
    Output('ots', 'value'),
    Output('rpmp', 'value'),
    Output('rpms', 'value'),
    Output('rpmr', 'value'),
    Output('trimP', 'value'),
    Output('trimS', 'value'),   
    Output('tdp', 'figure'),
    Output('tdmpg', 'figure'),
    Output('tdmph', 'figure'),
    Output('text-output', 'children'),
    Input('interval-component', 'n_intervals')

    
)
def update_gauge(n):
    rd = 5
    r = (rd/2)+4*rd   

    tdpmpgf = go.Figure(data = px.density_contour(\
        d.df, y="RPMs", x="rpmr", z="MPG",histfunc="avg"
        )) 
    tdpmpgf.update_traces(contours_coloring="heatmap", contours_showlabels = True, zmax=2.4, zmin=1,  ybins=dict(start=2250, end=5250, size=500), xbins=dict(start=-r, end=r, size=rd),)
    tdpmpgf.update_layout( width=500, height=500, autosize=False, title="MPG",margin={'t':0,'l':0,'b':0,'r':0})    
    
    tdpf = go.Figure(data = px.density_contour(\
        d.df, y="SOG", x="rpmr", nbinsx=10, nbinsy=10
        ))
    tdpf.update_traces(contours_coloring="heatmap", contours_showlabels = True, zmax=100, zmin=0, ybins=dict(start=2250, end=5250, size=500), xbins=dict(start=-r, end=r, size=rd),)
    tdpf.update_layout( width=500, height=500, autosize=False, title="Total Points",margin={'t':0,'l':0,'b':0,'r':0})       
 

    # tdpmphf = go.Figure(data = px.density_contour(\
        # d.df, y="RPMs", x="rpmr", z="SOG",histfunc="avg"
        # ))
    
    # tdpmphf.update_traces(contours_coloring="heatmap", contours_showlabels = True, zmax=30, zmin=15,  ybins=dict(start=2250, end=5250, size=500), xbins=dict(start=-r, end=r, size=rd),)
    # tdpmphf.update_layout( width=500, height=500, autosize=False, title="MPG",margin={'t':0,'l':0,'b':0,'r':0})  

    # tdpmphf = go.Figure(data = px.density_contour(\
        # d.df, y="RPMs", x="RPMp", z="SOG",histfunc="avg"
        # ))
    
    # tdpmphf.update_traces(contours_coloring="heatmap", contours_showlabels = True, zmax=30, zmin=5,  ybins=dict(start=2250, end=5250, size=500), xbins=dict(start=2250, end=5250, size=500),)
    # tdpmphf.update_layout( width=500, height=500, autosize=False, title="MPG",margin={'t':0,'l':0,'b':0,'r':0})         
 
    # tdpmphf = go.Figure(data = px.density_contour(\
        # d.df, y="RPMs", x="RPMp", z="MPG",histfunc="avg"
        # ))
    
    # tdpmphf.update_traces(contours_coloring="heatmap", contours_showlabels = True, zmax=2, zmin=1,  ybins=dict(start=3250, end=5250, size=500), xbins=dict(start=3250, end=5250, size=500),)
    # tdpmphf.update_layout( width=500, height=500, autosize=False, title="MPG",margin={'t':0,'l':0,'b':0,'r':0})         
 

    tdpmphf = go.Figure(data = px.density_contour(\
        d.df, y="SOG", x="rpmr"
        ))
    
    tdpmphf.update_traces(contours_coloring="heatmap", contours_showlabels = True, ybins=dict(start=15, end=30, size=2), xbins=dict(start=-r, end=r, size=rd),)
    tdpmphf.update_layout( width=500, height=500, autosize=False, title="MPG",margin={'t':0,'l':0,'b':0,'r':0})      
 
    return  d.sog, d.mpg,\
    round(d.engines[0].op),  round(d.engines[1].op), \
    round(d.engines[0].ct),  round(d.engines[1].ct), round(d.engines[1].ot),  \
    d.engines[0].rpm.filtered(), d.engines[1].rpm.filtered(), d.rpmr, \
    d.engines[0].trimCalibrated, d.engines[1].trimCalibrated,\
    tdpf, tdpmpgf, tdpmphf,\
    d.latesttext



def s16(value):
    return -(value & 0x8000) | (value & 0x7fff)


def decode(line, d):  
    d.count += 1
    words = line.split(" ")
    updateCalcs = False
    
    if len(words) > 2:
        format_string = "%H:%M:%S.%f"
        time =  datetime.strptime(words[0], format_string)      
        if time < (d.time - timedelta(seconds=1.5)):
            print("ERROR" + str(time) + "  " + str(d.time) + " " + str(d.time - time))       
        d.time = time
        
        if words[2] == "09F11200":
            d.heading = s16(int(words[5]+words[4],16))*0.0001*57.2958
            
            updateCalcs = True
            trigger = "Heading"  
            print("SOG: " + str(round(d.sog,1)) + " Heading: " + str(round(d.heading,1)) + " COG: " + str(round(d.cog,1)) + " diff:" + str(round(d.heading - d.cog,1)))
        
        if words[2] == "09F80203":
            d.cog = s16(int(words[6]+words[5],16))*0.0001*57.2958
            d.sog = s16(int(words[8]+words[7],16))*0.01*2.23694
            updateCalcs = True
            trigger = "SOG"
        if words[2] == "0DF11900":
            d.yaw = s16(int(words[5]+words[4],16))*0.0001*57.2958
            d.pitch = s16(int(words[7]+words[6],16))*0.0001*57.2958
            d.roll = s16(int(words[9]+words[8],16))*0.0001*57.2958
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
        d.rpmd = d.engines[1].rpm.latestVal() - d.engines[0].rpm.latestVal()
        d.rpmr = 1
        if (d.engines[1].rpm.latestVal()) >0:
            d.rpmr  = (d.rpmd / float(d.engines[1].rpm.latestVal())) *100
       
    
    
        #update the RPM Ratio of the port engine as a percentage of the starboard engine
        d.rpmdf = d.engines[1].rpm.filtered() - d.engines[0].rpm.filtered()
        d.rpmrf = 1
        if (d.engines[1].rpm.filtered()) >0:
            d.rpmrf  = (d.rpmdf / float(d.engines[1].rpm.filtered())) *100
   
        #total fuel flow
        d.tff = d.engines[0].ff + d.engines[1].ff  
        
        #Ratio of fuel flows, accounting for difference in horsepower
        d.ffrc = 1
        if (d.tff) >0:
            d.ffrc = (((d.engines[1].ff/d.tff)/(200/(115+200)))-1)*100
               
        #MPG
        d.mpg = 0
        if d.tff >0:
          d.mpg = d.sog/d.tff
 
        d.latesttext = str(d.time)
 
        #Build Test Point Datbase
        if True: #(d.sog > 5) and (d.rpmr < 100) and (d.rpmr > -100) and (d.engines[1].rpm.latestVal() > 2000):  
            df2 = pd.DataFrame({\
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
                'yaw': [d.yaw],\
                'pitch': [d.pitch],\
                'roll': [d.roll],\
                'rpmd': [d.rpmd],\
                'rpmr': [d.rpmr],\
                'rpmdf': [d.rpmd],\
                'rpmrf': [d.rpmr],\
                'trimd': [d.trimd],\
                'trimr': [d.trimr],\
                'tff': [d.tff],\
                'ffrc': [d.ffrc],\
                'trigger': trigger\
                })         
        d.df = pd.concat([d.df, df2], ignore_index=True)
        #d.df = d.df.append(df2)



# TCP server function
def tcp_server():
    print("HERE")
    if(not os.path.isfile("lock")):
            print("2 copies")
            f2 = open('lock','a')
            return  
    d.running += 1
    directory_path = os.getcwd() + "\\TestData"
    for filename in os.listdir( directory_path):
        file_path = os.path.join(directory_path, filename)
        if os.path.isfile(file_path):
            print(file_path)
            with open(file_path, 'r') as file:
                Lines = file.readlines()
                for line in Lines:
                    decode(line, d)
                    #if d.sog > 6:
                    #   #time.sleep(0.0001)
    
    #f1 = open('processed'+str(time.time()), 'a')
    d.df.to_csv('processed'+str(time.time()), sep=',', header=True)
    quit()
    
    
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
        decode(line,d)
    
    

# Start TCP server in a separate thread
server_thread = threading.Thread(target=tcp_server)
server_thread.daemon = True
server_thread.start()

# Run the Dash app
if __name__ == '__main__':
    app.run_server(debug=True)
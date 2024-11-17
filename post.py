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

df = pd.read_csv("processed1730046495.8207157")

#print(df)

rd = 5
r = (rd/2)+4*rd   

df = df[(df.filterx< 1) & (df.SOG >10) & (df.SOG <30) & (df.rpmr>-15) & (df.rpmr < 15)]

dff3 = df[(df.rpmr > 2.5) & (df.rpmr < 7.5)]
dff2 = df[(df.rpmr > -5) & (df.rpmr < 5)]
dff1 = df[(df.rpmr > -7.5) & (df.rpmr < 2.5)]



fig1 = px.histogram(dff1, x="SOG", y="MPG",histfunc="avg", opacity=0.8, nbins = 20,
                   color_discrete_sequence=['red'] # color of histogram bars)) 
                   )
fig2 = px.histogram(dff2, x="SOG", y="MPG",histfunc="avg", opacity=0.8, nbins = 20,
                   color_discrete_sequence=['green'], trendline="lowess" # color of histogram bars)) 
                   )
fig3 = px.histogram(dff3, x="SOG", y="MPG",histfunc="avg", opacity=0.8, nbins = 20,
                   color_discrete_sequence=['blue'] # color of histogram bars)) 
                   )
fig = go.Figure(data = fig1.data + fig2.data + fig3.data )
#fig = go.Figure(data =  fig2.data)
fig.show()

quit()





fig = go.Figure(data = px.scatter(df, x="SOG", y="roll", trendline="lowess",  trendline_color_override="red"))


fig.show()

quit()









tdpmpgf = go.Figure(data = px.density_contour(\
     dff2, y="SOG", x="rpmr", z="MPG",histfunc="avg"
     )) 
tdpmpgf.update_traces(contours_coloring="heatmap", contours_showlabels = True)
tdpmpgf.update_layout( title="MPG",margin={'t':0,'l':0,'b':0,'r':0})    

#
tdpmpgf.show()



quit()


tdpmpgf = go.Figure(data = px.histogram(\
     df, x="filterx", y="trigger"\
     )) 


tdpmpgf.show()

tdpmpgf = go.Figure(data = px.line(\
    df, x="filterx"\
    )) 


tdpmpgf.show()

quit()


tdpmpgf = go.Figure(data = px.line(\
    df, x="Heading"\
    )) 
#tdpmpgf.show()


tdpmpgf = go.Figure(data = px.line(\
    df, x="SOG"\
    )) 
#tdpmpgf.show()
#quit()

dff3 = df[(df.rpmr > 2.5) & (df.rpmr < 7.5)]
dff2 = df[(df.rpmr > -2.5) & (df.rpmr < 2.5)]
dff1 = df[(df.rpmr > -7.5) & (df.rpmr < 2.5)]



fig1 = px.histogram(dff1, x="SOG", y="MPG",histfunc="avg", opacity=0.8, nbins = 20,
                   color_discrete_sequence=['red'] # color of histogram bars)) 
                   )
fig2 = px.histogram(dff2, x="SOG", y="MPG",histfunc="avg", opacity=0.8, nbins = 20,
                   color_discrete_sequence=['green'] # color of histogram bars)) 
                   )
fig3 = px.histogram(dff3, x="SOG", y="MPG",histfunc="avg", opacity=0.8, nbins = 20,
                   color_discrete_sequence=['blue'] # color of histogram bars)) 
                   )
fig = go.Figure(data = fig1.data + fig2.data + fig3.data )
#fig = go.Figure(data =  fig2.data)
fig.show()

quit()



dff1 = df[(df.rpmr > 0) & (df.rpmr < 5)]
#dff2 = df[(df.rpmr > -2.5) & (df.rpmr < 2.5)]
#dff3 = df[(df.rpmr > -7.5) & (df.rpmr < -2.5)]
dff3 = df[(df.rpmr > -5) & (df.rpmr < 0)]

dff2 = df[(df.rpmr > -5) & (df.rpmr < 5)]

fig1 = px.histogram(dff1, x="SOG", y="MPG",histfunc="avg", opacity=0.8, nbins = 30,
                   color_discrete_sequence=['red'] # color of histogram bars)) 
                   )
fig2 = px.histogram(dff2, x="SOG", y="MPG",histfunc="avg", opacity=0.8, nbins = 30,
                   color_discrete_sequence=['green'] # color of histogram bars)) 
                   )
fig3 = px.histogram(dff3, x="SOG", y="MPG",histfunc="avg", opacity=0.8, nbins = 30,
                   color_discrete_sequence=['blue'] # color of histogram bars)) 
                   )
fig = go.Figure(data = fig1.data + fig2.data + fig3.data )
#fig = go.Figure(data =  fig2.data + fig3.data)
fig.show()

quit()

tdpmpgf = go.Figure(data = px.histogram(\
     dff, x="SOG", y="MPG",histfunc="avg", color="rpmr"\
     )) 
     
tdpmpgf.update_layout( width=500, height=500, autosize=False, title="MPG",margin={'t':0,'l':0,'b':0,'r':0})    

tdpmpgf.show()
quit()




tdpmpgf = go.Figure(data = px.scatter(dff, x="rpmr", y="COG_Heading_d", trendline="ols",  trendline_color_override="red"))

tdpmpgf.update_layout( width=500, height=500)

tdpmpgf.show()

quit()

dff = df[(df.index > 6750) & (df.index < 10900) & (df.RPMs < 2650)]

tdpmpgf = go.Figure(data = px.line(\
    dff, x="RPMs"\
    )) 

tdpmpgf.update_layout( width=500, height=500)

tdpmpgf.show()

quit()

tdpmpgf = go.Figure(data = px.line(\
    df, x="Heading"\
    )) 

tdpmpgf.update_layout( width=500, height=500)    

tdpmpgf.show()

quit()

tdpmpgf = go.Figure(data = px.histogram(\
    df, x="COG"\
    )) 

tdpmpgf.update_layout( width=500, height=500, autosize=False, title="MPG",margin={'t':0,'l':0,'b':0,'r':0})    

tdpmpgf.show()

quit()

dff = df[(df.RPMs >3600) & (df.RPMs<3900)]

#dff = dff[(df.Heading >80) & (df.Heading <90)]

tdpmpgf = go.Figure(data = px.scatter(dff, x="MPG", y="ffrc", trendline="ols",  trendline_color_override="red")) 

tdpmpgf.update_layout( width=500, height=500, autosize=False)    

tdpmpgf.show()

# tdpmpgf = go.Figure(data = px.histogram(\
    # dff, x="trimCalibrateds", y="MPG",histfunc="avg"
    # )) 

# tdpmpgf.update_layout( width=500, height=500, autosize=False, title="MPG",margin={'t':0,'l':0,'b':0,'r':0})    

# tdpmpgf.show()

# tdpmpgf = go.Figure(data = px.density_contour(\
    # df, y="RPMs", x="rpmr", z="MPG",histfunc="avg"
    # )) 
# tdpmpgf.update_traces(contours_coloring="heatmap", contours_showlabels = True, zmax=2.4, zmin=1,  ybins=dict(start=2250, end=5250, size=500), xbins=dict(start=-r, end=r, size=rd),)
# tdpmpgf.update_layout( width=500, height=500, autosize=False, title="MPG",margin={'t':0,'l':0,'b':0,'r':0})    

# tdpmpgf.show()

# tdpmpgf = go.Figure(data = px.density_contour(\
    # df, y="SOG", x="rpmr", z="MPG",histfunc="avg"
    # )) 
# tdpmpgf.update_traces(contours_coloring="heatmap", contours_showlabels = True, zmax=2.4, zmin=1,  ybins=dict(start=16, end=28, size=2), xbins=dict(start=-r, end=r, size=rd),)
# tdpmpgf.update_layout( width=500, height=500, autosize=False, title="MPG",margin={'t':0,'l':0,'b':0,'r':0})    

# tdpmpgf.show()

# tdpmpgf = go.Figure(data = px.density_contour(\
    # df, y="tff", x="rpmr", z="SOG",histfunc="avg"
    # )) 
# tdpmpgf.update_traces(contours_coloring="heatmap", contours_showlabels = True, zmax=30, zmin=1,  ybins=dict(start=10, end=28, size=2), xbins=dict(start=-r, end=r, size=rd),)
# tdpmpgf.update_layout( width=500, height=500, autosize=False, title="MPG",margin={'t':0,'l':0,'b':0,'r':0})    


# tdpmpgf.show()

# tdpmpgf = go.Figure(data = px.density_contour(\
    # df, y="SOG", x="trimCalibrateds", z="MPG",histfunc="avg"
    # )) 
# tdpmpgf.update_traces(contours_coloring="heatmap", contours_showlabels = True, zmax=2.4, zmin=1,  ybins=dict(start=14, end=28, size=2), xbins=dict(start=-5, end=5, size=3),)
# tdpmpgf.update_layout( width=500, height=500, autosize=False, title="MPG",margin={'t':0,'l':0,'b':0,'r':0})    

# tdpmpgf.show()

#!/usr/bin/env python
# -*- coding: utf-8 -*-
from gluon import *

#check graph period to display time
def check_graph_period(graph_period):
    if graph_period == 'hour':	
        valueformat="hh:mm TT"
    elif graph_period == 'day':
        valueformat=" hh:mm TT"
    elif graph_period == 'month':
        valueformat="DDMMM"
    elif graph_period == 'week':
        valueformat="DDD,hh:mm TT"
    elif graph_period == 'year':
        valueformat="MMMYY "
    
    return valueformat


#check graph type
def check_graph_type(g_type,vm_ram,m_type):
    title={}
    if g_type=='cpu':
        title['y_title']='cpu(%)'
        title['g_title']="CPU PERFORMANCE"
    if g_type=='disk':
        title['y_title']='disk(B/s)'
        title['g_title']="DISK PERFORMANCE"
    if g_type=='nw':
        title['y_title']='net(MB/s)'
        title['g_title']="NETWORK PERFORMANCE"
    if g_type=="ram":
        title['y_title']="ram(MB)"
        title['g_title']="MEMORY PERFORMANCE"
    if m_type=='host':
        if g_type=='tmp':
            title['y_title']='t(Degree Celcius)'
            title['g_title']="TEMPERATURE PERFORMANCE"
        if g_type=='power':
            title['y_title']='power(Watt)'
            title['g_title']="POWER PERFORMANCE"
    return title

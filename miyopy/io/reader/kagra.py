#
#! coding:utf-8

import os
from scipy import signal
import miyopy.signal.mpfilter as mpf
import miyopy
import miyopy.io.readNDS2 as readNDS2
import platform
#
if platform.system() == 'Linux':
    DATAdir = '/users/Miyo/KagraDropboxMiyo/GIF/data/'
else:
    DATAdir = '/Users/miyo/Dropbox/KagraMiyo/GIF/data/'
    
import numpy as np
import pickle





def dumpPickle(fn,channel,chlst='1.chlst'):
    with open(DATAdir+chlst,'r') as f:
        chlst = f.read().splitlines()    
        chdic = {str(ch):i for i,ch in enumerate(chlst)}            
    with open(fn, 'rb') as f:
        pdata = pickle.load(f)
    data = [ pdata[chdic[ch]] for ch in channel]
    fs = 16.0
    return data,fs
           
def getpicklefname(start,tlen,chlst_num=1):
    strList2intList = lambda List: map(lambda x:int(x),List)    
    files = os.listdir(DATAdir)
    files = filter(lambda x:'chlst' not in x, files)
    files = filter(lambda x:'pickle' in x, files)
    info = map(lambda x:x.replace('.pickle',''),files)
    info = map(lambda x:x.split('_'),info)
    info = map(lambda x:strList2intList(x),info)
    for i,inf in enumerate(info):
        #print inf,start,tlen,inf[0]<start
        if ((start+tlen)-inf[0]<=inf[1])and(inf[0]<=start):
            pickle_fname = DATAdir + '{0}_{1}_{2}.pickle'.format(info[i][0],info[i][1],info[i][2])            
            return pickle_fname,[start-info[i][0],(start+tlen)-info[i][0]]

def DumpedFile_is_exist(start,tlen,channel):
    return True

def loaddata_nds(start,tlen):
    try:
        with open(DATAdir+'1.chlst','r') as f:
            channels = f.read().splitlines()            
        data = readNDS2.fetch_data(start,start+tlen,channels)
        fs = 16
        fname = DATAdir+'{0}_{1}_{2}.pickle'.format(start,tlen,1)
        print fname
        readNDS2.dump(fname,data)        
    except TypeError as e:
        print e
        print 'huge'
        exit()
    return data



def readKAGRAdata(start,tlen,channels,fs_resample=8):
    '''
    KAGRAデータを読み込む
    '''    
    try:
        fname,idx = getpicklefname(start,tlen)
        data,fs = dumpPickle(fname,channels)
    except TypeError as e:
        print type(e),e
        print 'There is no pickle data'
        print ' please save pickle data from nds or gwf'
        data = loaddata_nds(start,tlen)
        exit()
        #fname,idx = getpicklefname(start,tlen)
        fs = 16.0       
    data = map(lambda x:x[int(fs*idx[0]):int(fs*idx[1])],data)
    data = mpf.decimate(data,fs_befor=fs,fs_after=fs_resample)
    #data = signal.detrend(data)
    return data
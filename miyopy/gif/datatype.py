import numpy as np
from astropy import units as u
from miyopy.time import to_JSTdatetime,to_GPStime





Hz = 1
byte = 1


datatype = {
    # Data Loction   : [ Sampling Frequncy, Data Size, c2V or Strain]
    '/NAS/cRIO01_data/':[(200*Hz,4*byte), np.int32, 1.25e-6*u.Volt],
    '/NAS/cRIO02_data/':[(200*Hz,4*byte), np.int32, 1.25e-6*u.Volt],
    '/NAS/cRIO03_data/':[(200*Hz,4*byte), np.int32, 1.25e-6*u.Volt],
    '/NAS/PXI1_data/5000Hz/':[(5000*Hz,4*byte), np.int32, 5.525e-9*u.Volt],
    '/NAS/PXI1_data/50000Hz/':[(50000*Hz,4*byte), np.int32, 5.525e-9*u.Volt],
    '/data1/PHASE/50000Hz/':[(200*Hz,8*byte),np.float64,1],
    '/data2/CLIO/LIN/':[(200*Hz,8*byte), np.float64, 1],
    '/data2/CLIO/SHR/':[(200*Hz,8*byte), np.float64, 1],
}
    
fname_fmt={
    # ChannelName:Format,Mustreplace<filename>.
    'X500_TEMP':'/NAS/cRIO01_data/<filename>.AD00',
    'X500_HUMD':'/NAS/cRIO01_data/<filename>.AD01',
    'X500_BARO':'/NAS/cRIO01_data/<filename>.AD02',
    'X500_VACU':'/NAS/cRIO01_data/<filename>.AD03',
    'X500_04':'/NAS/cRIO01_data/<filename>.AD04',
    'X500_05':'/NAS/cRIO01_data/<filename>.AD05',
    'X500_06':'/NAS/cRIO01_data/<filename>.AD06',
    'X500_07':'/NAS/cRIO01_data/<filename>.AD07',
    'X2000_TEMP':'/NAS/cRIO02_data/<filename>.AD00',
    'X2000_HUMD':'/NAS/cRIO02_data/<filename>.AD01',
    'X2000_BARO':'/NAS/cRIO02_data/<filename>.AD02',
    'X2000_VACU':'/NAS/cRIO02_data/<filename>.AD03',
    'X2000_04':'/NAS/cRIO02_data/<filename>.AD04',
    'X2000_05':'/NAS/cRIO02_data/<filename>.AD05',
    'X2000_06':'/NAS/cRIO02_data/<filename>.AD06',
    'X2000_07':'/NAS/cRIO02_data/<filename>.AD07',
    #
    'X1500_TR240velEW'	:'/NAS/cRIO03_data/<filename>.AD00',
    'X1500_01'	:'/NAS/cRIO03_data/<filename>.AD01',
    'X1500_TR240velNS':'/NAS/cRIO03_data/<filename>.AD02',
    'X1500_TR240velUD':'/NAS/cRIO03_data/<filename>.AD03',
    'X1500_TR240posEW':'/NAS/cRIO03_data/<filename>.AD04',
    'X1500_TR240posNS':'/NAS/cRIO03_data/<filename>.AD05',
    'X1500_TR240posUD':'/NAS/cRIO03_data/<filename>.AD06',
    'X1500_07':'/NAS/cRIO03_data/<filename>.AD07',
    'X1500_CMG3TvelEW':'/NAS/cRIO03_data/<filename>.AD08',
    'X1500_CMG3TvelNS':'/NAS/cRIO03_data/<filename>.AD09',
    'X1500_CMG3TvelUD':'/NAS/cRIO03_data/<filename>.AD10',
    'X1500_11':'/NAS/cRIO03_data/<filename>.AD11',
    'X1500_CMG3TposEW':'/NAS/cRIO03_data/<filename>.AD12',
    'X1500_CMG3TposNS':'/NAS/cRIO03_data/<filename>.AD13',
    'X1500_CMG3TposUD':'/NAS/cRIO03_data/<filename>.AD14',
    'X1500_15':'/NAS/cRIO03_data/<filename>.AD15',
    #
    'PD_PWAVE_PXI01_50k':'/NAS/PXI1_data/50000Hz/<filename>.AD00',
    'PD_SWAVE_PXI01_50k':'/NAS/PXI1_data/50000Hz/<filename>.AD01',
    'PD_INPUTWAVE_PXI01_50k':'/NAS/PXI1_data/50000Hz/<filename>.AD02',
    'PD_ABSORP_PXI01_50k':'/NAS/PXI1_data/50000Hz/<filename>.AD03',
    'PD_PWAVE_PXI01_5k':'/NAS/PXI1_data/5000Hz/<filename>.AD00',
    'PD_SWAVE_PXI01_5k':'/NAS/PXI1_data/5000Hz/<filename>.AD01',
    'PD_INPUTWAVE_PXI0_5k':'/NAS/PXI1_data/5000Hz/<filename>.AD02',
    'PD_ABSORP_PXI0_5k':'/NAS/PXI1_data/5000Hz/<filename>.AD03',
    'CALC_PHASE':'/data1/PHASE/50000Hz/<filename>.PHASE',
    'CALC_STRAIN':'/data1/PHASE/50000Hz/<filename>.STRAIN',
    'CALC_ZOBUN':'/data1/PHASE/50000Hz/<filename>.ZOBUN',
    'CALC_SQRT':'/data1/PHASE/50000Hz/<filename>.SQRT',
    'CLIO_CALC_STRAIN_LIN':'/data2/CLIO/LIN/<filename>.LIN',
    'CLIO_CALC_STRAIN_SHR':'/data2/CLIO/SHR/<filename>.SHR',
}
    
import logging

    
class NoChannelNameError(Exception):
    def __init__(self,chname):
        self.chname = chname
        keys = [key for key in fname_fmt.keys() if self.chname in key]
        if len(keys)==0:
            keys = fname_fmt.keys()
        self.text = '\n Is it in these channel name?'
        keys.sort(reverse=False)
        for key in keys:
            self.text += '\n- '+key
            
    def __str__(self):
        return "Invalid channel name '{0};{1}'".format(self.chname,self.text)
    
class gifdatatype(object):
    def __init__(self,chname,t0=None):
        self.chname = chname
        self._check_chname()
        self._get_info()
        if not isinstance(t0,type(None)):
            self.t0 = t0
            self._get_fname()

    def _check_chname(self):
        ''' check wheter channel name exit or not.        
        
        '''        
        if not self.chname in fname_fmt.keys():
            raise NoChannelNameError(self.chname)
        
        
    def _get_info(self):
        DataLocation = fname_fmt[self.chname].split('<filename>')[0]
        info = datatype[DataLocation]        
        self.dtype = info[1]
        self.byte = info[0][1]
        self.fs = info[0][0]
        self.c2V = info[2]        
            
    def _get_fname(self):
        date = to_JSTdatetime(int(self.t0))
        date_str = date.strftime('%Y/%m/%d/%H/%y%m%d%H%M')
        self.fname = fname_fmt[self.chname].replace('<filename>',date_str)
        

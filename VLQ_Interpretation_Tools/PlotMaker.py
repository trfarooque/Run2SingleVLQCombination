from Interp_Utils import *

#### Mass and Kappa ranges

Ms = range(10, 24, 1)
Ks = ['015', '020','025', '030', '035', '040', '045', '050', '060', '070', '080', '090', '100', '110', '120', '130', '140', '150', '160']

### Map of All Limits

Limit_map_all = LimitMapMaker("/afs/cern.ch/work/a/avroy/TRExFitter/SingleVLT_3l_Results/FitResults/")

### Make XS vs M plot for all couplings

for k in Ks:
    kappa = int(k)/100.
    XSLimit_Plotter(Limit_map_all, kappa)

### Make CW vs M plot

CWLimit_Plotter(Limit_map_all)

### Make cW - cZ - M plot

Limit_map = LimitReader(Limit_map_all, label="exp")
ATLASstyle_Map(Limit_map, kfact=1.0)

### Make sin(theta)-M plot

MixAngleLimit_Plotter(Limit_map_all, 'T')
#MixAngleLimit_Plotter(Limit_map_all, 'XTB')
Newstyle_Map(Limit_map)

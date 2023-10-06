from Interp_Utils import *
import json

#### Mass and Kappa ranges

Ms = range(10, 24, 1)
#Ks = ['015', '020','025', '030', '035', '040', '045', '050', '060', '070', '080', '090', '100', '110', '120', '130', '140', '150', '160']
Ks = ['010', '020', '030', '040', '050', '060', '070', '080', '090', '100', '110', '120', '130', '140', '150', '160']
BRWs = '50'

# Fit type
fit_to = 'data'
# fit_to = 'asimov_mu0'
analysis = 'SPT_COMBINED'

### Map of All Limits
loc = "/lustre/ific.uv.es/grid/atlas/t3/adruji/VLQcomb/fits/limits/%s/" % analysis
Limit_map_all = LimitMapMaker(loc, Ms, Ks, BRWs, analysis, fit_to)

### Make XS vs M plot for all couplings

for k in Ks:
    kappa = int(k)/100.
    XSLimit_Plotter(Limit_map_all, kappa)

### Make CW vs M plot

CWLimit_Plotter(Limit_map_all)

### Make cW - cZ - M plot
Limit_map = LimitReader(Limit_map_all, label="exp")
# Dump into json files
with open('Limit_map.json', 'w') as f:
    json.dump(Limit_map, f)

ATLASstyle_Map(Limit_map, kfact=1.0)

### Make sin(theta)-M plot

MixAngleLimit_Plotter(Limit_map_all, 'T')
#MixAngleLimit_Plotter(Limit_map_all, 'XTB')
Newstyle_Map(Limit_map)

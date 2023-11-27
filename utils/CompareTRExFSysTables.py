import numpy as np
import sys

##### Utility function to read systematics table file #####
def ReadAndParseSysInfo(fname):

    infile = open(fname,'r')
    lines = infile.readlines()
    infile.close()

    sysinfo={}
    split_lines = [ [e.strip() for e in ln.split('|')[1:len(ln.split('|'))-1]] for ln in lines ] 

    sysinfo['samples'] = split_lines[0][1:]
    sysinfo['systs'] = np.array(split_lines)[1:,0].tolist()
    sysinfo['zeroinds'] = np.array(np.where(np.array(split_lines)=='0 / 0'))

    sysinfo['upvals'] = np.array([ [float(e.split('/')[0].strip()) for e in line[1:]] \
                                   for line in split_lines[1:] ])
    sysinfo['downvals'] = np.array([ [float(e.split('/')[0].strip()) for e in line[1:]] \
                                   for line in split_lines[1:] ])

    return sysinfo

###### Read the two files to compare and check consistency of format ##### 
fname1 = 'SPT_MONOTOP_TCR_MONOTOP_scaled_M16K050BRW50_data_BONLY_syst_postFit.txt'
fname2 = 'SPT_MONOTOP_TCR__BONLY_syst_postFit.txt'

sysinfo1 = ReadAndParseSysInfo(fname1)
sysinfo2 = ReadAndParseSysInfo(fname2)

if(sysinfo1['samples'] != sysinfo2['samples']):
    print("<ERROR>:: Mismatched sample lists")
    print("Sample list 1 :",sysinfo1['samples'])
    print("Sample list 2 :",sysinfo2['samples'])
    sys.exit()

if(sysinfo1['systs'] != sysinfo2['systs']):
    print("<ERROR>:: Mismatched syst lists. Please check.")
    print("Sys list 1 :",sysinfo1['systs'])
    print("Sys list 2 :",sysinfo2['systs'])

    sys.exit()

### Check if identically zero elements are in the same positions in
### the two lists
if not np.array_equal(sysinfo1['zeroinds'],sysinfo2['zeroinds']):
    print("<WARNING>:: Location of zero uncertainties differ")
    
    print("Systematics 1:")
    print(" Sys     |    Sample") 
    for i in range(0, sysinfo1['zeroinds'].shape[1]):
        print( sysinfo1['systs'][sysinfo1['zeroinds'][0][i]], '  |   ', 
               sysinfo1['samples'][sysinfo1['zeroinds'][1][i]] )
               
        print("Systematics 2:")
        print(" Sys     |    Sample") 
    for i in range(0, sysinfo2['zeroinds'].shape[1]):
        print( sysinfo2['systs'][sysinfo2['zeroinds'][0][i]], '  |   ', 
               sysinfo2['samples'][sysinfo2['zeroinds'][1][i]] )


#### Now check if differences above threshold for any values ####
threshold = 0.1
reldiff_up = np.fabs(np.divide(np.subtract(sysinfo1['upvals'],sysinfo2['upvals']),
                               sysinfo1['upvals'],where=(sysinfo1['upvals'] != 0.)))
reldiff_down = np.fabs(np.divide(np.subtract(sysinfo1['downvals'],sysinfo2['downvals']),
                                 sysinfo1['downvals'], where=(sysinfo1['downvals'] != 0.)))

print("Maximum relative difference in up values: ", np.max(reldiff_up))
print("Maximum relative difference in down values: ", np.max(reldiff_down))

if(np.any(reldiff_up > threshold)):
    print( "Large differences in up variation observed: " )
    large_up = np.array(np.where(reldiff_up > threshold))
    for i in range(0, large_up.shape[1]):
        print( sysinfo2['systs'][large_up[0][i]], '  |   ', 
               sysinfo2['samples'][large_up[1][i]], ' >> ', 
               reldiff_up[large_up[0][i]][large_up[1][i]] )

if(np.any(reldiff_down > threshold)):
    print( "Large differences in down variation observed: " )
    large_down = np.array(np.where(reldiff_down > threshold))
    for i in range(0, large_down.shape[1]):
        print( sysinfo2['systs'][large_down[0][i]], '  |   ', 
               sysinfo2['samples'][large_down[1][i]], ' >> ', 
               reldiff_down[large_down[0][i]][large_down[1][i]] )


######################################################################################################

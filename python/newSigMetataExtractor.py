import ROOT, os, sys, subprocess, multiprocessing, re, json
from datetime import  datetime

def getMap_SumWeights(dsid_map, N0_map, _index = -1):  ## Index = -1 for nominal, other indices for accessing the variations
    for rtag in dsid_map.keys():
        if rtag not in N0_map.keys():
            N0_map[rtag] = 0.0
        this_files = dsid_map[rtag]
        for _file in this_files:
            this_file = ROOT.TFile.Open(_file)
            try:
                this_tree = this_file.Get("sumWeights")
            except:
                print "Warning! Could not access the file " + _file + ". Setting N0 = 0. for dsid " + str(dsid) + "for rtag " + rtag
                N0_map[rtag] = 0.
                break
            if(_index == "-1" or _index == -1):
                for entry in this_tree:
                    N0_map[rtag] += entry.totalEventsWeighted
            else:                    
                for entry in this_tree:
                    N0_map[rtag] += entry.totalEventsWeighted_mc_generator_weights[_index]
            this_file.Close()




def getN0(filelist_map2):
    #print "Starting multiprocessing"
    #t_multi0 = datetime.now()
    #manager = multiprocessing.Manager()
    N0_map = {}#manager.dict()                                                                                                                                        
    list_procs = []
    for _dsid in filelist_map2.keys():
        N0_map[_dsid] = {}
        for _index in range(1,41):
            #N0_map[_dsid][_index] = manager.dict()
            N0_map[_dsid][_index] = {}
            #list_procs.append(multiprocessing.Process(target = getMap_SumWeights, args = ( filelist_map2[_dsid], N0_map[_dsid][_index], _index )))
            getMap_SumWeights(filelist_map2[_dsid], N0_map[_dsid][_index], _index)
    #for th in list_procs: th.start()
    #for th in list_procs: th.join()
    
    # for _dsid in filelist_map2.keys():
    #     for _index in range(1,41):
    #         N0_map[_dsid][_index] = dict(N0_map[_dsid][_index])
    # print "Finished multiprocessing"
    #t_multi = datetime.now() - t_multi0
    #print "time needed: " , t_multi.seconds
    #print N0_map
    return dict(N0_map)


# def getIndexMap(_file, dsid, idx_map):
#     this_file = ROOT.TFile.Open(_file)
#     this_hist = this_file.Get("vlqRW_sumOfWeights")
#     for ii in range(this_hist.GetXaxis().GetNbins()):
#         print this_hist.GetXaxis().GetBinLabel(ii)
#         idx_map[dsid] = int(ii)
#     exit()

def getIndexMap(mktag, key):
    ktag = mktag[-3:]
    mtag = int(mktag[1:3])
    kdict = {}
    for n,k in enumerate(range(10,50,5) + range(50,170,10)):
        kdict['{0:03d}'.format(k)] = n+1 if(("WT" in key) and (mtag%2==0) and int(ktag)>60) else n+21
    try:
        return kdict[ktag]
    except KeyError:
        print "Wrong ktag given!"

datasets = { 'WTZt': [
'mc16_13TeV.508617.MGPy8EG_WTZt1100LH100_sig.recon.AOD.e8307_s3126_r9364',
'mc16_13TeV.508618.MGPy8EG_WTZt1300LH100_sig.recon.AOD.e8307_s3126_r9364',
'mc16_13TeV.508619.MGPy8EG_WTZt1500LH100_sig.recon.AOD.e8307_s3126_r9364',
'mc16_13TeV.508620.MGPy8EG_WTZt1700LH100_sig.recon.AOD.e8307_s3126_r9364',
'mc16_13TeV.508621.MGPy8EG_WTZt1900LH100_sig.recon.AOD.e8307_s3126_r9364',
'mc16_13TeV.508622.MGPy8EG_WTZt2100LH100_sig.recon.AOD.e8307_s3126_r9364',
'mc16_13TeV.508623.MGPy8EG_WTZt2300LH100_sig.recon.AOD.e8307_s3126_r9364',
'mc16_13TeV.508624.MGPy8EG_WTZt2500LH100_sig.recon.AOD.e8307_s3126_r9364',
'mc16_13TeV.508625.MGPy8EG_WTZt2700LH100_sig.recon.AOD.e8307_s3126_r9364',
'mc16_13TeV.508682.MGPy8EG_WTZt900LH100_sig.recon.AOD.e8307_s3126_r9364',
'mc16_13TeV.508626.MGPy8EG_WTZt1000LH040_sig.recon.AOD.e8307_s3126_r9364',
'mc16_13TeV.508627.MGPy8EG_WTZt1100LH040_sig.recon.AOD.e8307_s3126_r9364',
'mc16_13TeV.508628.MGPy8EG_WTZt1200LH040_sig.recon.AOD.e8307_s3126_r9364',
'mc16_13TeV.508629.MGPy8EG_WTZt1300LH040_sig.recon.AOD.e8307_s3126_r9364',
'mc16_13TeV.508630.MGPy8EG_WTZt1400LH040_sig.recon.AOD.e8307_s3126_r9364',
'mc16_13TeV.508631.MGPy8EG_WTZt1500LH040_sig.recon.AOD.e8307_s3126_r9364',
'mc16_13TeV.508632.MGPy8EG_WTZt1600LH040_sig.recon.AOD.e8307_s3126_r9364',
'mc16_13TeV.508633.MGPy8EG_WTZt1700LH040_sig.recon.AOD.e8307_s3126_r9364',
'mc16_13TeV.508634.MGPy8EG_WTZt1800LH040_sig.recon.AOD.e8307_s3126_r9364',
'mc16_13TeV.508635.MGPy8EG_WTZt1900LH040_sig.recon.AOD.e8307_s3126_r9364',
'mc16_13TeV.508636.MGPy8EG_WTZt2000LH040_sig.recon.AOD.e8307_s3126_r9364',
'mc16_13TeV.508637.MGPy8EG_WTZt2100LH040_sig.recon.AOD.e8307_s3126_r9364',
'mc16_13TeV.508638.MGPy8EG_WTZt2300LH040_sig.recon.AOD.e8307_s3126_r9364',
'mc16_13TeV.508639.MGPy8EG_WTZt2500LH040_sig.recon.AOD.e8307_s3126_r9364',
'mc16_13TeV.508640.MGPy8EG_WTZt2700LH040_sig.recon.AOD.e8307_s3126_r9364',
'mc16_13TeV.508680.MGPy8EG_WTZt800LH040_sig.recon.AOD.e8307_s3126_r9364',
'mc16_13TeV.508681.MGPy8EG_WTZt900LH040_sig.recon.AOD.e8307_s3126_r9364'
],
'ZTZt': [
'mc16_13TeV.501695.MGPy8EG_ZTZt1000LH040_sig.recon.AOD.e8307_s3126_r9364',
'mc16_13TeV.501696.MGPy8EG_ZTZt1100LH040_sig.recon.AOD.e8307_s3126_r9364',
'mc16_13TeV.501697.MGPy8EG_ZTZt1200LH040_sig.recon.AOD.e8307_s3126_r9364',
'mc16_13TeV.501698.MGPy8EG_ZTZt1300LH040_sig.recon.AOD.e8307_s3126_r9364',
'mc16_13TeV.501699.MGPy8EG_ZTZt1400LH040_sig.recon.AOD.e8307_s3126_r9364',
'mc16_13TeV.501700.MGPy8EG_ZTZt1500LH040_sig.recon.AOD.e8307_s3126_r9364',
'mc16_13TeV.501701.MGPy8EG_ZTZt1600LH040_sig.recon.AOD.e8307_s3126_r9364',
'mc16_13TeV.501702.MGPy8EG_ZTZt1700LH040_sig.recon.AOD.e8307_s3126_r9364',
'mc16_13TeV.501703.MGPy8EG_ZTZt1800LH040_sig.recon.AOD.e8307_s3126_r9364',
'mc16_13TeV.501704.MGPy8EG_ZTZt1900LH040_sig.recon.AOD.e8307_s3126_r9364',
'mc16_13TeV.501705.MGPy8EG_ZTZt2000LH040_sig.recon.AOD.e8307_s3126_r9364',
'mc16_13TeV.501706.MGPy8EG_ZTZt2100LH040_sig.recon.AOD.e8307_s3126_r9364',
'mc16_13TeV.501707.MGPy8EG_ZTZt2300LH040_sig.recon.AOD.e8307_s3126_r9364',
'mc16_13TeV.501708.MGPy8EG_ZTZt2500LH040_sig.recon.AOD.e8307_s3126_r9364',
'mc16_13TeV.501709.MGPy8EG_ZTZt2700LH040_sig.recon.AOD.e8307_s3126_r9364',
'mc16_13TeV.508870.MGPy8EG_ZTZt1000LH100_sig.recon.AOD.e8307_s3126_r9364',
'mc16_13TeV.508871.MGPy8EG_ZTZt1100LH100_sig.recon.AOD.e8307_s3126_r9364',
'mc16_13TeV.508872.MGPy8EG_ZTZt1200LH100_sig.recon.AOD.e8307_s3126_r9364',
'mc16_13TeV.508873.MGPy8EG_ZTZt1300LH100_sig.recon.AOD.e8307_s3126_r9364',
'mc16_13TeV.508874.MGPy8EG_ZTZt1400LH100_sig.recon.AOD.e8307_s3126_r9364',
'mc16_13TeV.508875.MGPy8EG_ZTZt1500LH100_sig.recon.AOD.e8307_s3126_r9364',
'mc16_13TeV.508876.MGPy8EG_ZTZt1600LH100_sig.recon.AOD.e8307_s3126_r9364',
'mc16_13TeV.508877.MGPy8EG_ZTZt1700LH100_sig.recon.AOD.e8307_s3126_r9364',
'mc16_13TeV.508878.MGPy8EG_ZTZt1800LH100_sig.recon.AOD.e8307_s3126_r9364',
'mc16_13TeV.508879.MGPy8EG_ZTZt1900LH100_sig.recon.AOD.e8307_s3126_r9364',
'mc16_13TeV.508880.MGPy8EG_ZTZt2000LH100_sig.recon.AOD.e8307_s3126_r9364',
'mc16_13TeV.508881.MGPy8EG_ZTZt2100LH100_sig.recon.AOD.e8307_s3126_r9364',
'mc16_13TeV.508882.MGPy8EG_ZTZt2300LH100_sig.recon.AOD.e8307_s3126_r9364',
'mc16_13TeV.508883.MGPy8EG_ZTZt2500LH100_sig.recon.AOD.e8307_s3126_r9364',
'mc16_13TeV.508884.MGPy8EG_ZTZt2700LH100_sig.recon.AOD.e8307_s3126_r9364',
],
'WTHt': [
'mc16_13TeV.313330.MGPy8EG_NNPDF30LO_A14NNPDF23LO_WTHt1100LH100_sig.recon.AOD.e8070_s3126_r9364',
'mc16_13TeV.313331.MGPy8EG_NNPDF30LO_A14NNPDF23LO_WTHt1300LH100_sig.recon.AOD.e8070_s3126_r9364',
'mc16_13TeV.313332.MGPy8EG_NNPDF30LO_A14NNPDF23LO_WTHt1500LH100_sig.recon.AOD.e8070_s3126_r9364',
'mc16_13TeV.313333.MGPy8EG_NNPDF30LO_A14NNPDF23LO_WTHt1700LH100_sig.recon.AOD.e8070_s3126_r9364',
'mc16_13TeV.313334.MGPy8EG_NNPDF30LO_A14NNPDF23LO_WTHt1900LH100_sig.recon.AOD.e8070_s3126_r9364',
'mc16_13TeV.313335.MGPy8EG_NNPDF30LO_A14NNPDF23LO_WTHt2100LH100_sig.recon.AOD.e8070_s3126_r9364',
'mc16_13TeV.313336.MGPy8EG_NNPDF30LO_A14NNPDF23LO_WTHt2300LH100_sig.recon.AOD.e8070_s3126_r9364',
],
'ZTHt': [
'mc16_13TeV.508720.MGPy8EG_ZTHt1000LH100_sig.recon.AOD.e8307_s3126_r9364',
'mc16_13TeV.508721.MGPy8EG_ZTHt1100LH100_sig.recon.AOD.e8307_s3126_r9364',
'mc16_13TeV.508722.MGPy8EG_ZTHt1200LH100_sig.recon.AOD.e8307_s3126_r9364',
'mc16_13TeV.508723.MGPy8EG_ZTHt1300LH100_sig.recon.AOD.e8307_s3126_r9364',
'mc16_13TeV.508724.MGPy8EG_ZTHt1400LH100_sig.recon.AOD.e8307_s3126_r9364',
'mc16_13TeV.508725.MGPy8EG_ZTHt1500LH100_sig.recon.AOD.e8307_s3126_r9364',
'mc16_13TeV.508726.MGPy8EG_ZTHt1600LH100_sig.recon.AOD.e8307_s3126_r9364',
'mc16_13TeV.508727.MGPy8EG_ZTHt1000LH020_sig.recon.AOD.e8307_s3126_r9364',
'mc16_13TeV.508728.MGPy8EG_ZTHt1000LH040_sig.recon.AOD.e8307_s3126_r9364',
'mc16_13TeV.508729.MGPy8EG_ZTHt1000LH070_sig.recon.AOD.e8307_s3126_r9364',
'mc16_13TeV.508730.MGPy8EG_ZTHt1100LH020_sig.recon.AOD.e8307_s3126_r9364',
'mc16_13TeV.508731.MGPy8EG_ZTHt1100LH040_sig.recon.AOD.e8307_s3126_r9364',
'mc16_13TeV.508732.MGPy8EG_ZTHt1100LH070_sig.recon.AOD.e8307_s3126_r9364',
'mc16_13TeV.508733.MGPy8EG_ZTHt1200LH020_sig.recon.AOD.e8307_s3126_r9364',
'mc16_13TeV.508734.MGPy8EG_ZTHt1200LH040_sig.recon.AOD.e8307_s3126_r9364',
'mc16_13TeV.508735.MGPy8EG_ZTHt1200LH070_sig.recon.AOD.e8307_s3126_r9364',
'mc16_13TeV.508736.MGPy8EG_ZTHt1300LH020_sig.recon.AOD.e8307_s3126_r9364',
'mc16_13TeV.508737.MGPy8EG_ZTHt1300LH040_sig.recon.AOD.e8307_s3126_r9364',
'mc16_13TeV.508738.MGPy8EG_ZTHt1300LH070_sig.recon.AOD.e8307_s3126_r9364',
'mc16_13TeV.508739.MGPy8EG_ZTHt1400LH020_sig.recon.AOD.e8307_s3126_r9364',
'mc16_13TeV.508740.MGPy8EG_ZTHt1400LH040_sig.recon.AOD.e8307_s3126_r9364',
'mc16_13TeV.508741.MGPy8EG_ZTHt1400LH070_sig.recon.AOD.e8307_s3126_r9364',
'mc16_13TeV.508742.MGPy8EG_ZTHt1500LH020_sig.recon.AOD.e8307_s3126_r9364',
'mc16_13TeV.508743.MGPy8EG_ZTHt1500LH040_sig.recon.AOD.e8307_s3126_r9364',
'mc16_13TeV.508744.MGPy8EG_ZTHt1500LH070_sig.recon.AOD.e8307_s3126_r9364',
'mc16_13TeV.508745.MGPy8EG_ZTHt1600LH020_sig.recon.AOD.e8307_s3126_r9364',
'mc16_13TeV.508746.MGPy8EG_ZTHt1600LH040_sig.recon.AOD.e8307_s3126_r9364',
'mc16_13TeV.508747.MGPy8EG_ZTHt1600LH070_sig.recon.AOD.e8307_s3126_r9364',
'mc16_13TeV.508748.MGPy8EG_ZTHt1700LH020_sig.recon.AOD.e8307_s3126_r9364',
'mc16_13TeV.508749.MGPy8EG_ZTHt1700LH040_sig.recon.AOD.e8307_s3126_r9364',
'mc16_13TeV.508750.MGPy8EG_ZTHt1700LH070_sig.recon.AOD.e8307_s3126_r9364',
'mc16_13TeV.508751.MGPy8EG_ZTHt1800LH020_sig.recon.AOD.e8307_s3126_r9364',
'mc16_13TeV.508752.MGPy8EG_ZTHt1800LH040_sig.recon.AOD.e8307_s3126_r9364',
'mc16_13TeV.508753.MGPy8EG_ZTHt1800LH070_sig.recon.AOD.e8307_s3126_r9364',
'mc16_13TeV.508754.MGPy8EG_ZTHt1900LH020_sig.recon.AOD.e8307_s3126_r9364',
'mc16_13TeV.508755.MGPy8EG_ZTHt1900LH040_sig.recon.AOD.e8307_s3126_r9364',
'mc16_13TeV.508756.MGPy8EG_ZTHt1900LH070_sig.recon.AOD.e8307_s3126_r9364',
'mc16_13TeV.508757.MGPy8EG_ZTHt2000LH020_sig.recon.AOD.e8307_s3126_r9364',
'mc16_13TeV.508758.MGPy8EG_ZTHt2000LH040_sig.recon.AOD.e8307_s3126_r9364',
'mc16_13TeV.508759.MGPy8EG_ZTHt2000LH070_sig.recon.AOD.e8307_s3126_r9364',
'mc16_13TeV.508760.MGPy8EG_ZTHt2100LH020_sig.recon.AOD.e8307_s3126_r9364',
'mc16_13TeV.508761.MGPy8EG_ZTHt2100LH040_sig.recon.AOD.e8307_s3126_r9364',
'mc16_13TeV.508762.MGPy8EG_ZTHt2100LH070_sig.recon.AOD.e8307_s3126_r9364',
'mc16_13TeV.508763.MGPy8EG_ZTHt2300LH020_sig.recon.AOD.e8307_s3126_r9364',
'mc16_13TeV.508764.MGPy8EG_ZTHt2300LH040_sig.recon.AOD.e8307_s3126_r9364',
'mc16_13TeV.508765.MGPy8EG_ZTHt2300LH070_sig.recon.AOD.e8307_s3126_r9364',
'mc16_13TeV.508766.MGPy8EG_ZTHt2500LH020_sig.recon.AOD.e8307_s3126_r9364',
'mc16_13TeV.508767.MGPy8EG_ZTHt2500LH040_sig.recon.AOD.e8307_s3126_r9364',
'mc16_13TeV.508768.MGPy8EG_ZTHt2500LH070_sig.recon.AOD.e8307_s3126_r9364',
'mc16_13TeV.508769.MGPy8EG_ZTHt2700LH020_sig.recon.AOD.e8307_s3126_r9364',
'mc16_13TeV.508770.MGPy8EG_ZTHt2700LH040_sig.recon.AOD.e8307_s3126_r9364',
'mc16_13TeV.508771.MGPy8EG_ZTHt2700LH070_sig.recon.AOD.e8307_s3126_r9364',
]
}

ntuples_loc = "/data/at3/scratch2/farooque/MBJOutputs/tag-21.2.121-htztx-3-syst-1/"
all_ntuples = os.listdir("/data/at3/scratch2/farooque/MBJOutputs/tag-21.2.121-htztx-3-syst-1/")

ntuples = {}
idx_map = {}

for _ii, ntuple in enumerate(all_ntuples):
    dsid = int(ntuple.split('.')[2])
    if dsid not in ntuples:
        ntuples[dsid] = {'r9364':[], 'r10201':[], 'r10724': []}
    for key in ntuples[dsid].keys():
        if key in ntuple:
            for _file in os.listdir(ntuples_loc + '/' + ntuple):
                ntuples[dsid][key].append(ntuples_loc +'/' + ntuple + '/' + _file)
            break

# # skipping WTHt for now
mktag_dict = {'WTZt':{},
              'ZTZt':{},
              # 'WTHt':{},
              'ZTHt':{}}

all_mktags = ["M{0:02d}K{1:03d}".format(m, k) for m in list(range(10,22)) + [23, 25, 27] for k in list(range(10,50,5)) + list(range(50, 170, 10))]

for key in mktag_dict.keys():
    this_datasets = datasets[key]
    for ds in this_datasets:
        dsid = int(ds.split('.')[1])
        # if dsid not in ntuples.keys():
        #     continue
        ntuples[dsid] = {}
        phys_short = ds.split('.')[2]
        _nums = re.findall(r'\d+', phys_short.split('_')[1])
        m = int(int(_nums[0])/100)

        # WTZt and ZTZt
        if 'Zt' in key:
            if 'LH100' in phys_short:
                #this_mktags = ["M{0:02d}K{1:03d}".format(m, k) for k in [45] + list(range(50, 170, 10)) ] #k45-170 from LH100
                this_mktags = ["M{0:02d}K{1:03d}".format(m, k) for k in list(range(70, 170, 10)) ] #k70-170 from LH100
                if key == 'WTZt' and m <= 21:
                    #this_mktags += ["M{0:02d}K{1:03d}".format(m-1, k) for k in [45] + list(range(50, 170, 10)) ] #k45-170 from LH100
                    this_mktags += ["M{0:02d}K{1:03d}".format(m-1, k) for k in list(range(70, 170, 10)) ] #k70-170 from LH100
            else:
                #this_mktags = ["M{0:02d}K{1:03d}".format(m, k) for k in list(range(10,45,5)) ] #k10-45 from LH040
                this_mktags = ["M{0:02d}K{1:03d}".format(m, k) for k in list(range(10,55,5)) + [60] ] #k10-60 from LH040

        # ZTHt
        if key == 'ZTHt':
            if 'LH020' in phys_short:
                this_mktags = ["M{0:02d}K{1:03d}".format(m, k) for k in range(10,30,5) ]
            if 'LH040' in phys_short:
                this_mktags = ["M{0:02d}K{1:03d}".format(m, k) for k in range(30,55,5) ]
            if 'LH070' in phys_short:
                this_mktags = ["M{0:02d}K{1:03d}".format(m, k) for k in range(60,90,10) ]
            if 'LH100' in phys_short and m <= 16:
                this_mktags = ["M{0:02d}K{1:03d}".format(m, k) for k in range(90,170,10) ]

        # skipping WTHt for now
        # if key == 'WTHt':
        #     this_mktags = ["M{0:02d}K{1:03d}".format(m, k) for k in range(10,55,5) + range(60,170,10) ]

        for mktag in this_mktags:
            mktag_dict[key][mktag] = [dsid, 
                                      getIndexMap(mktag, key)
            ]

f_mktag = open("newSig_mktags_TEST.json","w")
json.dump(mktag_dict, f_mktag, indent=1, sort_keys=True)
f_mktag.close()

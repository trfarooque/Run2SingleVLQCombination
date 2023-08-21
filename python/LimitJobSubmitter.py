#!/bin/python3

import sys, os
from CombUtils import *
from RankingPlotter import *
from Job import *
from itertools import *
import time
from optparse import OptionParser

if 'VLQCOMBDIR' not in os.environ.keys():
    print("Setup not done properly! Please run the setup.sh script")
    sys.exit(1)

if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("--data-loc", 
                      dest="dataloc",
                      help='location of data',
                      default='data/')
    parser.add_option("--script-subdir", 
                      dest="scriptsubdir",
                      help='location of generating batch submission scripts',
                      default='batch_scripts/')
    parser.add_option("--inws-subdir", 
                      dest="inwssubdir",
                      help='location of input ws sub-directories',
                      default='workspaces/input_workspaces')
    parser.add_option("--scaledws-subdir", 
                      dest="scaledwssubdir",
                      help='location of scaled ws sub-directories',
                      default='workspaces/scaled_workspaces')
    parser.add_option("--scalingconfig-subdir", 
                      dest="scalingconfigsubdir",
                      help='location of scaling config sub-directories',
                      default='xml/scaling')
    parser.add_option("--asimovws-subdir", 
                      dest="asimovwssubdir",
                      help='location of asimov ws sub-directories',
                      default='workspaces/asimov_workspaces')
    parser.add_option("--asimovconfig-subdir", 
                      dest="asimovconfigsubdir",
                      help='location of asimov config sub-directories',
                      default='xml/asimov')
    parser.add_option("--combinedws-subdir", 
                      dest="combinedwssubdir",
                      help='location of combined ws sub-directories',
                      default='workspaces/combined_workspaces')
    parser.add_option("--combconfig-subdir", 
                      dest="combconfigsubdir",
                      help='location of combination config sub-directories',
                      default='xml/combination')
    parser.add_option("--fittedws-subdir", 
                      dest="fittedwssubdir",
                      help='location of fitted ws sub-directories',
                      default='workspaces/fitted_workspaces')
    parser.add_option("--limit-subdir", 
                      dest="limitsubdir",
                      help='location of limit sub-directories',
                      default='limits')
    parser.add_option("--log-subdir", 
                      dest="logsubdir",
                      help='location of log sub-directories',
                      default='logs')
    parser.add_option("--ranking-subdir", 
                      dest="rankingsubdir",
                      help='location of ranking fit output sub-directories',
                      default='ranking')
    parser.add_option("--masses", 
                      dest="masses",
                      help='Provide a comma separated list of masses with GeV units (e.g. 1200,1600)',
                      default='1600')
    parser.add_option("--kappas", dest="kappas",
                      help='Provide a comma separated list of kappas (e.g. 0.3,0.5)',
                      default='0.5')
    parser.add_option("--brws", dest="brws",
                      help='Provide a comma separated list of T > Wb BRs (e.g. 0.0,0.5)',
                      default='0.5')
    parser.add_option("--batch-system",
                      dest="batchsystem",
                      help='Type of batch system (pbs,condor,...) to which jobs should be sent. The default option will be chosen based on the running platform.',
                      default='lxplus')
    parser.add_option("--batch-queue",
                      dest="batchqueue",
                      help='Name of batch queue/flavour (short,long,...) to which jobs should be sent. The default option will be chosen based on the running platform.',
                      default='')
    parser.add_option("--dry-run", 
                      dest="dryrun",
                      help='set if you want to write commands to scripts without executing them',
                      action='store_true',
                      default=False)
    parser.add_option("--debug", 
                      dest="debug",
                      help='set for debug messages',
                      action='store_true',
                      default=False)


    (options, args) = parser.parse_args()

    # use_data = False if do_Asimov else bool(options.usedata) # This flag is overwritten when asimov workspaces are required
    DataLoc = str(options.dataloc)
    BatchJobLoc = DataLoc + '/' + str(options.scriptsubdir) + '/'
    do_dry_run = bool(options.dryrun)
    debug_level = bool(options.debug)

    pathdict = {'InWSSubDir' : str(options.inwssubdir),
                'ScaledWSSubDir' : str(options.scaledwssubdir),
                'ScalingConfigSubDir' : str(options.scalingconfigsubdir),
                'AsimovWSSubDir' : str(options.asimovwssubdir),
                'AsimovConfigSubDir' : str(options.asimovconfigsubdir),
                'CombinedWSSubDir' : str(options.combinedwssubdir),
                'CombinationConfigSubDir' :str(options.combconfigsubdir),
                'FittedWSSubDir' : str(options.fittedwssubdir),
                'LimitSubDir' : str(options.limitsubdir),
                'LogSubDir' : str(options.logsubdir),
                'RankingSubDir' : str(options.rankingsubdir)
                }

    # mu = float(options.mu)
    masses = list(map(float, str(options.masses).split(',')))
    kappas = list(map(float, str(options.kappas).split(',')))
    BRWs = list(map(float, str(options.brws).split(',')))
    # BRWs = str(options.brws)
    InDataName =  "obsData"
    datatag = 'data' 


    batchSystem = str(options.batchsystem)
    batchQueue = str(options.batchqueue)

    # if os.path.exists(os.environ['VLQCOMBDIR'] + '/CombCode.tgz'):
    #     print("Deleting pre-existing tarball!!")
    #     os.system('rm ' + os.environ['VLQCOMBDIR'] + '/CombCode.tgz')
    # prepareTarBall(pathToPackage = os.environ['VLQCOMBDIR'], 
    #                pathToTarball = os.environ['VLQCOMBDIR'] + '/CombCode.tgz')

    mkdir_tmp = "mkdir -p {}"
    
    OUTLOC = BatchJobLoc + 'outputs/' 
    os.system(mkdir_tmp.format(OUTLOC))
    LOGLOC = BatchJobLoc + 'logs/'
    os.system(mkdir_tmp.format(LOGLOC))
    SCRIPTLOC = BatchJobLoc + 'scripts/'
    os.system(mkdir_tmp.format(SCRIPTLOC))


    for (mass, kappa) in product(*[masses, kappas]):
        mktag = getMKTag(mass, kappa)
        these_jobs = []
        for brw in BRWs:
            jobtag = getSigTag(mass, kappa, brw)
            # jobtag = mktag
            this_job = Job(batchSystem)
            this_job.setDebug(debug_level)
            this_job.setName("LimitBatchJob_{}".format(jobtag))
            this_job.addOption("--data-loc", DataLoc)
            this_job.addOption("--inws-subdir", pathdict['InWSSubDir'])
            this_job.addOption("--scaledws-subdir", pathdict['ScaledWSSubDir'])
            this_job.addOption("--scalingconfig-subdir", pathdict['ScalingConfigSubDir'])
            this_job.addOption("--asimovws-subdir", pathdict['AsimovWSSubDir'])
            this_job.addOption("--asimovconfig-subdir", pathdict['AsimovConfigSubDir'])
            this_job.addOption("--combinedws-subdir", pathdict['CombinedWSSubDir'])
            this_job.addOption("--combconfig-subdir", pathdict['CombinationConfigSubDir'])
            this_job.addOption("--fittedws-subdir", pathdict['FittedWSSubDir'])
            this_job.addOption("--limit-subdir", pathdict['LimitSubDir'])
            this_job.addOption("--log-subdir", pathdict['LogSubDir'])
            this_job.addOption("--ranking-subdir", pathdict['RankingSubDir'])
            this_job.addOption("--masses", str(int(mass)))
            this_job.addOption("--kappas", str(kappa))
            this_job.addOption("--brws", str(brw))
            this_job.addOption("--use-data", "")
            this_job.addOption("--skip-asimov", "")
            this_job.addOption("--skip-separate-fitting", "")
            this_job.addOption("--skip-separate-limits", "")
            this_job.addOption("--skip-trexf-configs", "")
            this_job.addOption("--skip-trexf-comp", "")
            this_job.setOutDir(DataLoc + '/' + pathdict['LimitSubDir'] + '/SPT_COMBINED/')
            this_job.setOutputFile('SPT_COMBINED_limits_{}_data.txt'.format(jobtag))
            this_job.setExecutable("python python/CombRunner.py")

            command = this_job.execName + " "
            for opt in this_job.jobOptions:
                command += opt[0] + ' ' 
                if opt[1]: 
                    command += opt[1] + ' '
            this_job.setExecutable(command)
            these_jobs.append(this_job)
        
        this_js = JobSet("lxplus")
        this_js.setJobRecoveryFile(SCRIPTLOC + '/JobCheck.chk')
        for job in these_jobs:
            this_js.addJob(job)
        
        this_js.setOutDir(OUTLOC)     # FIXME
        this_js.setLogDir(LOGLOC)        # FIXME
        this_js.setScriptDir(SCRIPTLOC)  # FIXME

        this_js.setScriptName("script_{}.sh".format(mktag))
        this_js.setTarBall(os.environ['VLQCOMBDIR'] + '/CombCode.tgz')  #FIXME
        
        this_js.writeScript()

        # A little hack to get the limit results in the output directory so that the JobCheck file can be used

        f_tmp = open(this_js.scriptDir + "/" + this_js.scriptName , "a")
        f_tmp.write("\n")
        f_tmp.write("cp {}/SPT_COMBINED_limits_{}*_data.txt $OUTDIR".format(DataLoc + '/' + pathdict['LimitSubDir'] + '/SPT_COMBINED', mktag))
        f_tmp.close()
        
        if not options.debug:
            this_js.submitSet()
        
    

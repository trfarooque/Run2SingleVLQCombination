This Repository is being built for combination of  Single VLQ Searches within ATLAS. More information can be found in the [combination twiki](https://twiki.cern.ch/twiki/bin/viewauth/AtlasProtected/SingleCombinationRun2).

To clone this project, run the following commands:

```
	git clone ssh://git@gitlab.cern.ch:7999/atlas-phys/exot/hqt/VLQ_Single_Run2/Run2SingleVLQCombination.git
	cd Run2SingleVLQCombination
	git submodule init
	git submodule update
```
## Setup
The `setup.sh` script should be run **every time beroe using this package** to set up the necessary StatAnalysis release and the environment variables.


## WorkspaceChecks

``WorkspaceChecks`` is used to check that the individual workspaces are built in the right way for combination. It checks the names of the samples, regions, systematic nuisance parameters, and normalization factors. It needs to be compiled during the first time (and after any changes to it) by running the `make` command.


## The Combination Super-script

All steps of the combination workflow can be run using the super-script `CombRunner.py`. 

```
python python/CombRunner.py <options>
```
where `<options>` can be chosen from the following list-

```
  -h, --help 			            show this help message and exit
  --data-loc		     	        location of data
  --inws-subdir         	    location of input ws sub-directories
  --scaledws-subdir     	    location of scaled ws sub-directories
  --scalingconfig-subdir	    location of scaling config sub-directories
  --asimovws-subdir		        location of asimov ws sub-directories
  --asimovconfig-subdir		    location of asimov config sub-directories
  --combinedws-subdir		      location of combined ws sub-directories
  --combconfig-subdir		      location of combination config sub-directories
  --fittedws-subdir		        location of fitted ws sub-directories
  --limit-subdir		          location of limit sub-directories
  --log-subdir			          location of log sub-directories
  --ranking-subdir            location of ranking fit output sub-directories
  --masses			              Provide a comma separated list of masses with GeV units (e.g. 1200,1600)
  --kappas			              Provide a comma separated list of kappas (e.g. 0.3,0.5)
  --brws	    		            Provide a comma separated list of T > Wb BRs (e.g. 0.0,0.5)
  --mu	                	    Choice of mu for asimov dataset
  --use-defScaling            set if the mu is to set the signal scale factor to correspond to the theory XS. 
                              If set, the mu value will be overwritten
  --fit-type			            Provide the fit type: BONLY (default) or SPLUSB
  --ranking-nmerge            Number of jobs to merge together when running ranking fits
  --batch-system              Type of batch system (pbs,condor,...) to which jobs should be sent. 
                              The default option will be chosen based on the running platform.
  --batch-queue               Name of batch queue/flavour (short,long,...) to which jobs should be sent. 
                              The default option will be chosen based on the running platform.

  --use-data			            set if real data is to be used, otherwise asimov will be used
  --skip-scaling		          set if scaling input workspaces is not required (i.e. already done)
  --skip-asimov			          set if real data is to be used instead of asimov
  --skip-combine          	  set if combination of workspaces is not required
  --skip-separate-fitting	    set if independent fitting of workspaces is not required
  --skip-combined-fitting     set if fitting of combined workspaces is not required
  --skip-separate-limits  	  set if independent limits are not required
  --skip-combined-limits  	  set if combined limits not required
  --do-separate-ranking-fits  set if you want to run ranking plot fits for individual workspaces
  --do-combined-ranking-fits  set if you want to run ranking plot fits for combined workspaces
  --overwrite-ranking-jobs    set if you want to overwrite preexisting ranking jobs
  --ranking-includeGammas     Include gamma parameters in ranking fits
  --skip-trexf-configs    	  set if TRExFitter Configs are not required
  --skip-trexf-comp       	  set if TRExFitter Comps are not required
  --do-separate-ranking-plots set if you want to make ranking plots for individual workspaces. NOTE: Ranking fits must have already been run
  --do-combined-ranking-plots set if you want to make ranking plots for combined workspaces. NOTE: Ranking fits must have already been run
  --dry-run                   set if you want to write commands to scripts without executing them
  --debug                     set for debug messages

```
Running a full combination chain will require a number of steps to be completed. The workflows for combination with Asimov and data are illustrated with the flowchart diagrams below-

![Combination workflow](workflows.png)

Each bounding box of the workflow diagram represents the part that can be standalone executed by the workflow given (a) the previous steps are already done, (b) the corresponding outputs from those steps are preserved, and (c) the same directory structure is used.

The backbone of this code is in the `CombUtils.py` module which defines the necessary class and wrappers to run the different steps of combination. Please note that-

- The `--data-loc` option takes in the full path to a location or the relative path of the directory with respect to the directory from where the code is being run. This is where all results and workspaces are meant to be stored. Before running the combination, one must place the necessary input workspaces in a particular directory structure. For each participating analysis, there should be a directory of the format `<dataloc>/<wsloc>/<ANACODE>` where `<dataloc>` is the directory specified by the `--data-loc` option (the default choice is `data`), `<wsloc>` is the location specified by the `--inws-subdir` (the default choice is `workspaces/input_workspaces` option  and `<ANACODE>` is the analysis codename specified in the [combination twiki](https://twiki.cern.ch/twiki/bin/viewauth/AtlasProtected/SingleCombinationRun2)
- The workspaces must be named as `<ANACODE>_combined_<SIGCODE>.root` where `<SIGCODE>` is the signal tag in the form `MxxKyyy`. `xx` is the signal mass in units of 100 GeV and `yyy` is hundred times the signal kappa, with preceding zero(s) if needed. For instance, the workspace for a 1.4 TeV signal at a kappa = 0.35 from the OSML analysis must be named `SPT_OSML_combined_M14K035.root` and placed under the directory `<dataloc>/<wsloc>/SPT_OSML/`
- The combination workflow allows either a specific asimov run with a certain choice of mu or a run with observed data in a single call, but not both. This is controlled by the `--skip-asimov` and `--use-data` flags. To run a  fit with data, both flags must be passed to command line argument.  Without the `--skip-asimov` flag the code will run the Asimov workflow and will override the`--use-data` flag. Using the `--skip-asimov` flag alone will cause the code to skip generation of Asimov Workspaces but will run the rest of the workflow assuming the Asimov workspaces already exist.

## Running Benchmark Fits

The team has decided to run and examine benchmark fits at 1200, 1600, and 2000 GeV for couplings of 0.3, 0.5, and 0.7 at singlet (BRW = 0.5) and doublet (BRW = 0.0) benchmarks. All of these jobs except the ranking fits can be run locally (i.e. w/o using a job scheduler like condor) on a computing node. The standard set of jobs require-

- Performing Asimov and Data fits in background-only (BONLY) and signal-plus-background (SPLUSB) settings
- Producing corresponding pull plots and correlation matrices for individual and combined fits and compare them
- Obtaining individual and combined limits
- Producing ranking plots

One can run the following commands to perform these tasks. For a BONLY Asimov fit with mu = 0, the command will be-

```
python python/CombRunner.py --data-loc <location/to/data> --inws-subdir <location/to/input-workspaces> --masses 1200,1600,2000 --kappas 0.3,0.5,0.7 --brws 0.0,0.5 --fit-type BONLY --mu 0
```
This command will get all the necessary results except the ranking fits and plots. A similar sommand can be used for the fit with data, where one needs to additionally use the `--skip-asimov` and `--use-data` flags as explained above.

### The Ranking Plots

Once the fits have been performed as in with the previous command, one can get the ranking plots in two steps: (1) by submitting the ranking fits as condor/batch jobs, and (2) getting the ranking plot by after those jobs finish. The first step can be done with the command-

```
python python/CombRunner.py --data-loc <location/to/data> --inws-subdir <location/to/input-workspaces> --masses 1200,1600,2000 --kappas 0.3,0.5,0.7 --brws 0.0,0.5 --fit-type BONLY --mu 0 --skip-scaling --skip-asimov --skip-combine --skip-separate-fitting --skip-combined-fitting --skip-separate-limits --skip-combined-limits --do-separate-ranking-fits --do-combined-ranking-fits --skip-trexf-configs --skip-trexf-comp
```
This command will get the necessary fit jobs submitted and the corresponding logs and scripts will be collected inside of the `<dataloc>/<ranking-subdir>/<ANACODE>` directory. Each subdirectory there will have a name of the form `<ANACODE>_<SIGTAG>_<DATATAG>` where `<SIGTAG>` is the signal tag of the form `MxxKyyyBRWzz`. `<DATATAG>` is either `data` or `asimov_mu<MU>` where `<MU>` is the integer portion of the value `mu * 100`. A file called `JobCheck.chk` will be collected inside the `Scripts` subdirectory of each of the ranking jobs. This file can be used to look for and resubmit failed jobs by using the command

```
python python/CheckOutputs.py input=<path/to/JobCheck.chk> relaunch=<TRUE/FALSE>
```
Once all the jobs are successfully completed, run the following command to get the ranking plots-

```
python python/CombRunner.py --data-loc <location/to/data> --inws-subdir <location/to/input-workspaces> --masses 1200,1600,2000 --kappas 0.3,0.5,0.7 --brws 0.0,0.5 --fit-type BONLY --mu 0 --skip-scaling --skip-asimov --skip-combine --skip-separate-fitting --skip-combined-fitting --skip-separate-limits --skip-combined-limits --do-separate-ranking-plots --do-combined-ranking-plots --skip-trexf-configs --skip-trexf-comp
```

## Running All Limits

To submit the limit jobs, one needs to use the `python/LimitJobSubmitter.py` script and run it like 

```
python python/LimitJobSubmitter.py <options>

```
The possible options are-

```
  -h, --help              show this help message and exit
  --data-loc              location of data
  --script-subdir         location of generating batch submission scripts
  --inws-subdir           location of input ws sub-directories
  --scaledws-subdir       location of scaled ws sub-directories
  --scalingconfig-subdir  location of scaling config sub-directories
  --asimovws-subdir       location of asimov ws sub-directories
  --asimovconfig-subdir   location of asimov config sub-directories
  --combinedws-subdir     location of combined ws sub-directories
  --combconfig-subdir     location of combination config sub-directories
  --fittedws-subdir       location of fitted ws sub-directories
  --limit-subdir          location of limit sub-directories
  --log-subdir            location of log sub-directories
  --ranking-subdir        location of ranking fit output sub-directories
  --masses                Provide a comma separated list of masses with GeV units (e.g. 1200,1600)
  --kappas                Provide a comma separated list of kappas (e.g. 0.3,0.5)
  --brws                  Provide a comma separated list of T > Wb BRs (e.g. 0.0,0.5)
  --batch-system          Type of batch system (pbs,condor,...) to which jobs should be sent. The default option will be chosen based on the running platform.
  --batch-queue           Name of batch queue/flavour (short,long,...) to which jobs should be sent. The default option will be chosen based on the running platform.
  --dry-run             set if you want to write commands to scripts without executing them
  --debug               set for debug messages

```

These options are indeed a subset of the options for the `CombRunner.py` script except the `--script-subdir` option which determines the location of where the scripts, logs, and outputs of the batch jobs will be collected. This script is written to submit jobs that calculate combined limits with data for all the mass-kapp-BRW combinations. It also collects a `JobCheck.chk` file inside the `scripts` subdirectory which can be used with `python/CheckOutputs.py` to look for and resubmit unsuccessful jobs.


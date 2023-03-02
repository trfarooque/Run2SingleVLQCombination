This Repository is being built for combination of  Single VLQ Searches within ATLAS. More information can be found in the [combination twiki](https://twiki.cern.ch/twiki/bin/viewauth/AtlasProtected/SingleCombinationRun2).

To clone this project, run the following commands:

```
	git clone ssh://git@gitlab.cern.ch:7999/atlas-phys/exot/hqt/VLQ_Single_Run2/Run2SingleVLQCombination.git
	cd Run2SingleVLQCombination
	git submodule init
	git submodule update
```

## WorkspaceChecks

``WorkspaceChecks`` is used to check that the individual workspaces are built in the right way for combination. It checks the names of the samples, regions, systematic nuisance parameters, and normalization factors. The instructions for compiling and running this is given in [this README file](https://gitlab.cern.ch/atlas-phys/exot/hqt/VLQ_Single_Run2/Run2SingleVLQCombination/-/blob/master/WorkspaceChecks/README.rst)


## Running combination

All steps of the combination workflow can be run using the super-wrapper `CombRunner.py`. 

```
python CombRunner.py <options>
```
where `<options>` can be chosen from the following list-

```
  -h, --help            show this help message and exit
  --data-loc		location of data
  --masses		Provide a comma separated list of masses with GeV
                        units (e.g. 1200,1600)
  --kappas		Provide a comma separated list of kappas (e.g.
                        0.3,0.5)
  --brws	    	Provide a comma separated list of T > Wb BRs (e.g.
                        0.0,0.5)
  --no-scaling          set if scaling input workspaces is not required
  --no-asimov           set if real data is to be used instead of asimov
  --mu	                Choice of mu for asimov dataset
  --no-combine          set if combination of workspaces is not required
  --no-separate-fitting
                        set if independent fitting of workspaces is not
                        required
  --no-combined-fitting
                        set if fitting of combined workspaces is not required
  --no-separate-limits  set if independent limits are not required
  --no-combined-limits  set if combined limits not required
  --no-trexf-configs    set if TRExFitter Configs are not required
  --no-trexf-comp       set if TRExFitter Comps are not required
```
The backbone of this code is in the `CombUtils.py` module which defines the necessary class and wrappers to run the different steps of combination. Please note that-

- The `--data-loc` option takes in the **relative path** of the directory where all results and workspaces are stored. Before running the combination, one must place the necessary input workspaces in a particular directory structure. For each participating analysis, there must be a directory called `<dataloc>/workspaces/input_workspaces/<ANACODE>` where `<dataloc>` is the directory specified by the `--data-loc` option (the default choice is `data`) and `<ANACODE>` is the analysis codename specified in the [combination twiki](https://twiki.cern.ch/twiki/bin/viewauth/AtlasProtected/SingleCombinationRun2)
- The workspaces must be named as `<ANACODE>_combined_<SIGCODE>.root` where `<SIGCODE>` is the signal tag in the form `MxxKyyy`. `xx` is the signal mass in units of 100 GeV and `yyy` is hundred times the signal kappa, with preceding zero(s) if needed. For instance, the workspace for a 1.4 TeV signal at a kappa = 0.35 from the OSML analysis must be named `SPT_OSML_combined_M14K035.root` and placed under the directory `<dataloc>/workspaces/input_workspaces/SPT_OSML/`
- The combination workflow allows either a specific asimov run or a run with observed data in a single call, but not both. This is controlled by the `--no-asimov` flag. Without this flag, the code will run the workflow for asimov data created with the choice of `mu` specified by the `--mu` flag (default zero).

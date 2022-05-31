This Repository is being built for combination of  Single VLQ Searches within ATLAS. More information can be found in the [combination twiki](https://twiki.cern.ch/twiki/bin/viewauth/AtlasProtected/SingleCombinationRun2).

To clone this project, run the following commands:

```
	git clone ssh://git@gitlab.cern.ch:7999/atlas-phys/exot/hqt/VLQ_Single_Run2/Run2SingleVLQCombination.git
	git submodule init
	git submodule update
```

## WorkspaceChecks

``WorkspaceChecks`` is used to check that the individual workspaces are built in the right way for combination. It checks the names of the samples, regions, systematic nuisance parameters, and normalization factors. The instructions for compiling and running this is given in [this README file](https://gitlab.cern.ch/atlas-phys/exot/hqt/VLQ_Single_Run2/Run2SingleVLQCombination/-/blob/master/WorkspaceChecks/README.rst)

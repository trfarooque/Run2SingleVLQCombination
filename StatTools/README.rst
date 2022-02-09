Getting the package
---------

To get the tool, just do::

  git clone ssh://git@gitlab.cern.ch:7999/VLQComb/StatTools.git

ROOT must be set up before. A ``setup.sh`` code has been added. To setup ROOT
from cvmfs-aware machines::

  source setup.sh

To compile all the executable::

  make


Dumping an Asimov dataset
---------

You can add an Asimov dataset built on a configuration of POI and NP values.
To do so::

  ./bin/create_asimov.exe file_path=<string> workspace_name=<string> asimov_name=<string> np_values=<string> poi_value=<double> debug=<bool>

where:
  * ``file_path``: full path to the file containing the workspace
  * ``workspace_name``: the name of the RooWorkspace object to look for
  * ``asimov_name``: name of the output Asimov RooDataSet object that will be added in the workspace
  * ``np_values``: values of the NPs to be used to build the Asimov dataset. It takes the following format: ``np1name:np1value,np2name:np2value,np3name:np3value``
  * ``poi_value``: values of the POI to be used to build the Asimov
  * ``debug`` [``true``/``false``]: prints more message if true


Computing limits
---------

To compute the limit, you can execute the ``runAsymptoticsCLs.C`` macro stored in
the ``macros/`` folder. The execution follows the pattern below::

  root -l -b -q 'runAsymptoticsCLs.C+(<path_to_file>,<workspace name>,<model config name>,<dataset name>,"asimovData_0",<output folder>,<signal name>,0.95)'

where:
  * ``path_to_file``: full path to the file containing the workspace
  * ``workspace_name``: the name of the RooWorkspace object to look for
  * ``model_config_name``: the name of the ModelConfig object to look for
  * ``dataset name``: name of the dataset used to compute the observed limit (and to build the Asimov for the expected)
  * ``output_folder``: place where the output rootfile is stored
  * ``signal_name``: indication for the signal name


Comparing limit results
---------

The comparison of the limit results can be done through the ``compare_limits.C``
macro, stored in the ``macros`` folder. The execution follows the pattern
below::

  root -l -b -q 'macros/compare_limits.C+( <map_to_individual_limits>, <path_to_combined_limit>, <show_obs>, <output_dir>, <legend>)'

with:
  * ``map_to_individual_limits`` is an ``std::map`` containing, as key, the legend of the limit, and as value the absolute path to the limit rootfile:
    * example: ``{{"Wb+X","/Users/lvalery/Desktop/VLQComb/StatTools/LimitWb/Singlet1200.root"}, {"Ht+X","/Users/lvalery/Desktop/VLQComb/StatTools/LimitHt/Singlet1200.root"}}``
  * ``path_to_combined_limit`` is the absolute path to the combined limit result
  * ``showObs``: shows the observed limit [default is ``false``]
  * ``output_dir`` is the folder in which the file is created [default is ``outComp``]
  * ``signal_legend`` is the legend for the considered signal [default is ``""``]


  ``path_to_combined_limit`` can be set to ``""``. In such a case, the combination
  will be omitted.


One can also compare the limit vs mass results for different analyses and the combination. 
So far, this is a pretty dirty python code, but this is intended to be improved :) To obtain
the plot, you can do::

  python macros/compare_limits_vs_mass.py -o <output> -s <signal> -t <template> -a <analyses> -c <combo> -b <br>

with:
   * ``output`` is the name of the folder where the outputs will be stored 
   * ``signal`` is TT or BB depending on the signal you consider
   * ``template`` is the template path to the files, i.e. the path to each analysis results with a few keywords being replaced on the fly for the specific analyses/masses/BR:
      * ANALYSIS, MASS and BR will be replaced by the correct values
      * Example: ``~/scratch2/VLQCombination/2017_12_Workspaces/workspace_${or}_OR/Limits/ANALYSIS/Limits_ANALYSIS_MASS_BR/signal.root``
   * ``analyses`` is the coma spearatedl list of analyses considered in the plot (i.e. what the ``ANALYSIS`` keyword will be replaced with)
   * ``combo`` is the equivalent of ``analyses`` but only for the combination
   * ``br`` is the branching ratio configuration (Singlet, Doublet or any other BR)


Perform the fit
---------

You can compile the fitting code by doing::

  make

Execution of the code can be done through::

  ./bin/fit.exe file_path=<file_path> workspace_name=<workspace_name> data_name=<data_name> output_folder=<output_folder> output_suffix=<output_suffix> poi_value=<poi_value> poi_fixed=<true/false>

where:
  * ``path_to_file``: full path to the file containing the workspace
  * ``workspace_name``: the name of the RooWorkspace object to look for
  * ``dataset name``: name of the dataset used to compute the observed limit (and to build the Asimov for the expected)
  * ``output_folder``: place where the outputs are stored
  * ``poi_value``: the initial value of the POI to be considered in the fit (default is 0)
  * ``poi_fixed``: boolean to define if the POI is fixed in the fit (default is ``true``)


Compare the fit results
---------

You can run the comparison between the fit results by doing the following::

  root -l -b -q 'macros/draw_fits.C+( map_results, output_dir )'

where:
  * ``map`` contains pairs of strings
     * the key is the analysis abbreviation (WBX, ZTMET, ...)
     * the element is the path to the rootfile containing the RooFitResult object
    Example: ``{ {"WBX","output_fit/FitResultWBX.root"} }``
  * ``output_dir`` is the place where you will store the output plots

Drawing plots from the workspace
---------

To draw plots from a workspace and a fit result, you need to have a workspace and a fit result ;-) 
You can then run the command::

  ./bin/draw.exe file_path=<workspace> fr_file_path=<fit_results_file> fr_name=<fit_result_name> do_prefit=<pre> do_postfit=<post>

where: 

Example for prefit plots::

  ./bin/draw.exe file_path=example/input.root workspace_name=combined data_name=obsData output_folder=test_output/ do_prefit=true region_file=example/region_config.txt sample_file=example/sample_config.txt


Example for prefit plots::

  ./bin/draw.exe file_path=example/input.root workspace_name=combined data_name=obsData output_folder=test_output/ do_postfit=true fr_file_path=example/fit_results/FitResult.root fr_name=nll_simPdf_obsData_with_constr region_file=example/region_config.txt sample_file=example/sample_config.txt




















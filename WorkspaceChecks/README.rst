ROOT must be set up before compiling the code. A ``setup.sh``
code has been added. To setup ROOT from cvmfs-aware machines::

  source setup.sh

NOTE: If your worspaces are created by TRExFitter, you need to setup the same ROOT version as the one you used during creating the workspaces. Instead of using the ``setup.sh`` given with this repo, run the ``setup.sh`` file with your TRExFitter installation.

The compilation of the code should be done by::

  make


Running the workspace checker
---------

You can execute the code by doing::

  ./bin/workspace.exe file_path=<file> workspace_name=<workspace> data_name=<data_name> do_checks=<do_checks> abort_on_error=<abort_on_error>

* ``file_path``: full path to the file containing the workspace
* ``workspace_name``: the name of the RooWorkspace object to look for
* ``data_name``: name of the RooDataSet object in the workspace (``obsData`` or ``asimovData``, based on your Fit setting)
* ``do_checks`` [``true``/``false``]: perform the checks on the workspace (naming convention)
* ``abort_on_error`` [``true``/``false``]: stop the checks at the first error


Running the config file dumper
---------

You can dump config files by doing::

  ./bin/workspace.exe file_path=<file> workspace_name=<workspace> do_config_dump=<do_config> abort_on_error=<abort_on_error>

* ``file_path``: full path to a text with the structure ``<analysis code> : <path to workspace> : <path to textfile for NP naming>`` where:

    * ``analysis code`` the short code for the analysis
    * ``path to workspace`` the absolute path to the file containing the workspace
    * ``path to textfile for NP naming`` the absolute path to a text file containing naming conversion (optional)

* ``workspace_name``: the name of the RooWorkspace object to look for
* ``data_name``: name of the RooDataSet object in the workspace
* ``do_config_dump`` [``true``/``false``]: dumps a config file for each workspaces
* ``abort_on_error`` [``true``/``false``]: stop the execution of the code at the first error
* ``decorr_all`` [``true``/``false``]: keep the nuisance parameters uncorrelated in the different analyses

Note that, in case ``<path to textfile for NP naming>`` is specified, the file it is pointing to should have a format like::

   <old name> : <new name>

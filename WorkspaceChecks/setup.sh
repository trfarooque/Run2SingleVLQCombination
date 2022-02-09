echo "Setting up ROOT ... "
export ATLAS_LOCAL_ROOT_BASE=/cvmfs/atlas.cern.ch/repo/ATLASLocalRootBase 
source ${ATLAS_LOCAL_ROOT_BASE}/user/atlasLocalSetup.sh --quiet
localSetupROOT 6.08.00-x86_64-slc6-gcc49-opt --quiet
echo "... done !"

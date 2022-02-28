echo "Setting up ROOT ... "
export ATLAS_LOCAL_ROOT_BASE=/cvmfs/atlas.cern.ch/repo/ATLASLocalRootBase 
source ${ATLAS_LOCAL_ROOT_BASE}/user/atlasLocalSetup.sh --quiet
localSetupROOT 6.20.06-x86_64-centos7-gcc8-opt --quiet
echo "... done !"

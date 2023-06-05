SDIR  = WorkspaceChecks/src/
IDIR  = WorkspaceChecks/WorkspaceChecks/
APPDIR  = WorkspaceChecks/app/
UTILDIR = ./utils/
BINDIR  = ./bin/
MAKEFLAGS = --no-print-directory -r -s
INCLUDE = $(shell root-config --cflags)
LIBS    = $(shell root-config --libs) -lHistFactory -lRooStats -lRooFit -lRooFitCore
#BINS = workspace makeCorrMatrix
#OBJS =

all: workspace makeCorrMatrix

workspace: $(APPDIR)/workspace.cxx $(SDIR)/*.cxx
	@echo "Building $@ ... "
	mkdir -p $(BINDIR)
	$(CXX) $(CCFLAGS) $< -I$(IDIR) $(INCLUDE) $(LIBS) $(SDIR)/*.cxx -o $(BINDIR)/$@
	@echo "Done"

makeCorrMatrix: $(UTILDIR)/makeCorrMatrix.cxx
	@echo "Building $@ ... "
	mkdir -p $(BINDIR)
	$(CXX) $(CCFLAGS) $< $(INCLUDE) $(LIBS) -o $(BINDIR)/$@
	@echo "Done"


clean:
	rm -f bin/*

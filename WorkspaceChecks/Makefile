SDIR  = ./src/
IDIR  = ./WorkspaceChecks/
LDIR  = ./bin/
UDIR  = ./util/
MAKEFLAGS = --no-print-directory -r -s
INCLUDE = $(shell root-config --cflags)
LIBS    = $(shell root-config --libs) -lHistFactory -lRooStats -lRooFit -lRooFitCore
BINS = workspace
OBJS =
all: $(BINS)
$(BINS): % :  $(UDIR)workspace.cxx
	@echo "Building $@ ... "
	mkdir -p $(LDIR)
	$(CXX) $(CCFLAGS) $< -I$(IDIR) $(INCLUDE) $(LIBS) $(SDIR)/string_utils.cxx $(SDIR)/messages.cxx $(SDIR)/WSChecker.cxx $(SDIR)/WSConfig.cxx $(SDIR)/file_utils.cxx -o "$(LDIR)workspace.exe"
	@echo "Done"
clean:
	rm -rf bin

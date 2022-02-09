SDIR  = ./src/
IDIR  = ./StatTools/
LDIR  = ./bin/
UDIR  = ./util/
MAKEFLAGS = --no-print-directory -r -s
INCLUDE = $(shell root-config --cflags)
LIBS    = $(shell root-config --libs) -lHistFactory -lRooStats -lRooFit -lRooFitCore
BINS = asimov
BINS2 = fit
BINS3 = draw
OBJS =
all: asimov fit draw

$(BINS): % :  $(UDIR)create_asimov.cxx
	@echo "Building $@ ... "
	mkdir -p $(LDIR)
	$(CXX) $(CCFLAGS) $< -I$(IDIR) $(INCLUDE) $(LIBS) $(SDIR)/string_utils.cxx $(SDIR)/messages.cxx -o "$(LDIR)create_asimov.exe"
	@echo "Done"

$(BINS2): % :  $(UDIR)fit.cxx
	@echo "Building $@ ... "
	mkdir -p $(LDIR)
	$(CXX) $(CCFLAGS) $< -I$(IDIR) $(INCLUDE) $(LIBS) $(SDIR)/string_utils.cxx $(SDIR)/messages.cxx $(SDIR)/FittingTool.cxx -o "$(LDIR)fit.exe"
	@echo "Done"

$(BINS3): % :  $(UDIR)draw.cxx
	@echo "Building $@ ... "
	mkdir -p $(LDIR)
	$(CXX) $(CCFLAGS) $< -I$(IDIR) $(INCLUDE) $(LIBS) $(SDIR)/string_utils.cxx $(SDIR)/messages.cxx $(SDIR)/RooExpandedFitResult.cxx $(SDIR)/draw_utils.cxx  $(SDIR)/canvas_style.cxx -o "$(LDIR)draw.exe"
	@echo "Done"

clean:
	rm -rf bin

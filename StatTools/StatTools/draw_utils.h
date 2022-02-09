#ifndef DRAW_UTILS_H

#include <vector>
#include <string>
#include <map>

#include "RooStats/ModelConfig.h"

class RooFitResult;
class RooSimultaneous;
class RooDataSet;

namespace draw_utils {
	//___________________________________________
	//
	struct Region {
		std::map < std::string, std::string > keys;
		std::vector < double > binning;
	};

	//___________________________________________
	//
	struct Sample {
		std::map < std::string, std::string > keys;
	};

	//___________________________________________
	//
	struct RegionHists {
		std::string name;
		std::map < std::string, TH1* > hist;
		TGraph* total_central;
		TGraph* total_err;
		TGraph* data;
	};

	//Reading the config files
	void ExtractConfigFileInfo( const std::string &file_path, std::vector < std::map < std::string, std::string > > &vec_entries );
	void ExtractRegionConfigFileInfo( std::map < std::string, Region > &vec_regions, const std::string &file_path );
	void ExtractSampleConfigFileInfo( std::map < std::string, Sample > &vec_samples, const std::string &file_path );

	//Getting the fit results
	RooFitResult* GetFitResults( RooStats::ModelConfig *mc, const double mu_val, 
								 const std::string &fr_file_path = "",
								 const std::string &fr_name = "",
								 const bool postFit = true );

	//Getting the ROOT objects
	void GetAllROOTObjects( RooStats::ModelConfig *mc, RooSimultaneous *simPdf, 
									RooDataSet* data, 									
									RooFitResult *rfr,
									std::map < std::string, draw_utils::RegionHists > &map_regions );

	//Drawing the objects in a canvas
	void DrawCanvas( const std::string &output_folder,
					 const std::pair < std::string, draw_utils::RegionHists > &region_hists, 
					 const std::map < std::string, draw_utils::Region > &map_regions, 
					 const std::map < std::string, draw_utils::Sample > &map_samples,
					 const bool isPostFit );

};

#endif //DRAW_UTILS_H
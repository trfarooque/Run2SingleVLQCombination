#include "draw_utils.h"
#include "string_utils.h"
#include "messages.h"
#include "canvas_style.h"

#include "RooRealVar.h"
#include "RooExpandedFitResult.h"
#include "RooFitResult.h"
#include "RooPlot.h"
#include "RooSimultaneous.h"
#include "RooCategory.h"
#include "RooCatType.h"
#include "RooDataSet.h"
#include "RooHist.h"
#include "RooRealSumPdf.h"
#include "RooProduct.h"

#include "TFile.h"
#include "TGraph.h"
#include "TH1.h"
#include "TCanvas.h"
#include "THStack.h"

#include <fstream>
#include <string>
#include <iostream>
#include <vector>

//________________________________________________________________________
//
void draw_utils::ExtractConfigFileInfo( const std::string &file_path, std::vector < std::map < std::string, std::string > > &vec_entries ){
	std::ifstream file(file_path.c_str());
	if(!file.is_open()){
		std::cerr << "<!> Error in ConfigParser::ReadFile: The file cannot be opened !" << std::endl;
		return;
	}
	std::string str, val;

  	//loop over the file once and stores the content in a vector
  	std::map < std::string, std::string > map_temp; 
  	bool ongoing = false; 
	while (getline(file, str)){
		//removing end-of-line symbols
		str = string_utils::replace_string( str, "\n", " ");
		str = string_utils::replace_string( str, "\r", " ");
		str = string_utils::replace_string( str, "\t", " ");
		str = string_utils::replace_string( str, ": ", ":");
		str = string_utils::replace_string( str, " :", ":");
		//skipping comments 
		if ( str.find("%%")!=std::string::npos || str.find("##")!=std::string::npos) continue;
		//every new block starts with BEGIN and finished with END
		if ( str.find("-BEGIN")!=std::string::npos ){
			ongoing = true;
			map_temp.clear();
			continue;
		} else if( str.find("-END")!=std::string::npos ){
			ongoing = false;
			vec_entries.push_back(map_temp);
			map_temp.clear();
			continue;
		} else if (ongoing){
			std::vector < std::string > vec_temp = string_utils::split_string(str, ':');
			if(vec_temp.size()!=2){
				std::cout << "Problem with line: " << str << std::endl;
				continue;
			}
			map_temp.insert( std::pair < std::string, std::string >( vec_temp[0], vec_temp[1]));
		}
	}
	file.close();
}

//________________________________________________________________________
//
void draw_utils::ExtractRegionConfigFileInfo( std::map < std::string, Region > &vec_regions, const std::string &file_path ){
	std::vector < std::map < std::string, std::string > > config_content;
	ExtractConfigFileInfo( file_path, config_content );
	//looping over the blocks (1 block per region)
	for( const auto &region : config_content ){
		//declaring the region object
		Region reg;

		//
		// Now looping over the info contained for each region
		//
		// Starting from the mandatory informations
		std::vector< std::string > mandatory_information = {"NAME","LEGEND","LEGENDX"};
		for ( const auto &mandat : mandatory_information ){
			if( region.find(mandat)!=region.end() ){
				reg.keys.insert( std::pair < std::string, std::string >(mandat,region.at(mandat)));
			} else {
				std::cout << "The " << mandat << " information cannot be found ... This is a big problem ! Please fix !" << std::endl;
				abort();
			}
		}
		//Now the rest of the informations
		std::vector< std::string > optional_information = {"LEGEND","LEGENDX","BINNING"};
		for ( const auto &opt : optional_information ){
			if( region.find(opt)!=region.end() ){
				reg.keys.insert( std::pair < std::string, std::string >(opt,region.at(opt)));
				if(opt=="BINNING"){
					std::vector < std::string > split = string_utils::split_string(region.at(opt), ',');
					for( const std::string &bin : split ){
						reg.binning.push_back( atof(bin.c_str()) );
					}
				}
			}
		}
		vec_regions.insert( std::pair < std::string, Region > (region.at("NAME"), reg) );
	}
}

//________________________________________________________________________
//
void draw_utils::ExtractSampleConfigFileInfo( std::map < std::string, Sample > &vec_samples, const std::string &file_path ){
	std::vector < std::map < std::string, std::string > > config_content;
	ExtractConfigFileInfo( file_path, config_content );
	//looping over the blocks (1 block per region)
	for( const auto &sample : config_content ){
		//declaring the Sample object
		Sample smp;

		//
		// Now looping over the info contained for each region
		//
		// Starting from the mandatory informations
		std::vector< std::string > mandatory_information = {"NAME","LINECOLOR","FILLCOLOR"};
		for ( const auto &mandat : mandatory_information ){
			if( sample.find(mandat)!=sample.end() ){
				smp.keys.insert( std::pair < std::string, std::string >(mandat,sample.at(mandat)));
			} else {
				std::cout << "The " << mandat << " information cannot be found ... This is a big problem ! Please fix !" << std::endl;
				abort();
			}
		}
		//Now the rest of the informations
		std::vector< std::string > optional_information = {"LEGEND","FILLSTYLE","MARKERSTYLE"};
		for ( const auto &opt : optional_information ){
			if( sample.find(opt)!=sample.end() ){
				smp.keys.insert( std::pair < std::string, std::string >(opt,sample.at(opt)));
			}
		}
		vec_samples.insert( std::pair < std::string, Sample > (sample.at("NAME"), smp) );
	}
}

//________________________________________________________________________
//
RooFitResult* draw_utils::GetFitResults( RooStats::ModelConfig *mc, const double mu_val, 
										 const std::string &fr_file_path,
										 const std::string &fr_name,
										 const bool postFit ){
	/*
	Returns a fit result. In the prefit case, this returns a set of NPs 
	centered on 0 and of width 1, uncorrelated. For the postfit values,
	the fit result is used. 
	*/
	RooFitResult *rfr;

	if(!postFit){

	    RooRealVar* var(nullptr);

		//Nuisance parameters
		auto *nps = mc -> GetNuisanceParameters();
		TIterator *npIterator = nps -> createIterator();
		while( (var = (RooRealVar*) npIterator->Next()) ){
			const TString name = var->GetName();
			if( name.Contains("alpha") ){
				var -> setVal(0.);
				var -> setError(1.);
			} else {
				var -> setError(1.e-5);
			}
		}

		//POI
		RooRealVar *poi = dynamic_cast<RooRealVar*>(mc->GetParametersOfInterest()->first());
		poi -> setVal(mu_val);
		poi -> setError(1.e-5);
		poi -> setConstant(true);

		//Importing all NPs in the RooArgList
		RooArgList* np = new RooArgList(*nps);
		np -> add(*mc -> GetParametersOfInterest());

		//Creating the RooExpandedFitResult
		RooExpandedFitResult *re = new RooExpandedFitResult(*np);
		rfr = (RooFitResult*)re;

	} else {

    	RooRealVar* var(nullptr);

		//Nuisance parameters
		TIterator *npIterator = mc -> GetNuisanceParameters() -> createIterator();

		//POI
		RooRealVar *poi = dynamic_cast<RooRealVar*>(mc->GetParametersOfInterest()->first());

		//Importing all NPs in the RooArgList
		RooArgList* np = new RooArgList(*mc -> GetNuisanceParameters());
		if(poi->getVal()!=0 && poi->getVal()!=1) np -> add(*mc -> GetParametersOfInterest());

		//Create a RooFitResults
		TFile *ffit = TFile::Open(fr_file_path.c_str(),"READ");
		if(!ffit){
    		messages::print_error( __func__, __FILE__, __LINE__, "Cannot find the fit result file. Aborting !" );
    		abort();
		}

		rfr = (RooFitResult*)ffit->Get(fr_name.c_str());
		if(!rfr){
    		messages::print_error( __func__, __FILE__, __LINE__, "Cannot find the RooFitResult object. Aborting !" );
    		abort();
		}

		RooExpandedFitResult *re = new RooExpandedFitResult(rfr,*np);
		rfr = (RooFitResult*)re;
		ffit -> Close();
	}

	return rfr;
}

//__________________________________________________________________
//
void draw_utils::GetAllROOTObjects( RooStats::ModelConfig *mc, RooSimultaneous *simPdf, 
									RooDataSet* data, 									
									RooFitResult *rfr,
									std::map < std::string, draw_utils::RegionHists > &map_regions ){

    //
    // Getting the categories
    //
	RooCategory* channelCat = (RooCategory*) (&simPdf->indexCat());
	TString chanName = channelCat -> GetName();
	TIterator *iter = channelCat->typeIterator() ;
	RooCatType *tt  = NULL;

	//
	// Setting up the values of the NPs 
	//

	RooRealVar *poi = dynamic_cast<RooRealVar*>(mc->GetParametersOfInterest()->first());
	poi -> setVal(0.);
	RooArgList* np = new RooArgList(*mc -> GetNuisanceParameters());
	np -> add(*mc -> GetParametersOfInterest());

	RooArgList *fpf = (RooArgList*)rfr -> floatParsFinal().Clone();
	RooArgList cp = (RooArgList)rfr -> constPars();

	fpf -> add(cp);
	np -> assignValueOnly(*fpf);

    //
    // Looping over the regions
    //
	while((tt=(RooCatType*) iter->Next()) ){

		draw_utils::RegionHists rg_hist;

	    //
     	// Getting the name
     	//
		TString chanName(tt->GetName());
		std::cout << chanName << std::endl;

	    //
        // Getting RooFit objects
        //
		auto *pdftmp  = simPdf -> getPdf( chanName );
		RooAbsData *datatmp = data->reduce(Form("%s==%s::%s",channelCat->GetName(),channelCat->GetName(),tt->GetName()));
		RooArgSet  *obstmp  = pdftmp->getObservables( *mc->GetObservables() );
		RooRealVar *obs     = ((RooRealVar*) obstmp->first());
		RooArgSet obs_set   = RooArgSet(*obs);

        //
        // Getting the total backgrounds
        //
		RooPlot* frame = obs->frame();
		pdftmp->plotOn(frame,RooFit::FillColor(kBlack),RooFit::FillStyle(3002),RooFit::VisualizeError(*rfr,1), RooFit::Normalization(1,RooAbsReal::RelativeExpected),RooFit::Name("Total_PreFitError_NotAppears"));
		TGraph * tot_error = frame -> getCurve();
		rg_hist.total_err = tot_error;

		pdftmp->plotOn(frame,RooFit::LineWidth(2),RooFit::LineColor(kBlack),RooFit::Normalization(1,RooAbsReal::RelativeExpected),RooFit::Name("Total_CentralPreFit_NotAppears"));
		TGraph * tot_central = frame -> getCurve();
		rg_hist.total_central = tot_central;

        //
        // Getting the data
        //
		datatmp->plotOn(frame,RooFit::MarkerSize(1),RooFit::Name("Data"),RooFit::DataError(RooAbsData::Poisson));
		TGraph* data = frame -> getHist();
		rg_hist.data = data;

        // Bin Width
		RooRealVar* binWidth = ((RooRealVar*) pdftmp->getVariables()->find(Form("binWidth_obs_x_%s_0",tt->GetName())));
		if(!binWidth){
			//For the combined workspace, the naming convention is not exactly the same ... 
			TString chanName_cpy = chanName;
			chanName_cpy.ReplaceAll("combCat_","");
			std::string str_modelName1 = (std::string) chanName_cpy;
			std::vector < std::string > vec_temp = string_utils::split_string(str_modelName1, '_');
			str_modelName1 = "";
			int counter = 0;
			for( const auto &temp : vec_temp ){
				if(counter>0)str_modelName1 += "_";
				if(counter==vec_temp.size()-2)break;
				str_modelName1 += temp; 
				counter++;
			}
			binWidth = ((RooRealVar*) pdftmp->getVariables()->find(Form("binWidth_obs_x_%s0_%s_binned",str_modelName1.c_str(),vec_temp[(const int)(vec_temp.size()-2)].c_str())));
		}
		pdftmp->getVariables()->Print();

        //Getting the model
		TString modelName1(chanName);
		modelName1.Append("_model");
		RooRealSumPdf *pdfmodel1 = (RooRealSumPdf*) (pdftmp->getComponents())->find(modelName1);
		if(!pdfmodel1){
			//For the combined workspace, the naming convention is not exactly the same ... 
			TString chanName_cpy = chanName;
			modelName1 = chanName_cpy.ReplaceAll("combCat_","");
			std::string str_modelName1 = (std::string) modelName1;
			std::vector < std::string > vec_temp = string_utils::split_string(str_modelName1, '_');
			str_modelName1 = "";
			int counter = 0;
			for( const auto &temp : vec_temp ){
				if(counter>0)str_modelName1 += "_";
				if(counter==vec_temp.size()-2)str_modelName1 += "model_";
				str_modelName1 += temp; 
				counter++;
			}
			pdfmodel1 = (RooRealSumPdf*) (pdftmp->getComponents())->find(str_modelName1.c_str());
		}


		RooArgList funcList1 =  pdfmodel1->funcList();
		RooLinkedListIter funcIter1 = funcList1.iterator();
		RooProduct* comp1 = 0;
        //Looping over the samples to build the stack (later)
		while( (comp1 = (RooProduct*) funcIter1.Next()) ) {
        	//Getting the name of the background
			TString compname(comp1->GetName());
			compname.ReplaceAll("L_x_","");
			compname.ReplaceAll(((TString)tt->GetName()).ReplaceAll("combCat_",""),"");
			compname.ReplaceAll("_overallSyst_x_StatUncert","");
			compname.ReplaceAll("_overallSyst_x_HistSyst","");
			compname.ReplaceAll("_overallSyst_x_Exp","");
			compname.ReplaceAll("_","");
			double Ntemp = (comp1->createIntegral(*obs))->getVal() * binWidth->getVal();
			if (Ntemp!=0){
				// std::cout << compname << "    " << Ntemp << std::endl;
				TH1* temp = comp1 -> createHistogram(compname, *obs);
				temp -> Scale( Ntemp / temp -> Integral() );
				rg_hist.hist.insert( std::pair < std::string, TH1* >( (std::string)compname, temp ) );
			}
		}
		map_regions.insert( std::pair < std::string, draw_utils::RegionHists > ( (std::string)chanName, rg_hist ) );
		//break;
	}
}

//________________________________________________________________
//
void draw_utils::DrawCanvas( 	const std::string &output_folder,
								const std::pair < std::string, draw_utils::RegionHists > &region_hists, 
								const std::map < std::string, draw_utils::Region > &map_regions, 
								const std::map < std::string, draw_utils::Sample > &map_samples,
								const bool isPostFit ){

	canvas_style oCan;

	std::string cname = output_folder + "/can_Distrib";
	if(isPostFit)cname += "PostFit";
	else cname+="PreFit"; 
	cname += "_" + region_hists.first;
	oCan.SetName(cname.c_str());


	oCan.init();

	oCan.SetTotalErr(region_hists.second.total_err);
	oCan.SetTotal(region_hists.second.total_central);
	oCan.SetData(region_hists.second.data);

	for( auto temp : region_hists.second.hist ){
    	if( map_samples.find(temp.first)!=map_samples.end()){
    		temp.second -> SetLineColor(atoi(map_samples.at(temp.first).keys.at("LINECOLOR").c_str()));
    		temp.second -> SetFillColor(atoi(map_samples.at(temp.first).keys.at("FILLCOLOR").c_str()));
    		oCan.AddStackedSample(temp.second, map_samples.at(temp.first).keys.at("LEGEND"));
    	} else {
    		temp.second -> SetLineColor(1);
    		temp.second -> SetFillColor(0);
    		oCan.AddStackedSample(temp.second, temp.first);

    	}
    }

    oCan.DrawAll();
   	oCan.SaveAllInfo();
}

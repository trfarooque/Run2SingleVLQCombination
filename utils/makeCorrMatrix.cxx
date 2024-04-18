#include <string>
#include <TFile.h>
#include <TH2.h>
#include <TCanvas.h>
#include <TStyle.h>
#include "RooWorkspace.h"
#include "RooFitResult.h"
#include <vector>
#include <fstream>
#include <string>

/*
#include "RooRealVar.h"
#include "RooDataSet.h"
#include "RooGaussian.h"
#include "RooPlot.h"
#include "RooFitResult.h"
#include "RooGenericPdf.h"
#include "RooConstVar.h"
*/

std::string ReplaceString(const std::string& inputStr, const std::string& orig, const std::string& replacement){

  std::string newStr = inputStr;
  for( std::string::size_type  pos = 0; ; pos += replacement.length() ){
    pos = newStr.find(orig, pos);
    if(pos == std::string::npos) break;
    newStr.erase( pos, orig.length() );
    newStr.insert( pos, replacement );
  }

  return newStr;

}

const double minCorr=0.199;

int num_NF=0;
int num_NP=0;
int num_Gamma=0;

int num_Param=0;
int num_RedParam=0;

std::vector<std::string> NFList={};
std::vector<std::string> NPList={};
std::vector<std::string> GammaList={};

std::vector<std::string> FullParamList={};
std::vector<std::string> ReducedParamList={};

std::vector<std::vector<double> > CorrelationList={};

TH2D* CorrelationMatrix = nullptr;

RooWorkspace* workspace = nullptr;
RooFitResult* fitResult = nullptr;

void Init(const std::string& wsFileName, const std::string& fitFileName, const std::string& wsName, const std::string& fitName){

  TFile* wsFile = TFile::Open(wsFileName.c_str());
  workspace = (RooWorkspace*)(wsFile->Get(wsName.c_str()));
  //workspace->SetDirectory(0);
  wsFile->Close();

  TFile* fitFile = TFile::Open(fitFileName.c_str());
  fitResult = (RooFitResult*)(fitFile->Get(fitName.c_str()));
  //fitResult->SetDirectory(0);
  fitFile->Close();

  return;
}



void makeParamList(const bool useGammas=false){
  RooArgSet varList = workspace->allVars();

  for (auto variable : varList){
    std::string varName = variable->GetName();
    if(varName.find("_In") == varName.size()-3) continue; //ignore these arguments in combined WS
    if( (varName.find("BKGNF_") != std::string::npos) || (varName.find("mu_signal") != std::string::npos) ){
      NFList.push_back(varName);
      FullParamList.push_back(varName);
      num_NF++;
    }
    else if( (varName.find("alpha_") != std::string::npos) && (varName.find("nom_") == std::string::npos) ){
      NPList.push_back(varName);
      FullParamList.push_back(varName);
      num_NP++;
    }
    else if( (varName.find("gamma_") != std::string::npos) && (varName.find("nom_") == std::string::npos) ){
      GammaList.push_back(varName);
      if(useGammas) FullParamList.push_back(varName);
      num_Gamma++;
    }
  }

  num_Param = num_NF + num_NP;
  if(useGammas) num_Param += num_Gamma;


  return;
}

void makeReducedParamList(double _minCorr){

  //Loop over the parameters and find their correlations with every other parameter
  //If any of the correlations exceed the minimum threshold, retain this parameter in the reduced list

  for(int i = 0; i < num_Param; i++){

    const std::string& iname = FullParamList.at(i);

    for(int j = 0; j < num_Param; j++){

      if(i==j) continue;

      const std::string& jname = FullParamList.at(j);
      const double corr = fitResult->correlation(iname.c_str(), jname.c_str());

      if(fabs(corr) > _minCorr){
	ReducedParamList.push_back(iname);
	num_RedParam++;
	break;
      }

    }//j

  }//i

  return;

}

void makeCorrMatrix(const std::string& plotName){

  CorrelationMatrix = new TH2D("CorrelationMatrix", "", num_RedParam,1,num_RedParam, num_RedParam,1,num_RedParam);
  for(int i = 0; i < num_RedParam; i++){

    const std::string& iname = ReducedParamList.at(i);
    std::string binlabel = ReplaceString(iname, "alpha_", "");
    binlabel = ReplaceString(binlabel, "gamma_", "");

    CorrelationMatrix->GetXaxis()->SetBinLabel(i+1, binlabel.c_str());
    CorrelationMatrix->GetYaxis()->SetBinLabel(i+1, binlabel.c_str());
    CorrelationMatrix->GetXaxis()->LabelsOption("v");
    CorrelationMatrix->GetXaxis()->SetLabelSize(0.017);
    CorrelationMatrix->GetYaxis()->SetLabelSize(0.017);

    for(int j = i; j < num_RedParam; j++){

      //if(i==j) continue;
      const std::string& jname = ReducedParamList.at(j);
      const double corrln = fitResult->correlation(iname.c_str(), jname.c_str());
      CorrelationMatrix->SetBinContent(i+1,j+1,corrln*100.);

    }//j

  }//i
  CorrelationMatrix->GetZaxis()->SetRangeUser(-100.,100.);

  int size = 200;
  if(num_RedParam>4){
    //size = num_RedParam*50;
    size = num_RedParam*40;
  }

  //int _resize = size+300;
  int _resize = size+200;

  float markersize = (num_RedParam <=10) ? 1 : 1 - (0.25/20.)*(num_RedParam - 10);
  std::cout << " num_RedParam: " << num_RedParam << " markersize: " << markersize << std::endl;
  TCanvas* canvas = new TCanvas(plotName.c_str(), "", _resize, _resize);
  gStyle->SetPalette(87);
  //CorrelationMatrix->SetMarkerSize(0.75*1000);
  CorrelationMatrix->SetMarkerSize(markersize);
  gStyle->SetPaintTextFormat(".1f");
  gPad->SetLeftMargin(240./(_resize));
  gPad->SetBottomMargin(240./(_resize));
  gPad->SetRightMargin(60./(_resize));
  gPad->SetTopMargin(60./(_resize));

  std::cout << "xlabel : " << CorrelationMatrix->GetXaxis()->GetLabelSize()
	    << "ylabel : " << CorrelationMatrix->GetYaxis()->GetLabelSize() << std::endl;

  CorrelationMatrix->GetXaxis()->LabelsOption("v");
  CorrelationMatrix->GetXaxis()->SetLabelSize( CorrelationMatrix->GetXaxis()->GetLabelSize()*0.75 );
  CorrelationMatrix->GetYaxis()->SetLabelSize( CorrelationMatrix->GetYaxis()->GetLabelSize()*0.75 );



  /*
  gStyle->SetPalette(87);
  CorrelationMatrix->SetMarkerSize(0.75*1000);
  gStyle->SetPaintTextFormat(".1f");
  gPad->SetLeftMargin(240./(_resize));
  gPad->SetBottomMargin(240./(_resize));
  gPad->SetRightMargin(60./(_resize));
  gPad->SetTopMargin(60./(_resize));

  CorrelationMatrix->GetXaxis()->LabelsOption("v");
  CorrelationMatrix->GetXaxis()->SetLabelSize( CorrelationMatrix->GetXaxis()->GetLabelSize()*0.75 );
  CorrelationMatrix->GetYaxis()->SetLabelSize( CorrelationMatrix->GetYaxis()->GetLabelSize()*0.75 );
  */

  canvas->SetTickx(0);
  canvas->SetTicky(0);
  CorrelationMatrix->GetYaxis()->SetTickLength(0);
  CorrelationMatrix->GetXaxis()->SetTickLength(0);
  canvas->SetGrid();
  CorrelationMatrix->Draw("coltext");
  canvas->RedrawAxis("g");

  /*
  canvas->SetTickx(0);
  canvas->SetTicky(0);
  CorrelationMatrix->GetYaxis()->SetTickLength(0);
  CorrelationMatrix->GetXaxis()->SetTickLength(0);
  canvas->SetGrid();
  CorrelationMatrix->Draw("coltext");
  canvas->RedrawAxis("g");
  */
  std::cout << "Writing to file : " << plotName+".png" << std::endl;
  canvas->SaveAs((plotName+".png").c_str());

  return;


}

void printUsage(){

  std::cout << "Usage: " << std::endl;
  std::cout << " makeCorrMatrix --wsFile=<path to workspace file> --fitResultFile=<path to fit result> \
--outputPath=<output directory path> --plotName=<name of output plot>(optional) \
--wsName=<workspace name>(optional) <fit result name (optional)>"
	    << std::endl;
  std::cout << " default arguments:" << std::endl;
  std::cout << " wsName: combined" << std::endl;
  std::cout << " fitResultName: fitResult" << std::endl;
  std::cout << " plotName: CorrelationMatrix" << std::endl;
   
  return;
}

int main(int argc, char** argv){

  if(argc > 0)
  if(argc < 4){
    std::cerr << "ERROR: Insufficient number of arguments to makeCorrMatrix" << std::endl;
    printUsage();
    abort();
  } 

  std::string wsFileName = "";
  std::string fitResultFileName = "";
  std::string outputPath = "";
  std::string plotName = "CorrelationMatrix";
  std::string wsName = "combined";
  std::string fitResultName = "fitResult";

  //====================================
  for(int i = 1; i<argc; i++){

    std::string opt(argv[i]);
    std::string argument,value;
    size_t pos = opt.find("=");
    if(pos == std::string::npos){//the sign = is not found, skip the argument with a warning message                              
      std::cout << "<!> Argument has no '=' sign, skipping : " << opt << std::endl;
      continue;
    }
    argument = opt.substr(0, pos);
    std::transform(argument.begin(), argument.end(), argument.begin(), toupper);//convert to upper case                           
    value=opt.erase(0, pos + 1);

    if(argument=="--WSFILE"){ wsFileName = value; }
    else if(argument=="--FITRESULTFILE"){ fitResultFileName = value; }
    else if(argument=="--WSNAME"){ wsName = value; }
    else if(argument=="--FITRESULTNAME"){ fitResultName = value; }
    else if(argument=="--OUTPUTPATH"){ outputPath = value; }
    else if(argument=="--PLOTNAME"){ plotName = value; }
    else{ std::cerr << "Unknown argument : " << argument << "... Skipping." << std::endl; }
  }

  if(wsFileName == ""){
    std::cerr << "Missing argument --wsFile" << std::endl;
    abort();
  }
  if(fitResultFileName == ""){
    std::cerr << "Missing argument --fitResultFile" << std::endl;
    abort();
  }
  if(outputPath == ""){
    std::cerr << "Missing argument --outputPath" << std::endl;
    abort();
  }
  

  //====================================

  Init(wsFileName, fitResultFileName, wsName, fitResultName); 

  gStyle->SetOptStat(0);
  gStyle->SetPalette(87);
  gStyle->SetPaintTextFormat(".1f");
  gStyle->SetTextFont(42);

  makeParamList(/*useGammas*/ false);

  std::cout << " num_NF : " << num_NF << std::endl;
  std::cout << " num_NP : " << num_NP << std::endl;
  std::cout << " num_Gamma : " << num_Gamma << std::endl;

  makeReducedParamList(/*_minCorr*/ minCorr);

  std::cout << " num_Param : " << num_Param << std::endl;
  std::cout << " num_RedParam : " << num_RedParam << std::endl;

  std::cout << "Making correlation matrix plot: " << outputPath+"/"+plotName << std::endl;
  makeCorrMatrix(outputPath+"/"+plotName);

  return 0;


}


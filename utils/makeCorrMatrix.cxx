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

const double minCorr=0.20;

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

    if( (varName.find("mu_") != std::string::npos) && (varName.find("mu_signal") == std::string::npos) ){
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

  //fitResult
  //Loop over the parameters and find their correlations with every other parameter
  //If any of the correlations exceed the minimum threshold, retain this parameter in the reduced list

  for(int i = 0; i < num_Param; i++){

    const std::string& iname = FullParamList.at(i);

    for(int j = 0; j < num_Param; j++){

      if(i==j) continue;

      const std::string& jname = FullParamList.at(j);
      const double corr = fitResult->correlation(iname.c_str(), jname.c_str());
      if(corr > _minCorr){
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

  TCanvas* canvas = new TCanvas(plotName.c_str(), "", 800, 800);
  canvas->SetBottomMargin(0.3);
  canvas->SetLeftMargin(0.3);
  canvas->SetRightMargin(0.001);
  canvas->SetTopMargin(0.001);
  canvas->SetGrid();
  canvas->cd();
  CorrelationMatrix->Draw("coltext");
  canvas->SaveAs((plotName+".png").c_str());

  return;


}

void printUsage(){

  std::cout << "Usage: " << std::endl;
  std::cout << " makeCorrMatrix <workspace file name> <fit file name> <workspace name>(optional) <fit result name (optional)>"
	    << std::endl;
  std::cout << " default arguments:" << std::endl;
  std::cout << " workspace name: combined" << std::endl;
  std::cout << " fit result name: fitResult" << std::endl;
   
  return;
}


int main(int argc, char** argv){

  if(argc < 3){
    std::cerr << "ERROR: makeCorrMatrix needs at least 2 arguments" << std::endl;
    printUsage();
  } 
  std::string wsFileName = argv[1];
  std::string fitFileName = argv[2];
  std::string wsName = (argc > 3) ? argv[3] : "combined";
  std::string fitName = (argc > 4) ? argv[4] : "fitResult";

  Init(wsFileName, fitFileName, wsName, fitName); 

  gStyle->SetOptStat(0);
  gStyle->SetPalette(87);
  gStyle->SetPaintTextFormat(".1f");
  gStyle->SetTextFont(42);

  makeParamList(/*useGammas*/ false);
  makeReducedParamList(/*_minCorr*/ minCorr);

  std::cout << " num_NF : " << num_NF << std::endl;
  std::cout << " num_NP : " << num_NP << std::endl;
  std::cout << " num_Gamma : " << num_Gamma << std::endl;

  std::cout << " num_Param : " << num_Param << std::endl;
  std::cout << " num_RedParam : " << num_RedParam << std::endl;

  makeCorrMatrix("correlation_matrix_OSML");

  return 0;


}


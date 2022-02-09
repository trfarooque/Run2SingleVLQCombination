#ifndef FITTINGTOOL_H
#define FITTINGTOOL_H

class RooFitResult;
class RooAbsPdf;
class RooAbsData;

#include <string>
#include <map>
#include <vector>
#include "RooStats/ModelConfig.h"
#include "TVirtualFitter.h"

class FittingTool {

public:

  //
  // Standard C++ functions
  //
  FittingTool();
  ~FittingTool();
  FittingTool( const FittingTool & );

  //
  // Gettters and setters
  //
  inline void SetDebug ( const int debug ){ m_debug = debug>0; }
  inline void OutputFolder( const std::string &str ){ m_output_folder = str; };
  inline void OutputSuffix( const std::string &str ){ m_output_suffix = str; };

  inline void MinimType ( const std::string &type ){ m_minimType = type; }
  inline std::string GetMinimType(){ return m_minimType; }

  inline int GetMinuitStatus() { return m_minuitStatus; }
  inline int GetHessStatus() { return m_hessStatus; }
  inline double GetEDM() { return m_edm; }

  inline void ValPOI( const double value ) { m_valPOI = value; }
  inline double GetValPOI() { return m_valPOI; }

  inline void ConstPOI( const bool constant ) { m_constPOI = constant; }
  inline double GetConstPOI() { return m_constPOI; }

  inline RooFitResult* GetFitResult() { return m_fitResult; }

  inline void UseMinos( const std::vector<std::string> &minosvar ){ m_useMinos = true; m_varMinos = minosvar; }
  inline void UseMinos( const bool use ){ m_useMinos = use; }

  //
  // Specific functions
  //
  void FitPDF( RooStats::ModelConfig* model, RooAbsPdf* fitpdf, RooAbsData* fitdata, bool fastFit = false );
  void ExportFitResultInTextFile( const std::string &finaName );
  void ExportFitResultInROOTFile( const std::string &finaName );
  std::map < std::string, double > ExportFitResultInMap();

private:
  std::string m_minimType;
  std::string m_output_folder, m_output_suffix;
  int m_minuitStatus, m_hessStatus;
  double m_edm,m_valPOI,m_randomNP;
  long int m_randSeed;
  bool m_useMinos,m_constPOI;
  std::vector<std::string> m_varMinos;
  RooFitResult* m_fitResult;
  bool m_debug;
};

#endif //FITTINGTOOL_H

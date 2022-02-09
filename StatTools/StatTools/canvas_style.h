#ifndef CANVAS_STYLE_H
#define CANVAS_STYLE_H

#include "TCanvas.h"
#include <map>
#include <string>

class TPad;
class THStack;
class TGraph;
class TLegend;
class TH1;
class TGraphAsymmErrors;

class canvas_style: public TCanvas {
public:
	canvas_style();
	canvas_style( const canvas_style& );
	~canvas_style();

	//
	// Inline functions
	//
	inline void SetXTitle( const std::string &title ){ m_xtitle = title; }
	inline void SetYTitle( const std::string &title ){ m_ytitle = title; }
	inline void SetLumiLabel( const std::string &title ){ m_lumiLabel = title; }
	inline void SetCMELabel( const std::string &title ){ m_CME = title; }
	inline void SetATLASLabel( const std::string &title ){ m_ATLASLabel = title; m_useATLASLabel = true;}
	inline void UseATLASLabel( const bool use ){ m_useATLASLabel = use; }
	inline void SetData( TGraph *graph, const std::string &legend = "Data" ){ m_data = graph; m_data_lgd = legend; }
	inline void SetTotalErr( TGraph *graph, const std::string &legend = "Total background"  ){ m_tot_err = graph; m_tot_err_lgd = legend; }
	inline void SetTotal( TGraph *graph ){ m_tot = graph; }

	//
	// Initialisation function
	//
	void init();

	//
	// Adding samples to the stack
	//
	void AddStackedSample( TH1 *hist, const std::string &leg );
	void DrawAll();
	void SaveAllInfo();

private:
	TPad* m_pad0;
	TPad* m_pad1;
	THStack* m_stack;
	std::map < std::string, TH1* > m_histograms;
	TH1F* m_h_tot;
	TGraphAsymmErrors* m_ratio;
	TGraph *m_tot;
	TGraph *m_tot_err; std::string m_tot_err_lgd;
    TGraph *m_data; std::string m_data_lgd;
    TLegend *m_lgd;
    std::string m_xtitle;
    std::string m_ytitle;
    std::string m_lumiLabel;
    std::string m_CME;
    bool m_useATLASLabel;
    std::string m_ATLASLabel;
};

#endif //CANVAS_STYLE_H
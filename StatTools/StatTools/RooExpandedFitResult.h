// vim: ts=4:sw=4
/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// Creation: March 2012, Alex Koutsman (CERN/TRIUMF)                               //
// Class derived from RooFitResult, to be able to add more parameters       //
//    for error propagation (calculation & visualization)                                   //
/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

#ifndef ROOEXPANDEDFITRESULT_H
#define ROOEXPANDEDFITRESULT_H

#include "TString.h"
#include "RooFitResult.h"
#include "RooArgList.h"

#include <iostream>
#include <vector>

class RooExpandedFitResult: public RooFitResult{

    public:
        RooExpandedFitResult(RooFitResult* origResult, RooArgList extraPars);
        RooExpandedFitResult(RooArgList extraPars);

        ~RooExpandedFitResult(){}

        //ClassDef(RooExpandedFitResult,1) // Container class for expanded fit result
};

#endif

from numpy import array, log, exp

XS_map_singleWb = {600.:9060., 700.:5820., 800.:3860., 900.:2720., 1000.:1950.,
          1100.:1350., 1200.:982., 1300.:716., 1400.:540., 1500.:408.,
          1600.:305., 1700.:230., 1800.:174., 1900.:136., 2000.:102.}

XS_map_singleWb_new = {700.:6420., 800.:4360., 900.:3180., 1000.:2240,
                       1100.:1630., 1200.:1220., 1300.:884., 1400.:674., 
                       1500.:513., 1600.:385., 1700.: 299., 1800.:231.,
                       1900.:179., 2000.:139., 2100.:105., 2200.: 84.3, 
                       2300.: 66.7, 2400.: 51.9, 2500.: 40.8, 2600.: 32.5,
                       2700.: 26.4, 2800.: 20.8, 2900.: 16.3, 3000.: 12.9}

XS_map_singleZt_new = {900.0: 282.28377835211074, 1800.0: 22.81680445504944, 650.0: 686.9041705929574, 2700.0: 2.4532184965910533, 2450.0: 4.629773244676519, 1300.0: 98.66082737366983, 2200.0: 8.387020878097285, 1950.0: 15.834804636525941, 800.0: 395.9734602800336, 1700.0: 29.540171397500174, 2600.0: 3.253035906565995, 1200.0: 116.91783359877833, 2100.0: 10.83233896979884, 3000.0: 1.2491356006878573, 1850.0: 19.965723743894095, 1600.0: 38.041605368093585, 1100.0: 154.93632246375287, 2000.0: 13.956112830100503, 2900.0: 1.4749552804803197, 1500.0: 50.4320103988614, 2400.0: 5.185806732346921, 1000.0: 211.38138390318542, 750.0: 470.76486643015807, 2800.0: 1.9711578189015033, 2550.0: 3.626965741430595, 1400.0: 65.25040943632594, 2300.0: 6.60422176578673}

XS_map_singleWt = {600.:1060., 700.:745., 800.:532., 900.:388., 1000.:285.,
                   1100.:212., 1200.:159., 1300.:120., 1400.:91.7, 1500.:70.6,
                   1600.:54.1, 1700.:42.0, 1800.:32.4, 1900.:25.2, 2000.:19.8}

XS_map_singleZt = {600.:698., 700.:500., 800.:365., 900.:271., 1000.:203.,
                   1100.:152., 1200.:116., 1300.:89.4, 1400.:69.2, 1500.:54.0,
                   1600.:42.0, 1700.:33.0, 1800.:25.9, 1900.:20.5, 2000.:16.2}

XS_map_pair = {500.:3270., 600.:1130., 700.:442., 800.:190., 900.:87.7, 1000.:42.7,
               1100.:21.7, 1200.:11.4, 1300.:6.18, 1400.:3.42, 1500.:1.93, 1600.:1.11,
               1700.:0.641, 1800.:0.376, 1900.:0.222, 2000.:0.132}

XSUncertainty_map_Stat_SingleWb = {700.:1.0, 800.:1.3, 900.:1.2, 1000.:1.1, 1100.:1.3, 1200.:1.3, 1300.:1.3, 1400.:1.1, 1500.:1.3, 1600.:1.4, 1700.:1.4, 1800.:1.4, 1900.:1.3, 2000.:1.4, 2100.:1.3, 2200.:1.3, 2300.:1.6, 2400.:1.4, 2500.:1.4, 2600.:1.6, 2700.: 1.2, 2800.: 1.2, 2900.:1.7, 3000.:1.4}

XSUncertainty_map_PDF_SingleWb = {700.:0.9, 800.:1.2, 900.:2.1, 1000.:1.7, 1100.:1.4, 1200.:1.6, 1300.:1.5, 1400.:1.8, 1500.:2.3, 1600.:1.9, 1700.:2.4, 1800.:1.9, 1900.:2.3, 2000.:2.5, 2100.:15.9, 2200.:2.8, 2300.:3.1, 2400.:3.2, 2500.:3.6, 2600.:3.8, 2700.:4.3, 2800.: 5.1, 2900.:5.8, 3000.:5.6}


XSUncertainty_map_ScaleUp_SingleWb = {700.:2.2, 800.:2.4, 900.:2.5, 1000.:1.8, 1100.:2.7, 1200.:2.2, 1300.:1.8, 1400.:1.7, 1500.:2.1, 1600.:1.9, 1700.:1.9, 1800.:1.7, 1900.:1.3, 2000.:1.9, 2100.:2.3, 2200.:2.1, 2300.:2.6, 2400.:2.5, 2500.:2.6, 2600.:3.1, 2700.: 2.5, 2800.: 3.6, 2900.:3.2, 3000.:3.5}

XSUncertainty_map_ScaleDown_SingleWb = {700.:1.4, 800.:1.4, 900.:1.5, 1000.:1.0, 1100.:1.6, 1200.:1.0, 1300.:0.8, 1400.:1.0, 1500.:1.3, 1600.:1.0, 1700.:1.5, 1800.:1.6, 1900.:1.1, 2000.:0.8, 2100.:2.2, 2200.:1.9, 2300.:2.5, 2400.:2.4, 2500.:2.5, 2600.:3.0, 2700.: 2.7, 2800.: 3.5, 2900.:3.1, 3000.:3.5}


def interpolator(x1, y1, x2, y2, x):
    if x1==x2:
        print("Input x values are same. Cannot interpolate. Returning (y1+y2)/2.")
        return (y1+y2)/2.0
    if float(x)==float(x1): return y1
    elif float(x)==float(x2): return y2
    return y1 + (x-x1)*(y2-y1)/(x2-x1)

def XS_NWA(mass, cw, mode='WT'):

    ## Returns the NW cross-section corresponding to a total coupling of cW (the Wulzer Couplings)
    ## The NW total cross-section for WT process is fitted as y = exp(A0 + A1*x + A2*x^2 + A3*x^3 + A4*x^4)
    ## This fit works pretty well to predict values within the range that is in the Wulzer/Fuks paper, 
    ## Allowed mode is 'WT', 'ZT', 'WB', or 'ZB'
    m = mass/100.
    # These values are from the Wulzer paper
    #A, A0 = array([ -7.39028425e-01,   3.32655022e-02,  -1.08256630e-03,   1.38042384e-05]), 12.5570351663
    # These values are from the New paper by Fuks
    x =  array( [ m, m**2, m**3, m**4 ] ) 
    if mode == 'WT':
        A, A0 = array([-0.532, 0.015, -3.54e-4, 3.35e-6]), 11.9
    if mode == 'ZT':
        A, A0 = array([-4.74655447e-01,  1.22370471e-02, -2.95886410e-04 , 2.79057526e-06]), 9.150415284734407
    XS = exp(A0 + A.dot(x))
    return XS*(cw**2)/1000.0  ## Returns XS value in pb

def PNWA(proc, mass, GM):

    ## Correction factor between NWA and full-width cross-section: PNWA = (NWA cross-section)(FW cross-section)
    ## Parameters:
    ##   proc : process type in the form <production-boson><VLQ><decay>.  E.g. WTWb, WTHt, WTZt, ZTWb, etc.
    ##   mass : mass of VLQ in GeV
    ##   GM   : width/mass (i.e., Gamma/Mass)
    ## See https://arxiv.org/abs/2003.00640 for details

    ## Customized for different processes following parameterization in https://arxiv.org/abs/2003.00640
    ## Use bilinear interpolation for intermediate masses    
    if proc == "WTWb":
        As = {1000:  0.526, 1200:  0.638, 1400:  0.708, 1600: 0.697, 1800: 0.784, 2000: 0.764, 2200: 0.720}
        Bs = {1000: -0.123, 1200: -0.048, 1400: -0.054, 1600: 0.171, 1800: 0.153, 2000: 0.235, 2200: 0.346}
    elif proc == "WTZt":
        As = {1000:  0.55720, 1200:  0.68056, 1400:  0.73284, 1600: 0.71534, 1800: 0.75899, 2000: 0.77691, 2200: 0.69649 }
        Bs = {1000: -0.24681, 1200: -0.17556, 1400: -0.00117, 1600: 0.25712, 1800: 0.23967, 2000: 0.22725, 2200: 0.45627 }
    elif proc == "WTHt":
        As = { 1000:  0.057, 1200:  0.189, 1400: 0.319, 1600: 0.433, 1800: 0.522, 2000: 0.613, 2200:  0.658 }
        Bs = { 1000: 35.032, 1200: 10.005, 1400: 7.923, 1600: 7.801, 1800: 8.771, 2000: 9.329, 2200: 12.082 }
        x0 = { 1000:  0.052, 1200:  0.035, 1400: 0.026, 1600: 0.022, 1800: 0.023, 2000: 0.021, 2200:  0.024 }
    elif proc == "ZTWb":
        As = {1000:  0.507, 1200:  0.639, 1400:  0.737, 1600: 0.757, 1800: 0.807, 2000: 0.820, 2200: 0.754 }
        Bs = {1000: -0.272, 1200: -0.126, 1400: -0.046, 1600: 0.141, 1800: 0.160, 2000: 0.195, 2200: 0.356 }
    elif proc == "ZTZt":
        As = {1000:  0.734, 1200:  0.550, 1400:  0.664, 1600: 0.730, 1800: 0.746, 2000: 0.786, 2200: 0.709 }
        Bs = {1000:  0.013, 1200:  0.035, 1400:  0.087, 1600: 0.166, 1800: 0.312, 2000: 0.275, 2200: 0.477 }
    elif proc == "ZTHt":
        As = { 1000:  0.0, 1200:  0.078, 1400: 0.199, 1600: 0.321, 1800: 0.428, 2000: 0.526, 2200:  0.601 }
        Bs = { 1000:  0.0, 1200: 20.616, 1400: 9.290, 1600: 7.936, 1800: 8.072, 2000: 8.456, 2200:  9.896 }
        x0 = { 1000:  0.0, 1200:  0.047, 1400: 0.030, 1600: 0.026, 1800: 0.023, 2000: 0.021, 2200:  0.022 }
    else:
        print("ERROR: proc",proc,"is not a valid process! (returning 0)")
        return 0;

    ### Determine known mass below and above requested mass that has a PNWA fucntion
    known_masses = array(sorted(As.keys()))
    if mass <= float(min(known_masses)): mlow, mhigh = float(known_masses[0]), float(known_masses[1])
    elif mass >= float(max(known_masses)): mlow, mhigh = float(known_masses[-2]), float(known_masses[-1])
    else:
        for ii in range(len(known_masses)-1):
            if mass >= known_masses[ii] and mass < known_masses[ii+1]:
                mlow, mhigh = float(known_masses[ii]), float(known_masses[ii+1])
                break


    _A = interpolator(mlow, As[mlow], mhigh, As[mhigh], mass)
    _B = interpolator(mlow, Bs[mlow], mhigh, Bs[mhigh], mass)
    if "H" in proc:
        _x0 = interpolator(mlow, x0[mlow], mhigh, x0[mhigh], mass)

    # ### Define the funtional forms for PNWA
    # # ... for W and Z decays and H decays with Gamma/M < x0:
    # PNWAfunction = lambda mass, GM : 1.0 +  As[int(mass)]*GM + Bs[int(mass)]*GM**2
    # # ... for H decays with Gamma/M >= x0:
    # PNWAfunction2 = lambda mass, GM : 1.0 - As[int(mass)]*( 1.0 - exp( -Bs[int(mass)]*(GM - x0[mass]) ) )

    # ### Get PNWA value for mlow
    # if "H" in proc and GM >= x0[mlow] :
    #     flow = PNWAfunction2(mlow,GM)
    # else :
    #     flow = PNWAfunction(mlow,GM)

    # ### Get PNWA value for mhigh
    # if "H" in proc and GM >= x0[mhigh] :
    #     fhigh = PNWAfunction2(mhigh,GM)
    # else :
    #     fhigh = PNWAfunction(mhigh,GM)
    if "H" not in proc:
        return 1.0 + _A*GM + _B*GM**2
    elif GM < _x0:
        return 1.0 +_A*_B*GM -(_A*_B/_x0)*GM**2
    else:
        return 1.0 - _A*(1 - exp(-_B*(GM - _x0)))
    #return interpolator(mlow, flow, mhigh, fhigh, mass)

def XSUncertainty(mass):
    known_masses = array(sorted(XSUncertainty_map_Stat_SingleWb.keys()))
    if mass <= float(min(known_masses)): mlow, mhigh = float(known_masses[0]), float(known_masses[1])
    elif mass >= float(max(known_masses)): mlow, mhigh = float(known_masses[-2]), float(known_masses[-1])
    else:
        for ii in range(len(known_masses)-1):
            if mass >= known_masses[ii] and mass < known_masses[ii+1]:
                mlow, mhigh = float(known_masses[ii]), float(known_masses[ii+1])
                break
    fup_low = (XSUncertainty_map_Stat_SingleWb[mlow]**2 + XSUncertainty_map_PDF_SingleWb[mlow]**2 + XSUncertainty_map_ScaleUp_SingleWb[mlow]**2)**0.5/100.0
    fup_high = (XSUncertainty_map_Stat_SingleWb[mhigh]**2 + XSUncertainty_map_PDF_SingleWb[mhigh]**2 + XSUncertainty_map_ScaleUp_SingleWb[mhigh]**2)**0.5/100.0
    fdown_low = (XSUncertainty_map_Stat_SingleWb[mlow]**2 + XSUncertainty_map_PDF_SingleWb[mlow]**2 + XSUncertainty_map_ScaleDown_SingleWb[mlow]**2)**0.5/100.0
    fdown_high = (XSUncertainty_map_Stat_SingleWb[mhigh]**2 + XSUncertainty_map_PDF_SingleWb[mhigh]**2 + XSUncertainty_map_ScaleDown_SingleWb[mhigh]**2)**0.5/100.0
    return [interpolator(mlow, fup_low, mhigh, fup_high, mass), interpolator(mlow, fdown_low, mhigh, fdown_high, mass)]

def FtFactor(proc, mass, GM):
    if proc in ['WTWb','WTZt','WTHt','ZBWt']:
        return 1.0
    elif proc == 'ZTZt':
        As = {'low': {1000.0: 0.9694110113247894, 
                      1200.0: 0.9589911555945622, 
                      1400.0: 0.9542319706981397, 
                      1600.0: 0.9505205665336554, 
                      1800.0: 0.9478867479160621, 
                      2000.0: 0.9449261210380525, 
                      2200.0: 0.9440950010333032, 
                      2400.0: 0.9368601844670403, 
                      2600.0: 0.9381265125972342}, 
              'high': {1000.0: 1.0675136197603414, 
                       1200.0: 1.0784822610477485, 
                       1400.0: 1.0759352030736185, 
                       1600.0: 1.0796884306459775, 
                       1800.0: 1.0902476909486913, 
                       2000.0: 1.0830544018678439, 
                       2200.0: 1.097614485004791, 
                       2400.0: 1.1015850504657756, 
                       2600.0: 1.1011262157275725}}
        Bs = {'low': {1000.0: -0.7482434525643866, 1200.0: -0.47119892633257704, 1400.0: -0.3731706237419776, 1600.0: -0.21938065102307053, 1800.0: -0.10816849981545607, 2000.0: 0.02894418887135209, 2200.0: 0.07067916383018459, 2400.0: 0.3317469155268278, 2600.0: 0.4087246390807451}, 'high': {1000.0: -0.7079336902578997, 1200.0: -0.5883217107278437, 1400.0: -0.38444847905941915, 1600.0: -0.23809289156725913, 1800.0: -0.1752482290244645, 2000.0: 0.015220113329158779, 2200.0: 0.026841925864909816, 2400.0: 0.13419851650838013, 2600.0: 0.2752357958410574}}
        Cs = {'low': {1000.0: 0.0, 1200.0: 0.0, 1400.0: 0.0, 1600.0: 0.0, 1800.0: 0.0, 2000.0: 0.0, 2200.0: 0.0, 2400.0: 0.0, 2600.0: 0.0}, 'high': {1000.0: 0.3673992315304307, 1200.0: 0.3576324663892575, 1400.0: 0.18529637509248245, 1600.0: 0.1046109953497519, 1800.0: 0.14985359361494044, 2000.0: -0.03120971028245153, 2200.0: 0.11597011742395424, 2400.0: 0.07751488487372908, 2600.0: -0.011837950047630663}}
    else:
        return 1.0
    
    if GM < 0.1:
        As_,Bs_,Cs_ = As['low'],Bs['low'],Cs['low']
        _As, _Bs, _Cs = As['high'],Bs['high'],Cs['high']
    else:
        As_,Bs_,Cs_ = As['high'],Bs['high'],Cs['high']
        _As, _Bs, _Cs = As['low'],Bs['low'],Cs['low']
    known_masses = array(sorted(As_.keys()))
    if mass <= float(min(known_masses)): mlow, mhigh = float(known_masses[0]), float(known_masses[1])
    elif mass >= float(max(known_masses)): mlow, mhigh = float(known_masses[-2]), float(known_masses[-1])
    else:
        for ii in range(len(known_masses)-1):
            if mass >= known_masses[ii] and mass < known_masses[ii+1]:
                mlow, mhigh = float(known_masses[ii]), float(known_masses[ii+1])
                break
    

    ### GetFt value for mlow
    flow = As_[mlow] + Bs_[mlow]*GM + Cs_[mlow]*GM**2 + 0.5*((_As[mlow] + _Bs[mlow]*0.1 + _Cs[mlow]*0.1**2) - (As_[mlow] + Bs_[mlow]*0.1 + Cs_[mlow]*0.1**2))
    fhigh = As_[mhigh] + Bs_[mhigh]*GM + Cs_[mhigh]*GM**2 + 0.5*((_As[mhigh] + _Bs[mhigh]*0.1 + _Cs[mhigh]*0.1**2) - (As_[mhigh] + Bs_[mhigh]*0.1 + Cs_[mhigh]*0.1**2))

    return interpolator(mlow, flow, mhigh, fhigh, mass)


        


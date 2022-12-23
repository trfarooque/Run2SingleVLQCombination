from VLQCouplingCalculator import VLQCouplingCalculator as vlq
from VLQCouplingCalculator import VLQMixAngleCalculator as vlqx
import sys

## Showing the different methods that facilitate using these classes

mass = 1100.0 # mass to use unless a different mass is given on command line

# Check if mass if give on command line
if len(sys.argv) > 1: 
    mass = float(sys.argv[1])
    print("mass set to ", mass)

print( "Each of the following cases was set for a 'T' with M =", mass/1000, "TeV")

## Initialize - 1
c = vlq(mass, 'T')  ## Use mass and vlq mode

## Initialize - 2
c = vlq()
c.setMVLQ(mass)  # Set mass of VLQ in GeV
c.setVLQMode('T')  # Set vlq type ('X', 'Y', 'T' or 'B')

## Set the VLQ Parameters: kappa, xi parameterization as in https://arxiv.org/pdf/1305.4172.pdf
print( "\n\nUsing Kappa-Xi parameterization. Kappa = 0.5, xiW = 0.5, xiZ = xiH = 0.25")
c.setKappaxi(0.5, 0.5, 0.25) # the first number if kappa, the second and third numbers are xiW and xiZ. xiH = 1 - xiW - xiZ
print( "Kappa = ", c.getKappa())
print( "BRs(W,Z,H,S) = ", c.getBRs())
print( "Total Decay Width [GeV] = ", c.getGamma())

## Set the VLQ Parameters: cW/Z/H parameterization as in https://arxiv.org/pdf/1409.0100.pdf
print( "\n\nUsing cW/Z/H parameterization. cW = 0.5, cZ = 0.5, cH = 1.38")
c.setcVals(0.5, 0.5, 1.38) # the first number if kappa, the second and third numbers are xiW and xiZ. xiH = 1 - xiW - xiZ
print( "Kappa = ", c.getKappa())
print( "BRs(W,Z,H,S) = ", c.getBRs())
print( "Total Decay Width [GeV] = ", c.getGamma())

## Set the VLQ Parameters: kW/Z/H parameterization as in https://arxiv.org/pdf/1610.06422.pdf
print( "\n\nUsing kW/Z/H parameterization. kW = 0.5, kZ = 0.5, kH = 1.38")
c.setKappas(0.5, 0.5, 1.38) # the first number if kappa, the second and third numbers are xiW and xiZ. xiH = 1 - xiW - xiZ
print( "Kappa = ", c.getKappa())
print( "BRs(W,Z,H,S) = ", c.getBRs())
print( "Total Decay Width [GeV] = ", c.getGamma())

## Set the VLQ Parameters: tilde couplings as in https://arxiv.org/pdf/2003.00640.pdf
print( "\n\nUsing tilde parameterization. cW_ = 0.5, cZ_ = 0.25, cH_ = 0.25")
c.setc_Vals(0.5, 0.25, 0.25) # the first number if kappa, the second and third numbers are xiW and xiZ. xiH = 1 - xiW - xiZ
print( "Kappa = ", c.getKappa())
print( "BRs(W,Z,H,S) = ", c.getBRs())
print( "Total Decay Width [GeV] = ", c.getGamma())

## Set the VLQ Parameters: Gamma-BR parameterization
print( "\n\nUsing Gamma-BR parameterization. Gamma = 220., BRW = 0.5, BRZ = BRH = 0.25")
c.setGammaBRs(220.0, 0.5, 0.25) # the first number if Gamma = total width, the second and third numbers are BRW and BRZ. BRH = 1 - BRW - BRZ
print( "Kappa = ", c.getKappa())
print( "BRs(W,Z,H,S) = ", c.getBRs())
print( "Total Decay Width [GeV] = ", c.getGamma())

## How to Use the mixing angle calculator

# initialize - 1
c = vlqx(mvlq=mass, mode = 'T', multiplet = 'XTB')

# initialize - 2
c = vlqx()
c.setMVLQ(mass)
c.setVLQMode('T')
c.setMultiplet('XTB')

# Setting mixing angles
# Always set the angle for the leading coupling for each representation
# Unless it is a doublet representation, don't set multiple coupling angles at the same instance
# Higher order multiplets assume M(T) = M(B) (so no VLQ -> VLQ branching)
# 0 < Angle < pi/2 for singlets, -pi/4 < Angle < pi/4 for doublets, -pi/8 < Angle < pi/8 for triplets

print( "\n\nUsing Mixing angle parameterization. 'T' in 'XTB' multiplet with angle_UL = 0.2")
c.setAngleUL(0.2) # angle in radians)
c.setCouplings()
print( "Kappa = ", c.getKappa())
print( "BRs(W,Z,H,S) = ", c.getBRs())
print( "Total Decay Width [GeV] = ", c.getGamma())


c.setMultiplet('T')
print( "\n\nUsing Mixing angle parameterization. 'T' singlet with angle_UL = 0.2")
c.setAngleUL(0.2) # angle in radians)
c.setCouplings()
print( "Kappa = ", c.getKappa())
print( "BRs(W,Z,H,S) = ", c.getBRs())
print( "Total Decay Width [GeV] = ", c.getGamma())


### Testing cross section calculation
mass = 1600.
print( "\n============================\n")

print( "T singlet with mass", mass, "\n")
#kappas = [0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6]
#kappas = [0.1, 0.2, 0.4, 1.0, 1.6]
kappas = [0.5]

print( "Method 1:")
from VLQCrossSectionCalculator import *
c.setMVLQ(mass)
c.setVLQMode('T')
c.setMultiplet('T')

for kappa in kappas:
    c.setKappaxi(kappa, 0.5, 0.25)
    width = c.getGamma()
    #print "width/mass : ", width/mass
    cw = c.getcVals()[0]
    #print "cw : ", cw
    (BRW,BRZ,BRH,BRS) = c.getBRs()
    #print "BRs : ", c.getBRs()

    print( "M =",mass,", kappa =",kappa,", width/mass =",width/mass)
    print( "  Xsec(Wb->T->Wb) = ", 1000*XS_NWA(mass, cw, mode='WT')*BRW/PNWA(proc='WTWb', mass=mass, GM=width/mass), "fb")
    print( "  Xsec(Wb->T->Zt) = ", 1000*XS_NWA(mass, cw, mode='WT')*BRZ/PNWA(proc='WTZt', mass=mass, GM=width/mass), "fb")
    print( "  Xsec(Wb->T->Ht) = ", 1000*XS_NWA(mass, cw, mode='WT')*BRH/PNWA(proc='WTHt', mass=mass, GM=width/mass), "fb")
    print( "  Xsec(Zt->T->Zt) = ", 1000*XS_NWA(mass, cw, mode='ZT')*BRZ/PNWA(proc='ZTZt', mass=mass, GM=width/mass), "fb")
    print( "  Xsec(Zt->T->Ht) = ", 1000*XS_NWA(mass, cw, mode='ZT')*BRH/PNWA(proc='ZTHt', mass=mass, GM=width/mass), "fb")
    print( "  Xsec Uncertianty: (up) ", 100*XSUncertainty(mass)[0], "%, (down) ", 100*XSUncertainty(mass)[1], "%" )

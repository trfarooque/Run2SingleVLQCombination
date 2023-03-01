#!/usr/bin/perl
use strict;
use warnings;

###
#
# Script to take output from quickFit and make
# NP file in format needed for TREx-fitter.
#
# joseph.haley@cern.ch
###

my $input_quickFit_file;
my $output_TREx_file;


sub usage(){ # Fucntion to print usage info
    print
"Usage:
  $0 <input file> [<output file>]
Required args:
  <input file> = file from quickFit with NP info
Optional args:
  <output file> = file created with NP info in format needed for TREx-fitter (default: trex_<input file>).
";
}


### Parse command line args:

if ($#ARGV < 0){
    usage();
    exit(0);
}else{
    $input_quickFit_file = $ARGV[0];
}
if ($#ARGV < 1){
    $output_TREx_file = "trex_$input_quickFit_file";
}else{
    $output_TREx_file = $ARGV[1];
}

print "Input quickFit file: $input_quickFit_file\n";
print "Output TRex file: $output_TREx_file\n";


### Collect NP data from quickFit file:

open(my $infile, '<', $input_quickFit_file) or die "Could not open '$input_quickFit_file' $!\n";

my $n = 0;
my @name;
my @value;
my @sigma;
 
while (my $line = <$infile>) {
  chomp $line;

  # We want to find and capture info from the lines with the format:
  #     mu_signal  	  =  <value>	 +/-  <sigma>	(limited)
  #     alpha_*  	  =  <value>	 +/-  <sigma>	(limited)
  #     gamma_*  	  =  <value>	 +/-  <sigma>	(limited)
  #     *_BKGNF_*  	  =  <value>	 +/-  <sigma>	(limited)
  # Eg:
  #    mu_signal    			= 1    +/-  0.121597  (limited)
  #    alpha_EG_RESOLUTION_ALL   	= 0    +/-  0.992969  (limited)
  #    gamma_shape_stat_WTHt-M16K050_SPT_OSML_2l_CR1_bin_0       = 1    +/-  0.240579  (limited)
  #    SPT_OSML_BKGNF_2l_z_hf    	= 1    +/-  0.121597  (limited)
  # And convert them to this:
  #    mu_signal    			1    +0.121597  -0.121597
  #    EG_RESOLUTION_ALL   		0    +0.992969 -0.992969
  #    gamma_shape_stat_WTHt-M16K050_SPT_OSML_2l_CR1_bin_0       1    +0.240579 -0.240579
  #    SPT_OSML_BKGNF_2l_z_hf     	1    +0.121597  -0.121597
      

  if($line =~ m#(mu_signal)\s+\=\s+([-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]*)?)\s+(\+/-)\s+([-+]?[0-9]*\.?[0-9]+([eE][+-]?[0-9]*)?)\s*\(limited\)# ){
      #    mu_signal    			= 1    +/-  0.121597  (limited)
      
      push @name, $1;
      push @value, $2;
      push @sigma, $5;

  }elsif($line =~ m#alpha_([\w\-]+)\s+\=\s+([-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]*)?)\s+(\+/-)\s+([-+]?[0-9]*\.?[0-9]+([eE][+-]?[0-9]*)?)\s*\(limited\)# ){
      #     alpha_*  	  =  <value>	 +/-  <sigma>	(limited)
      # and the name is what comes after the "alpha_"
      push @name, $1;
      push @value, $2;
      push @sigma, $5;

  }elsif($line =~ m#(gamma_[\w\-]+)\s+\=\s+([-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]*)?)\s+(\+/-)\s+([-+]?[0-9]*\.?[0-9]+([eE][+-]?[0-9]*)?)\s*\(limited\)# ){
      #     gamma_*  	  =  <value>	 +/-  <sigma>	(limited)
      # and the name is the gamma_*

      
      push @name, $1;
      push @value, $2;
      push @sigma, $5;

  }elsif($line =~ m#([\w\-]+_BKGNF_[\w\-]+)\s+\=\s+([-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]*)?)\s+(\+/-)\s+([-+]?[0-9]*\.?[0-9]+([eE][+-]?[0-9]*)?)\s*\(limited\)# ){
      #     *_BKGNP_*  	  =  <value>	 +/-  <sigma>	(limited)
      # and the name is the *_BKGNF_*
      
      push @name, $1;
      push @value, $2;
      push @sigma, $5;

  }
}

close($infile);

### Testing:
#print "@name \n";
#print "@value \n";
#print "@sigma \n";

### Make NP file for TREx-fitter

open(my $outfile, '>', $output_TREx_file) or die "Could not open '$output_TREx_file' $!\n";

# Required first line of output file
print $outfile "NUISANCE_PARAMETERS\n";

# Print lines with NP info in TREx format:
#     <name>  <value>  +<sigma>  -<sigma>
# Eg: EL_SF_ID 0.0560168 +0.99083 -0.99083

for (my $i=0; $i <= $#name; $i++){
    print $outfile "$name[$i] $value[$i] +$sigma[$i] -$sigma[$i]\n"
}

close($outfile);


import os
import sys
import json
import numpy as np
# Third-party library imports for data analysis and option parsing
from argparse import ArgumentParser
# Importing utility functions from a custom module
from Utils import *

# Define constants for file paths and patterns to avoid hardcoding within the code
DEFAULT_LIMITS_FILE = 'ALL_LIMITS.json'

def main():
    # Parse command line arguments
    parser = ArgumentParser(description="Utility for handling limit calculations and visualizations.")
    parser.add_argument("--InputDir",
                        help="location of the limit files",
                        required=True)
    parser.add_argument("--Config",
                        help="",
                        default="SPT_COMBINED")
    parser.add_argument("--renewLimits",
                        help='Set this flag to renew limits',
                        action='store_true',
                        default=False)
    parser.add_argument("--LimitsFile",
                        help="JSON file containing all limits",
                        default=DEFAULT_LIMITS_FILE)
    parser.add_argument("--do1DLimits",
                      help='Set this flag to redraw XS Limits',
                      action='store_true',
                      default=False)
    parser.add_argument("--do2DLimits",
                        help='Set this flag to redraw generalized Limits',
                        action='store_true',
                        default=False)
    parser.add_argument("--do2DMassLimits",
                        help='Set this flag to redraw generalized Limits',
                        action='store_true',
                        default=False)
    
    options = parser.parse_args()

    # Extract options
    input_dir = options.InputDir
    config = options.Config
    renew_limits = options.renewLimits
    limits_file = options.LimitsFile
    do_1d_limits = options.do1DLimits
    do_2d_limits_contour = options.do2DLimits
    do_2d_mass_limits = options.do2DMassLimits

    # Renew limits if the corresponding flag is set
    limits_file = input_dir + '/' + config + '_' +limits_file
    if renew_limits:
        limit_map_all, fails = LimitMapMaker(Loc=input_dir, Cfg=config)
        print(fails)
        with open(limits_file, "w") as file:
            json.dump(limit_map_all, file)
    else:
        # Load existing limits from file
        with open(limits_file, 'r') as file:
            limit_map_all = json.load(file)

    if do_1d_limits:
        for k in np.arange(0.1, 1., .1):
            k = round(k, 2)
            XSLimitPlotter(limit_map_all, k=k, brw=0.5, plotnametag=config, plotsubdir='')
            XSLimitPlotter(limit_map_all, k=k, brw=0.0, plotnametag=config, plotsubdir='')

    if do_2d_limits_contour:
        for brw in np.arange(0., 1.1, .1):
            brw = round(brw, 2)
            KappaLimitPlotter(limit_map_all, brw=brw, plotnametag = config, plotsubdir = '', dm = 20.)

    # Generate 2D mass limits contour if the corresponding flag is set
    if do_2d_mass_limits:
        MassLimitsPlotter(limit_map_all, plotnametag=config, plotsubdir="", limit_type='obs')
        MassLimitsPlotter(limit_map_all, plotnametag=config, plotsubdir="", limit_type='exp')

if __name__ == "__main__":
    main()

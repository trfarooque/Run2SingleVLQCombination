#!/bin/bash

quickAsimov -x asimov_HTZT.xml -w combined -m ModelConfig -d asimovData
quickAsimov -x asimov_OSML.xml -w combined -m ModelConfig -d asimovData
quickAsimov -x asimov_combined.xml -w combWS -m ModelConfig -d combData

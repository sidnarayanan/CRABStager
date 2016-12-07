A simple tool to stage out output from CRAB3 that is stuck in 'transferring' state. Two environments are needed: one to catalog CRAB jobs (set up CMSSW and CRAB), and another to do gfal-copy (CMSSW interferes with the gfal libraries).

In the CMSSW environment:

```
# ./collectPFNs.py --subdir /path/to/CRAB/submission/directory/ --outdir /path/to/task/output/
./collectPFNs.py --subdir /afs/cern.ch/user/s/snarayan/private/CMSSW_8_0_20/src/PandaProd/Ntupler/test/Submission/crab_SingleElectron_Run2016E-23Sep2016-v1/ --outdir /afs/cern.ch/user/s/snarayan/eos/cms/store/group/phys_exotica/monotop/pandaprod/v_8022_2_snarayan/SingleElectron/SingleElectron_Run2016E-23Sep2016-v1/161206_231050/
```

This will dump to screen a bunch of `gfal-copy` commands for jobs that are in 'transferring' state and the output does not yet exist in `--outdir`. Simply run these commands in the second environment and watch your output appear! (Although gfal-copy fails a bunch). The default behavior is not to overwrite files that exist, so there should be no danger of losing data.

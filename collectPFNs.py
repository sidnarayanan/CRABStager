#!/usr/bin/env python

import subprocess
import re
import json
import argparse
from sys import argv
import pprint 
from StringIO import StringIO
import os

class Job():
  def __init__(self,jid):
    self.jid=jid
    self.site=None
    self.pfn=None
    self.lfn=None

parser = argparse.ArgumentParser(description='determine which outputs are stuck transferring')
parser.add_argument('--outdir',metavar='outdir',type=str)
parser.add_argument('--subdir',metavar='subdir',type=str)
args = parser.parse_args()

transferring = [] # list of Jobs

print 'Requesting summary'
# determine stuck jobs
proc_crabStatus = subprocess.Popen(['crab','status','--long',args.subdir],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
out_crabStatus,err_crabStatus = proc_crabStatus.communicate()
state=0
for line in out_crabStatus.split('\n'):
  if 'Most Recent Site' in line:
    state=1
    continue
  if 'Summary' in line or line.strip()=='':
    state=0
    continue
  if state==1:
    ll = line.split()
    if ll[1]=='transferring':
      j = Job(int(ll[0]))
      j.site=ll[2].strip()
      if 'T1' in j.site:
        j.site += '_Disk'
      transferring.append(j)

#pprint.pprint(transferring)

# request logs for those jobs
jidsToGet = []
for job in transferring:
  fpath = args.subdir+'/results/job_out.%i.0.txt'%(job.jid)
  if not os.path.exists(fpath): # log doesn't exist
    jidsToGet.append(job.jid)
jobidstr = ','.join([str(x) for x in jidsToGet])
print 'Requesting logs for %i jobs'%(len(jidsToGet))
proc_crabLog = subprocess.Popen(['crab','getlog','--short','--dir',args.subdir,'--jobids',jobidstr],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
out_crabLog,err_crabLog = proc_crabLog.communicate()

print 'Parsing logs'
# parse logs to determine lfns
for job in transferring:
  fpath = args.subdir+'/results/job_out.%i.0.txt'%(job.jid)
  flog = open(fpath)
  for line in flog:
    if 'JOB_CMSSite' in line and job.site==None: # why?
      sitename = re.sub('["\s]','',line.strip().split('=')[-1])
      if 'T1' in sitename:
        sitename += '_Disk'
      job.site = sitename
    if 'source_lfn' in line:
      lfn = re.sub("[',\s]","",line.strip().split(':')[-1])
      job.lfn = lfn

print 'Converting LFNs'
# determine the pfns
for job in transferring:
  url = 'https://cmsweb.cern.ch/phedex/datasvc/json/prod/lfn2pfn?lfn=%s&node=%s&protocol=srmv2'%(job.lfn,job.site)
  try:
    proc_phedexPFN = subprocess.Popen(['curl','-k',url],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    out_phedexPFN,err_phedexPFN = proc_phedexPFN.communicate()
    io = StringIO(out_phedexPFN)
    payload = json.load(io)['phedex']
    pfn = payload['mapping'][0]['pfn'] # hopefully exactly one?
    job.pfn = pfn
  except:
    print url

# check if file is not there, and if not, then print as a candidate for copying
for job in transferring:
  if job.pfn==None:
    # something failed
    continue
  if 'failed' in job.pfn:
    # not valid output
    continue
  adddir = job.jid/1000
  outpath = '%s/%.4i/%s'%(args.outdir,adddir,job.pfn.split('/')[-1])
  if not os.path.exists(outpath):
    print 'gfal-copy %s %s/%.4i/'%(job.pfn,args.outdir,adddir)
#  else:
#    print outpath














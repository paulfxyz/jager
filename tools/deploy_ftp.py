#!/usr/bin/env python3
"""Upload ./jager to SiteGround over FTPS/FTP. Usage:
   JAGER_FTP_HOST=gnldm1132.siteground.biz JAGER_FTP_USER='ftp255@jager.social' JAGER_FTP_PASS='...' python3 deploy_ftp.py [remote_dir=public_html]
"""
import ftplib, os, sys
host=os.environ['JAGER_FTP_HOST']; user=os.environ['JAGER_FTP_USER']; pw=os.environ['JAGER_FTP_PASS']
remote=sys.argv[1] if len(sys.argv)>1 else '.'
src=os.path.join(os.path.dirname(os.path.abspath(__file__)),'jager')
try:
    f=ftplib.FTP_TLS(host,timeout=30); f.login(user,pw); f.prot_p()
except Exception as e:
    print('FTPS failed, trying plain FTP:',e); f=ftplib.FTP(host,timeout=30); f.login(user,pw)
print(f.pwd(), f.nlst()[:10])
def mk(d):
    try: f.mkd(d)
    except ftplib.error_perm: pass
if remote not in ('.',''): mk(remote); f.cwd(remote)
for root,dirs,files in os.walk(src):
    rel=os.path.relpath(root,src); 
    if rel!='.': mk(rel.replace(os.sep,'/'))
    for n in files:
        p=os.path.join(root,n); r=(n if rel=='.' else rel.replace(os.sep,'/')+'/'+n)
        with open(p,'rb') as fh: f.storbinary('STOR '+r,fh)
        print('uploaded',r)
f.quit()

#!/usr/bin/python3.5
# coding: utf-8

import os
from pystemd.systemd1 import Unit
import time
import sys
import subprocess
#import string
import urllib.parse
import urllib.request

hosts_file = '/etc/hosts'
#confLUA="/etc/fusionpbx/config.lua"
#confPHP="/etc/fusionpbx/config.php"
# time settings to stop / start (in seconds) FreeSwitch:
time_stop = 150
time_start = 15
# DB settings:
localDB = '127.0.0.1'
remoteDB = 'REMOTE_DB_IP_ADDRESS'
# server names settings:
local_serv = 'LOCAL_SERVER_NAME'
remote_serv = 'REMOTE_SERVER_NAME'
db_host = 'YOUR_DB_HOST'
# telegram variables:
token = 'TELEGRAM_TOKEN'
tel_addr = 'https://api.telegram.org/bot'
chat_id = '-CHAT_ID'
# emojies:
EM_FIRE = u'\U0001F525'
EM_FIRECAR = u'\U0001F692'
EM_BAKLAJAN = u'\U0001F346'
EM_SCREAM = u'\U0001F631'
EM_OK = u'\U0001F44C'


def send_to_telegram(text):
   url = tel_addr + token + '/'
   message = urllib.parse.urlencode(
       {'chat_id': format(chat_id),
        'text': text.encode('utf-8', 'strict'),
        'disable_web_page_preview': True})
   response = urllib.request.urlopen(url + 'sendMessage', message.encode('utf-8'))


def fsStartStop(op):
   wait_flag = 1
   fs = Unit(b'freeswitch.service')
   fs.load()
   if op == 'stop':
       #print("FreeSwitch before stop state:",fs.Unit.ActiveState)
       while wait_flag:
           fs.Unit.Stop('replace')
           time.sleep(time_stop)
           wait_flag = 0
       if fs.Unit.ActiveState.decode() in {'inactive', 'failed'}:
           message = '{scream} {fire} Local DB on {local_serv} is not responding. DB at {remote_serv} is not
responding from {local_serv} server to !!! Stopping FreeSwitch at {local_serv}...!'.format(scream = EM_SCREA
M, fire = EM_FIRE, local_serv = local_serv, remote_serv = remote_serv)
           send_to_telegram(message)
       elif fs.Unit.ActiveState.decode() not in {'inactive', 'failed'}:
           message = '{fire} {scream} {fire} ALARM! Local DB on {local_serv} is not responding. DB at {remot
e_serv} is not responding from {local_serv} server to !!! Failed to stop FreeSwitch at {local_serv}! Trafic w
ill go there!'.format(scream = EM_SCREAM, fire = EM_FIRE, local_serv = local_serv, remote_serv = remote_serv)
           send_to_telegram(message)
   if op == 'start':
       #print("FreeSwitch before stop state:",fs.Unit.ActiveState)
       while wait_flag:
           fs.Unit.Start('replace')
           time.sleep(time_start)
           wait_flag = 0
       if fs.Unit.ActiveState.decode() in {'active'}:
           message = '{0} {1} --> {2} Freeswitch started at {local_serv}'.format(EM_FIRE, EM_FIRECAR, EM_BAK
LAJAN, local_serv = local_serv)
           send_to_telegram(message)
       if fs.Unit.ActiveState.decode() not in {'active'}:
           message = '{scream} {fire} Failed to start FreeSwitch at {local_serv}!'.format(scream = EM_SCREAM
, fire = EM_FIRE, local_serv = local_serv)
           send_to_telegram(message)


def checkFSstate(op):
   fs = Unit(b'freeswitch.service')
   fs.load()
   if op == 'start':
       if fs.Unit.ActiveState.decode() not in {'active'}:
    #       print("need to start")
           fsStartStop('start')
   elif op == 'stop':
       if fs.Unit.ActiveState.decode() not in {'inactive', 'failed'}:
   #        print("need to stop")
           fsStartStop('stop')


def changeIP(ips):
#    ip_old, ip_new = [i for i in ips]
   replace_host = '%s %s' %(ips[0], db_host)
   old_host = '%s %s' %(ips[1], db_host)
   file_handle = open(hosts_file, 'r')
   file_string = file_handle.read()
   file_handle.close()
   if old_host in file_string:
   #        print("Found")
           file_string = file_string.replace(old_host, replace_host)
           file_handle = open(hosts_file, 'w')
           file_handle.write(file_string)
           file_handle.close()
   message = '{0} {1} --> {2}. {local_serv}. Changed /etc/hosts from {old} to {new}.'.format(EM_FIRE, EM_FIR
ECAR, EM_BAKLAJAN, old = ips[1], new = ips[0], local_serv = local_serv)     
   send_to_telegram(message)
   return


def checkConfig(dbs):
       # LUA config:
       #if (  
       #    'database.switch = "pgsql://hostaddr=%s"'%addr not in open(confLUA).read() and
       #    "$db_host = '%s'"%addr not in open(confPHP).read()
       #    ):
       #    print("DB at %s is ok. Not found %s in config LUA" %(addr, addr))
       #ip_to_check, db_host = [i for i in dbs]
       ip_to_check =  dbs[0]
    #   print(dbs)
    #   print(ip_to_check)
       if "%s %s" %(ip_to_check, db_host) not in open(hosts_file).read():
           # DB at host is ok, configs don't corresponding to the DB state,
           # change config and check freeswitch (and run it if necessary)
          # print("not found in hosts1")
           changeIP(dbs)
           checkFSstate('start')
           return
       else:
           # DB at host is ok, config are corresponding to the DB state,
           # check freeswitch and run it if necessary
     #      print("DB at %s is ok. Found %s hosts file" %(ip_to_check, ip_to_check))
           checkFSstate('start')
           return


def checkDB(addr):
   ip_local, ip_remote = [i for i in addr]
   # local postgre status:
   ps_local = subprocess.run(['/usr/bin/pg_isready', '-h', ip_local], stdout=subprocess.PIPE)
   ps_local = ps_local.stdout.decode('utf-8').rstrip()
   if '%s:5432 - accepting connections'%ip_local == ps_local:
       # Local DB is ok
     #  print("Local DB is ok")
       # Check configs:
       checkConfig(addr)
       sys.exit()
   # remote postgre status:
   ps_remote = subprocess.run(['/usr/bin/pg_isready', '-h', ip_remote], stdout=subprocess.PIPE)
   ps_remote = ps_remote.stdout.decode('utf-8').rstrip()
   if '%s:5432 - accepting connections'%ip_remote == ps_remote:
       # Remote DB is ok
    #   print("Remote DB is ok")
       # Check configs:
       #checkConfig(addr.reverse())
       checkConfig(addr[::-1])
       sys.exit()
   if ('accepting connection' not in ps_local) and ('accepting connection' not in ps_remote):
       # DB at local host and remote is not responding, shut down FreeSwitch:
   #    print("Local and remote DB is not ok")
       checkFSstate('stop')


if __name__ == '__main__':
   dbs = []
   dbs.extend((localDB, remoteDB))
   checkDB(dbs)

# FusionPBX-clustering
FusionPBX clustering by checking the DB state
I had an issue to create script to check DB state on the local server and turn on or turn off FusionPBX. 
In the project I had two FusionPBX that had master-master replication of their DB.
So, if one DB is down, I had to turn off FusionPBX at this server and informabout that by Telegram.

What need to do at the server:
1) cat /etc/hosts                           
127.0.0.1 localhost
127.0.0.1 YOUR_LOCAL_DB_HOST
2) sudo vim /etc/fusionpbx/config.lua
       --database.system = "pgsql://hostaddr=127.0.0.1 port=5432 dbname=fusionpbx user=fusionpbx password=PASSWORD options=''";
       database.system = "pgsql://host=YOUR_LOCAL_DB_HOST port=5432 dbname=fusionpbx user=fusionpbx password=PASSWORD options=''";
       --database.switch = "pgsql://hostaddr=127.0.0.1 port=5432 dbname=freeswitch user=fusionpbx password=PASSWORD options=''";
       database.switch = "pgsql://host=YOUR_LOCAL_DB_HOST port=5432 dbname=freeswitch user=fusionpbx password=PASSWORD options=''";
3) sudo vim /etc/fusionpbx/config.php
$db_host = 'YOUR_DB_HOST'; //set the host only if the database is not local
4) crontab:
# check local and remote db and change /etc/hosts:
*/5 * * * * root /YOUR_DESTINATION_TO_THE_SCRIPT




from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from datetime import datetime
from airflow.decorators import dag, task
import os 
import sys
import tsslogging
import time 
import subprocess
import shutil
import glob

sys.dont_write_bytecode = True
######################################################USER CHOSEN PARAMETERS ###########################################################
default_args = {
 'owner': 'Sebastian Maurice',  # <<< ******** change as needed 
 'brokerhost' : '127.0.0.1',  # <<<<***************** THIS WILL ACCESS LOCAL KAFKA - YOU CAN CHANGE TO CLOUD KAFKA HOST
 'brokerport' : '9092',     # <<<<***************** LOCAL AND CLOUD KAFKA listen on PORT 9092
 'cloudusername' : '',  # <<<< --THIS WILL BE UPDATED FOR YOU IF USING KAFKA CLOUD WITH API KEY  - LEAVE BLANK
 'cloudpassword' : '',  # <<<< --THIS WILL BE UPDATED FOR YOU IF USING KAFKA CLOUD WITH API SECRET - LEAVE BLANK   
 'solutionname': '_mysolution_',   # <<< *** DO NOT MODIFY - THIS WILL BE AUTOMATICALLY UPDATED
 'solutiontitle': 'My Solution Title', # <<< *** Provide a descriptive title for your solution
 'solutionairflowport' : '-1', # << If -1, TSS will choose a free port randonly, or set this to a fixed number
 'solutionexternalport' : '-1', # << If -1, TSS will choose a free port randonly, or set this to a fixed number
 'solutionvipervizport' : '-1', # << If -1, TSS will choose a free port randonly, or set this to a fixed number   
 'description': 'This is an awesome real-time solution built by TSS',   # <<< *** Provide a description of your solution
 'HTTPADDR' : 'https://',
 'COMPANYNAME' : 'My company',       
 'WRITELASTCOMMIT' : '0',   ## <<<<<<<<< ******************** FOR DETAILS ON BELOW PARAMETER SEE: https://tml.readthedocs.io/en/latest/viper.html
 'NOWINDOWOVERLAP' : '0',
 'NUMWINDOWSFORDUPLICATECHECK' : '5',
 'DATARETENTIONINMINUTES' : '30',
 'USEHTTP' : '0',
 'ONPREM' : '0',
 'WRITETOVIPERDB' : '0',
 'VIPERDEBUG' : '2',
 'MAXOPENREQUESTS' : '10',
 'LOGSTREAMTOPIC' : 'viperlogs',
 'LOGSTREAMTOPICPARTITIONS' : '1',
 'LOGSTREAMTOPICREPLICATIONFACTOR' : '3',
 'LOGSENDTOEMAILS' : '',
 'LOGSENDTOEMAILSSUBJECT' : '[VIPER]',
 'LOGSENDTOEMAILFOOTER' : 'This e-mail is auto-generated by Transactional Machine Learning (TML) Technology Binaries: Viper, HPDE or Viperviz.  For more information please contact your TML Administrator.  Or, e-mail info@otics.ca for any questions or concerns regarding this e-mail. If you received this e-mail in error please delete it and inform your TML Admin or e-mail info@otics.ca, website: https://www.otics.ca.  Thank you for using TML Data Stream Processing and Real-Time Transactional Machine Learning technologies.',
 'LOGSENDINTERVALMINUTES' : '500',
 'LOGSENDINTERVALONLYERROR' : '1',
 'MAXTRAININGROWS' : '300',
 'MAXPREDICTIONROWS' : '50',
 'MAXPREPROCESSMESSAGES' : '5000',
 'MAXPERCMESSAGES' : '5000',
 'MAXCONSUMEMESSAGES' : '5000',
 'MAXVIPERVIZROLLBACKOFFSET' : '',
 'MAXVIPERVIZCONNECTIONS' : '10',
 'MAXURLQUERYSTRINGBYTES' : '10000',
 'MYSQLMAXLIFETIMEMINUTES' : '4',
 'MYSQLMAXCONN' : '4',
 'MYSQLMAXIDLE' : '10',
 'SASLMECHANISM' : 'PLAIN',
 'MINFORECASTACCURACY' : '55',
 'COMPRESSIONTYPE' : 'gzip',
 'MAILSERVER' : '', #i.e.  smtp.broadband.rogers.com,
 'MAILPORT' : '', #i.e. 465,
 'FROMADDR' : '',
 'SMTP_USERNAME' : '',
 'SMTP_PASSWORD' : '',
 'SMTP_SSLTLS' : 'true',
 'SSL_CLIENT_CERT_FILE' : 'client.cer.pem',
 'SSL_CLIENT_KEY_FILE' : 'client.key.pem', 
 'SSL_SERVER_CERT_FILE' : 'server.cer.pem',  
 'KUBERNETES' : '0',
}

############################################################### DO NOT MODIFY BELOW ####################################################
# Instantiate your DAG
@dag(dag_id="tml_system_step_1_getparams_dag", default_args=default_args, tags=["tml_system_step_1_getparams_dag"], schedule=None, catchup=False)
def tmlparams():
    # Define tasks
    def empty():
        pass
dag = tmlparams()

    
def reinitbinaries(sname):  
    pywindowfiles=glob.glob("/tmux/pythonwindows_*") 
    
    for f in pywindowfiles: 
        try:
          with open(f, 'r', encoding='utf-8') as file: 
            data = file.readlines() 
            for d in data:          
              if d != "":             
                d=d.rstrip()            
                v=subprocess.call(["tmux", "kill-window", "-t", "{}".format(d)])   
          os.remove(f)        
        except Exception as e:
         print("ERROR=",e)   
         pass

    vizwindowfiles=glob.glob("/tmux/vipervizwindows_*") 
    
    for f in vizwindowfiles: 
        try:
          with open(f, 'r', encoding='utf-8') as file: 
             data = file.readlines()  
             for d in data:
                 d=d.rstrip()
                 dsw = d.split(",")[0]             
                 dsp = d.split(",")[1]
                 if dsw != "":  
                   subprocess.call(["tmux", "kill-window", "-t", "{}".format(dsw)])        
                   v=subprocess.call(["kill", "-9", "$(lsof -i:{} -t)".format(dsp)])
                   time.sleep(1) 
          os.remove(f)                    
        except Exception as e:
         pass
       
    # copy folders
    shutil.copytree("/tss_readthedocs", "/{}".format(sname),dirs_exist_ok=True)
    #remove local logs
    os.remove('/dagslocalbackup/logs.txt')    
        
def updateviperenv():
    # update ALL
    os.environ['tssbuild']="0"
    os.environ['tssdoc']="0"

    cloudusername = ""
    cloudpassword = ""
    
    if 'KAFKACLOUDUSERNAME' in os.environ:
          cloudusername = os.environ['KAFKACLOUDUSERNAME']
    if 'KAFKACLOUDPASSWORD' in os.environ:
          cloudpassword = os.environ['KAFKACLOUDPASSWORD']

    if '127.0.0.1' in default_args['brokerhost']:
      cloudusername = ""
      cloudpassword = ""
        
    filepaths = ['/Viper-produce/viper.env','/Viper-preprocess/viper.env','/Viper-preprocess-pgpt/viper.env','/Viper-preprocess2/viper.env','/Viper-ml/viper.env','/Viper-predict/viper.env','/Viperviz/viper.env']
    for mainfile in filepaths:
     with open(mainfile, 'r', encoding='utf-8') as file: 
       data = file.readlines() 
     r=0 
     for d in data:  
       if d[0] == '#':
          r += 1  
          continue 
        
       if 'KAFKA_CONNECT_BOOTSTRAP_SERVERS' in d: 
         if default_args['brokerport'] == '':
           data[r] = "KAFKA_CONNECT_BOOTSTRAP_SERVERS={}\n".format(default_args['brokerhost'])    
         else:       
           data[r] = "KAFKA_CONNECT_BOOTSTRAP_SERVERS={}:{}\n".format(default_args['brokerhost'],default_args['brokerport'])
       if 'CLOUD_USERNAME' in d: 
         data[r] = "CLOUD_USERNAME={}\n".format(cloudusername)
       if 'CLOUD_PASSWORD' in d: 
         data[r] = "CLOUD_PASSWORD={}\n".format(cloudpassword)                
       if 'WRITELASTCOMMIT' in d: 
         data[r] = "WRITELASTCOMMIT={}\n".format(default_args['WRITELASTCOMMIT'])
       if 'NOWINDOWOVERLAP' in d: 
         data[r] = "NOWINDOWOVERLAP={}\n".format(default_args['NOWINDOWOVERLAP'])
       if 'NUMWINDOWSFORDUPLICATECHECK' in d: 
         data[r] = "NUMWINDOWSFORDUPLICATECHECK={}\n".format(default_args['NUMWINDOWSFORDUPLICATECHECK'])
       if 'USEHTTP' in d: 
         data[r] = "USEHTTP={}\n".format(default_args['USEHTTP'])
       if 'ONPREM' in d: 
         data[r] = "ONPREM={}\n".format(default_args['ONPREM'])
       if 'WRITETOVIPERDB' in d: 
         data[r] = "WRITETOVIPERDB={}\n".format(default_args['WRITETOVIPERDB'])
       if 'VIPERDEBUG' in d: 
         data[r] = "VIPERDEBUG={}\n".format(default_args['VIPERDEBUG'])
       if 'MAXOPENREQUESTS' in d: 
         data[r] = "MAXOPENREQUESTS={}\n".format(default_args['MAXOPENREQUESTS'])
       if 'LOGSTREAMTOPIC' in d: 
         data[r] = "LOGSTREAMTOPIC={}\n".format(default_args['LOGSTREAMTOPIC'])
       if 'LOGSTREAMTOPICPARTITIONS' in d: 
         data[r] = "LOGSTREAMTOPICPARTITIONS={}\n".format(default_args['LOGSTREAMTOPICPARTITIONS'])
       if 'LOGSTREAMTOPICREPLICATIONFACTOR' in d: 
         data[r] = "LOGSTREAMTOPICREPLICATIONFACTOR={}\n".format(default_args['LOGSTREAMTOPICREPLICATIONFACTOR'])
       if 'LOGSENDTOEMAILS' in d: 
         data[r] = "LOGSENDTOEMAILS={}\n".format(default_args['LOGSENDTOEMAILS'])
       if 'LOGSENDTOEMAILSSUBJECT' in d: 
         data[r] = "LOGSENDTOEMAILSSUBJECT={}\n".format(default_args['LOGSENDTOEMAILSSUBJECT'])
       if 'LOGSENDTOEMAILFOOTER' in d: 
         data[r] = "LOGSENDTOEMAILFOOTER={}\n".format(default_args['LOGSENDTOEMAILFOOTER'])
       if 'LOGSENDINTERVALMINUTES' in d: 
         data[r] = "LOGSENDINTERVALMINUTES={}\n".format(default_args['LOGSENDINTERVALMINUTES'])
       if 'LOGSENDINTERVALONLYERROR' in d: 
         data[r] = "LOGSENDINTERVALONLYERROR={}\n".format(default_args['LOGSENDINTERVALONLYERROR'])
       if 'MAXTRAININGROWS' in d: 
         data[r] = "MAXTRAININGROWS={}\n".format(default_args['MAXTRAININGROWS'])
       if 'MAXPREDICTIONROWS' in d: 
         data[r] = "MAXPREDICTIONROWS={}\n".format(default_args['MAXPREDICTIONROWS'])
       if 'MAXPREPROCESSMESSAGES' in d: 
         data[r] = "MAXPREPROCESSMESSAGES={}\n".format(default_args['MAXPREPROCESSMESSAGES'])
       if 'MAXPERCMESSAGES' in d: 
         data[r] = "MAXPERCMESSAGES={}\n".format(default_args['MAXPERCMESSAGES'])
       if 'MAXCONSUMEMESSAGES' in d: 
         data[r] = "MAXCONSUMEMESSAGES={}\n".format(default_args['MAXCONSUMEMESSAGES'])
       if 'MAXVIPERVIZROLLBACKOFFSET' in d: 
         data[r] = "MAXVIPERVIZROLLBACKOFFSET={}\n".format(default_args['MAXVIPERVIZROLLBACKOFFSET'])
       if 'MAXVIPERVIZCONNECTIONS' in d: 
         data[r] = "MAXVIPERVIZCONNECTIONS={}\n".format(default_args['MAXVIPERVIZCONNECTIONS'])
       if 'MAXURLQUERYSTRINGBYTES' in d: 
         data[r] = "MAXURLQUERYSTRINGBYTES={}\n".format(default_args['MAXURLQUERYSTRINGBYTES'])
       if 'MYSQLMAXLIFETIMEMINUTES' in d: 
         data[r] = "MYSQLMAXLIFETIMEMINUTES={}\n".format(default_args['MYSQLMAXLIFETIMEMINUTES'])
       if 'MYSQLMAXCONN' in d: 
         data[r] = "MYSQLMAXCONN={}\n".format(default_args['MYSQLMAXCONN'])
       if 'MYSQLMAXIDLE' in d: 
         data[r] = "MYSQLMAXIDLE={}\n".format(default_args['MYSQLMAXIDLE'])
       if 'SASLMECHANISM' in d: 
         data[r] = "SASLMECHANISM={}\n".format(default_args['SASLMECHANISM'])
       if 'MINFORECASTACCURACY' in d: 
         data[r] = "MINFORECASTACCURACY={}\n".format(default_args['MINFORECASTACCURACY'])
       if 'COMPRESSIONTYPE' in d: 
         data[r] = "COMPRESSIONTYPE={}\n".format(default_args['COMPRESSIONTYPE'])
       if 'MAILSERVER' in d: 
         data[r] = "MAILSERVER={}\n".format(default_args['MAILSERVER'])
       if 'MAILPORT' in d: 
         data[r] = "MAILPORT={}\n".format(default_args['MAILPORT'])
       if 'FROMADDR' in d: 
         data[r] = "FROMADDR={}\n".format(default_args['FROMADDR'])
       if 'SMTP_USERNAME' in d: 
         data[r] = "SMTP_USERNAME={}\n".format(default_args['SMTP_USERNAME'])
       if 'SMTP_PASSWORD' in d: 
         data[r] = "SMTP_PASSWORD={}\n".format(default_args['SMTP_PASSWORD'])
       if 'SMTP_SSLTLS' in d: 
         data[r] = "SMTP_SSLTLS={}\n".format(default_args['SMTP_SSLTLS'])
       if 'SSL_CLIENT_CERT_FILE' in d: 
         data[r] = "SSL_CLIENT_CERT_FILE={}\n".format(default_args['SSL_CLIENT_CERT_FILE'])
       if 'SSL_CLIENT_KEY_FILE' in d: 
         data[r] = "SSL_CLIENT_KEY_FILE={}\n".format(default_args['SSL_CLIENT_KEY_FILE'])
       if 'SSL_SERVER_CERT_FILE' in d: 
         data[r] = "SSL_SERVER_CERT_FILE={}\n".format(default_args['SSL_SERVER_CERT_FILE'])                
       if 'KUBERNETES' in d: 
         data[r] = "KUBERNETES={}\n".format(default_args['KUBERNETES'])                
       if 'COMPANYNAME' in d: 
         data[r] = "COMPANYNAME={}\n".format(default_args['COMPANYNAME'])                

       r += 1
     with open(mainfile, 'w', encoding='utf-8') as file: 
      file.writelines(data)

    subprocess.call("/tmux/starttml.sh", shell=True)
    time.sleep(3)

def getparams(**context):
  args = default_args    
  VIPERHOST = ""
  VIPERPORT = ""
  HTTPADDR = args['HTTPADDR']
  HPDEHOST = ""
  HPDEPORT = ""
  VIPERTOKEN = ""
  HPDEHOSTPREDICT = ""
  HPDEPORTPREDICT = ""

  tsslogging.locallogs("INFO", "STEP 1: Build started") 
    
  sname = args['solutionname']    
  desc = args['description']        
  stitle = args['solutiontitle']    
  
  brokerhost = args['brokerhost']   
  brokerport = args['brokerport'] 
  reinitbinaries(sname)
  updateviperenv()

  with open("/Viper-produce/admin.tok", "r") as f:
    VIPERTOKEN=f.read()

  if VIPERHOST=="":
    with open('/Viper-produce/viper.txt', 'r') as f:
      output = f.read()
      VIPERHOST = output.split(",")[0]
      VIPERPORT = output.split(",")[1]
    with open('/Viper-preprocess/viper.txt', 'r') as f:
      output = f.read()
      VIPERHOSTPREPROCESS = output.split(",")[0]
      VIPERPORTPREPROCESS = output.split(",")[1]    
    with open('/Viper-preprocess2/viper.txt', 'r') as f:
      output = f.read()
      VIPERHOSTPREPROCESS2 = output.split(",")[0]
      VIPERPORTPREPROCESS2 = output.split(",")[1]        
    with open('/Viper-preprocess-pgpt/viper.txt', 'r') as f:
      output = f.read()
      VIPERHOSTPREPROCESSPGPT = output.split(",")[0]
      VIPERPORTPREPROCESSPGPT = output.split(",")[1]        
    with open('/Viper-ml/viper.txt', 'r') as f:
      output = f.read()
      VIPERHOSTML = output.split(",")[0]
      VIPERPORTML = output.split(",")[1]    
    with open('/Viper-predict/viper.txt', 'r') as f:
      output = f.read()
      VIPERHOSTPREDICT = output.split(",")[0]
      VIPERPORTPREDICT = output.split(",")[1]    
    with open('/Hpde/hpde.txt', 'r') as f:
      output = f.read()
      HPDEHOST = output.split(",")[0]
      HPDEPORT = output.split(",")[1]
    with open('/Hpde-predict/hpde.txt', 'r') as f:
      output = f.read()
      HPDEHOSTPREDICT = output.split(",")[0]
      HPDEPORTPREDICT = output.split(",")[1]

  
  if 'CHIP' in os.environ:
     chip = os.environ['CHIP']
     chip = chip.lower()   
  else:   
      chip = 'amd64'
       
  if 'VIPERVIZPORT' in os.environ:
      if os.environ['VIPERVIZPORT'] != '' and os.environ['VIPERVIZPORT'] != '-1':
           vipervizport = int(os.environ['VIPERVIZPORT'])
      else:
           vipervizport=tsslogging.getfreeport()
  else:
           vipervizport=tsslogging.getfreeport()
        
  if default_args['solutionairflowport'] != '-1':
           solutionairflowport = int(default_args['solutionairflowport'])
  else:
           solutionairflowport=tsslogging.getfreeport()

  if default_args['solutionexternalport'] != '-1':
           solutionexternalport = int(default_args['solutionexternalport'])
  else:
           solutionexternalport=tsslogging.getfreeport()
        
  if default_args['solutionvipervizport'] != '-1':
          solutionvipervizport = int(default_args['solutionvipervizport'])
  else:
           solutionvipervizport=tsslogging.getfreeport()

  if 'AIRFLOWPORT' in  os.environ:
      airflowport = os.environ['AIRFLOWPORT']
  else:
      airflowport = tsslogging.getfreeport()

  externalport=VIPERPORT          
  if 'EXTERNALPORT' in  os.environ:
      if os.environ['EXTERNALPORT'] != "-1":  
        externalport = os.environ['EXTERNALPORT']
        
  tss = os.environ['TSS']          
  sd = context['dag'].dag_id 
  task_instance = context['task_instance']
    
  if tss == "1":  
    task_instance.xcom_push(key="{}_SOLUTIONEXTERNALPORT".format(sname),value="_{}".format(solutionexternalport)) 
    task_instance.xcom_push(key="{}_SOLUTIONVIPERVIZPORT".format(sname),value="_{}".format(solutionvipervizport))  
    task_instance.xcom_push(key="{}_SOLUTIONAIRFLOWPORT".format(sname),value="_{}".format(solutionairflowport)) 
  else:
    task_instance.xcom_push(key="{}_SOLUTIONEXTERNALPORT".format(sname),value="_{}".format(os.environ['SOLUTIONEXTERNALPORT'])) 
    task_instance.xcom_push(key="{}_SOLUTIONVIPERVIZPORT".format(sname),value="_{}".format(os.environ['SOLUTIONVIPERVIZPORT']))  
    task_instance.xcom_push(key="{}_SOLUTIONAIRFLOWPORT".format(sname),value="_{}".format(os.environ['SOLUTIONAIRFLOWPORT'])) 
    

  if 'MQTTUSERNAME' in os.environ:
    task_instance.xcom_push(key="{}_MQTTUSERNAME".format(sname),value=os.environ['MQTTUSERNAME'])
  else:
    task_instance.xcom_push(key="{}_MQTTUSERNAME".format(sname),value="")

  if 'MQTTPASSWORD' in os.environ:
    task_instance.xcom_push(key="{}_MQTTPASSWORD".format(sname),value=os.environ['MQTTPASSWORD'])
  else:
    task_instance.xcom_push(key="{}_MQTTPASSWORD".format(sname),value="")

  if 'KAFKACLOUDUSERNAME' in os.environ:
    task_instance.xcom_push(key="{}_KAFKACLOUDUSERNAME".format(sname),value=os.environ['KAFKACLOUDUSERNAME'])
  else:
    task_instance.xcom_push(key="{}_KAFKACLOUDUSERNAME".format(sname),value="")

  if 'KAFKACLOUDPASSWORD' in os.environ:
    task_instance.xcom_push(key="{}_KAFKACLOUDPASSWORD".format(sname),value=os.environ['KAFKACLOUDPASSWORD'])
  else:
    task_instance.xcom_push(key="{}_KAFKACLOUDPASSWORD".format(sname),value="")
    
  task_instance.xcom_push(key="{}_TSS".format(sname),value="_{}".format(tss))  
    
  task_instance.xcom_push(key="{}_EXTERNALPORT".format(sname),value="_{}".format(externalport)) 
  task_instance.xcom_push(key="{}_AIRFLOWPORT".format(sname),value="_{}".format(airflowport)) 
  
  task_instance.xcom_push(key="{}_VIPERVIZPORT".format(sname),value="_{}".format(vipervizport))  
  task_instance.xcom_push(key="{}_VIPERTOKEN".format(sname),value=VIPERTOKEN)
  task_instance.xcom_push(key="{}_VIPERHOST".format(sname),value=VIPERHOST)
  task_instance.xcom_push(key="{}_VIPERPORT".format(sname),value="_{}".format(VIPERPORT))
  task_instance.xcom_push(key="{}_VIPERHOSTPRODUCE".format(sname),value=VIPERHOST)
  task_instance.xcom_push(key="{}_VIPERPORTPRODUCE".format(sname),value="_{}".format(VIPERPORT))
  task_instance.xcom_push(key="{}_VIPERHOSTPREPROCESS".format(sname),value=VIPERHOSTPREPROCESS)
  task_instance.xcom_push(key="{}_VIPERPORTPREPROCESS".format(sname),value="_{}".format(VIPERPORTPREPROCESS))
  task_instance.xcom_push(key="{}_VIPERHOSTPREPROCESS2".format(sname),value=VIPERHOSTPREPROCESS2)
  task_instance.xcom_push(key="{}_VIPERPORTPREPROCESS2".format(sname),value="_{}".format(VIPERPORTPREPROCESS2))

  task_instance.xcom_push(key="{}_VIPERHOSTPREPROCESSPGPT".format(sname),value=VIPERHOSTPREPROCESSPGPT)
  task_instance.xcom_push(key="{}_VIPERPORTPREPROCESSPGPT".format(sname),value="_{}".format(VIPERPORTPREPROCESSPGPT))
    
  task_instance.xcom_push(key="{}_VIPERHOSTML".format(sname),value=VIPERHOSTML)
  task_instance.xcom_push(key="{}_VIPERPORTML".format(sname),value="_{}".format(VIPERPORTML))
  task_instance.xcom_push(key="{}_VIPERHOSTPREDICT".format(sname),value=VIPERHOSTPREDICT)
  task_instance.xcom_push(key="{}_VIPERPORTPREDICT".format(sname),value="_{}".format(VIPERPORTPREDICT))
  task_instance.xcom_push(key="{}_HTTPADDR".format(sname),value=HTTPADDR)
  task_instance.xcom_push(key="{}_HPDEHOST".format(sname),value=HPDEHOST)
  task_instance.xcom_push(key="{}_HPDEPORT".format(sname),value="_{}".format(HPDEPORT))
  task_instance.xcom_push(key="{}_HPDEHOSTPREDICT".format(sname),value=HPDEHOSTPREDICT)
  task_instance.xcom_push(key="{}_HPDEPORTPREDICT".format(sname),value="_{}".format(HPDEPORTPREDICT))
  task_instance.xcom_push(key="{}_solutionname".format(sd),value=sname)
  task_instance.xcom_push(key="{}_solutiondescription".format(sname),value=desc)
  task_instance.xcom_push(key="{}_solutiontitle".format(sname),value=stitle)

  task_instance.xcom_push(key="{}_containername".format(sname),value='')
  task_instance.xcom_push(key="{}_brokerhost".format(sname),value=brokerhost)
  task_instance.xcom_push(key="{}_brokerport".format(sname),value="_{}".format(brokerport))
  task_instance.xcom_push(key="{}_chip".format(sname),value=chip)
    
  tsslogging.locallogs("INFO", "STEP 1: completed - TML system parameters successfully gathered")

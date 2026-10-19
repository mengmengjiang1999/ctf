**烦请在文末补充一段安全措施或建议，为读者做正面引导，感谢！**

## 扫描原理

Fortify通过内置的五大主要分析引擎：数据流、语义、结构、控制流、配置流等对应用软件的源代码进行静态的分析，分析的过程中与它特有的软件安全漏洞规则集进行全面地匹配、查找，从而将源代码中存在的安全漏洞扫描出来，并给予整理报告。

![](https://image.3001.net/images/20210719/1626624582_60f4524604f3312df600f.png!small)

## linux环境安装

1.使用ftp/rz等方式上传安装包到机器

2.跳转至系统根目录并解压

![](https://image.3001.net/images/20210719/1626624860_60f4535caf58c90c3859f.png!small)

3.命令行执行HP_Fortify_SCA_and_Apps_4.40_Linux_x64.run进行安装

![1626624902_60f45386e374ad92f134e.png!small?1626624940061](https://image.3001.net/images/20210719/1626624902_60f45386e374ad92f134e.png!small?1626624940061)

![1626624921_60f453994d5274a4ff2bd.png!small?1626624957990](https://image.3001.net/images/20210719/1626624921_60f453994d5274a4ff2bd.png!small?1626624957990)

![1626624933_60f453a5ae1ee20ee677d.png!small?1626624970332](https://image.3001.net/images/20210719/1626624933_60f453a5ae1ee20ee677d.png!small?1626624970332)

安装成功，路径为：/opt/HP_Fortify/HP_Fortify_SCA_and_Apps_4.40/bin

4.将sourceanalyzer和report-generator-exe.jar加入环境变量

将report-generator-exe.jar加入环境变量，编辑/etc/profile文件

export PATH=$PATH:/opt/HP_Fortify/HP_Fortify_SCA_and_Apps_4.40/Core/lib/exe  
  
---  
  
![1626625060_60f454243acc57451ff20.png!small?1626625096923](https://image.3001.net/images/20210719/1626625060_60f454243acc57451ff20.png!small?1626625096923)

5.设置源代码存放地址：/httx/svn/applicationName/projectName

设置fortify.py存放路径：/opt/HP_Fortify/fortify.py

设置fortify扫描结果与报告地址：/httx/fortify_result/

## fortify扫描步骤

为了使扫描流程看起来更加友好和清晰化，使用项目：test为例，采用最基础的扫描配置进行扫描。

Fortify扫描的相关程序在bin文件夹下的sourceanalyzer,主要有以下几个步骤

1.静态代码扫描的第一步：为了避免重名或清除已经存在的项目，此处清除id为test的项目

> sourceanalyzer -b test -clean

2.静态代码扫描的第二步：将指定将要扫描的系统源码/httx/svn/test【表示扫描test文件夹下的所有文件】，并创建项目名test，以此同时已将源码转换为适合fortify扫描的中间代码。

> sourceanalyzer -b test /httx/svn/test

3.静态代码扫描的第三步：查看扫描代码转换为中间代码是否成功

> sourceanalyzer -b test -show-files

4.静态代码扫描的第四步：正式进入扫描阶段

> sourceanalyzer -b test -Xmx1250m -scan -f test.fpr

5.生成报告相关jar文件在Core\lib\exe\report-generator-exe.jar下，可以通过命令进行运行，标准格式为：

    
    
    HPE Security Fortify Report Rendering Commandline Interface:
    Usage: -format pdf -f outputFile.pdf -source myAuditedProject.fpr
    
    Required Options:
    
     -format         Desired output format (pdf, rtf, xml)
    
     -f               The file to which results are written    
    
    -source          The audit project to base the report on
    
    Additional Options:
    
     -template       The Fortify Report template used to define the report.
    
    If omitted then the     default   template   will be used      
    
    -user            The username to be baked into the report.      
    
    -showRemoved    Include removed issues in the report.    
    
    -showSuppressed  Include suppressed issues in the report.      
    
    -showHidden      Include hidden issues in the report.    
    
     -filterSet          The filterset used when generating the report.
    
       -verbose         Output verbose status messages to the console.

根据fortify扫描结果xx.fpr文件生成xml报告：

> java -jar %FORTIFY_HOME%\Core\lib\exe\report-generator-exe.jar -format xml
> -f test.xml -source test.fpr -template DeveloperWorkbook.xml

根据fortify扫描结果xx.fpr文件生成pdf报告：

> java -jar %FORTIFY_HOME%\Core\lib\exe\report-generator-exe.jar -format pdf
> -f test.pdf -source test.fpr -verbose

一般简单输出格式为-verbose ，漏洞细节详细查看使用-template DeveloperWorkbook.xml

  

## 自动化简单实现

以下为python实现自动化上述流程，供参考：

    
    
    #!/usr/bin/env python
    # -*- coding:utf-8 -*-    
    import os
    import sys
    import time
    import subprocess 
    from optparse import OptionParser
    
    
    def listDir(fileDir):
      for eachFile in os.listdir(fileDir):
          if os.path.isdir(fileDir + "/" + eachFile):   #判断文件夹创建时间，符合条件进行删除
              ft = os.stat(fileDir + "/" + eachFile)
              ftime = int(ft.st_ctime)                  #文件创建时间即systemTime、eachFile
              ntime = int(time.time())-60*60*24*30      #当前时间减去30天
              if ftime <= ntime:
                  os.remove(fileDir + '/' + eachFile + projectName + '.fpr')
                  print ('delete %s sucess ' % fileDir + eachFile + projectName + '.fpr') 
          else:
              print 'null or delete fpr failed'
    
    
    def commandScan(oscmd):
      p = subprocess.Popen(oscmd, stdout=subprocess.PIPE, shell=True, stderr=subprocess.PIPE, close_fds=True)
      print 'running: %s' % oscmd
      out, err = p.communicate()
      print out
      if p.returncode != 0:
          print 'Non zero exit code: %s executing: %s' % (p.returncode, oscmd)
      return p.stdout
    
    
    def getAnalyzer():     
      #code path
      #url = '/httx/run/fortifyCode'
      url = '/httx/run/workspace'
      if (os.path.exists(url + '/' + applicationName + '/' + projectName + '/' + branchName)):
          url += '/' + applicationName + '/' + projectName + '/' + branchName + '/**/*'
      else:
          print 'Failed:the project does not exist,please check again.'
          exit()
    
      #sourceanalyzer path
      
      #global environment var in localhost
       
      #report-generator-exe.jar path
      generatorPath = '/httx/run/fortify/Core/lib/exe/report-generator-exe.jar'
      
      #report path
      # reportPath = '/httx/run/fortifyResult'
      reportPath = '/httx/run/workfortify'
      deletePath = reportPath + '/' + applicationName + '/' + projectName 
      dirPath = reportPath + '/' + applicationName + '/' + projectName + '/' + tim
      if (os.path.exists(dirPath) == False): 
       cmdmkdir = 'mkdir -p %s' % dirPath
       childmkdir = subprocess.Popen(cmdmkdir, shell=True)
       outmkdir = childmkdir.communicate()
      else:
       print '%s is existed' % dirPath
    
      #fortify scan
      cmd1 = "/httx/run/fortify/bin/sourceanalyzer -b %s -clean" % projectId
      cmd2 = "/httx/run/fortify/bin/sourceanalyzer -b %s %s" % (projectId, url)
      cmd3 = "/httx/run/fortify/bin/sourceanalyzer -b %s -show-files" % projectId
      cmd4 = "/httx/run/fortify/bin/sourceanalyzer -b %s -Xmx1800m -scan -f %s/%s.fpr" % (projectId, dirPath, projectName)
      cmdList = []
      cmdList.append(cmd1)
      cmdList.append(cmd2)
      cmdList.append(cmd3)
      cmdList.append(cmd4)
      print '*'*40 + 'The Analyzer is Scanning, please wait ...' + '*'*40
      for cmd in cmdList:
          commandScan(cmd)  
    
      #create report
      if (os.path.exists(dirPath + '/' + projectName + '.fpr')):
          cmdpdf = 'java -jar %s -format pdf -f %s/%s.pdf -source %s/%s.fpr -verbose' % (generatorPath, dirPath, projectName, dirPath, projectName)
          cmdxml = 'java -jar %s -format xml -f %s/%s.xml -source %s/%s.fpr -verbose' % (generatorPath, dirPath, projectName, dirPath, projectName)   
          # childpdf = subprocess.Popen(cmdpdf, shell=True)
          # outpdf = childpdf.communicate()
          commandScan(cmdpdf)
          print '*'*40 + 'Generating PDF Document Success' + '*'*40
          commandScan(cmdxml)
          print '*'*40 + 'Generating XML Document Success' + '*'*40
      else:
          print 'The scanning result is existed or generating reporter has failed!'
          # exit()
      listDir(deletePath)
    
    
    
    
    def main():
      #input application name , project name and branch name
      parser = OptionParser('usage: python %prog -a application -p project -b branch')
      parser.add_option('-a', '--application', dest='applicationName', type='string', help='input application name')
      parser.add_option('-p', '--project', dest='projectName', type='string', help='input project name')
      parser.add_option('-b', '--branch', dest='branchName', type='string', help='input branch name')
     
      (options, args) = parser.parse_args()
      if options.applicationName == None or options.projectName == None or options.branchName == None:
          parser.print_help()
          sys.exit()
      
      #add time and projectName into projectId
      global applicationName, projectName, branchName, projectId, tim 
      applicationName = options.applicationName
      projectName = options.projectName
      branchName = options.branchName
      tim = time.strftime('%Y%m%d%H%M%S',time.localtime(time.time()))
      projectId = applicationName + tim 
       
      #goto code analyzer
      getAnalyzer()
     
     
    if __name__ == '__main__':
      main()


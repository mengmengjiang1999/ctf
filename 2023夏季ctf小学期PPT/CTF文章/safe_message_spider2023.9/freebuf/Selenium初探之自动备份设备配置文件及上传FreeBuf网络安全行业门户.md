***本文原创作者：hackerbaba，本文属FreeBuf原创奖励计划，未经许可禁止转载**  

## 一、背景介绍

**在传统的网络安全架构中，难免会有一些重要的安全设备或是软件配置需要定期备份，统一归档。一是为了满足合规，二是在设备变更出现问题的时候，能够快速回滚。手工定期备份难免会有遗漏，且浪费大量人力。**

为了满足这一需求，我利用Selenium
（浏览器自动化测试框架）实现这个自动备份功能，当然其他的python爬虫模块（比如request）也能实现这个功能（大体步骤都差不多），这个后续会继续分享给大家，这次就不在这里讨论。实现自动备份后，再利用python
FTP模块实现统一归档到FTP服务器。备份周期直接利用cron命令即可。既然有脚本自然少不了是否备份成功告警，利用logging模块记录日志，然后再通过rsyslog或第三方转发器传至日志分析平台即可实现告警，我们公司由于使用的splunk，利用splunk
forward传输日志即可。有些人可能对Selenium不是太了解，下面我稍微简单介绍一下Selenium。

## 二、Selenium+Chrome配置及功能说明

Selenium是一个浏览器自动化测试框架。Selenium测试直接运行在浏览器中，就像真正的用户在操作一样。Selenium在爬虫中的运用主要就是查找html相应元素并进行元素交互操作，常见的8种元素定位的方法如下：

> find_element_by_name
>
> find_element_by_id
>
> find_element_by_xpath
>
> find_element_by_link_text
>
> find_element_by_partial_link_text
>
> find_element_by_tag_name
>
> find_element_by_class_name
>
> find_element_by_css_selector

其中最常用的就是find_element_by_name/id/xpath/link_text，其中xpath推荐使用浏览器插件定位元素。火狐浏览器一般使用
firebug 和 firepath 定位元素；谷歌浏览器一般使用xpath helper插件定位元素。

Windows/linux除了安装Selenium模块外，一般需要下载浏览器对应的webdriver驱动到相应文件夹声明并调用浏览器，一个简单的示例如下：

> from selenium import webdriver
>
> browser = webdriver.Chrome() 或 browser =webdriver.Firefox() #调用谷歌或者火狐浏览器
>
> browser.get("<http://www.baidu.com>") #浏览器打开百度
>
> print(browser.page_source) #打印百度首页的源码
>
> browser.close() #关闭浏览器

在linux系统中，还需要声明一些“无头”配置，具体见实现见脚本。

## 三、python+selenium+无头Chrome具体实现脚本

Python环境：3.7.0 selenium：3.141.0 chrome：72.0.3626.119

Webdriver下载地址 <https://chromedriver.storage.googleapis.com/index.html>

自动备份对象：某品牌WAF设备，其他设备更改IP地址、定位相关html元素即可。

    
    
    #coding=utf-8
    
    import os
    
    import time
    
    import logging
    
    import ftplib
    
    from ftplib import FTP
    
    from selenium import webdriver
    
    from selenium.webdriver.common.by import By
    
    from selenium.webdriver.common.keys importKeys
    
    from selenium.webdriver.support.ui import Select
    
    from selenium.webdriver importDesiredCapabilities
    
    from selenium.webdriver.chrome.optionsimport Options
    
     
    
    Device = 'WAF'     #定义设备类型
    
    IP = 'x.x.x.x'         #目标IP
    
    dir_time = time.strftime('%Y-%m-%d',time.localtime())
    
    #输出当前"年-月-日"时间 
    
    dir_backup =f'/opt/sec_backup/{IP}_{Device}/{dir_time}'
    
    #chrome下载的地址备份文件的路径
    
    log_name =f'/opt/sec_backup/log/{IP}/{dir_time}.log'
    
    #存放日志文件的路径
    
    if os.path.exists(dir_backup):
    
       pass
    
    else:
    
       os.mkdir(f'/opt/sec_backup/{IP}_{Device}/{dir_time}')
    
    #创建dir_backup路径
    
     
    
    host = 'X.X.X.X'
    
    port = 21
    
    user = 'XXXX'
    
    pwd = 'XXXXX'
    
    #以上定义FTP服务器相关信息
    
    logging.basicConfig(filename=log_name,level=logging.INFO,format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    logger = logging.getLogger(__name__)
    
    #定义日志输出格式
    
    try:
    
       opts = Options()
    
       opts.headless=True
    
       opts.add_argument('--no-sandbox') 
    
       opts.add_argument('--disable-gpu')
    
       capabilities = DesiredCapabilities.CHROME.copy()
    
       capabilities['acceptSslCerts'] = True 
    
       capabilities['acceptInsecureCerts'] = True
    
       prefs = {'download.prompt_for_download': False,
    
                'download.directory_upgrade': True,
    
                'safebrowsing.enabled': False,
    
                'safebrowsing.disable_download_protection': True}
    
       opts.add_experimental_option('prefs', prefs)
    
       driver = webdriver.Chrome(options=opts,desired_capabilities=capabilities)
    
    #以上是“无头”的一些配置，具体就不一一展开
    
    driver.implicitly_wait(10)  
    
    #设置超时时间10秒钟
    
       driver.command_executor._commands["send_command"] =("POST",'/session/$sessionId/chromium/send_command')
    
       driver.desired_capabilities['browserName'] = 'ur mum'
    
       params = {'cmd': 'Page.setDownloadBehavior', 'params': {'behavior':'allow', 'downloadPath': '%s' %dir_backup }}
    
       driver.execute("send_command", params)
    
    #Chrome下载备份文件到dir_backup目录
    
       driver.get(f"https://{IP}/login/requireLogin")
    
       driver.find_element_by_id("username").send_keys("xxx")
    
       driver.find_element_by_id("password").send_keys("xxx")
    
       driver.find_element_by_id("loginButton").click() 
    
        driver.find_element_by_id("one3").click()
    
       driver.find_element_by_id("two32").click()
    
       driver.switch_to.frame("mainFrame")
    
       driver.find_element_by_link_text("配置同步").click()
    
       driver.find_element_by_xpath("(//input[@id='tmp'])[2]").click()
    
       time.sleep(30)
    
       driver.switch_to.alert.accept()
    
       driver.find_element_by_xpath("//*[@id='backpointtable']/tbody/tr[2]/td[5]/img[3]").click()
    
       while True:
    
           if os.listdir(dir_backup) andos.listdir(dir_backup)[0].endswith('.wafc'):
    
    #备份周期是天，一天只生成一个固定目录，里面只有一个备份文件，故判断是否有文件即可
    
               logger.info('备份成功')
    
               break
    
           else:
    
               continue
    
        
    
       driver.find_element_by_link_text("配置同步").click()
    
       driver.find_element_by_xpath("//*[@id='backpointtable']/tbody/tr[2]/td[5]/img[4]").click()
    
       confirm2 = driver.switch_to.alert
    
       confirm2.accept()
    
       driver.quit()
    
       #logger.info('删除旧备份成功')
    
    except Exception as e:
    
       logger.info(f"自动备份出现异常，异常内容：{e}")
    
        
    
    def ftpconnect():
    
       ftp_server = host
    
       username = user
    
        password = pwd
    
       ftp = FTP()
    
       ftp.set_debuglevel(0)
    
       ftp.connect(ftp_server, 21)
    
       ftp.login(username, password)
    
       return ftp
    
     
    
    def uploadfile():
    
       try:
    
           ftp = ftpconnect()
    
           remotepath = ftp.mkd(f'/{IP}-{Device}/{dir_time}')
    
       except:
    
           pass
    
       ftp.cwd(remotepath)
    
       bufsize = 1024
    
       localfile = dir_backup + '/' + os.listdir(dir_backup)[0]
    
       remotefile = os.listdir(dir_backup)[0]
    
       print(localfile)
    
       fp = open(localfile, 'rb')
    
       ftp.storbinary('STOR ' + remotefile, fp, bufsize)
    
    #上传本地localfile，至remotepath，并命名remotefile
    
       ftp.set_debuglevel(0)
    
    #关闭ftp的调试模式，如果设置为2，则输出详细信息
    
       fp.close()  
    
     
    
    if __name__ == '__main__':
    
       try:
    
           uploadfile()
    
       except Exception as e:
    
           logger.info(f"文件上传出现异常，异常内容：{e}")
    
       else:
    
           logger.info('文件上传成功')

## 四、效果图

![image.png](https://image.3001.net/images/20190310/1552205984_5c84c8a082fe9.png!small)![image.png](https://image.3001.net/images/20190310/1552205988_5c84c8a4882aa.png!small)
![image.png](https://image.3001.net/images/20190310/1552205993_5c84c8a9d5a37.png!small)![image.png](https://image.3001.net/images/20190310/1552205999_5c84c8af743b2.png!small)

关于告警：log文件出现“异常”字样即可告警。

 ***本文原创作者：hackerbaba，本文属FreeBuf原创奖励计划，未经许可禁止转载**


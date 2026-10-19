Splunk就不多说了，懂的都懂，不懂的百度，Gartner魔力象限第一的。

## 下载并安装Splunk(苹果电脑)

### 1、下载软件

MAC版本下载链接:

    
    
    wget -O splunk-8.1.2-545206cc9f70-macosx-10.11-intel.dmg 'https://www.splunk.com/bin/splunk/DownloadActivityServlet?architecture=x86&platform=macos&version=8.1.2&product=splunk&filename=splunk-8.1.2-545206cc9f70-macosx-10.11-intel.dmg&wget=true'
    
    

md5值：

    
    
    MD5 (splunk-8.1.2-545206cc9f70-macosx-10.11-intel.dmg) = a7c703608a9ab57c57b5a3097b038e46
    

### 2、安装splunk

苹果版本的，点击dmg安装便可，无须多言

安装后程序目录在/Applications/Splunk/

splunk相关命令:

    
    
    ./splunk
    
    start      //启动splunk
    
    --accept-license  //自动接收许可
    
    restart   //重启splunk
    
    status    //查看splunk状态
    
    version   //查看splunk版
    

## 安装splunk转发器(windows 10 机器)

### 1、下载软件

链接如下:

    
    
    wget -O splunkforwarder-8.1.2-545206cc9f70-x64-release.msi 'https://www.splunk.com/bin/splunk/DownloadActivityServlet?architecture=x86_64&platform=windows&version=8.1.2&product=universalforwarder&filename=splunkforwarder-8.1.2-545206cc9f70-x64-release.msi&wget=true'
    

下载后比对md5值，md5如下:

    
    
    MD5 (splunkforwarder-8.1.2-545206cc9f70-x64-release.msi) = 38713da01a391150968dc668d848d489
    

### 2、安装splunk forward

勾选check this box to accept the liencense agreement

勾选an on-premises splunk enterprise instance

点击view license aggreement

点击 customize Options![splunk forwar
安装1](https://image.3001.net/images/20210312/1615515698_604ad032b8219577ef4c9.png!small)  
设置配置的用户名和密码，测试环境就没有配置s s
l证书了![image](https://image.3001.net/images/20210312/1615515739_604ad05bdd4b69420d703.png!small)  
勾选需要监控的数据类型，如需要自定义监控某些路径的文件，可以用path to
monitor![image](https://image.3001.net/images/20210312/1615515763_604ad073e8b8322d7724b.png!small)  
Deployment
server，可用于批量下发配置，这里我配置成splunk服务器的地址![image](https://image.3001.net/images/20210312/1615515813_604ad0a596f4f17b00ecf.png!small)  
配置forwarder接收数据地址  
![image](https://image.3001.net/images/20210312/1615515846_604ad0c657fd2b1e49479.png!small)

## splunk配置forward转发数据接收

1、设置-> 转发和接收->配置接收->新接收端口->侦听上面forward配置的9997端口  
![image](https://image.3001.net/images/20210312/1615515887_604ad0ef9e40ebbd25234.png!small)![image](https://image.3001.net/images/20210312/1615515906_604ad10214872e0daa319.png!small)

## splunk日志查询

Search&Reporting ->在搜索中输入index='main',便能查看windows
10的日志信息![image](https://image.3001.net/images/20210312/1615515941_604ad12581e0d536d7ba9.png!small)


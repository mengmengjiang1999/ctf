## **概述：**

KONNI是一类远控木马病毒，很早之前就由思科Talos团队披露过。在2014年的时候就开始活跃起来了。针对的主要攻击对象有俄罗斯、韩国等地区。在PaloAlto团队的研究中发现此类木马病毒家族与Nokki有很多相似之处，疑似这个与东亚的APT组织存在关联性。此后Konni被当做疑似具有东亚背景的APT组织。

暗影实验室根据捕获的样本发现，此样本仿冒安全软件，以检测用户设备安全情况为诱饵，诱导用户使用此软件。用户安装应用之后向主控地址请求远控命令，获取用户联系人、短信、应用安装列表等信息，将获取的隐私信息上传到服务器。

##  **1\. 样本信息**

 **MD5** **：** 0ce1648ff7553189e5b5db2252e27fd5

 **包名：** com.json

 **应用名：** AoneSmmitz

 **安装图标：**

![](https://image.3001.net/images/20201104/1604475794_5fa25b9233b61d3088523.png!small)

##  **2\. 恶意行为综述**

该程序一款仿冒检测手机漏洞的安全软件。用户运行后提示用户这个工具是检测设备漏洞的工具，当用户点击检测选项，提示用户此设备安全。其实际行为是向指定远控发送请求，获取一个txt远控文件，txt远控文件当中包含远控指令，根据远控指令获取用户包括短信、联系人、应用安装列表等用户隐私数据，将获取的用户隐私数据上传到指定服务器。

##  **3\. 运行流程图**

仿冒安全软件，诱导用户下载安装，用户安装后，仿冒安全功能诱导用户使用，开启电源锁常驻后台运行，向服务器请求远控指令，执行远控指令，获取用户短信、联系人、应用安装列表、sd卡文件名称等信息，将获取的隐私信息上传到服务器。

![](https://image.3001.net/images/20201104/1604475809_5fa25ba1e70a5b12cbe09.png!small)

图3-1 程序运行流程图

##  **4\. 技术原理分析**

###  **4.1 仿冒安全应用**

仿冒安全软件AoneSmmitz诱导用户安装，当用户打开软件，提示用户这个工具是检测用户设备有没有漏洞的工具，当用户点击开始检测，返回用户的是您的设备无安全漏洞。从功能上仿冒安全软件，让用户放松警惕。

仿冒AoneSmmitz应用：

![](https://image.3001.net/images/20201104/1604475854_5fa25bce9c4f2ce685346.png!small)图4-1
仿冒AoneSmmitz软件

提示用此工具为检测设备漏洞工具：

![](https://image.3001.net/images/20201104/1604475879_5fa25be712e300e473dcf.png!small)图4-2提示检测漏洞

向用户反馈经检测结果，设备无漏洞：

![](https://image.3001.net/images/20201104/1604475910_5fa25c067e0336b805330.png!small)图4-3
反馈设备无漏洞信息

###  **4.2 程序加载运行**

恶意程序在诱导用户安装完成之后，向主控地址请求远控文本。获取用户IMEI、系统版本信息，用来区别用户的唯一性。设置电源锁，当屏幕处于关闭状态时，保障恶意程序的监听服务处于监听状态，确保对用户处于一直监听状态。

1）向主控地址请求远控文本，请求之后向用户反馈远控文件。主控地址是：http://cloudsec***service.net/。

初始化地址：

![](https://image.3001.net/images/20201104/1604475940_5fa25c24625cf271756f9.png!small)图4-4
初始化地址

向主控地址发送txt文本请求：

![](https://image.3001.net/images/20201104/1604475962_5fa25c3a717b94f69ea46.png!small)图4-5
向主控发送远控文本请求

获取用户IMEI、设备系统版本等信息，用来区别用户的唯一性：

![](https://image.3001.net/images/20201104/1604475985_5fa25c51c32a9b25209f2.png!small)图4-6
获取用户IMEI等信息

2）设置电源锁，当屏幕处于关闭状态时，保障恶意程序的监听服务处于监听状态，确保对用户处于一直监听状态。

![](https://image.3001.net/images/20201104/1604476010_5fa25c6aaaa0b262d3fd5.png!small)图4-7
开启电源锁

###  **4.3 远程控制**

恶意程序向服务器请求远控文件之后获取远控文件，恶意程序根据远控文件当中的内容来区分远控指令。获取用户通讯录、获取用户短信、获取外部存储器文件目录、获取已安装应用列表数据等隐私数据。将获取的用户隐私信息上传到指定服务器。

 **4.3.1 获取信息**

1）请求的远控文件，解析远控指令。

请求的远控文件：

http://cloudsecur***ervice.net/json/files/To_5063967640744206.txt

![](https://image.3001.net/images/20201104/1604476037_5fa25c858dd8dc15f9df3.png!small)图4-8
请求远控文件

读取远控文件，解析远控指令：

![](https://image.3001.net/images/20201104/1604476056_5fa25c989c23e0900ba90.png!small)图4-9
解析远控指令

2）恶意程序的远控指令。

指令列表：

 **远控指令**

  

|

 **远控指令的意义**

  
  
  
---|---  
  
del_file

  

|

删除指定文件

  
  
  
del_sms

  

|

删除指定短信

  
  
  
download

  

|

下载文件

  
  
  
get_account

  

|

获取用户账户信息

  
  
  
get_app

  

|

采集用户安装的所有APP信息

  
  
  
get_contact

  

|

获取联系人数据

  
  
  
get_keylog

  

|

获取键盘记录数据

  
  
  
get_sdcard

  

|

获得sd卡的文件目录

  
  
  
get_sms

  

|

获取短信内容

  
  
  
get_time

  

|

获取时间

  
  
  
get_user

  

|

获取手机基本系信息如IMEI、用户手机号、OSType、OSAPI

  
  
  
open_app

  

|

打开APP

  
  
  
open_dlg

  

|

弹框

  
  
  
open_web

  

|

打开网页

  
  
  
screen

  

|

截屏

  
  
  
send_sms

  

|

发送短信

  
  
  
uninstall_app

  

|

卸载APP

  
  
  
upload

  

|

上传文件

  
  
  
volume

  

|

获取文件系统主目录

  
  
  
3）解析远控文件当中的远控指令，当指令是get_contact，将bGetContract的值设置为true，当bGetContract的值为true时，获取用户联系人数据。

设置bGetContract的值为true：

![](https://image.3001.net/images/20201104/1604476085_5fa25cb51d3326ed12938.png!small)图4-11
设置bGetContract的值

获取用户联系人数据。

![](https://image.3001.net/images/20201104/1604476102_5fa25cc604140a7ab6479.png!small)图4-12
获取用户联系人数据

4）解析远控文件当中的远控指令，当指令是bGetSms，将bGetSms的值设置为true，当bGetSms的值为true时，获取用户短信。

设置bGetSms的值为true：

![](https://image.3001.net/images/20201104/1604476123_5fa25cdb2768b98f487f3.png!small)图4-13
设置bGetSms的值为true

获取用户短信。

![](https://image.3001.net/images/20201104/1604476137_5fa25ce9f3ff8800912e5.png!small)图4-14
获取用户短信

5）解析远控文件当中的远控指令，当指令是get_app，将bGetApp的值设置为true，当bGetApp的值为true时，获取用户安装的应用程序信息。

设置bGetApp的值为true：

![](https://image.3001.net/images/20201104/1604476154_5fa25cfa48e952bee105b.png!small)图4-15
设置设置bGetApp的值为true

获取用户安装的应用程序信息。

![](https://image.3001.net/images/20201104/1604476168_5fa25d08c750e8d997072.png!small)图4-16
获取用户安装的应用程序信息

6）解析远控文件当中的远控指令，当指令是get_sdcard，将get_sdcard的值设置为true，当get_sdcard的值为true时，获取用户sd卡目录。

设置get_sdcard的值为true:

![](https://image.3001.net/images/20201104/1604476184_5fa25d18400cc19ea4f7c.png!small)图4-17
设置get_sdcard的值为true

获取用户sd卡目录。

![](https://image.3001.net/images/20201104/1604476200_5fa25d2877567e9363ebd.png!small)图4-18
获取用户sd目录

7）解析远控文件当中的远控指令，当指令是get_account，将get_account的值设置为true，当get_account的值为true时，获取用户账户信息。

设置get_account的值为true：

![](https://image.3001.net/images/20201104/1604476218_5fa25d3a1f6ce41d521e6.png!small)图4-19
设置get_account的值为true

获取用户账号信息。

![](https://image.3001.net/images/20201104/1604476270_5fa25d6e14d740334d992.png!small)图4-20
获取用户账号信息

 **4.3.2 上传信息**

1）解析远控文件当中的远控指令，当指令是upload，将bUpload的值设置为true，当bUpload的值为true时，获取用户隐私信息。

设置bUpload的值为true：

![](https://image.3001.net/images/20201104/1604476288_5fa25d80b50fc2378fe50.png!small)图4-21
设置bUpload的值为true

获取用户隐私信息：

![](https://image.3001.net/images/20201104/1604476315_5fa25d9b2a2f841355915.png!small)图4-22
获取用户隐私信息

2）上传用户隐私信息，上传地址是http://cloudsec****service.net/json/up.php。

上传用户IMEI等信息。

![](https://image.3001.net/images/20201104/1604476334_5fa25dae204414fa00629.png!small)图4-23
上传IMEI等信息

上传用通信录信息。

![](https://image.3001.net/images/20201104/1604476417_5fa25e01b409042dbd072.png!small)图4-24
上传用户通讯录

上传用户短信信息。

![](https://image.3001.net/images/20201104/1604476438_5fa25e160c8a8da18b4be.png!small)图4-25
上传用户短信信息

上传用户安装应用列表信息。

![](https://image.3001.net/images/20201104/1604476458_5fa25e2ac1ea48a4d243f.png!small)图4-26
上传用户应用列表信息

##  **5\. 扩展分析**

###  **5.1 样本信息**

MD5

  

|

包名

  

|

通讯地址

  
  
  
---|---|---  
  
0ce1648ff7553189e5b5db2252e27fd5

  

|

com.json

  

|

http://cloudse***tyservice.net/

  
  
  
###  **5.2 样本域名信息**

域名

  

|

IP

  

|

归属地

  
  
  
---|---|---  
  
http://cloud***trityservice.net/

  

|

​27.255.79.205

  

|

韩国 ehost数据中心

  
  
  
##  **6\. 安全建议**

> 安全类软件，建议去正规的应用市场下载、去官方下载。
>
> 在手机当中安装必要的安全软件，并保持安全软件更新。

  


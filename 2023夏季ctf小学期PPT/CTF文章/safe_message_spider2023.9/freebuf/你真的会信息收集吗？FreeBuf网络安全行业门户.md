在一次渗透测试过程中，最重要的就是信息收集，占测试流程的80%可能还要多，信息收集的越多，发现漏洞的可能性就越大，渗透测试成功率越高。对一个站点的测试信息收集主要分为几类：域名信息，子域名信息，指纹信息，端口信息，敏感信息，查找真实IP，站点目录扫描，第三应用信息，c段和旁站，社会工程学。

##  **一：域名信息收集**

### 1.1 注册人信息：

whois查询了ip，电话，邮箱等信息可以扩展注册人信息，微信等应用信息，确定公司或者个人信息，反查公司域名，c段等

1.1.1 站长之家whois查询：http://whois.chinaz.com

![1606702722_5fc4568287a4826cc7506.png!small?1606702723826](https://image.3001.net/images/20201130/1606702722_5fc4568287a4826cc7506.png!small?1606702723826)

1.1.2 爱站长工具网：https://whois.aizhan.com

![1606702837_5fc456f5561130f7c9e4e.png!small?1606702838208](https://image.3001.net/images/20201130/1606702837_5fc456f5561130f7c9e4e.png!small?1606702838208)

1.1.3 Vieus Total： https:// www.virustotal.

![1606703006_5fc4579e772b526ebe9c8.png!small?1606703007338](https://image.3001.net/images/20201130/1606703006_5fc4579e772b526ebe9c8.png!small?1606703007338)

1.1.4 Icannlookup: https://lookup.icann.org

![1606703124_5fc45814c92343254807e.png!small?1606703125676](https://image.3001.net/images/20201130/1606703124_5fc45814c92343254807e.png!small?1606703125676)

  

### 1.2 备案信息查询

通过备案信息查询可以了解注册人相关信息，查询到邮箱，公司地址，架构，公司相关的资产信息

1.2.1 IPC备案查询网：http://www.beianbeian.com

1.2.2 天眼查：http://tianyancha.com

![1606703465_5fc45969295294891116f.png!small?1606703466545](https://image.3001.net/images/20201130/1606703465_5fc45969295294891116f.png!small?1606703466545)

1.2.3 阿里企查查：https://www.qcc.com/

![1606703516_5fc4599c7b09fa6ffb2be.png!small?1606703517670](https://image.3001.net/images/20201130/1606703516_5fc4599c7b09fa6ffb2be.png!small?1606703517670)

  

## 二：子域名信息收集

### 2.1 收集工具

2.1.1 ayer子域名挖掘机

  

2.1.2 wydomain

github下载地址：<https://github.com/ring04h/wydomain>

2.1.3 sublist3r

复制到kali进行下载：git clone <https://github.com/aboul3la/Sublist3r.git>

2.1.4 subdomainbrute

github下载地址：https://github.com/lijiejie/subDomainsBrute

  

### 2.2 搜索引擎

site：baidu.com

子域名信息查询枚举:通过查询枚举子域名是为了在主站域名找不到突破口或者利用方式，来到子域名查找真实ip，子域名网站是否存在漏洞，是否有利用的方式，能否通过子域名来渗透到主站.

  

### 2.3 第三方聚合应用枚举

DNSdumpster.com

![1606707523_5fc469438324686f0d1e3.png!small?1606707524399](https://image.3001.net/images/20201130/1606707523_5fc469438324686f0d1e3.png!small?1606707524399)

  

### 2.4 在线网站查询子域名

[2.4.1 ](https://phpinfo.me/domain)子域名爆破

<https://phpinfo.me/domain>

![1606707641_5fc469b90b4f932840499.png!small?1606707641883](https://image.3001.net/images/20201130/1606707641_5fc469b90b4f932840499.png!small?1606707641883)

2.4.2 ip反查绑定域名网站

<https://dns.aizhan.com>

  

## 三 指纹信息收集

### 3.1

指纹识别是为了识别web运用的哪些应用，服务器版本，脚本语言等，可以为漏洞挖掘提供支撑。

![1606707928_5fc46ad8a9fdd4694a9df.png!small?1606707929573](https://image.3001.net/images/20201130/1606707928_5fc46ad8a9fdd4694a9df.png!small?1606707929573)

### 3.2 收集指纹常用工具

3.2.1 Whatweb

![1606716817_5fc48d91417fe8b8a1b63.png!small?1606716818137](https://image.3001.net/images/20201130/1606716817_5fc48d91417fe8b8a1b63.png!small?1606716818137)

以百度为列，whatweb baidu.com 直接搜索指纹信息。  
![1606716866_5fc48dc26a9433b0f5273.png!small?1606716867548](https://image.3001.net/images/20201130/1606716866_5fc48dc26a9433b0f5273.png!small?1606716867548)

3.2.2 webrobo 收集指纹的工具。

3.2.3 在线网站查询

bugscaner：http//whatweb.bugscaner.com/

![1606716671_5fc48cff68fdb7abf5d1b.png!small?1606716672268](https://image.3001.net/images/20201130/1606716671_5fc48cff68fdb7abf5d1b.png!small?1606716672268)

云悉指纹：http://www.yunsee.cn/finger.

![1606717168_5fc48ef0dd63f44d940cc.png!small?1606717170090](https://image.3001.net/images/20201130/1606717168_5fc48ef0dd63f44d940cc.png!small?1606717170090)

潮汐指纹： http://finger.tidesec.net/

![1606717198_5fc48f0e8f421f302cfe8.png!small?1606717199490](https://image.3001.net/images/20201130/1606717198_5fc48f0e8f421f302cfe8.png!small?1606717199490)

  

## 四：端口信息收集

常见协议的端口信息如80，4321，3306等

4.1：Nmap

以百度为例

![1606717509_5fc49045388e683d727e0.png!small?1606717510112](https://image.3001.net/images/20201130/1606717509_5fc49045388e683d727e0.png!small?1606717510112)

4.2: Masscan

下载地址：https://github.com/robertdavidgraham/masscan

4.3：Zmap

GitHub地址：https://github.com/zmap/zmap/

4.4：scanport windows端口扫描工具

4.5 御剑端口扫描工具

![1606718183_5fc492e7a5e530f9a0633.png!small?1606718184552](https://image.3001.net/images/20201130/1606718183_5fc492e7a5e530f9a0633.png!small?1606718184552)

  

## 五：敏感信息收集

### 5.1 通过googlehack查询

5.5.1 敏感文件收集语法

site:xxx.com filetype:doc intext:pass

site:xxx.com filetype:xls intext:pass

site:xxx.com filetype:conf

site:xxx.com filetype:inc

5.5.2 管理后台收集语法

site:xxx.com 管理

site:xxx.com admin

site:xxx.com login

5.5.3 搜索mail

site:xxx.com intext:@xxx.com

5.5.4 敏感web路径

site:xxx.com intitle:mongod inurl:28017

site:xxx.com inurl:sql.php

site:xxx.com inurl:phpinfo.php

### 5.2 网络工具搜索

5.2.1 shodan

搜索指定ip或子网 net:0.0.0.0/24

hostname：搜索指定的主机或域名，例如 hostname:"google"port：搜索指定的端口或服务，例如
port:"21"country：搜索指定的国家，例如 country:"CN"city：搜索指定的城市，例如
city:"Hefei"org：搜索指定的组织或公司，例如 org:"google"isp：搜索指定的ISP供应商，例如 isp:"China
Telecom"product：搜索指定的操作系统/软件/平台，例如 product:"Apache httpd"version：搜索指定的软件版本，例如
version:"1.6.2"geo：搜索指定的地理位置，参数为经纬度，例如 geo:"31.8639,
117.2808"before/after：搜索指定收录时间前后的数据，格式为dd-mm-yy，例如
before:"11-11-15"net：搜索指定的IP地址或子网，例如 net:"210.45.240.0/24"

  

5.2.2 fofa

关键词：title=‘关键词’

http响应头：header=‘thinkphp’

正文：body=‘后台’

.....

  

5.2.3 github敏感信息泄露

GitMAD

Hawkeye:https://github.com/0xbug/Hawkeye

gitee

码云、华为开源平台、阿里云code

  

## 六：查找真实IP

### 6.1 判断目标是否使用了cdn

在线网站17ce：https://www.17ce.com

![1606718985_5fc49609cedca2e49a96d.png!small?1606718987109](https://image.3001.net/images/20201130/1606718985_5fc49609cedca2e49a96d.png!small?1606718987109)

站长之家超级ping：http://ping.chinaz.com/

![1606719055_5fc4964fab1322dbb29c1.png!small?1606719056503](https://image.3001.net/images/20201130/1606719055_5fc4964fab1322dbb29c1.png!small?1606719056503)

爱站：http://ping.aizhan.com/

![1606719077_5fc4966518e14d0857a85.png!small?1606719077954](https://image.3001.net/images/20201130/1606719077_5fc4966518e14d0857a85.png!small?1606719077954)

nslookup

![1606719165_5fc496bd6cf5734cf7eac.png!small?1606719166275](https://image.3001.net/images/20201130/1606719165_5fc496bd6cf5734cf7eac.png!small?1606719166275)

### 6.2 绕过cdn寻找真实的IP

内部邮箱源(注意，必须是自己的邮箱，第三方或公共邮件服务器是没有用的)

搜索引擎查询：fofa，shodan

SecurityTrails平台

利用SSL证书寻找真实原始IP：Censys

扫描网站测试文件，如phpinfo、test等

查询域名的解析记录，也许目标很久以前并没有用过cdn，通过网站NETCRAFT(https://www.netcraft.com/)来观察余名的IP历史记录，分析真实ip段

  

## 七：站点目录扫描

### 7.1 工具扫描

DirBuster

**[下载链接：https://sourceforge.net/projects/dirbuster/files/latest/download](https://links.jianshu.com/go?to=https%3A%2F%2Fsourceforge.net%2Fprojects%2Fdirbuster%2Ffiles%2Flatest%2Fdownload)**

![1606720909_5fc49d8db85b4475366b3.png!small?1606720910763](https://image.3001.net/images/20201130/1606720909_5fc49d8db85b4475366b3.png!small?1606720910763)

Dirmap 打开cmd安装python环境再安装就能使用

御剑后台扫描珍藏版

![1606721875_5fc4a153bea1e5fd4bbe5.png!small?1606721876651](https://image.3001.net/images/20201130/1606721875_5fc4a153bea1e5fd4bbe5.png!small?1606721876651)

spinder.py(轻量级快速但文件目录后台扫描)

Sensitivefilescan(轻量级快速单文件目录台天扫描)

Weakfilescan(轻量级快速单文件目录台天扫描)

dirsearch(python文件个人使用比较多的一款工具)

### 7.2 在线网站

WebScan：<http://www.webscan.cc/>

  

## 八 第三应用信息收集

### 8.1 WordPress版本，插件信息收集

在线网站扫描

<http://wpthemedetector.coderschool.cn/>

![1606722199_5fc4a29744922df8261c7.png!small?1606722200210](https://image.3001.net/images/20201130/1606722199_5fc4a29744922df8261c7.png!small?1606722200210)

<https://www.wpthemedetector.com>

![1606722324_5fc4a31499adcee197fff.png!small?1606722325658](https://image.3001.net/images/20201130/1606722324_5fc4a31499adcee197fff.png!small?1606722325658)

  

<https://whatwpthemeisthat.com/>

![1606722349_5fc4a32d180ca68cf0abb.png!small?1606722349951](https://image.3001.net/images/20201130/1606722349_5fc4a32d180ca68cf0abb.png!small?1606722349951)

工具扫描

WPGrabInfo工具（使用perl语言开发的轻量级WordPress扫描器）

WPScan工具（扫描WordPress网站中的多种安全漏洞）

### 8.2 编辑器信息收集

FCK编辑器

① FCK编辑页 _samples/default.html

② 查看FCK编辑器版本/_whatsnew.html

③
查看文件上传路径/editor/filemanager/browser/default/connectors/asp/connector.asp?Command=GetFoldersAndFiles&Type=Image&CurrentFolder=/

  

EWEbeditor编辑器

默认数据库：ewebeditor/db/ewebeditor.mdb

修改上传类型

自己添加上传样式以后添加上传按钮一一上传

  

南方数据编辑器

访问admin/southidceditor/admin_style.asp

修改编辑器样式，增加asa(不要asp).然后直接后台编辑新闻上传

  

DotNetTextBox编辑器

关键字:system_dntb/

确定有system_dntb/uploadimg.aspx并能打开，这时候是不能上传的，由于他是验证cookie来得出上传后的路径，这样我们可以用cookie欺骗工具cookie:UserType=0;IsEdition=0;Info=1;

uploadFolder=../system_dntb/Upload/;路径可以修改，只要权限够，上传后改名为1.asp;.jpg利用iis解析漏洞

  

## 九：C段和旁站

### 9.1 旁站：同服务器不同站点

在线网站收集

站长之家 地址：http://stool.chinaz.com/same

WebScan 地址：https://webscan.cc

工具扫描

K8c段旁注工具(轻量级旁站查询)

  

### 9.2 C段：同网段不同服务器

C段扫描：快速扫描C段的工具有nmap、masscan、zenmap和webscancc。也可以用python脚本扫描C段。

网站快照：可用linux命令行抓取网页快照，需要用到软件xvfb，CutyCapt，Qt。

<https://www.cnblogs.com/xiaojikuaipao/p/6437065.html>

可用php抓取网站或者某个网页的快照图片，php利用CutyCapt抓取网页高清图片快照

<https://jingyan.baidu.com/article/37bce2be0e31a01003f3a25b.html>

后台识别/登录：

①字典查找：平时可以把一些上传地址，后台地址，表段记录下来，也可以收集别人的字典，以后可能会用到。

②工具扫描：明小子的后台扫描功能，wwwscan目录扫描器，御剑和阿D注入工具的后台扫描功能等等。

③搜索引擎查找：<https://blog.csdn.net/chance2015/article/details/50402487/>

目录扫描：

wwwscan可以扫描目录，而webdirscan是一个较简单的多线程Web目录扫描工具

DirBuster是一款专门用于探测Web服务器的目录和隐藏文件

在线网站收集：

Fafo 地址：https://fofa.so/

Shodan 地址：https://www.shodan.io/

  

## 十 ：社会工程学

社会工程学是黑客米特尼克悔改后在《欺骗的艺术》中所提出的，是一种通过对受害者心理弱点、本能反应、好奇心、信任、贪婪等心理陷阱进行诸如欺骗、伤害等危害手段。

在信息安全整个环节中，最薄弱的往往在人身上，黑客通过各种手段从受害者身上获取有利信息。比如说一个电话号码，一个人的名字，或者工作的ID号码，都可能会被社会工程师所利用。

  

## 最后

渗透测试的前提是收集足够的信息，只有越了解目标才能更快的击败目标。


## 一、前言

致远OA系统由北京致远互联软件股份有限公司开发，是一款基于互联网高效协作的协同管理软件，在各企业机构中被广泛使用。近期致远OA系统被爆出存在任意文件写入漏洞，已经被发现在野外利用。

![1.png](https://image.3001.net/images/20190627/15616144161142.png!small)

网藤CRS/ARS产品已全面支持该漏洞的检测与验证，网藤用户可直接登陆[www.riskivy.com](http://www.riskivy.com)进行验证。

## 二、漏洞简介  

致远 OA 系统的一些版本存在任意文件写入漏洞，远程攻击者在无需登录的情况下可通过向 URL /seeyon/htmlofficeservlet POST
精心构造的数据即可向目标服务器写入任意文件，写入成功后可执行任意系统命令进而控制目标服务器。

## 三、漏洞验证

访问URL /seeyon/htmlofficeservlet 出现如下内容可能存在漏洞，需要关注。

![2.png](https://image.3001.net/images/20190627/15616145108881.png!small)

## 四、漏洞危害

成功利用此漏洞的攻击者可以在目标系统上执行任意代码。然后攻击者查看，更改或删除数据。

## 五、影响范围

> 致远A8-V5协同管理软件V6.1sp1
>
> 致远A8+协同管理软件V7.0、V7.0sp1、V7.0sp2、V7.0sp3
>
> 致远A8+协同管理软件V7.1

## 六、修复方案

### 1.配置访问控制策略：

对路径 /seeyon/htmlofficeservlet 进行限制访问

### 2.修改应用程序配置文件:

修改

> Seeyon/A8/ApacheJetspeed/webapps/seeyon/WEB-INF/web.xml文件

将如下内容进行注释，并重启应用程序

![3.png](https://image.3001.net/images/20190627/15616147856736.png!small)

### 3.联系官方获取补丁程序：

官网地址:

> <http://www.seeyon.com/Info/constant.html>

以上是本次高危漏洞预警的相关信息，如有任何疑问或需要更多支持，可通过以下方式与我们取得联系。

> 联系电话：400-156-9866
>
> Email：help@tophant.com


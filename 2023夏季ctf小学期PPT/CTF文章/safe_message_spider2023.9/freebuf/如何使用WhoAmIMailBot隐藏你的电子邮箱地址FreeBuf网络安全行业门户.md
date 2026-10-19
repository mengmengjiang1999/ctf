![](https://image.3001.net/images/20230421/1682087514_64429e5a89e242b54cfb7.jpeg!small)

## 关于WhoAmIMailBot

WhoAmIMailBot是一款针对电子邮件服务的安全工具，该工具可以帮助广大研究人员通过自定义配置来隐藏自己的真实电子邮箱地址。该工具受到了[
_Blur项目_](https://abine.com/)的启发，而该项目允许我们为自己的电子邮件创建一个别名，并用这个别名来实现应用程序的注册。但Blur项目的问题在于，所有的电子邮件内容都会通过该服务的基础设施，但我们其实并不希望任何人查看到我们的电子邮件内容。

因此，WhoAmIMailBot便应运而生，而该工具将允许我们使用自己搭建的基础设施服务。

## 工作机制

为了实现我们的目标，我们需要准备好下列内容：

> 1、一个域名（如果想省钱的话，也可以使用no-ip 服务）；
>
> 2、一台允许SMTP出站流量的VPS；
>
> 3、一个Telegram Bot ID；
>
> 4、自己的Telegram用户ID；
>
> 5、WhoAmIMailBot项目代码；

这台VPS将负责运行一台邮件服务器，并使用邮件系统功能和虚拟别名来重定向电子邮件。此时，我们可以设置一个电子邮件地址，并将所有传入的邮件重定向到另一个电子邮箱。如果使用了no-ip域名的话，我们可以使用Telegram Bot来管理电子邮箱别名。

下图显示的是该工具的运行机制流程图：

![](https://image.3001.net/images/20230421/1682087531_64429e6bb477656fd6c5a.png!small)

## 工具安装

### 源码安装

由于该工具基于Python开发， 因此我们首先需要在本地设备上安装并配置好Python环境。接下来，广大研究人员可以使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/mthbernardes/WhoAmIMailBot.git

然后切换到项目目录中，使用docker命令构建项目代码：

    
    
    cd WhoAmIMailBot
    
    docker build -t whoamimailbot .
    
    docker run -d -p 25:25 --name whoamimailbot -v /data/postfix/:/data -e TELEGRAM_BOT_TOKEN="BOT_TOKEN" -e TELEGRAM_USER_ID="USER_ID" -e FAKE_DOMAIN="mail.example.com" whoamimailbot

### Hub Docker安装

我们也可以使用下列命令来下载该工具的Docker镜像：

    
    
    docker pull btamburi/whoamimailbot

或者：

    
    
    docker run -d -p 25:25 --name whoamimailbot -v /data/postfix/:/data -e TELEGRAM_BOT_TOKEN="BOT_TOKEN" -e TELEGRAM_USER_ID="USER_ID" -e FAKE_DOMAIN="mail.example.com" btamburi/whoamimailbot

## 环境变量

工具镜像使用了环境变量来允许用户在工具运行时调整某些配置：

> TELEGRAM_BOT_TOKEN：Telegram Bot令牌；
>
> TELEGRAM_USER_ID：你的Telegram ID；
>
> FAKE_DOMAIN：用于接收电子邮件的虚假域名（例如mailbot.ddns.net）；

## 工具使用

工具配置完成后，我们就可以在Telegram Bot上执行下列命令了：

 ** **命令****

|

 ** **描述****  
  
---|---  
  
/list

|

查看所有可用的别名  
  
/new [mail@mail.com](mailto:mail@mail.com)

|

针对给定电子邮件地址创建一个新的别名  
  
/delete string

|

根据给定的字符串删除邮箱别名  
  
## 项目地址

 **WhoAmIMailBot** ：【[
_GitHub传送门_](https://github.com/mthbernardes/WhoAmIMailBot)】

## 参考资料

> [ _https://abine.com/_](https://abine.com/)


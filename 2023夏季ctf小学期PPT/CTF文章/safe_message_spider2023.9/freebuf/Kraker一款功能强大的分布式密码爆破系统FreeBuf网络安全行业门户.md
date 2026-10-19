![](https://image.3001.net/images/20210328/1616945114_60609fda2d31dd48c7431.png!small)

## 关于Kraker

Kraker是一款功能强大的分布式密码爆破系统，它允许我们在不同的服务器和工作站上轻松运行和管理hashcat。该工具使用起来非常简单，其设计意图主要有两点，即创建一个简单的工具来实现分布式密码哈希破解，并且具有较高容错性。

Kraker由两大组件组成，即服务器端和客户端代理，这两者通过一个REST API来通信交互。

Kraker目前仍处于积极开发状态，因此随时会更新更多的功能。如果你对Kraker有什么改进建议，或需要提交漏洞，可以直接与我们联系（[
_@_w34kp455_](https://twitter.com/w34kp455)和[
_@_asSheShouldBe_](https://twitter.com/asSheShouldBe)），或在本项目的GitHub上pull
request。

## 服务器端安装&配置

Kraker的服务器端基于Laravel开发，并且提供了Web接口来帮助用户创建暴力破解任务以及客户端代理的管理。安装与配置命令如下：

    
    
    sudo apt update
    
    sudo apt-get -y install unzip git
    
    curl -fsSL https://get.docker.com -o get-docker.sh
    
    sh get-docker.sh
    
    rm get-docker.sh
    
    sudo curl -L "https://github.com/docker/compose/releases/download/1.25.3/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    
    sudo chmod +x /usr/local/bin/docker-compose
    
    sudo systemctl enable docker
    
     
    
    git clone https://github.com/zzzteph/kraker
    
    cd kraker/server
    
    sudo docker-compose build app
    
    sudo docker-compose up -d
    
    sudo docker-compose exec app composer install
    
    sudo docker-compose exec app php artisan key:generate
    
    sudo docker-compose exec app php artisan migrate
    
    sudo docker-compose exec app php artisan db:seed --class=HashtypeSeeder
    
    sudo docker-compose exec app php artisan db:seed --class=UserSeeder

在浏览器中输入服务器端IP地址，然后输入下列登录凭证：

> 用户名：admin
>
> 密码：kraker

## 客户端代理安装&配置

Kraker的客户端代理基于.NET Core
5开发，并且支持在安装并配置好该框架环境的任意操作系统平台上运行，其中包括Linux、Windows和macOS。客户端代理能够响应并执行它从服务器端接收到的暴力破解任务。

如需客户端代理在主机系统上正常运行，我们需要先安装并配置好.NET Core 5框架环境，点击【[
_这里_](https://dotnet.microsoft.com/download/dotnet/5.0)】下载.NET Core 5。

Linux：【[ _传送门_](https://docs.microsoft.com/ru-ru/dotnet/core/install/linux)】

Windows：【[ _传送门_](https://dotnet.microsoft.com/download/dotnet/thank-you/runtime-5.0.4-windows-x64-installer)】

## 从源码构建

1、安装.NET Core 5 SDK，下面给出的是Linux安装样例：

    
    
    wget https://packages.microsoft.com/config/debian/10/packages-microsoft-prod.deb -O packages-microsoft-prod.deb
    
    sudo dpkg -i packages-microsoft-prod.deb
    
    sudo apt-get update
    
    sudo apt-get install -y apt-transport-https
    
    sudo apt-get update
    
    sudo apt-get install -y dotnet-sdk-5.0

2、从源码编译客户端代理，在命令行窗口中切换到代理目录下，然后运行下列命令：

    
    
    dotnet build --configuration Release

接下来，切换到Kracker.App/bin/Release/net5.0目录下，你将会看到构建好的项目。

3、我们需要从官方页面下载【[ _Hashcat_](https://hashcat.net/hashcat/)】，然后将其解压至代理目录中。

4、修改Kracker.App/bin/Release/net5.0目录中的appsettings.json文件，然后填写ServerURL和Hashcat.Path值：

    
    
    {
    
            "HashCat":{
    
            "Path": "/home/admin/Kraker/agent/Kracker.App/bin/Release/net5.0/hashcat/hashcat.bin", //hashcat path
    
                    "SilencePeriodBeforeKill": 5, //default - 60 minutes
    
                    "RepeatedStringsBeforeKill": 100, //defaut 1000 strings
    
                    "NeedForce": true,
    
                    "Options": "--quiet --status --status-timer=1 --machine-readable --logfile-disable --restore-disable --outfile-format=2"
    
            },
    
            "ServerUrl": "http://8.8.8.8/", //server url
    
            "InventoryCheckPeriod": 600,
    
            "HearbeatPeriod": 15
    
    }

5、创建一个wordlist和一个rule目录，将我们的字典和规则存放在里面。

6、运行Karker.app.exe或运行下列命令：

    
    
    dotnet run Kraker.app.dll

7、你可以直接将代理文件夹拷贝到其他服务器上，以方便进行配置和安装。

## 使用发布版本

预安装hashcat：【[ _传送门_](https://hashcat.net/hashcat/)】

规则集：【[ _传送门_](https://github.com/ttmyst/tmyst_rules)】

### 使用发布版本运行客户端代理

> 安装.NET Core 5运行时环境；
>
> 修改App/bin/Release/net5.0目录中的appsettings.json文件，然后填写ServerURL和Hashcat.Path值；
>
> 创建一个wordlist和一个rule目录，将我们的字典和规则存放在里面。你可以从【[
> _这里_](https://weakpass.com/)】找到合适你的字典文件。
>
> 运行app.exe或运行下列命令：
    
    
    dotnet run Kraker.app.dll

## 工具使用

演示GIF1：【[
_点我观看_](https://github.com/zzzteph/Kraker/raw/main/docs/pics/agent_setup.gif?raw=truehttps:/github.com/zzzteph/Kraker/raw/main/docs/pics/dotnet_install.gif?raw=true)】

演示GIF2：【[
_点我观看_](https://github.com/zzzteph/Kraker/raw/main/docs/pics/agent_setup.gif?raw=true)】

## 项目地址

Karker：【[ _GitHub传送门_](https://github.com/zzzteph/kraker)】

## 参考资料

[
_https://dotnet.microsoft.com/download/dotnet/5.0_](https://dotnet.microsoft.com/download/dotnet/5.0)

[ _https://docs.microsoft.com/ru-ru/dotnet/core/install/linux_](https://docs.microsoft.com/ru-ru/dotnet/core/install/linux)

[ _https://dotnet.microsoft.com/download/dotnet/thank-you/runtime-5.0.4-windows-x64-installer_](https://dotnet.microsoft.com/download/dotnet/thank-you/runtime-5.0.4-windows-x64-installer)

[ _https://hashcat.net/hashcat/_](https://hashcat.net/hashcat/)

[
_https://github.com/ttmyst/tmyst_rules_](https://github.com/ttmyst/tmyst_rules)

[ _https://weakpass.com/﻿_](https://weakpass.com/)


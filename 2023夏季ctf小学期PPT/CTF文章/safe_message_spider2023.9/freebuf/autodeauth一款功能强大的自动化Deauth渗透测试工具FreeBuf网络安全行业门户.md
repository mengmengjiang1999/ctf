## 关于autodeauth

autodeauth是一款功能强大的自动化Deauth渗透测试工具，该工具可以帮助广大研究人员以自动化的形式针对本地网络执行Deauth渗透测试，或者枚举公共网络。当前版本的autodeauth已在树莓派OS和Kali
Linux平台上进行过测试，之后的版本还将添加EAPOL包捕捉和路由信息提取等功能。

## 工具下载&安装

由于该工具基于Python开发，因此我们首先需要在本地设备上安装并配置好Python环境。接下来，使用下列命令将该项目源码克隆至本地：

    
    
    git clone https://github.com/Drew-Alleman/autodeauth.git

接下来，使用下列命令给工具的安装脚本提供可执行权限，然后执行setup.sh脚本即可：

    
    
    $ chmod +x setup.sh
    
    $ sudo ./setup.sh
    
     
    
    [*] This can be changed by editing /etc/systemd/system/autodeauth.service
    
    [?] Enter your WiFi interface to use with the autodeauth service: wlan0
    
    [*] Installed!, you can use sudo autodeauth -h to see available options.
    
    [*] Check the README for more infomation about configuring/starting the service

## 工具选项

    
    
    $ sudo autodeauth -h
    
            _       _       ___                _   _    
    
           /_\ _  _| |_ ___|   \ ___ __ _ _  _| |_| |_  
    
          / _ \ || |  _/ _ \ |) / -_) _` | || |  _| ' \
    
         /_/ \_\_,_|\__\___/___/\___\__,_|\_,_|\__|_||_|
    
     
    
    usage: autodeauth [-h] --interface INTERFACE [--blacklist BLACKLIST] [--whitelist WHITELIST] [--led LED] [--time TIME] [--random] [--ignore] [--count COUNT] [--verbose VERBOSE]
    
     
    
    Auto Deauth Tool
    
     
    
    options:
    
      -h, --help            显示工具帮助信息和退出
    
      --interface INTERFACE, -i INTERFACE
    
                           获取WiFi网络和发送Deauth包的接口
    
      --blacklist BLACKLIST, -b BLACKLIST
    
                            需要屏蔽的网络SSID/MAC地址列表（逗号分隔）
    
      --whitelist WHITELIST, -w WHITELIST
    
                            目标网络SSID/MAC地址列表（逗号分隔）
    
      --led LED, -l LED      Led针脚数量
    
      --time TIME, -t TIME   两个Deauth包发送的时间间隔，单位为秒，默认为0
    
      --random, -r           执行Deauth测试前随机化MAC地址
    
      --ignore           忽略MAC地址随机化时遇到的错误信息
    
      --count COUNT, -c COUNT
    
                            待发送的数据包数量，默认为5000
    
      --verbose VERBOSE, -v VERBOSE
    
                            开启Verbose模式，默认为0

## 工具使用

运行完工具的安装脚本之后，我们就可以在任意路径下直接运行autodeauth脚本了。

### 命令行

我们可以使用目标网络的MAC地址来代表需要测试的网络：

    
    
    $ sudo autodeauth -i wlan0 --blacklist FreeWiFi,E1:DB:12:2F:C1:57 -c 10000

### 服务

    
    
    $ sudo systemctl start autodeauth

### 数据存储

当autodeauth检测到一个目标网络之后，如果目标符合设置的黑名单/白名单配置，那么工具将会把目标网络的相关信息以JSON格式存储到/var/log/autodeauth/路径下：

    
    
    {
    
        "ssid": "MyWiFiNetwork",
    
        "mac_address": "10:0B:21:2E:C1:11",
    
        "channel": 1,
    
        "network.frequency": "2.412 GHz",
    
        "mode": "Master",
    
        "bitrates": [
    
            "6 Mb/s",
    
            "9 Mb/s",
    
            "12 Mb/s",
    
            "18 Mb/s",
    
            "24 Mb/s",
    
            "36 Mb/s",
    
            "48 Mb/s",
    
            "54 Mb/s"
    
        ],
    
        "encryption_type": "wpa2",
    
        "encrypted": true,
    
        "quality": "70/70",
    
        "signal": -35
    
    }

### 日志文件

    
    
    $ cat /var/log/autodeauth/log               
    
    2022-08-20 21:01:31 - Scanning for local networks
    
    2022-08-20 21:20:29 - Sending 5000 deauth frames to network: A0:63:91:D5:B8:76 -- MyWiFiNetwork
    
    2022-08-20 21:21:00 - Exiting/Cleaning up

### 编辑服务配置

如需修改autodeauth服务的配置，可以直接编辑/etc/systemd/system/autodeauth.service。假设我们需要将下列配置设置为一个服务：

    
    
    $ sudo autodeauth -i wlan0 --blacklist FreeWiFi,myWifi -c 10000
    
    
    $ vim /etc/systemd/system/autodeauth.service

那么我们只需要按下列形式修改ExecStart的值即可：

    
    
    ExecStart=/usr/bin/python3 /usr/local/bin/autodeauth -i wlan0 --blacklist FreeWiFi,myWifi -c 10000

## 许可证协议

本项目的开发与发布遵循[ _MIT_](https://github.com/Drew-Alleman/autodeauth/blob/main/LICENSE)开源许可证协议。

## 项目地址

 **autodeauth** ：【[ _GitHub传送门_](https://github.com/Drew-Alleman/autodeauth)】


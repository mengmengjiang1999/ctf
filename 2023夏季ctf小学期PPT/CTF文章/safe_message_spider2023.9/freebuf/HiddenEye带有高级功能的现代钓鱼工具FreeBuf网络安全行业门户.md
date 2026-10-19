![](https://image.3001.net/images/20190822/1566405303_5d5d72b7997d7.png!small)

## HiddenEye

HiddenEye是一款带有高级功能的现代网络钓鱼工具，目前该工具仅支持Android平台，广大研究人员可以使用该工具来进行网络钓鱼测试。

 **开发者 &代码贡献**

> ANONUD4Y (<https://github.com/An0nUD4Y>)
>
> USAMA ABDUL SATTAR (<https://github.com/usama7628674>)
>
> sTiKyt (<https://github.com/sTiKyt>)
>
> UNDEADSEC (<https://github.com/UndeadSec>)
>
> Micrafast (<https://github.com/Micrafast>)

___________ (下一个就是你)

## 工具运行截图（Android用户端）

![](https://image.3001.net/images/20190822/1566405316_5d5d72c41ff67.png!small)

## 已测试的平台

Kali Linux

Parrot OS

Linux Mint - 18.3 Sylvia

Ubuntu - 16.04.3 LTS

MacOS High Sierra

Arch Linux

Manjaro XFCE Edition 17.1.12

Black Arch

### 工具运行条件

Python3

Wget

PHP

Sudo

## 工具安装

BlackArch官方代码库：

    
    
    sudo pacman -S hidden-eye
    
    sudo hidden-eye

GitHub代码库克隆：

> git clone <https://github.com/DarkSecDevelopers/HiddenEye.git>

## 工具运行（Linux）

    
    
    chmod 777 HiddenEye  
    
    
    sudo apt install python3-pip  
    
    
    cd HiddenEye  
    
    
    sudo pip3 install -r requirements.txt  
    
    
    python3 HiddenEye.py

## 工具运行（Arch Linux或Manjaro）

    
    
    chmod 777 HiddenEye
    
    sudo pacman -Syu
    
    sudo pacman -S python-pip
    
    cd HiddenEye
    
    sudo pip3 install -r requirements.txt
    
    sudo python3 HiddenEye.py

## 针对Android用户

### 用户空间App安装

首先，从应用商店安装用户空间App，然后安装并配置Kali，接下来设置ssh用户名和密码。Kali运行之后，它将会要求用户输入ssh密码以及sudo密码，然后运行aptupdate来更新系统。操作命令如下：

    
    
    apt install python3 && python3-pip && unzip && php&& git
    
    git clone<https://github.com/DarkSecDevelopers/HiddenEye.git>
    
    chmod 777 HiddenEye
    
    cd HiddenEye
    
    pip3 install -r requirements.txt
    
    python3 HiddenEye.py

### TERMUX App安装

从PlayStore安装{Termux}，然后运行下列命令：

    
    
    pkg install git python php curl openssh grep
    
    pip3 install wget
    
    git clone -b Termux-Support-Branch<https://github.com/DarkSecDevelopers/HiddenEye.git>
    
    chmod 777 HiddenEye
    
    cd HiddenEye
    
    python HiddenEye.py

## 支持的钓鱼页面

1、 Facebook

2、 Google

3、 LinkedIn

4、 Github

5、 Stackoverflow

6、 Wordpress

7、 Twitter

8、 Instagram

9、 SNAPCHAT

10、YAHOO

11、TWITCH

12、MICROSOFT

13、STEAM

14、VK

15、ICLOUD

16、GitLab

17、NetFlix

18、Origin

19、Pinterest

20、Protonmail

21、Spotify

22、Quora

23、PornHub

24、Adobe

25、Badoo

26、CryptoCurrency

27、DevianArt

28、DropBox

29、eBay

30、MySpace

31、PayPal

32、Shopify

33、Verizon

34、Yandex

35、Reddit

## ASCII错误修复

找到dpkg-reconfigure，选择"All
locales"，然后选择"en_US.UTF-8"。重启设备之后，打开命令行窗口，然后运行命令："locale"。接下来，你将会使用"en_US.UTF-8"来作为默认语言，而不是之前的POSIX了。

项目地址

HiddenEye：【[GitHub传送门](https://github.com/DarkSecDevelopers/HiddenEye)】

 ***
参考来源：[DarkSecDevelopers](https://github.com/DarkSecDevelopers/HiddenEye)，Alpha_h4ck编译整理，转载请注明来自FreeBuf.COM**


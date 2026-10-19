![](https://image.3001.net/images/20220315/1647333927_62305227999762a5011a2.png!small)

## 关于Chaya

Chaya是一款功能强大的高级图像隐写工具，Chaya可以通过隐写术、数据加密和压缩技术保护广大用户的隐私安全。该工具使用了AES-256-GCM加密技术来对所有的Payload进行有效加密，并使用了LSB-LPS隐写技术来将加密数据嵌入到图像文件中，然后使用FLIF进行数据压缩，最后通过执行无损压缩来绕过各种数据检测。

Chaya专为用户隐私安全而生，并得到了社区中大量安全研究人员的支持，跟其他的FFOS图像隐写工具相比，Chaya已被证明是迄今为止最有效的图像隐写工具。

## Chaya的优势在哪里？

> 1、使用了目前社区中绝大多数公开可用的反隐写工具进行测试，检测率为0%。
>
> 2、100%的数据保留率，几乎与标准LSB技术和LBS-LPS的能力相同。
>
> 3、使用了优秀的透明加密技术。

## 安全性

除非Python的库或Python本身存在安全漏洞，否则哪怕你使用了超级计算机，也是无法破解Chaya的。LSB-LPS技术将花费大量时间来使用更大的图形图像来抵御暴力破解攻击，爆破过程中需要精确地处理每一个X、Y坐标组合，如果你想要通过机器学习方式实现破解的话，也只是徒劳，因为这里只能使用自然语言来处理Chaya的数据。因此，无论我们使用哪种暴力破解技术，得到的永远都只能是密文。毫无疑问，Chaya提供了完整的机密性服务。

## 功能介绍

> 支持AES-256-GCM加密
>
> 支持标准LSB隐写术
>
> 支持LSB-LPS隐写术
>
> 支持FLIF无损压缩
>
> 将数据日志加密存储为JSON
>
> 为你的实验提供分析支持
>
> 支持JSON到CSV的转换
>
> 详细的密码数据日志
>
> 工作区清理工具
>
> 易于安装、配置和初始化
>
> 附带更新工具

## 工具安装

由于该工具基于Python 3开发，因此我们首先需要在本地设备上安装并配置好Python 3环境。接下来，广大研究人员就可以使用下列命令来安装Chaya了。

### One-Line安装

 **Ubuntu发行版系统：**

    
    
    sudo apt install python3-pip && sudo apt install git && git clone --depth=1 https://github.com/xerohackcom/Chaya.git && cd Chaya && pip3 install -r requirements.txt && sudo apt update && sudo apt-add-repository ppa:linuxuprising/libpng12 && sudo apt update && sudo apt install -y libpng12-0
    

**Debian发行版系统：**

    
    
    sudo apt install python3-pip && sudo apt install git && git clone --depth=1 https://github.com/xerohackcom/Chaya.git && cd Chaya && pip3 install -r requirements.txt && sudo apt update && sudo apt install build-essential devscripts && cd ~/ && sudo touch /etc/apt/sources.list.d/libpng12.list && echo "deb https://ppa.launchpadcontent.net/linuxuprising/libpng12/ubuntu hirsute main" | sudo tee -a /etc/apt/sources.list.d/libpng12.list && echo "deb-src https://ppa.launchpadcontent.net/linuxuprising/libpng12/ubuntu hirsute main" | sudo tee -a /etc/apt/sources.list.d/libpng12.list && sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys 1CC3D16E460A94EE17FE581CEA8CACC073C3DB2A && sudo apt update && sudo apt install -y libpng12-0
    

### Installer.py安装

除此之外，我们还可以使用该项目提供的installer.py脚本来安装Chaya以及Chaya所需的依赖组件：

    
    
    sudo apt install python3-pip && sudo apt install git && git clone --depth=1 https://github.com/xerohackcom/Chaya.git && cd Chaya
    

**Ubuntu发行版系统：**

    
    
    python3 installer.py --ubuntu
    

**Debian发行版系统：**

    
    
    python3 installer.py --debian
    

## 工具使用

### 帮助菜单

    
    
    python3 chaya.py --help
    

### 自动化操作

首先，我们需要往“/autoexp/image_raw/”里面添加几张图片（png格式）。

接下来，移除“/autoexp”目录中所有子文件夹中的txt文本文件，以避免出现执行错误。

最后，运行下列命令即可：

    
    
    python3 chaya.py -enc
    

## 输出数据

> 加密数据 + 隐写图片 -> /autoexp/image_steg/
>
> 加密数据 + 隐写 + 压缩图片 -> /autoexp/image_steg_comp/
>
> 加密数据 -> /appdata/cipher_data.json
>
> 分析数据 -> /appdata/analysis_results_enc.json

## 工具运行截图

![](https://image.3001.net/images/20220315/1647334046_6230529e1918778645280.png!small)

## 许可证协议

本项目的开发与发布遵循[ _AGPLv_
_3_](https://github.com/xerohackcom/Chaya/blob/main/LICENSE)开源许可证协议。

## 项目地址

 **Chaya：** 【[ _GitHub传送门_](https://github.com/xerohackcom/chaya)】

## 参考资料

> [ _https://www.un.org/en/about-us/universal-declaration-of-human-> rights_](https://www.un.org/en/about-us/universal-declaration-of-human-> rights)
>
> [
> _https://en.wiki*pedia.org/wiki/International_Covenant_on_Civil_and_Political_Rights_](https://en.wikipedia.org/wiki/International_Covenant_on_Civil_and_Political_Rights)


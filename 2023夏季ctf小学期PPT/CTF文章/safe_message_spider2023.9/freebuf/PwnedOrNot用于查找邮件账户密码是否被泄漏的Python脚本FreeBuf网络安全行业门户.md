**![68747470733a2f2f692e696d6775722e636f6d2f7867616f6a464d2e706e67.png](https://image.3001.net/images/20181022/1540164988_5bcd0d7ca05e9.png!small)**

**PwnedOrNot是一个使用[haveibeenpwned](https://haveibeenpwned.com/API/v2) v2
api来测试电子邮件帐户，并尝试在Pastebin Dumps中查找其密码的Python脚本。**

## 特性

haveibeenpwned提供了大量关于受感染电子邮件的信息，脚本会为我们展示其中一些关键信息：

> 泄露名称
>
> 域名
>
> 泄露日期
>
> Fabrication状态
>
> Verification状态
>
> Retirement状态
>
> Spam状态

在获取到这些信息后，如果Pastebin Dumps可访问且包含了目标电子邮件帐户的密码，那么pwnedOrNot将可以为我们轻松的找到该密码。

目前该脚本已在以下平台进行测试：

> Kali Linux 18.2
>
> Ubuntu 18.04
>
> Kali Nethunter
>
> Termux

## 安装

 **Ubuntu / Kali Linux / Nethunter / Termux**

    
    
    chmod 777 install.sh
    ./install.sh

##
**![68747470733a2f2f61736369696e656d612e6f72672f612f3230303232312e706e67.png](https://image.3001.net/images/20181022/1540165016_5bcd0d986a574.png!small)**

##  **使用**

    
    
    python pwnedornot.py -h
    usage: pwnedornot.py [-h] [-e EMAIL] [-f FILE]
    
    optional arguments:
      -h, --help              显示帮助信息并退出
      -e EMAIL, --email EMAIL 你想要测试的目标Email账户
      -f FILE, --file FILE    加载包含多个Email账户的文件

##
![68747470733a2f2f61736369696e656d612e6f72672f612f3230303232352e706e67.png](https://image.3001.net/images/20181022/1540165034_5bcd0daaec5d2.png!small)

## Demo

 ***参考来源：[GitHub](https://github.com/thewhiteh4t/pwnedOrNot)，
FB小编secist编译，转载请注明来自FreeBuf.COM**


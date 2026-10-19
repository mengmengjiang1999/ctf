## 一、漏洞详情

在sudo解析命令行参数的方式中发现了基于堆的缓冲区溢出。任何本地用户（普通用户和系统用户，sudoer和非sudoers）都可以利用此漏洞，而无需进行身份验证，攻击者不需要知道用户的密码。成功利用此漏洞可以获得root权限。

## 二、影响版本

\- sudo:sudo: 1.8.2 - 1.8.31p2

\- sudo:sudo: 1.9.0 - 1.9.5p1

## 三、漏洞环境搭建

备注以非root用户登录系统，并使用命令sudoedit -s /

如果响应一个以sudoedit:开头的报错，那么表明存在漏洞。

如果响应一个以usage:开头的报错，那么表明补丁已经生效

1、我电脑本来安装的ubuntu版本是04，sudo 版本为version 1.8.31，在漏洞影响版本之内，但是通过sudoedit -s
/命令查看并不存在Sudo 堆缓冲区溢出漏洞

![1612168391_6017bcc72546cc6a4ecbd.png!small](https://image.3001.net/images/20210201/1612168391_6017bcc72546cc6a4ecbd.png!small)

图一：ubuntu20.04版本信息

2、后来从[https://releases.ubuntu.com/18.04.5/ubuntu-18.04.5-desktop-amd64.iso下载0.4](https://releases.ubuntu.com/18.04.5/ubuntu-18.04.5-desktop-amd64.iso%E4%B8%8B%E8%BD%BD18.0.4)版本后存在此漏洞![1612168440_6017bcf88f6f4340f95e3.png!small?1612168440187](https://image.3001.net/images/20210201/1612168440_6017bcf88f6f4340f95e3.png!small?1612168440187)

图二：ubuntu 18.0.4版本信息

## 四、漏洞复现

1、从github下载漏洞exp:https://codeload.github.com/blasty/CVE-2021-3156/zip/main,将下载好的文件解压，使用make进行编译，否则编译失败（编译之前需要安装make、make-guild、gcc组件）

![1612168512_6017bd400a749915cb525.png!small?1612168511628](https://image.3001.net/images/20210201/1612168512_6017bd400a749915cb525.png!small?1612168511628)

图3：安装make

![1612168524_6017bd4cd6953ab2168b0.png!small?1612168524271](https://image.3001.net/images/20210201/1612168524_6017bd4cd6953ab2168b0.png!small?1612168524271)

图四：安装make-guild

![1612168535_6017bd57d7df0d844042a.png!small?1612168535525](https://image.3001.net/images/20210201/1612168535_6017bd57d7df0d844042a.png!small?1612168535525)

图五：安装gcc

2、进入解压文件目录下，使用make命令进行编译，然后执行./sudo-hax-me-a-sandwich
命令，会提示选择相应的系统，这边使用的是ubuntu 18.0.4版本，直接在./sudo-hax-me-a-sandwich后面加上0执行，最终获得root权限

![1612168557_6017bd6d1ae9564b1ac65.png!small?1612168556524](https://image.3001.net/images/20210201/1612168557_6017bd6d1ae9564b1ac65.png!small?1612168556524)

图六：exp支持的系统版本

![1612168563_6017bd73f2061df598f38.png!small?1612168563477](https://image.3001.net/images/20210201/1612168563_6017bd73f2061df598f38.png!small?1612168563477)

图七：获得root权限

3、此漏洞可以用于本地提权，感兴趣的朋友可以尝试在这上面使用搭建vulhub漏洞，获取到一个低权限账户后进行本地提权

## 修复建议

下载升级sudo软件包，下载链接为：

sudo软件包下载地址

https://www.sudo.ws/dist/


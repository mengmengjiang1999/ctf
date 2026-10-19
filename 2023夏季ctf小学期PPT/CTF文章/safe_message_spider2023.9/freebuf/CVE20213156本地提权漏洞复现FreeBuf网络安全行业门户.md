## ****0x**** ** **00**** ** **漏洞简述****

Sudo是一个功能强大的工具，其允许普通用户执行root权限命令，大多数基于Unix和Linux的操作系统都包含sudo。

2021年01月26日，sudo被披露存在一个基于堆的缓冲区溢出漏洞（CVE-2021-3156，该漏洞被命名为“Baron
Samedit”），可导致本地权限提升。

当在类Unix的操作系统上执行命令时，非root用户可以使用sudo命令来以root用户身份执行命令。由于sudo错误地在参数中转义了反斜杠导致堆缓冲区溢出，从而允许任何本地用户（无论是否在sudoers文件中）获得root权限，无需进行身份验证，且攻击者不需要知道用户密码。

安全研究人员于1月26日公开披露了此漏洞，并表示该漏洞已经隐藏了近十年。

##  ** **0x**** ** **01**** ** **影响版本****

Sudo 1.8.2 - 1.8.31p2

Sudo 1.9.0 - 1.9.5p1

测试系统是否易受此漏洞影响：

> 1.以非root用户身份登录系统。
>
> 2.运行命令“sudoedit -s /”
>
> 3.如果出现以“ sudoedit：”开头的错误响应，则系统受到此漏洞影响；如果出现以“ usage：”开头的错误响应，则表示该漏洞已被补丁修复。

![1619310443_6084b76b79e484fdaf194.png!small](https://image.3001.net/images/20210425/1619310443_6084b76b79e484fdaf194.png!small)

#  ** **0**** ** **x02**** ** **漏洞复现****

1.部署虚拟机环境

![1619310487_6084b7972df1534c4f888.png!small](https://image.3001.net/images/20210425/1619310487_6084b7972df1534c4f888.png!small)

2.以普通用户通过ssh登录到服务器

![1619310535_6084b7c7622691c9c2e1e.png!small](https://image.3001.net/images/20210425/1619310535_6084b7c7622691c9c2e1e.png!small)

3.在普通用户权限上，输入：sudoedit -s /

![1619310583_6084b7f706b272d254edd.png!small](https://image.3001.net/images/20210425/1619310583_6084b7f706b272d254edd.png!small)

4.如果显示sudoedit: /: not a regular file，则表示该漏洞存在

5.下载漏洞poc：

https://haxx.in/CVE-2021-3156_nss_poc_ubuntu.tar.gz

6.上传poc到目标服务器，给予权限，然后执行  
make &&./sudo-hax-me-a-sandwich 0

![1619310677_6084b8556ddff4481b8c1.png!small](https://image.3001.net/images/20210425/1619310677_6084b8556ddff4481b8c1.png!small)

有#表示漏洞利用成功。

查看是否是root权限

![1619310705_6084b871b6dd4413ccff0.png!small](https://image.3001.net/images/20210425/1619310705_6084b871b6dd4413ccff0.png!small)

查看系统进程

![1619310727_6084b887221c7cddea38a.png!small](https://image.3001.net/images/20210425/1619310727_6084b887221c7cddea38a.png!small)

##  ** **0**** ** **x03**** ** **修复建议****

建议及时升级sudo至最新版本。

下载链接：

https://www.sudo.ws/dist/

#  ** **0**** ** **x04**** ** **参考链接****

https://www.venustech.com.cn/new_type/aqtg/20210127/22339.html


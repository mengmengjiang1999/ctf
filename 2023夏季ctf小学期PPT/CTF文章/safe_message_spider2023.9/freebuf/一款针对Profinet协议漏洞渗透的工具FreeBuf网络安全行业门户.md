***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

 **PROFINET由IP国际组织推出，是新一代基于工业以太网技术自动化总线标准，PROFINET-DCP是发现和基本配置协议，用于标识与查询有无指定IP地址节点，然后配置IP地址、默认网关、子网掩码。DCP是标准的PROFINET功能，可以读写设备与网络地址相关参数。由于只能在一个局域网中使用，通过实时通道传输，使用DCP协议可以实现不需要额外组态工程操作就能替换设备。**

##  PROFINET-DCP set ip流程

PROFINET-DCP设置IP地址流程如下图所示：

![image.png](https://image.3001.net/images/20190509/1557365437_5cd382bdf1ac9.png!small)

步骤  |  具体说明  
---|---  
1  |  控制器在网内以设备名为参数广播DCP_Identify.req请求，确认设备是否存在  
2  |  设备接收到请求，检查其中的设备名是否与设备自身名字匹配  
3  |  如果匹配则发送DCP_Identify.rsp响应控制器请求，否则不做处理  
4  |  控制器收到设备回复后，将设备MAC地址作为以太网报文的目标地址  
5  |  控制器将IP地址、子网掩码与网关作为参数发送报文DCP_Set.req给设备  
6  |  设备设置IP地址等参数完毕后，发送DCP_Set.rsp给控制器  
  
由于PROFINET-DCP为二层协议，本身缺乏鉴权机制，导致攻击者也是利用这个流程来篡改工控设备IP地址。

##  ISF工具漏洞利用PROFINET-DCP

工具介绍：

ISF是一款针对工业控制系统的漏洞利用框架，它是一款针对工业控制系统的漏洞利用框架。该工具基于开源项目routersploit，采用Python语言开发。ISF分为两个模块：工控协议模块与工控协议客户端模块，分别用于测试工控协议是否存在漏洞与模拟客户端数据通信。

ISF漏洞利用PROFINET-DCP篡改工控设备IP方法与说明：

###  使用Profinet set ip module

通过运行pythonisf.py启动isf，通过search命令来查找profinet的漏洞利用模块然后用use命令选择profinet_set_ip漏洞模块。具体的操作命令如下图所示：

![image.png](https://image.3001.net/images/20190509/1557365486_5cd382ee42c8e.png!small)

###  设置漏洞利用参数：

首先用show options命令，查看漏洞利用操作选项，如下图

![image.png](https://image.3001.net/images/20190509/1557365506_5cd383027d05b.png!small)

target为要修改目标机的mac地址，target_ip为想要设置的ip地址，nic为通信的网卡

第一步：由于Profinet dcp是以太网协议，因此我们首先要设置用哪个网口来发送和接收数据包。如下图所示：

![image.png](https://image.3001.net/images/20190509/1557365548_5cd3832c0c149.png!small)

第二步：设置目标机Mac地址

如果此时不知道目标机的Mac地址，可以运用scan命令来进行局域网设备探测，Device Type为工控设备硬件类型。如下图所示：

![image.png](https://image.3001.net/images/20190509/1557365686_5cd383b659b98.png!small)

探测到目标机mac地址后，设置target，如下图所示：

![image.png](https://image.3001.net/images/20190509/1557365760_5cd3840022018.png!small)

第三步：设置想要篡改的ip地址、子网掩码、网关，如下图所示：

![image.png](https://image.3001.net/images/20190509/1557365771_5cd3840b71bcd.png!small)

第四步：执行漏洞利用：

运行run命令，执行漏洞利用，篡改工控设备IP，如下图所示：

![image.png](https://image.3001.net/images/20190509/1557365788_5cd3841c56330.png!small)

###  测试结论

通过以上ISF漏洞利用测试与分析，发现PROFINET-DCP协议存在安全漏洞，没有鉴权的识别，让攻击者可以扫描局域网内工控设备的IP地址，从而对工控设备IP地址进行篡改。

***本文作者：zoucl123，转载请注明来自FreeBuf.COM**


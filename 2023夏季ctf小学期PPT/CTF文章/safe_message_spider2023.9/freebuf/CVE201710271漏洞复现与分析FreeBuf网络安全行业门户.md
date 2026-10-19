## 漏洞介绍

Weblogic的WLS
Security组件对外提供webservice服务，其中使用了XMLDecoder来解析用户传入的XML数据，在解析的过程中出现反序列化漏洞，导致可执行任意命令。攻击者发送精心构造的xml数据甚至能通过反弹shell拿到权限。

## 影响版本

OracleWebLogic Server10.3.6.0.0  
OracleWebLogic Server12.1.3.0.0  
OracleWebLogic Server12.2.1.1.0  
OracleWebLogic Server12.2.1.2.0

## 漏洞复现环境

攻击方：kali 2021

服务端：vulhub的weblogic的CVE-2017-10271环境

## 漏洞复现

攻击方使用Burp发送反弹shell的payload：

![](https://image.3001.net/images/20211105/1636096769_6184db01563c6f8fed1f5.jpg!small)

成功得到shell：

![1636092073_6184c8a9f3cbf9c6823a3.png!small](https://image.3001.net/images/20211105/1636092073_6184c8a9f3cbf9c6823a3.png!small)

## POC

https://github.com/NingKn/CVE_EXP/blob/main/cve-2017-10271/cve-2017-10271.py

## 漏洞分析

CVE-2017-10271漏洞是WebLogic Server WLS组件的远程命令执行漏洞，触发漏洞url如下：

http://192.168.124.42:7001/wls-wsat/CoordinatorPortType
发送post数据包，通过构造SOAP（XML）格式的请求，在解析的过程中导致XMLDecoder反序列化漏洞。

  1. 在weblogic/wsee/jaxws/workcontext/WorkContextServerTube类的processRequest方法中，处理我们发送的POST数据包中的SOAP（XML）数据。var1即是传入的SOAP数据，我们idea配置好远程调试并且开启debug后，在processRequest方法中下断点：![](https://image.3001.net/images/20211105/1636096910_6184db8e3c6aa342faad6.jpg!small)
  2. Burp通过post发送数据包后，idea停留在断点处，查看其中的var1变量既是我们发送的xml数据：![](https://image.3001.net/images/20211105/1636097000_6184dbe8d3f8053de7d73.jpg!small)

  3. 代码往下走，进入readHeaderOld方法，跟进前我们查看var3变量的信息：![](https://image.3001.net/images/20211105/1636097234_6184dcd2bc7a155851106.jpg!small)

![](https://image.3001.net/images/20211105/1636097213_6184dcbdc4967f86d6414.jpg!small)

  4. 跟进readHeaderOld方法，发现这里其实就是进行了一波转换，生成了WorkContextXmlInputAdapert var6对象，下图是该方法中的var4变量存放了的xml数据：![](https://image.3001.net/images/20211105/1636097266_6184dcf2689eec53ae5be.jpg!small)
  5. Var6中的buf集合就是var4中的数据，及我们传输的xml：![](https://image.3001.net/images/20211105/1636097296_6184dd108ebd06a906389.jpg!small)

  6. 跟进receive方法，var1实参是上面var6形参：![](https://image.3001.net/images/20211105/1636097377_6184dd61e8ecb192c8b11.jpg!small)

  7. 跟进var2的receiveRequest方法：![](https://image.3001.net/images/20211105/1636097386_6184dd6a73fb61262e180.jpg!small)

  8. 这里的var1就是上面的var1形参：![](https://image.3001.net/images/20211105/1636097396_6184dd74ceb01ab9cdcd0.jpg!small)

  9. 跟进receiveRequest方法：![1636092636_6184cadc0de543494253b.png!small](https://image.3001.net/images/20211105/1636092636_6184cadc0de543494253b.png!small)

  10. 跟进readEntry方法，var0存放了xml数据：![](https://image.3001.net/images/20211105/1636097683_6184de93395e409d6def9.jpg!small)

  11. 跟进var0的readUTF方法：![](https://image.3001.net/images/20211105/1636097740_6184decc12339fed59b00.jpg!small)

直接调用了xmlDecoder.readObject方法，产生漏洞。

## 总结：

XMLDecoder来解析用户传入的XML数据，在解析的过程中出现反序列化漏洞，导致可执行任意命令执行。

## 漏洞修复：

方法一：删除wls-wsat组件，然后重启weblogic

方法二：[官网下载，打补丁](https://www.oracle.com/security-alerts/cpuoct2017.html#AppendixFMW)


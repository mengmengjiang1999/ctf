## **情报背景**

该项目由名为FuckRedTeam 的 github 用户于2022年7月24日发布，项目描述为国内某安全厂商产品的远程执行漏洞脚本。项目会从常用
UserAgent
库中加载fake_useragent包，实际上则被导入了投毒的fake_useragant-0.1.12包，当前投毒的fake_useragant-0.1.12已经被从pypi的官方库中删除。

![1660209550_62f4c98e011e4aff3a2cc.png!small?1660209551467](https://image.3001.net/images/20220811/1660209550_62f4c98e011e4aff3a2cc.png!small?1660209551467)

 **组织名称**

|

未知  
  
---|---  
  
 **关联组织**

|

未知  
  
 **战术标签**

|

供应链、投毒、钓鱼  
  
 **技术标签**

|

python  
  
 **情报来源**

|

https://github.com/FuckRedTeam/360tianqingRCE  
  
##  **01** 攻击技术分析

 **亮点1 仿冒fake_useragent进行投毒**

引入的恶意fake_useragant，注意官方的拼写为fake_useragent（e被替换成a）

![1660209569_62f4c9a1506df39da0ed8.png!small?1660209570758](https://image.3001.net/images/20220811/1660209569_62f4c9a1506df39da0ed8.png!small?1660209570758)

fake_useragant中的urlib2.py被投毒

![1660209584_62f4c9b0d202ced2deb54.png!small?1660209586220](https://image.3001.net/images/20220811/1660209584_62f4c9b0d202ced2deb54.png!small?1660209586220)

疑似加密的恶意代码

![1660209601_62f4c9c145e25ee13dc9e.png!small?1660209603942](https://image.3001.net/images/20220811/1660209601_62f4c9c145e25ee13dc9e.png!small?1660209603942)

解密后的执行代码，从远程加载运行后续代码

![1660209634_62f4c9e25f88830a9c48e.png!small?1660209635743](https://image.3001.net/images/20220811/1660209634_62f4c9e25f88830a9c48e.png!small?1660209635743)

##  **亮点2 套娃解密shellcode**

PNG文件经过解密后，又是一段执行代码，经过2次套娃解密，最终将解密出shellcode创建线程加载运行。

整体步骤如下：

1\. urlib2.py 解密加密代码，拉取解密远程的png文件，并执行解密后的二段代码

2\. 二段代码使用AES解密执行代码，并执行

3\. 再次使用AES解密出最终的shellcode，申请内存并创建进程执行

![1660209658_62f4c9fa65ad9bf5881cf.png!small?1660209659829](https://image.3001.net/images/20220811/1660209658_62f4c9fa65ad9bf5881cf.png!small?1660209659829)

png文件解密结果，其中使用了AES库进行下一段解密

![1660209670_62f4ca06f4135c6e3fe97.png!small?1660209672498](https://image.3001.net/images/20220811/1660209670_62f4ca06f4135c6e3fe97.png!small?1660209672498)

创建的线程来运行解密后的shellcode

![1660209682_62f4ca125de23b5f6dd06.png!small?1660209684129](https://image.3001.net/images/20220811/1660209682_62f4ca125de23b5f6dd06.png!small?1660209684129)

##  **02 总结**

供应链攻击防不胜防。近期投毒事件频发，此次投毒绝不是唯一一次，大家在使用工具一定要擦亮眼睛，不要使用来源不明的工具软件。


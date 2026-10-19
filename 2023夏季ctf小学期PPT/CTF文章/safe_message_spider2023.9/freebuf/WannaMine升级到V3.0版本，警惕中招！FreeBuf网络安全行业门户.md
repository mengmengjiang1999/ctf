**近日，多个企业反馈大量主机和服务存在卡顿和蓝屏现象，在寻求深信服协助后，部署了深信服终端检测平台（EDR），使用EDR进行全网扫描发现大量主机感染了相同的病毒。**

深信服安全团队研究发现，该企业用户中的是最新型的WannaMine变种，之前有WannaMine1.0和WannaMine2.0版本。

此病毒变种，是基于WannaMine改造，加入了一些免杀技术，传播机制与WannaCry勒索病毒一致（可在局域网内，通过SMB快速横向扩散），故我们将其命名WannaMine3.0。

国内外发现的首例，国内安全厂商还没有相关报道。

我们对捕获的样本进行分析，发现其接入站点已变更为codidled.com。经查验，这是一个2018年11月11日刚申请注册的域名，也就是说，黑客重新编译WannaMine3.0的时间锁定为2018年11月11日或以后。

![1.png](https://image.3001.net/images/20181122/1542853547_5bf613ab8e056.png!small)

近日，多家医院先后中招，我们对其传播速度深感惊讶！未来，感染面也会跟原始变种WannaMine1.0和WannaMine2.0一样惊人！

##  **0x01** **攻击场景**

此次攻击，沿用了WannaMine1.0和WannaMine2.0的精心设计，涉及的病毒模块多，感染面广，关系复杂。

![2.png](https://image.3001.net/images/20181122/1542853556_5bf613b41516b.png!small)

所不同的是，原始“压缩包”已经变为 **MarsTraceDiagnostics.xml**
，其含有所需要的所有攻击组件。旧病毒的压缩包是可以直接解压的，但此变种做了免杀，MarsTraceDiagnostics.xml是一个特殊的数据包，需要病毒自己才能分离出各个组件。其组件有
**spoolsv.exe** 、 **snmpstorsrv.dll** 等病毒文件，此外，还有“永恒之蓝”漏洞攻击工具集（
**svchost.exe** 、 **spoolsv.exe** 、 **x86.dll/x64.dll** 等）。

本文所述病毒文件，释放在下列文件目录中：

    
    
    C:\Windows\System32\MarsTraceDiagnostics.xml
    
    C:\Windows\AppDiagnostics\
    
    C:\Windows\System32\TrustedHostex.exe

![3.png](https://image.3001.net/images/20181122/1542853566_5bf613be849d7.png!small)

### 攻击顺序：

1.有一个主服务 **snmpstorsrv** ,对应动态库为 **snmpstorsrv.dll**
（由系统进程svchost.exe加载），每次都能开机启动，启动后加载 **spoolsv.exe** 。

2. **spoolsv.exe** 对局域网进行445端口扫描，确定可攻击的内网主机。同时启动漏洞攻击程序 **svchost.exe** 和 **spoolsv.exe** **（另外一个病毒文件）** 。

3. **svchost.exe** 执行“永恒之蓝”漏洞溢出攻击（目的IP由第2步确认），成功后 **spoolsv.exe** (NSA黑客工具包DoublePulsar后门）安装后门，加载payload（ **x86.dll/x64.dll** ）。

4. **payload** （ **x86.dll/x64.dll** ）执行后，负责将 **MarsTraceDiagnostics.xml** 从本地复制到目的IP主机，再解压该文件，注册 **snmpstorsrv** 主服务，启动 **spoolsv** 执行攻击（每感染一台，都重复步骤1、2、3、4）。

![4.jpg](https://image.3001.net/images/20181122/1542853578_5bf613ca31409.jpg!small)

##  **0x02** **清理早期WannaMine版本**

WannaMine3.0特意做了清理早期WannaMine版本的动作，包括删除或者停掉WannaMine1.0和WannaMine2.0相关的文件、服务和计划任务等。

清理掉之前WannaMine版本的病毒样本，如下所示：

![5.png](https://image.3001.net/images/20181122/1542853590_5bf613d66bf1a.png!small)

1.停掉wmassrv服务，如下所示：

![6.png](https://image.3001.net/images/20181122/1542853601_5bf613e13e826.png!small)

2.删除UPnPHostServices计划任务，如下所示：

![7.png](https://image.3001.net/images/20181122/1542853617_5bf613f1b6b15.png!small)

3.删除EnrollCertXaml.dll，如下所示：

![8.png](https://image.3001.net/images/20181122/1542853629_5bf613fd610ee.png!small)

4.结束永恒之蓝攻击程序以及挖矿程序进程，并删除相应的文件，如下所示：

![9.png](https://image.3001.net/images/20181122/1542853638_5bf6140645d1c.png!small)

相应的进程文件如下：

    
    
    C:\Windows\SpeechsTracing\spoolsv.exe
    
    C:\Windows\System32\TasksHostServices.exe
    
    C:\Windows\SpeechsTracing\Microsoft\svchost.exe
    
    C:\Windows\SpeechsTracing\Microsoft\spoolsv.exe

5.删除之前wmassrv.dll文件，如下所示：

![10.png](https://image.3001.net/images/20181122/1542853649_5bf6141160875.png!small)

6.遍历之前版本目录下的文件，然后删除，如下所示：

![11.png](https://image.3001.net/images/20181122/1542853661_5bf6141d0a13f.png!small)

相应的目录，如下所示：

    
    
    C:\Windows\SpeechsTracing\
    
    C:\Windows\SpeechsTracing\Microsoft\

7.卸载之前的挖矿模块HalPluginsServices.dll，如下所示：

![12.png](https://image.3001.net/images/20181122/1542853676_5bf6142c49f08.png!small)

结束rundll32.exe进程，如下所示：

![13.png](https://image.3001.net/images/20181122/1542853685_5bf6143561dd8.png!small)

并删除相应挖矿的文件。

##  **0x03** **挖矿**

WannaMine3.0沿用WannaMine1.0和WannaMine2.0的套路，同样是瞄准了大规模的集体挖矿（利用了“永恒之蓝”漏洞的便利，迅速使之在局域网内迅猛传播），挖矿主体病毒文件为TrustedHostex.exe。

![14.png](https://image.3001.net/images/20181122/1542853694_5bf6143ead7e8.png!small)

连入地址为codidled.com。

![15.png](https://image.3001.net/images/20181122/1542853703_5bf6144730330.png!small)

##  **0x04** **解决方案**

1.隔离感染主机：已中毒计算机尽快隔离，关闭所有网络连接，禁用网卡。

2.切断传播途径：关闭潜在终端的SMB 445等网络共享端口，关闭异常的外联访问。深信服下一代防火墙用户，可开启IPS和僵尸网络功能，进行封堵。

3.查找攻击源：手工抓包分析或借助深信服安全感知。

4.查杀病毒：推荐使用深信服EDR进行查杀。

5.修补漏洞：打上“永恒之蓝”漏洞补丁，请到微软官网，下载对应的漏洞补丁（<https://technet.microsoft.com/zh-cn/library/security/ms17-010.aspx>）。

 ***本文作者：千里目安全实验室，转载请注明来自FreeBuf.COM**


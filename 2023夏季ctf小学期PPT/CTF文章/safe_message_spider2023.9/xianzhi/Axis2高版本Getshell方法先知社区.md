## 前言：

在一次SRC挖掘中，之前有人对这个站Getshell，再次测试中碰见Axis2无法登录，网上Getshell方法都是基于1.6.2版本getshell，在高版本axis2中，
service.xml 配置发生了变化,利用了URL解析错误，同时修改 aar包 service.xml 文件 最终成功RCE。

url解析特性：<https://xz.aliyun.com/t/10799>

## 过程：

使用burp替换功能.  
![](./img/4257585844517725530.png)

替换之前访问如下：  
![](./img/870316715359273703.png)  
替换之后。  
![](./img/2747338706137038757.png)  
然后使用弱口令进行登录.  
admin axis2  
![](./img/3482101348615054507.png)

从Github下载一个
<https://github.com/Lexus89/AxisInvoker/blob/master/build/AxisInvoker.aar>  
axis2 webshell  
不出意外，提示：  
![](./img/1172894202195198530.png)  
通过查看axis2版本号发现为，  
![](./img/1969046799959047432.png)

绕过 The ServiceClass object does not implement the required method in the
following form: OMElement info(OMElement e) 方法。

插件1.6.2生成的service.xml内容如下：

    
    
    <service name="HelloServer" >
        <description>
            Please Type your service description here
        </description>
        <messageReceivers>
            <messageReceiver mep="http://www.w3.org/2004/08/wsdl/in-only" class="org.apache.axis2.rpc.receivers.RPCInOnlyMessageReceiver" />
            <messageReceiver  mep="http://www.w3.org/2004/08/wsdl/in-out"  class="org.apache.axis2.rpc.receivers.RPCMessageReceiver"/>
        </messageReceivers>
        <parameter name="ServiceClass">com.hongbo.server.HelloServer</parameter>
    </service>
    

插件1.7.4生成的service.xml内容如下：

    
    
    <service name="HelloServer" >
        <description>
            Please Type your service description here
        </description>
        <messageReceivers>
            <messageReceiver mep="http://www.w3.org/ns/wsdl/in-only" class="org.apache.axis2.rpc.receivers.RPCInOnlyMessageReceiver" />
            <messageReceiver  mep="http://www.w3.org/ns/wsdl/in-out"  class="org.apache.axis2.rpc.receivers.RPCMessageReceiver"/>
        </messageReceivers>
        <parameter name="ServiceClass">com.hongbo.server.HelloServer</parameter>
    

</service>  
修改 services.xml文件.  
![](./img/4942850641864397680.png)  
成功RCE.  
![](./img/5274335023236030376.png)

获得奖励：  
![](./img/6735079086451415496.png)


***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

 ***本文原创作者：TopScrew，属于FreeBuf原创奖励计划，未经许可禁止转载**  

## 漏洞概要

 **Oracle官方发布了4月份的关键补丁更新CPU（Critical Patch
Update），其中包含Weblogic反序列化漏洞可导致远程代码执行漏洞，漏洞威胁等级为高危，对应的CVE编号为CVE-2018-2628。**

### 影响版本

> Oracle WebLogic Server10.3.6.0
>
> Oracle WebLogic Server12.2.1.2
>
> Oracle WebLogic Server12.2.1.3
>
> Oracle WebLogic Server12.1.3.0

### 环境搭建

在Oracle 官网下载相对应的weblogic安装包。进行下载安装即可。如果下载后只能在本地访问7001端口的话。进入console页面进行如下配置。

**![image.png](https://image.3001.net/images/20180421/15243007393628.png!small)**

将监听地址改为0.0.0.0 保存配置，并重启服务器。

**![image.png](https://image.3001.net/images/20180421/15243008021767.png!small)  
**

## 环境检测

检测weblogic版本信息和t3协议是否开启。只针对没打补丁的情况下的检测。

![image.png](https://image.3001.net/images/20180421/15243008673277.png!small)

## 简要分析

首先建立socket建立连接，使用t3协议进行握手。  

![image.png](https://image.3001.net/images/20180421/15242958696346.png!small)

握手成功后发送payload。

![image.png](https://image.3001.net/images/20180421/15242959387174.png!small)

### rmi知识补充

RMI：远程方法调用(Remote Method Invocation)。能够让在某个java虚拟机上的对象像调用本地对象一样调用另一个java
虚拟机中的对象上的方法。  

### 定义服务端接口

UnicastRemoteObject类的构造函数抛出了RemoteException，继承类的构造函数必须也抛出RemoteException。  

    
    
    import java.rmi.Remote;  
      
    public interface HelloWorld extends Remote{  
      
    public String sayHello()  throws java.rmi.RemoteException;  
    }

服务端接口的实现

    
    
    public class HelloWorldImpl extends UnicastRemoteObject implements HelloWorld {  
      
    protected HelloWorldImpl()   throws java.rmi.RemoteException {  
    super();  
        }  
      
    private static final long serialVersionUID = 4077329331699640331L;  
        public String sayHello()   throws java.rmi.RemoteException {  
    return "Hello  World ";  
        }  
    }

Server实现

    
    
    import java.rmi.registry.LocateRegistry;  
      
      
    public class HelloServer {  
    public static void main(String[] args) {  
    try {  
                HelloWorld hello = new HelloWorldImpl();  
                //本地创建并启动RMI Service，被创建的Registry服务将在指定的端口上侦听到来的请求  
                LocateRegistry.createRegistry(1099);  
                //把远程对象注册到RMI注册服务器上    
                java.rmi.Naming.bind("rmi://localhost:1099/aaa", hello);  
            } catch (Exception e) {  
                e.printStackTrace();  
            }  
        }  
    }

Client实现

    
    
    import java.rmi.Naming;  
      
      
    public class Client {  
    public static void main(String[] args) {  
    try {  
      
                HelloWorld obj = (HelloWorld) Naming.lookup("rmi://xx.xx.xx.xx:1099/aaa");  
                System.out.println(obj.sayHello());  
            } catch (Exception e) {  
                e.printStackTrace();  
            }  
        }  
    }

当客户端调用lookup方法时先根据服务名查找远程对象，然后会调用远程方法。

![image.png](https://image.3001.net/images/20180421/15243002039602.png!small)  

引用廖师傅的文章：[传送门](https://mp.weixin.qq.com/s/nYY4zg2m2xsqT0GXa9pMGA)

PoC中会序列化一个RemoteObjectInvocationHandler，它会利用UnicastRef建立到远端的tcp连接获取RMI
registry，加载回来再利用readObject解析，从而造成反序列化远程代码执行。

### 结合payload进行测试

本地构建rmi客户端  

![image.png](https://image.3001.net/images/20180421/1524296260437.png!small)

服务器端使ysoserial的 JRMP对1099
端口进行监听。Payload使用2015年的CommonsCollections反序列化的poc。为什么使用CommonsCollections，稍后解释。  

![image.png](https://image.3001.net/images/20180421/152429633480.png!small)

客户端调用lookup方法时，服务器端会将CommonsCollections反序列化的poc进行回传。当对其回传数据进行反序列化时，触发clac。

![image.png](https://image.3001.net/images/20180421/15242964553045.png!small)

### 为什么要利用CommonsCollections1来做poc？

因为weblogic中的依赖jar中，使用了CommonsCollections
3.2.0。在rmi远程记载后，对加载的内容进行反序列化时，将会触发RCE。

![image.png](https://image.3001.net/images/20180421/15242965241206.png!small)

CommonsCollections 文件存放路径。  

![image.png](https://image.3001.net/images/20180421/15242965687273.png!small)  

对其反编译进行查看。的确是CommonsCollections文件。

CommonsCollections又可以使用TransformedMap 和LazyMap 的方式构造poc。

TransformedMap

![image.png](https://image.3001.net/images/20180421/15242966427450.png!small)  

LazyMap 稍微复杂一点使用到了动态代理的知识。  

![image.png](https://image.3001.net/images/20180421/1524296664821.png!small)

不太清楚CommonsCollections反序列化漏洞的，可以直接在网上找资料。很多大佬都对这个经典的漏洞进行过详细分析了。在此不做详细的叙述。

### EXP的构造

1.通过上述分析可以得知，需要将廖师傅的poc的引用，改到我们自己用ysoseria实现的JRMP监听器，监听器会将指定的有效负载传递进行回传。回传后会进行反序列化操作。

2.使用ysoserial的 JRMP对端口进行监听。

Ysoserial JRMPListener使用 parameter:监听端口 payload类型 执行的命令参数。

![image.png](https://image.3001.net/images/20180421/15242968131657.png!small)

3.效果图：

![image.png](https://image.3001.net/images/20180421/15242972989609.png!small)  

 ***本文原创作者：TopScrew，属于FreeBuf原创奖励计划，未经许可禁止转载**


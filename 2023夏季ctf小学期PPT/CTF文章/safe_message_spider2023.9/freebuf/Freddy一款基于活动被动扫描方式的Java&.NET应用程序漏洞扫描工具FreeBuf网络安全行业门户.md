**今天给大家介绍的是一款名叫Freddy的开源工具，该工具的功能基于主动/被动式扫描，在Freddy的帮助下，研究人员可以快速查找Java和.NET应用程序中的反序列化安全问题。**  

![1.png](https://image.3001.net/images/20190430/1556588092_5cc7a63cf242d.png!small)

## Freddy介绍

工具引入了一款Burp Suite插件来检测并利用目标引用程序中序列化库/ API中的安全漏洞。

早在2017年美国Black Hat黑客大会以及DEF CON25上，研究人员Alvaro Muñoz和Oleksandr
Mirosh曾发布过一份标题为《[Fridaythe 13th: JSON
Attacks](https://www.blackhat.com/us-17/briefings.html#friday-the-13th-json-attacks)》的研究报告。研究人员在报告中指出，他们对大量Java和.NET应用程序中的JSON以及XML序列化库进行了安全分析，并且发现大多数库都支持对运行时对象进行序列化操作，而这种情况很容易引发反序列化安全问题，并导致任意代码/命令执行漏洞出现。

这款插件由Nick Bloor（@nickstadb）开发，基于的也是Alvaro Muñoz和Oleksandr Mirosh的研究成果。

该插件实现了主动式和被动式扫描这两种方式，可以识别并利用目标代码库中的安全漏洞。

## 功能介绍

### 被动式扫描

Freddy可以通过识别类型标识符、HTTP请求签名或HTTP响应来被动检测目标代码库或API中潜在的序列化/反序列化漏洞。比如说，代码库FastJson使用了一个JSON域“$types”来指定序列化对象的类型。

### 主动式扫描

Freddy引入了主动式扫描功能，可以在扫描的过程中，尝试对受影响的代码库进行漏洞利用测试。主动式扫描在检测和利用目标漏洞时使用了下列三种方法：基于异常的检测、基于时间的检测和基于Collaborator的检测。

### 基于异常的检测

在基于异常的主动扫描过程中，Freddy会向HTTP请求中注入测试数据，并尝试触发异常或错误信息。如果在目标应用程序所返回的响应信息中观察到了错误信息，那么就说明这里存在安全问题。

### 基于时间的检测

在某些情况下，基于时间的测试Payload可以用来检测安全漏洞，因为操作系统的命令执行会在反序列化的过程中被触发执行，在这个过程中，其他活动都会被阻止，直到操作系统命令执行完成。Freddy使用的Payload中包含了“ping
[-n|-c] 21 127.0.0.1”，目的就是为了实现命令的延迟执行。

### 基于Collaborator的检测

基于Collaborator的Payload使用了nslookup命令来解析Burp Suite
Collaborator生成的域名，并且会尝试从这个域名向Java应用程序中加载远程类。Freddy每隔60秒就会检查一次Collaborator的问题反馈，并以下列形式将问题记录在日志文件中。

    
    
    RCE(Collaborator)

## 支持的扫描对象

目前该工具支持的扫描对象有：

### Java

> BlazeDSAMF 0 (detection, RCE)
>
> BlazeDSAMF 3 (detection, RCE)
>
> BlazeDSAMF X (detection, RCE)
>
> Burlap(detection, RCE)
>
> Castor(detection, RCE)
>
> FlexJson(detection)
>
> Genson(detection)
>
> Hessian(detection, RCE)
>
> Jackson(detection, RCE)
>
> JSON-IO(detection, RCE)
>
> JYAML(detection, RCE)
>
> Kryo(detection, RCE)
>
> Kryousing StdInstantiatorStrategy (detection, RCE)
>
> ObjectInputStream(detection, RCE)
>
> Red5AMF 0 (detection, RCE)
>
> Red5AMF 3 (detection, RCE)
>
> SnakeYAML(detection, RCE)
>
> XStream(detection, RCE)
>
> XmlDecoder(detection, RCE)
>
> YAMLBeans(detection, RCE)

### .NET

> BinaryFormatter(detection, RCE)
>
> DataContractSerializer(detection, RCE)
>
> DataContractJsonSerializer(detection, RCE)
>
> FastJson(detection, RCE)
>
> FsPicklerJSON support (detection)
>
> FsPicklerXML support (detection)
>
> JavascriptSerializer(detection, RCE)
>
> Json.Net(detection, RCE)
>
> LosFormatter(detection, RCE) - Note not a module itself, supported
> throughObjectStateFormatter
>
> NetDataContractSerializer(detection, RCE)
>
> ObjectStateFormatter(detection, RCE)
>
> SoapFormatter(detection, RCE)
>
> Sweet.Jayson(detection)
>
> XmlSerializer(detection, RCE)

## 项目地址

Freddy：【[GitHub传送门](https://github.com/nccgroup/freddy)】

### 许可证协议

本项目遵循开源许可证协议agpl-3.0。

***参考来源：[nccgroup](https://github.com/nccgroup/freddy)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**


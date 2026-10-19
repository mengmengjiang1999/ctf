![](https://image.3001.net/images/20220706/1657094211_62c54043f37bc7c186976.jpeg!small)  

## 关于Gallia

Gallia是一款专注于汽车安全的可扩展渗透测试框架，该工具可以对整辆汽车执行渗透测试，而且甚至可以还可以单独对车辆ECU进行测试。目前，Gallia主要针对的是UDS接口，并利用了模块化的设计分别实现了日志记录和归档功能。作为一个通用接口，日志记录功能实现了可重复的测试，并支持后续处理任务。

## 工具架构

下图显示的是Gallia的内部模块以及运行机制：

![](https://image.3001.net/images/20220706/1657094225_62c540511b0edb980bd22.png!small)

## 工具依赖

> [ _Linux_](https://kernel.org/)>= 5.10
>
> [ _Python_](https://python.org/)>= 3.9
>
> [ _poetry_](https://python-poetry.org/)(可选，用于开发)
>
> [ _dumpcap_](https://www.wireshark.org/docs/man-pages/dumpcap.html)(可选，[
> _WireShark_](https://www.wireshark.org/)组件)

Python依赖组件可以在项目的pyproject.toml文件中查看。

## 扫描模式

常规的UDS扫描通常包含下列步骤：

> 1、在相关设备上搜索ECU：发现扫描；
>
> 2、在找到的ECU上搜索UDS服务：服务扫描；
>
> 3、在发现的UDS服务中搜索UDS标识符：标识符扫描；
>
> 4、针对其他特定服务的扫描：例如内存扫描、模糊测试等；

### 发现扫描

发现扫描特定于底层传输，如[ _DoIP_](https://www.iso.org/standard/74785.html)或[ _ISO-TP_](https://www.iso.org/standard/66574.html)。这个想法是制定一个有效的UDS
Payload。正常工作的Payload是1001，这也是DiagnosticSessionControl服务所要求的。该请求可以让ECU修改DefaultSession。DiagnosticSessionControl服务和DefaultSession是始终可用的，因此这个Payload是最佳选择。除此之外，1003这个Payload也可以使用，因为很多ECU在启用ExtendedDiagnosticsSession（会话ID为0x03）时会提供声音反馈。

ECU的寻址由底层传输协议提供，大多数情况下有两个地址：测试器地址和ECU地址。发现扫描的基本思想是使用固定的测试器地址将有效的UDS
Payload发送到所有有效的ECU地址。当收到有效应答时，说明找到了ECU。

### 服务扫描

服务扫描在UDS协议级别运行，UDS提供了几个称为服务的节点。每个服务都有一个标识符和一个特定的参数列表，扫描过程是使用固定Payload去请求所有可能的服务。Payload不必是特定的；它可以是空的，也可以是全零。一些ECU在接收到无效Payload时可能表现得不是很稳定。

为了识别可用的服务，工具使用了反向匹配机制。根据UDS标准，当请求未实现的服务时，ECU会使用错误代码serviceNotSupported或serviceNotSupportedInActiveSession进行回复。因此，每个以不同错误代码响应的服务都被认为是可用的。

### 标识符扫描

标识符扫描在UDS协议级别运行，更具体地说，它在特定UDS服务的级别上运行。大多数UDS服务需要标识符作为输入参数。比如说，ReadDataByIdentifier服务需要为请求的资源输入数据标识符。为了找出特定服务的可用标识符，工具引入了标识符扫描。

为了识别可用的数据标识符，工具使用了反向匹配机制。根据UDS标准，当请求未实现的服务时，ECU将使用错误代码serviceNotSupported或serviceNotSupportedInActiveSession进行回复。如果ECU响应serviceNotSupported、serviceNotSupportedInActiveSession、subFunctionNotSupported、subFunctionNotSupportedInActiveSession或requestOutOfRange中的任何一个，则认为标识符不可用。

一些服务（如RoutineControl）也提供了一个子功能，可以使用相同的技术发现子函数参数，但反向匹配的错误代码不同。为了发现可用的子功能，以下错误代码表示该子功能不可用：serviceNotSupported、serviceNotSupportedInActiveSession、subFunctionNotSupported或subFunctionNotSupportedInActiveSession。

每个以不同错误代码响应的标识符或子功能都被视为可用。

## 工具安装

### Arch Linux

    
    
    paru -S gallia

### 手动安装

    
    
    pip install gallia

## 工具使用

    
    
    $ gallia simple-dtc --target "isotp://can0?src_addr=0x123&dst_addr=0x312&tx_padding=0xaa℞_padding=0xaa" read

## 项目地址

 **Gallia** ：【[ _GitHub传送门_](https://github.com/Fraunhofer-AISEC/gallia)】

 **详细文档** ：【[ _点我查看_](https://fraunhofer-aisec.github.io/gallia)】

## 参考资料

> [
> _https://www.iso.org/standard/72439.html_](https://www.iso.org/standard/72439.html)
>
> [ _https://fraunhofer-aisec.github.io/gallia_](https://fraunhofer-> aisec.github.io/gallia)
>
> [ _https://www.secforcars.de/_](https://www.secforcars.de/)
>
> [
> _https://www.iso.org/standard/74785.html_](https://www.iso.org/standard/74785.html)
>
> [
> _https://www.iso.org/standard/66574.html_](https://www.iso.org/standard/66574.html)


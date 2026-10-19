![](https://image.3001.net/images/20200804/1596531234.jpg!small)

## Faxhell

Faxhell，又名“Fax Shell”，它是一个利用利用Fax服务和DLL劫持技术实现的Bind Shell，Faxhell本身就是一个针对Bind
Shell的概念验证PoC，其中的DLL劫持基于Ualapi.dll实现。

## 如何使用

首先，我们需要构建Ualapi.dll文件，并将其存放至“c:\windows\system32”路径下。接下来，开启系统的Fax服务，该服务启动后将会加载我们的DLL文件，并调用“UalStart”导出函数。

此时，“UalStart”会将线程池内的工作项加入一个队列之中，并开启一个针对“RpcSs”的控制器，然后寻找一个SYSTEM令牌。找到之后，代码便会复制其内容并伪装成该令牌。

接下来，它将会使用本地终端地址创建一个socket会话，并将其绑定至端口9299，然后使用线程池的IO Completion端口异步等待传入的链接。

配置好上述内容之后，我们需要使用熟悉的客户端（例如nc(at).exe <ip> 9299）来连接绑定端口9299的socket会话。然后输入“let me
in”并按下回车键。如果你编写了自定义代码，可以尝试发送字符串“let me in\n”。

I/O
Completion包将会唤醒线程池回调，而回调请求将会开启Cmd.exe进程，并使用SYSTEM权限运行DcomLaunch服务。此时，就会将其输入和输出处理器绑定到新创建的socket会话上了。![](https://image.3001.net/images/20200804/1596531255.png!small)

## 终端防护响应/反病毒绕过

  * 使用一个不常见或很少人知道的服务，或者使用EDR厂商不会监控或标记为“可疑”的服务。
  * 使用Windows线程池API来配置，增加栈内存的读取难度，通过多个线程来均衡工作负载，避免出现可疑情况的提示。
  * 伪造令牌的有效期非常短，必须让工作线程以SYSTEM权限运行，只有在每次API调用完成之后，才恢复网络服务，这样可以降低被扫描器捕捉到的机率。
  * 使用不常见的socket API，让导入的表没有那么可疑，并躲避EDR检测、LOCTL钩子和LSP。
  * 在DcomLaunch服务下创建Bind Shell，这个服务已经是一个拥有SYSTEM权限的服务了，因此我们的行为看起来会更加自然，避免出现可疑的进程树。
  * 利用Windows漏洞，让socket看起来属于Fax服务，而并非EcomLaunch或exe。如果我们终止Fax服务，那么socket将会属于System。

![](https://image.3001.net/images/20200804/1596531268.png!small)

## 注意事项

根据前文的介绍，想必大家应该已经了解了Faxhell的工作机制和使用方法了。但是，这并不意味着Faxhell是一个可以直接丢进目标系统执行，并且无法被检测和察觉的恶意攻击武器。

首先，Faxhell只是一个Bind Shell，大多数防火墙都可以阻止其活动。打开防火墙规则，或使用一个反向Bind
Shell，或者使用类似80和443这样的常见端口来实现数据通信会更加有效。

其次，比如说Spooler这样的常见服务同样也能够加载我们的Ualapi.dll。

第三，我们提供的这个Faxhell PoC可能会造成内存泄漏。

## 参考文档

1、[ _https://windows-internals.com/faxing-your-way-to-system/_](https://windows-internals.com/faxing-your-way-to-system/)

## 项目地址

Faxhell：【[ _GitHub传送门_](https://github.com/ionescu007/faxhell)】


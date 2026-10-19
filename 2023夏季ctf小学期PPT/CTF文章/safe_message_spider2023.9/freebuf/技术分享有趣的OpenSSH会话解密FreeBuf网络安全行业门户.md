![](https://image.3001.net/images/20201116/1605514034_5fb233320b53ef043eb6b.png!small)

## 前言

不久之前，我曾遇到过一个取证案例。当时，其中有一台Linux服务器受到了攻击，攻击者将一个经过修改后的OpenSSH二进制文件加载到了Web服务器的内存中。攻击者可以利用这个修改后的OpenSSH二进制文件作为控制目标系统的后门来使用。我们的客户当时保存了受感染Web服务器的系统快照以及相关的pcap文件，于是我们便想要知道，是否有可能通过内存快照恢复出相关的密钥材料，并解密SSH会话。

在这篇文章中，我们将对OpenSSH进行研究，并提供一些工具来帮助广大研究人员从内存中导出OpenSSH会话密钥，然后结合pcap来对会话内容进行解密和分析。

## SSH协议

首先，我们需要了解OpenSSH的基本知识及其工作原理。幸运的是，OpenSSH是开源的，因此我们可以下载其源代码并从中了解其实现细节。虽然RFC文档读起来非常无聊，但其中包含的丰富信息是我们必须要了解的。抽象一点来看，SSH协议包含了下列内容：

  * SSH协议+软件版本交换
  * 算法协商（KEX INIT）
    * 密钥交换算法
    * 加密算法
    * MAC算法
    * 压缩算法
  * 密钥交换
  * 用户身份验证
  * 客户端请求“会话”类型的通道
  * 客户端请求伪终端
  * 与客户端会话交互

一开始，客户端会跟服务器端连接，然后发送协议版本和软件版本信息：SSH-2.0-OpenSSH_8.3。接收到消息之后，服务器端会返回它的协议版本和软件版本。在这个初始协议和软件版本交换完成之后，所有的流量都被封装在SSH帧中。SSH帧主要包含帧的长度、填充长度、Payload数据、填充内容和MAC地址等信息。SSH帧示例如下：

![](https://image.3001.net/images/20201114/1605339849_5faf8ac9040bc440c8330.png!small)

在协商加密算法并生成会话密钥之前，SSH帧将被解密，即使帧被加密，根据算法的不同，帧的某些部分也可能不会被加密。例如，aes256
gcm算法不会加密帧中的4字节长度，但chacha20-poly1305算法则会进行加密。

接下来，客户端将向服务器发送KEX_INIT消息来开始协商会话所需的参数，例如密钥交换和加密算法等等。根据这些算法的顺序，客户端和服务器端都将选择双方都支持的首选算法。在KEX_INIT消息之后，则是多个跟密钥交换相关的消息，用于确定双方所使用的新密钥。这个消息用于告诉通信的双方，一切已经准备就绪，可以开始加密会话了，而之后的数据包都将进行加密。在双方使用新的加密密钥后，客户端将请求用户进行身份验证，并根据服务器上配置的身份验证机制执行基于密码或密钥的身份验证流程。经过身份验证之后，客户端将打开一个会话通道，并根据请求的操作（ssh/sftp/scp等）来通过该通道去请求服务。

## 恢复会话密钥

恢复会话密钥的第一步是分析OpenSSH源代码并调试现有的OpenSSH二进制文件。我试着自己编译OpenSSH，在某处记录生成的会话密钥，然后附加一个调试器并在程序内存中搜索这些密钥。没错，我成功了！会话的密钥保存在内存堆中，针对源代码的深入研究让我成功找到了负责发送和接收NEWKEYS帧的函数。我发现有一个“ssh”结构体中存储了一个“session\u
state”结构体，而这个结构体中存储了跟当前SSH会话相关的所有类型的消息，其中包括一个新的密钥结构（包含与加密、MAC和压缩算法相关的消息）。深入分析之后，我们终于找到了“sshenc”结构体，它包含了密码的名称、密钥、IV和块长度。

下面给出的是OpenSSH中关于各个结构体的信息：

![](https://image.3001.net/images/20201114/1605339860_5faf8ad4815c1f2eb2659.png!small)

下面给出的的是“sshenc”结构体的定义：

![](https://image.3001.net/images/20201114/1605339868_5faf8adc6c6a6ab7f52b9.png!small)

实际上，我们很难直接在内存中找出密钥，因为它只是一个随机字节的字符串。但是sshenc（和其他）结构体更加不同，它包含有一些我们可以验证的属性。接下来，我们可以获取程序的整个内存地址空间，并根据这些约束验证每个偏移量。我们可以检查以下属性：

  * 命名、密码、密钥、向量成员都是有效的指针；
  * 命名成员指向一个有效的密码名称，等效于cipher->name；
  * key_len在一个有效范围内；
  * iv_len在一个有效范围内；
  * block_size在一个有效范围内；

如果我们根据所有这些约束条件进行验证，我们就应该能够可靠地找到sshenc结构体了。于是，我构建了一个用于漏洞验证的PoC脚本【[
_点我获取_](https://github.com/fox-it/OpenSSH-Session-Key-Recovery/tree/main/pip-package)】，它可以在目标主机上实时运行，而这台主机能够跟目标进程连接并从内存中搜索目标结构体。在这个脚本的帮助下（Python和ptrace），我将能够从一台实时运行的主机中恢复出会话密钥，但是我们如何从系统快照中恢复出会话密钥呢？这里就要介绍[
_Volatility_](https://www.volatilityfoundation.org/)了，Volatility是一款基于Python开发的内存取证框架，而且还允许研究人员开发自定义的插件。经过一番努力之后，我自己编写了一个Volatility
2插件，它将帮助我们分析内存快照，并导出会话密钥。

![](https://image.3001.net/images/20201114/1605339879_5faf8ae76ea44418f7016.png!small)

## 流量的解密与分析

现在，我们已成功恢复出用于加密和解密流量的会话密钥了。那么下一步，就是解密流量！这里，我开始使用pynids（一个TCP解析库）来对pcap进行分析，我还使用了我们自己开发的[
_dissect.cstruct_](https://github.com/fox-it/dissect.cstruct)库来对数据结构进行解析，然后又开发了一个能够解析SSH协议的解析框架。这个解析框架基本上能够以正确的顺序将数据包提供给协议解析器，因此，如果客户机发送2个数据包，而服务器用3个数据包进行响应，则数据包也将以相同的顺序提供给解析器。而这个解析器可以处理OpenSSH支持的几乎所有加密算法。

SSH协议解析过程如下：

![](https://image.3001.net/images/20201114/1605339892_5faf8af475ef025d4c60b.gif!small)

解析完成后，我们就能够查看到解密后的SSH会话信息了，其中还包含用户用于身份验证的密码：

![](https://image.3001.net/images/20201114/1605339902_5faf8afe5c0eca60c19b9.png!small)

## 参考资料

  * [ _https://github.com/fox-it/OpenSSH-Session-Key-Recovery/tree/main/pip-package_](https://github.com/fox-it/OpenSSH-Session-Key-Recovery/tree/main/pip-package)
  * [ _https://github.com/fox-it/OpenSSH-Session-Key-Recovery/tree/main/volatility2_](https://github.com/fox-it/OpenSSH-Session-Key-Recovery/tree/main/volatility2)
  * [ _https://github.com/fox-it/OpenSSH-Session-Key-Recovery/tree/main/volatility3_](https://github.com/fox-it/OpenSSH-Session-Key-Recovery/tree/main/volatility3)
  * [ _https://github.com/fox-it/OpenSSH-Network-Parser_](https://github.com/fox-it/OpenSSH-Network-Parser)
  * [ _https://fossies.org/dox/openssh-8.4p1/structssh.html_](https://fossies.org/dox/openssh-8.4p1/structssh.html)
  * [ _https://fossies.org/dox/openssh-8.4p1/structsshenc.html_](https://fossies.org/dox/openssh-8.4p1/structsshenc.html)

  


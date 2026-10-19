![](https://image.3001.net/images/20230829/1693321424_64ee08d0449606757db62.jpg!small)

## 关于CenoCipher

CenoCipher是一款功能强大且易于使用的加密和隐写工具，该工具完全免费，且开放源代码，可以帮助广大研究人员实现在互联网上交换安全加密的通信。CenoCipher使用了强大的加密技术将消息和文本转换为加密的密码数据，然后我们就可以通过常规电子邮件或任何其他可用渠道（如即时消息或共享云存储）发送给收件人了。

## 支持的平台

> 所有版本的Windows操作系统
>
> Linux（需要使用Wine）

## 功能特性

> 1、易于使用，只需要键入一条消息，单击“加密”，然后跳转到“用于在Jpeg图像中嵌入加密数据的可选隐写术”功能；
>
> 2、轻松地将消息和文件附件放在一起处理；
>
> 3、端到端加密，完全在用户的机器上执行；
>
> 4、不依赖于任何特定的中间渠道-适用于任何可用的通信方法；
>
> 5、结合使用三种强大的加密算法来对数据进行三重保护；
>
> 6、无需安装-完全可移植的应用程序，可以在任何地方运行；
>
> 7、除非用户请求，否则从不将未加密的数据写入磁盘；
>
> 8、提供了多种输入/输出模式，操作方便；

## 技术细节

> 1、开源，使用C++开发构建；
>
> 2、使用了AES/Rijndael、Twofish和Serpent密码（256位密钥大小变种），以CTR模式级联在一起，用于消息和文件的三重加密；
>
> 3、HMAC-SHA-256，用于构建消息认证码；
>
> 4、PBKDF2-HMAC-SHA256，用于从用户选择的密码短语派生单独的AES、Twofish和Serpent密钥；
>
> 5、加密安全的伪随机数生成器ISAAC，用于生成初始化向量（AES/Twofish/Sepent）和盐值（PBKDF2）；

## 工具下载

由于该工具基于C++开发，如果你想要手动进行项目编译的话，则需要安装并部署好最新版本的Visual
Studio。接下来，广大研究人员可以直接使用下列命令将该项目源码克隆至本地：

    
    
    git clone git@gitlab.com:cenocipher/cenocipher.git

然后在Visual Studio中导入项目代码，并进行编译构建即可。

除此之外，我们也可以直接点击【[
_这里_](https://gitlab.com/cenocipher/cenocipher/-/raw/master/bin/CenoCipher.exe)】下载该工具的最新版本（v4.1）可执行文件（exe）。

## 工具运行截图

![](https://image.3001.net/images/20230829/1693321454_64ee08ee3076f760bf244.png!small)

## 许可证协议

本项目的开发与发布遵循GNU开源许可证协议。

## 项目地址

 **CenoCipher** ：【[ _GitLab传送门_](https://gitlab.com/cenocipher/cenocipher)】


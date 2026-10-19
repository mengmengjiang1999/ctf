**严正声明：本文仅用于实现安全教育目的，请不要将其用于恶意活动。**

## 前言

**如今，很多恶意软件和Payload都会使用各种加密技术和封装技术来绕过反病毒软件的检测，原因就是AV产品很难去检测到经过加密或加壳的恶意软件(Payload)。**

**今天，我们要学习是如何使用VENOM来生成经过加密的Payload，权当为加固安全保护措施抛砖引玉，未来或许会再出一篇文章来讲一讲如何堵住这个方法。**

![](https://image.3001.net/images/20181105/1541414452_5be01e3488efb.png!small)

## 概述

根据VENOM的介绍，该脚本会使用MSF venom(Metasploit)来以不同的格式生成Shellcode，比如说c | python | ruby
| dll | msi |hta-psh等格式，并将生成的Shellcode注入到一个函数之中（比如说Python函数）。

这个Python函数将会在RAM中执行Shellcode，并使用类似gcc、mingw32或Pyinstaller这样的编译工具来构建可执行文件，然后开启一个多处理器来处理远程连接(反向Shell货Meterpreter会话)。

### 第一步：

由于该工具并不是Kali自带的工具，所以我们需要在Kali
Linux上进行下载和安装。大家可以点击【[下载链接](https://sourceforge.net/projects/crisp-shellcode-generator/files/)】直接从Sourceforge网站下载VENOM。

下载并解压之后，大家就可以运行VENOM了。

![运行VENOM](https://image.3001.net/images/20181105/1541414463_5be01e3f9135b.png!small)

### 第二步：

启动工具之后，工具会要求继续处理后续选项。

![点击“OK”并继续处理后续选项](https://image.3001.net/images/20181105/1541414473_5be01e495026f.png!small)

### 第三步：

接下来，工具会给你显示代码构建、目标设备、Payload格式和数据输出等选项。

工具提供了20种不同类型的Shellcode构建选项，都列举在下图之中了。我们在本文中，选择使用选项10来进行演示。

![项10](https://image.3001.net/images/20181105/1541414484_5be01e543a66f.png!small)

输入10，并按下回车键。

### 第四步：

在这一步骤，我们需要设置本地主机IP地址，输入本地设备IP地址来监听Payload之后，按下OK键。

![按下OK键](https://image.3001.net/images/20181105/1541414495_5be01e5f9be0d.png!small)

设置好了我们的LHOST之后，工具会要求你设置LPORT，提供你想要设置的LPROT号，按下OK键。

### 第五步：

VENOM自带了很多默认的msf Payload，我们这里选择使用“windows/meterpreter/reverse_tcp”。

![默认的msf
Payload](https://image.3001.net/images/20181105/1541414527_5be01e7f4038f.png!small)

### 第六步：

输入需要生成的Payload名称，然后点击OK。

![点击OK](https://image.3001.net/images/20181105/1541414541_5be01e8d9b3d9.png!small)

### 第七步：

生成好加密的Payload之后，工具将会把Payload存储在VENOM的文件输出目录中：

    
    
    root/Desktop/shell/output/gbhackers.hta

![存储在VENOM的文件输出目录](https://image.3001.net/images/20181105/1541414562_5be01ea2a7db1.png!small)

### 第八步：

在成功生成加密后的Payload之后，我们可以用反病毒产品来检测一下：

![生成加密后的Payload](https://image.3001.net/images/20181105/1541414578_5be01eb2ce93d.png!small)

接下来，我们看看如何使用Metasploit和我们生成的Payload来绕过反病毒产品。

### 第九步：

我们需要开启Apache服务器来将恶意Payload发送到目标主机中，选择好服务器后点击OK继续。

![点击OK继续](https://image.3001.net/images/20181105/1541414596_5be01ec41d1e2.png!small)

### 第十步：

在这一步中，我们需要连接后渗透模块，这里我们可以随意选择一个。由于我需要访问的只有系统信息，所以我选择sysinfo.rc来进行后渗透操作。

这是一个可选操作，所以你甚至可以手动执行这个模块，然后用Metasploit实现绕过。

![用Metasploit实现绕过](https://image.3001.net/images/20181105/1541414615_5be01ed7743da.png!small)

### 第十一步：

最后，我需要用生成的加密Payload在目标主机和我的Windows 7主机之间建立Meterpreter会话。

在启动在会话处理器之前，确保你的Payload已经成功注入到目标主机之中了。我这里使用的URL为<http://192.168.56.103>。

注意：在开始之前，请检查LPORT和LHOST设置是否正确。

![](https://image.3001.net/images/20181105/1541414635_5be01eeb74ac6.png!small)

最后，我们成功绕过了目标主机的反病毒产品，并获得了目标设备的完整访问权。

 *** 参考来源：[gbhackers](https://gbhackers.com/bypass-antivirus-using-payload/)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**


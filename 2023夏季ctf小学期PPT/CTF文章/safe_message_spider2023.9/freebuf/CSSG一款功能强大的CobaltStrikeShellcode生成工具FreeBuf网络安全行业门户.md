![](https://image.3001.net/images/20210201/1612168436_6017bcf452e41cf23ebc8.jpg!small)

## CSSG

CSSG是一款功能强大的Cobalt Strike
Shellcode生成工具。本质上来说，CSSG是一个具备攻击性的Python脚本，广大研究人员可以使用它来轻松生成并格式化信标Shellcode。

该工具支持生成无阶段信标Shellcode，并带有暴露的退出方法、额外的格式化、加密、编码、压缩和多行输出等功能。

注意：Shellcode的转换通常需要按菜单顺序降序执行。

## 执行要求

可选的AES加密选项使用/assets文件夹中的python脚本实现。

具体取决于要安装的pycryptodome包来执行AES加密。

在使用pip命令安装pycryptodome包时，具体取决于你的Python环境：

    
    
    python -m pip install pycryptodome
    
    python3 -m pip install pycryptodome
    
    py -3 -m pip install pycryptodome
    
    py -2 -m pip install pycryptodome

我们可以在pip安装执行完成之后检测pycryptodome包的安装情况，使用命令如下：

    
    
    python -m pip list | grep crypto

生成器将会使用系统默认的“python”命令来启动AES加密脚本。

## 工具下载

广大研究人员可以使用下列命令将该项目源码克隆至本地并使用：

    
    
    git clone https://github.com/RCStep/CSSG.git

## Shellcode生成器选项

 **监听器：**

使用"..."按钮选择一个有效的监听器。Shellcode将会根据选择的监听器来生成。

 **发送器：**

无阶段（CSSG是一款不支持阶段操作的Shellcode生尘器）。

 **退出方法：**

进程：当信标关闭之后，退出整个进程；

线程：当信标关闭之后，退出运行信标的线程；

 **本地Shellcode选项：**

如果要从现有信标执行Shellcode，则可以使用该选项。

生成一个信标Shellcode Payload，该Payload可以从同一架构父信标继承关键函数指针。

 **现有会话：**

Shellcode会将会话元数据提取至父Beacon会话中。

Shellcode将会在此信标会话中执行。

 **x86选项：**

生成x86 Shellcode，默认生成x64 Shellcode。

 **使用Shellcode文件：**

使用外部生成的原始Shellcode文件代替生成信标Shellcode。

这将允许我们使用以前导出的Shellcode文件或其他工具（Donut、msfvenom等）的输出。

 **格式化：**

元数据 - Shellcode二进制源码输出，无格式化；

十六进制 - Shellcode十六进制格式输出；

0x90,0x90,0x90 - Shellcode C#风格字节数组输出；

\x90\x90\x90 - Shellcode C\C++风格字节数组输出；

b64 - Base64编码选项；

 **异或加密Shellcode：**

勾选以对Shellcode进行异或加密。

 **异或密钥：**

使用随机生成的或可编辑的异或密钥字符进行加密。

多个字符意味着多轮异或加密。

 **AES加密Shellcode：**

勾选以启用对Shellcode的AES加密，加密类型可选。

使用一个Python脚本来执行AES分组密码AES-CBC加密。

Shellcode将会填充\0值来满足分组大小要求。

除此之外，工具还会在在加密的Shellcode数据前面加上一个随机生成的向量。

 **AES密钥：**

用于加密的随机生成的可编辑AES密钥。

生成32字节的密钥，并优先用于256位加密强度。

接受的加密密钥字节长度为16、24和32位。

 **编码和压缩：**

无编码/压缩 - 不对Shellcode进行编码和压缩。

b64 - 进行Base64编码。

Gzip + b64 - 先进行gzip压缩，然后进行Base64编码。

gzip - 进行gzip压缩。

b64 + gzip - 先进行Base64编码，然后进行gzip压缩。

## 工具运行截图

添加Shellcode-Cobalt Strike顶部菜单栏的Shellcode生成器：

![](https://image.3001.net/images/20210201/1612168551_6017bd675e79da8224fd6.png!small)

## 项目地址

CSSG：【[ _GitHub传送门_](https://github.com/RCStep/CSSG)】


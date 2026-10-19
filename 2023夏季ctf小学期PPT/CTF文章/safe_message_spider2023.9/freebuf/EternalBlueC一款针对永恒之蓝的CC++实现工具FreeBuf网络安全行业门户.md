![](https://image.3001.net/images/20201031/1604134156_5f9d250c7c48d78e1d779.png!small)

## ****EternalBlueC****

EternalBlue
suite在C/C++中重新构建，其中包括：MS17-010漏洞、EternalBlue/MS17-010漏洞检测器、DoublePulsar检测器以及DoublePulsarUploadDLL和Shellcode上传工具。

##  ** **项目目标****

1.转换为其他语言，例如Java和C＃，并实现扫描和攻击GUI。

2.允许编辑的永恒之蓝漏洞利用有效负载以删除DoublePulsar后门，并允许发送自定义负载和Shellcode。

3.添加EternalRomance（需要命名管道）支持。

##  ** **附加的网络教育代码****

存储库还包含以下用于教育目的的内容：

1.DoublePulsar x86/x64上传DLL python脚本。

2.EternalBlue一体化二进制文件。

3.多体系结构内核队列apc汇编代码和Windows x86/x64多体系内核从环0到环3通过排队的APC内核代码。

4.来自worawit的EternalBlue x64/x86内核有效载荷Shellcode。

5.Eternalblue的回放文件

##  ** **EternalBlue Suite****

 ** **ms17_vuln_status.cpp -****
该程序发送了4个SMB数据包。1个协商、1个会话设置、1个树连接和1个TransNamedPipe请求。然后，该程序从TransNamedPipeRequest（PeekNamedPipe请求）中读取NT_STATUS响应，并确定SMB数据包中的NT_STATUS是否=0xC0000205（STATUS_INSUFF_SERVER_RESOURCES）。如果正确，则目标很容易受到MS17-010的攻击。已在未修补的Windows7x64位上进行了测试。

![](https://image.3001.net/images/20201031/1604134183_5f9d25272644f05d65628.png!small)

 ** **doublepulsar_check.cpp -**** 该程序发送了4个SMB数据包、1个协商、1个会话设置、1个树连接和Trans2
SESSION_SETUP数据包。通过发送Trans2 SESSION_SETUP数据包，可以将Trans2响应数据包中发送的Multiplex
ID（41）与Multiplex
ID：0x51或81进行比较。如果响应，则表示计算机上存在DoublePulsar后门。DoublePulsar后门读取发送的Multiplex
ID，在ping命令成功后，在Trans2 SESSION_SETUP响应中为Multiplex
ID返回十六进制的+10。之后，发送命令（在SMB数据包的超时参数中发送）以刻录DoublePulsar后门。DoublePulsar后门处于休眠状态，没有被移除。已在Windows7x64位上进行了测试。

![](https://image.3001.net/images/20201031/1604134191_5f9d252f46132bcabd6d8.png!small)

 ** **EternalBlue.cp**** ** **p**** ** **–****
该程序发送了多个SMB数据包。有协商、会话设置、树连接和多个NT
trans和Trans2数据包。这些NT传输包的格式不正确，这会在受害者计算机的内存中存在漏洞。更多的空白或空SMB数据包通过多个套接字发送到受害者的同一端口。大部分EternalBlue的base64有效负载都是通过socket1发送的，其中negotiation、SessionSetup和TreeConnect数据包都是在这个套接字上发送的。然后创建20个其他套接字，并将数据发送到这些套接字（套接字3到套接字21）中。之后，DoublePulsar后门通过插座3发送到插座21。然后由程序关闭插座，引爆受害者电脑上的EternalBlue
和DoublePulsar后门。然后发送SMB断开连接和SMB注销请求并关闭连接。此漏洞攻击有效，并在Windows 7
x64位上进行了测试。花了大约5秒的时间让后门完全运行，正如互联网上报道的永恒之蓝那样。可能需要更多的利用尝试。然而，目前有一个错误，TreeID和UserID没有被正确的设置在数据包中，这将在以后的版本中修复。当TreeID和UserID设置为默认值时，这将适用于最近打开的计算机。当默认值设置为“0800”时，这些数据包必须更新其TreeID和UserID值。

![](https://image.3001.net/images/20201031/1604134199_5f9d25376c83783b60aff.png!small)

![](https://image.3001.net/images/20201031/1604134206_5f9d253e636a9ea773009.png!small)

![](https://image.3001.net/images/20201031/1604134214_5f9d2546c262e9cedf651.png!small)

 ** **DoublePulsarXORKeyCalculator.cpp -****
该程序发送了4个SMB数据包。1个协商数据包和3个请求。最后一个请求是Trans2 SESSION_SETUP请求。然后，接收Trans2
SESSION_SETUP响应，并在（Recvbuff[18]->Recvbuff[22]）处提取SMB签名。SMB签名从十六进制字符转换为无符号整数。该无符号整数通过DoublePulsar
XOR key
calculator函数运行，该函数生成一个XOR密钥，该密钥可用于加密将上传到DoublePulsar后门的shellcode或DLL有效负载中。

注意：SESSION_SETUP数据参数必须包含此存储库的有效负载上传部分中计算出的DoublePulsar
XOR密钥的char版本。在Windows7x64位上测试。屏幕截图示例：

![](https://image.3001.net/images/20201031/1604134253_5f9d256d42103c1c23127.png!small)

 ** **doublepulsar_upload.cpp -**** 该程序发送了4个SMB数据包。1个协商、1个会话设置、1个树连接和1个Trans2
SESSION_SETUP数据包。发送Trans2 SESSION SETUP请求数据包以获取Trans2
SESSION_SETUP响应数据包中的SMB签名。该签名通过从DoublePulsar后门二进制文件中提取的DoublePulsar
XOR密钥计算器进行处理。然后，程序读取一个DLL文件（示例：payload.dll），并将其与userland
shellcode（userland_shellcode.bin）相结合，然后用我们根据SMB签名计算出的DoublePulsar
XOR密钥对缓冲区进行XOR运算。数据包通过分配内存，复制Trans2数据包，编辑SMB事务正常工作所需的值（UserID, ProcessID,
TreeID, MultiplexID），然后将XORed数据（shellcode +
DLL）复制到末尾，并通过它循环发送到DoublePulsar后门。每次发送的总数据包长度为4096字节。数据包总长度=4178。4096一般用于XOR加密数据。这项工作仍在进行中，无法正常工作。

TODO：可能需要使用TRANS2数据包结构实现Trans2上传函数，而不是使用十六进制编辑Trans2数据包进行捕获。

 ** **Doublepulsar_UploadShellcode.cpp -****
该程序发送了5个SMB数据包。1个协商，1个会话设置，1个树连接，1个ping Trans2 SESSION_SETUP数据包和1个exec Trans2
SESSION_SETUP数据包。发送Trans2 SESSION SETUP请求数据包以获取TRANS2
SESSION_SETUP响应数据包中的SMB签名。该签名通过从DoublePulsar后门二进制文件中提取的DoublePulsar
XOR密钥计算器进行处理。然后，程序从一个缓冲区（NOPs/x90）复制示例shellcode，它使用我们根据SMB签名计算出的DoublePulsar
XOR密钥对缓冲区进行XORs运算。数据包是通过分配内存，复制Trans2
exec数据包（来自Wannacry），编辑SMB事务正常工作所需的值（UserID，TreeID），然后将SESSION_PARAMETERS和4096字节的XORed数据（shellcode）复制到末尾，并以4178字节的数据包总长度将其发送到DoublePulsar后门。数据包总长度=4178，SESSION_PARAMETERS为12。4096一般用于XOR加密数据。这项工作仍在进行中，无法正常工作。

TODO：可能需要使用结构来实现Trans2上载函数，而不是使用十六进制编辑Trans2数据包进行捕获。

## 项目地址

EternalBlueC：[ _【GitHub传送门】_](https://github.com/bhassani/EternalBlueC)


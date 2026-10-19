近日，研究人员发现了一个攻击链较长的攻击事件，其中利用 Python 脚本作为 Loader 实现隐蔽攻击。

在用户的启动文件夹中，发现了可疑链接文件 `sysmon.lnk`，经过分析后发现该文件链接到恶意 Python 文件，利用 Python 文件将 RAT
远控木马注入系统。

整体攻击链情况如下所示：

![](https://image.3001.net/images/20210826/1629958530_612731821ff5b89a210bc.png!small)

名为 sysmon.lnk的 LNK 文件位于

c:\\\users\<username>\appdata\roaming\microsoft\windows\startmenu\programs\startup\sysmon.lnk处。该文件重定向到可疑的
ctfmon.exe update.py执行，这两个文件位于

c:\users\<username>\appdata\roaming\PpvcbBQh\ctfmon.exe和
c:\Users\<username>\AppData\Roaming\PpvcbBQh\update.py。

## ctfmon.exe

ctfmon.exe是重命名的 IronPython 解释器，该文件在 VirusTotal 上零检出。

![](https://image.3001.net/images/20210826/1629958533_61273185a3cdee29aa8d0.png!small)

在文件描述中就可以看到 IronPython 解释器的痕迹：

![](https://image.3001.net/images/20210826/1629958535_61273187ec035297b17dc.png!small)

![](https://image.3001.net/images/20210826/1629958540_6127318c0e0611f2951a0.png!small)

## stage1.py

脚本中包含大段的混淆字符串和混淆的变量名：

![](https://image.3001.net/images/20210826/1629958544_612731902c9655089a296.png!small)

经过分析，脚本使用 base64 解码混淆字符串、将解码字符串转换呈十六进制数、每个字节减去 12（十进制）。

![](https://image.3001.net/images/20210826/1629958547_61273193449b94280b1b1.png!small)

处理后可见：

![](https://image.3001.net/images/20210826/1629958550_6127319606cbc44f94b12.png!small)

## stage2.py

解开的脚本中有另一个混淆的字符串，并且引入了反射操作相关的库。

![](https://image.3001.net/images/20210826/1629958554_6127319a8f010b95d0b75.png!small)

用 A 替换字符串中所有 ! 后使用 base64 进行解码：

![](https://image.3001.net/images/20210826/1629958558_6127319e73783c2217a1d.png!small)

得到了一个新的 PE 文件。

## stage3.bin

可执行文件是 .NET 文件：

![](https://image.3001.net/images/20210826/1629958562_612731a28e8372d1fcea4.png!small)

在 PDB 路径中发现了 injector.pdb，表明其可能的功能：

![](https://image.3001.net/images/20210826/1629958566_612731a673633ca4c213c.png!small)

使用 Dnspy 进行分析：

![](https://image.3001.net/images/20210826/1629958569_612731a90473e9c1db01b.png!small)

查看函数名称就知道文件的功能，包括注入、加载和解码的函数，可以明白混淆后的 Payload 被解码注入进程中。

![](https://image.3001.net/images/20210826/1629958572_612731ac620a251ef4053.png!small)

msbuild.exe还是 Mandark.Load函数的第二个参数。

![](https://image.3001.net/images/20210826/1629958575_612731afd0949ac21122d.png!small)

这第二个参数是注入的目标进程：

![](https://image.3001.net/images/20210826/1629958579_612731b36c5cd73d5d5ec.png!small)

程序中使用了编码与压缩：

![](https://image.3001.net/images/20210826/1629958583_612731b7a95e47f49ef3f.png!small)

压缩使用的是 Gzip 方式：

![](https://image.3001.net/images/20210826/1629958587_612731bb135e44d95858f.png!small)

解码后可得到另一个 PE 文件：

![](https://image.3001.net/images/20210826/1629958590_612731be863335cda6590.png!small)

## stage4.bin

该文件是一个 C/C++ 编写的文件：

![](https://image.3001.net/images/20210826/1629958593_612731c12e03ebc93fc96.png!small)

根据导出函数，可以看出其是另一个 Loader：

![](https://image.3001.net/images/20210826/1629958598_612731c6569f0101c7597.png!small)

根据 PDB 路径可以看出一个类似 git 的文件结构：

![](https://image.3001.net/images/20210826/1629958601_612731c9d9818f9b3afad.png!small)

检索后可以发现，这是 [execute-assembly
loader](https://github.com/med0x2e/ExecuteAssembly)项目（Cobalt Strike 的 execute-assembly 模块开源实现）。

![](https://image.3001.net/images/20210826/1629958606_612731ce29ea227f3b86b.png!small)

在文档中可以看见，嵌入的 payload 格式为
0|0|0|0|1|sizeofpayload.b64_encoded_compressed_payload：

![](https://image.3001.net/images/20210826/1629958608_612731d0a93c4f7068478.png!small)

在文件中也可以找到该格式的长字符串：

![](https://image.3001.net/images/20210826/1629958611_612731d3c3c9801fac985.png!small)

根据文档进行处理后，发现了另一个 PE 文件:

![](https://image.3001.net/images/20210826/1629958614_612731d6b7b52ae2ff47d.png!small)

## stage5.bin

该文件是 .NET 文件：

![](https://image.3001.net/images/20210826/1629958617_612731d9e0083c56343ce.png!small)

程序中有对 AMSI 进行 Patch 的脚本：

![](https://image.3001.net/images/20210826/1629958620_612731dcb7d5712bc2132.png!small)

自定义加密/编码的方式如下所示：

![](https://image.3001.net/images/20210826/1629958623_612731dfc83d22d081efb.png!small)

密钥为 avyhk：

![](https://image.3001.net/images/20210826/1629958626_612731e2c3eb004c184db.png!small)

解密程序如下所示：

![](https://image.3001.net/images/20210826/1629958629_612731e51ad77658c5be0.png!small)

## stage6.bin

该文件仍然是一个 .NET 文件：

![](https://image.3001.net/images/20210826/1629958632_612731e82012089125572.png!small)

该文件实际为远控木马，其主要功能如下所示：

![](https://image.3001.net/images/20210826/1629958636_612731ecf0cd2c65cadc3.png!small)

该 RAT 木马使用 AES256 加密数据，再用 base64 进行编码：

![](https://image.3001.net/images/20210826/1629958639_612731efd2f55bc51f339.png!small)

解密后可得到配置信息：

![](https://image.3001.net/images/20210826/1629958642_612731f2893bc6fa8e7d1.png!small)

该木马有多种反分析检查的技术：

> DetectManufacturer：检查硬件描述判断是否在虚拟机中
>
> DetectDebugger：检查调试器与 dnspy.xml 文件是否存在
>
> DetectSandboxie：检查是否存在 Sandboxie 驱动程序（sbiedll.dll）
>
> IsSmallDisk：检查硬盘是否小于 61GB
>
> IsXP：检查操作系统是否为 XP

各功能结构如下所示：

![](https://image.3001.net/images/20210826/1629958649_612731f9de6bbcb815b4e.png!small)

还会利用计划任务和注册表进行持久化：

![](https://image.3001.net/images/20210826/1629958653_612731fdd9f3963cf6341.png!small)

支持的命令如下所示：

> Update：通过 PowerShell 下载恶意软件
>
> SavePlugin：下载并加载恶意 DLL
>
> Unload：通过命名管道发送终止命令
>
> Restart：终止当前进程并通过计划任务重启
>
> Self-delete：删除持久化并终止进程

![](https://image.3001.net/images/20210826/1629958657_612732019473fa1330f0a.png!small)

![](https://image.3001.net/images/20210826/1629958660_61273204c43b9b901a30c.png!small)

## IOC

> windowsupdatecdn.cn  
> gjghvga7ffgb.xyz  
> huugbbvuay4.cn  
> 3e442cda613415aedf80b8a1cfa4181bf4b85c548c043b88334e4067dd6600a6  
> dd1fa3398a9cb727677501fd740d47e03f982621101cc7e6ab8dac457dca9125  
> 2CCADFC32DB49E67E80089F30C81F91DFFF4B20B8FC61714DF9E2348542007FD  
> 4591EDA045E3587A714BB11062EB258F82EE6F0637E6AA4D90F2D0B447A48EF7  
> 4417298524182564AED69261B6C556BDCE1E5B812EDC8A2ADDFC21998447D3C6  
> 9B775DFC58B5F82645A3C3165294D51C18F82EC1B19AC8A41BB320BEE92484ED  
> 169F5DBCD664C0B4FD65233E553FF605B30E974B6B16C90A1FB03404F1B01980

## 参考来源

> [Huntress](https://www.huntress.com/blog/snakes-on-a-domain-an-analysis-of-> a-python-malware-loader)


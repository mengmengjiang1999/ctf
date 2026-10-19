近期攻击中使用加密勒索软件已成为一种常态。7月23日，导航设备和智能设备的主要制造商Garmin经历了大规模的服务中断，停机原因是有关数据加密的网络攻击事件。攻击者使用木马工具：WastedLocker，该恶意软件的活动有所增加，本文主要对WastedLocker的样本进行技术分析。

## 命令参数

WastedLocker具有命令行界面，该界面允许处理的参数如下：

> -p <directory-path>

优先处理：木马将首先加密指定的目录，然后将其添加到内部排除列表中（避免对其进行两次处理），并对驱动器上的所有其余目录进行加密。

> -f <directory-path>

仅加密指定的目录。

> -u username:password \\\hostname

使用提供的凭据对指定的网络资源上的文件进行身份验证。

> -r

启动动作序列：

  * 删除;
  * 使用注册表项SYSTEM\CurrentControlSet\Control\的子项列表中的随机子字符串将文件复制到%WINDIR%\system32\<rand>.exe；
  * 创建一个名称与上述方法类似的服务。如果已经存在该名称的服务，附加前缀“ Ms”。新服务命令设置为“%WINDIR%\system32\<rand>.exe -s”；
  * 启动此服务并等待其完成工作；
  * 删除服务。

> -s:

启动创建的服务，对可以找到的所有文件进行加密。

## UAC绕过

WastedLocker启动时，将检查运行该木马的完整性。如果运行权限不够，恶意软件将尝试使用已知的绕过技术以静默方式提升其特权。

1、在％appdata％中创建一个新目录；目录名称是从注册表项SYSTEM\CurrentControlSet\Control\的子项列表中找到的随机字符串；  
2、将随机EXE或DLL文件从系统目录复制到此新目录；  
3、将木马程序的主体写入该系统文件的备用NTFS流“:bin”中；  
4、使用带有标志IO_REPARSE_TAG_MOUNT_POINT的API函数NtFsControlFile创建一个新的临时目录并将其安装点设置为“C:\Windows
”；  
5、在临时目录中创建一个名为“ system32”的新子目录；  
6、将合法的winsat.exe和winmm.dll复制到该子目录中；  
7、补丁winmm.dll：用恶意代码替换入口点代码；  
8、启动winsat.exe，由于DLL劫持，触发修补后的winmm.dll加载。

![sl_WastedLocker_01.png](https://image.3001.net/images/20200820/1597886710.png!small)

## 加密分析

为了对受害者的文件进行加密，木马的开发人员采用了AES和RSA算法的组合。恶意软件配置中设置了选择要加密哪些文件以及忽略路径列表，配置文件如下：

![sl_WastedLocker_02.png](https://image.3001.net/images/20200820/1597886714.png!small)

对于每个处理的文件，WastedLocker都会生成一个唯一的256位密钥和一个128位IV，密钥将用于在CBC模式下使用AES-256算法对文件内容进行加密。恶意软件会计算每个已处理文件的原始内容的MD5哈希值，并且可以在解密过程中利用此哈希值来确保过程的正确性。

原始内容的AES密钥，IV和MD5哈希以及一些辅助信息均使用嵌入在木马程序中的公共RSA密钥进行加密。

![sl_WastedLocker_03.png](https://image.3001.net/images/20200820/1597886724.png!small)

如果大量传播WastedLocker，上述加密方案中的一个受害者的解密器必须包含唯一的RSA私钥，该密钥可解密所有受害者文件，但dWastedLocker只针对特定组织进行攻击。

RSA加密的结果是通过Base64编码并保存在扩展名为.garminwasted_info的新文件中，每个受加密文件会创建一个新的信息文件，
这是BitPaymer和DoppelPaymer木马以前使用的方法。

![sl_WastedLocker_04.png](https://image.3001.net/images/20200820/1597886731.png!small)

![sl_WastedLocker_05.png](https://image.3001.net/images/20200820/1597886734.png!small)

## 总结

WastedLocker是为特殊攻击而设计制造的，它使用了“经典”的AES + RSA加密方案，如果没有攻击者的私有RSA密钥，无法解密加密文件。

为了防止被此类勒索软件攻击，需要遵循如下建议：

1、使用最新的操作系统和应用程序；  
2、不要在Internet上打开RDP访问。最好使用VPN来保护远程访问；  
3、使用有效主机安全解决方案，支持行为检测，自动文件回滚和许多其他技术来防止勒索软件的攻击。  
4、增强网络安全用户教育。

## IOC

[2cc4534b0dd0e1c8d5b89644274a10c1](https://opentip.kaspersky.com/2cc4534b0dd0e1c8d5b89644274a10c1/)

## 参考链接

https://securelist.com/wastedlocker-technical-analysis/97944/


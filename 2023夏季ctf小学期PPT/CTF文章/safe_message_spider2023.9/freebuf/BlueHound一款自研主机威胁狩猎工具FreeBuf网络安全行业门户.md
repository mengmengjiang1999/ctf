# BlueHound

BlueHound
是一款GUI版本主机威胁狩猎工具。支持上机/离线扫描webshell、CobaltStrike的beacon程序扫描以及内存扫描，基于.NET 4.6编译。

## 支持系统

  *  **Windows 10 x64**

  *  **Windows Server 2012 R2 x64及以上**

  *  **其他安装了.NET framework 4.6及以上的x64位操作系统**

## 简介

![image](https://image.3001.net/images/20220701/1656658966_62be9c16f23d24c6bacc1.png!small)  
三个选项功能如下：

  *  **WebShell** \- 扫描webshell,可以在上机排查的时候直接选择web应用目录扫描，或者将受害机上的文件拷贝到自己的机器离线扫描

  *  **Beacon** \- 扫描进程内存中可能存在的CobaltStrike的beacon程序

  *  **MemHunter** \- 扫描进程内存，导出存在可疑注入内容的内存dmp文件

## 使用方法

  1. 拷贝整个文件夹至需要调查的主机上

  2. 以管理员权限启动“BlueHound.exe”

  3. 按需选择要调查项目

## 检测效果

### WebShell

![image](https://image.3001.net/images/20220701/1656658987_62be9c2bb99703fe3bff7.png!small)

出于威胁狩猎的目的，所以检测特征写的比较宽泛，在使用过程中可能会出现一些误报。

### Beacon

Beacon选项主要扫描进程内存中可能存在的CobaltStrike beacon程序、C2
profile。可以扫描出绕过BeaconEye的beacon程序，执行原版beacon程序上线后，管理员权限启动BlueHound,选择Beacon扫描结果如下：

#### Stage

![image](https://image.3001.net/images/20220701/1656659003_62be9c3bb37f849e0c774.png!small)

![image](https://image.3001.net/images/20220701/1656659015_62be9c47d46de7b89dd90.png!small)

BeaconEye扫描被绕过，但是自研的增强beacon扫描功能扫描出了C2 profile特征，并导出了C2
profile所在的内存为dmp文件。可以用十六进制编辑器打开dmp文件后使用cyberchef做异或解密，如上图BlueHound会给出异或的key,本例中为`0x2e`

![image](https://image.3001.net/images/20220701/1656659029_62be9c55b82e018d7b9fd.png!small)

![image](https://image.3001.net/images/20220701/1656659055_62be9c6f27c14fe97a1a6.png!small)

或者使用开源工具[CobaltStrikeParser](https://github.com/Sentinel-One/CobaltStrikeParser)解析导出的dmp文件

![image](https://image.3001.net/images/20220701/1656659073_62be9c816855357550aa8.png!small)

PS：如果BlueHound扫描出来的异或key不是`0x2e`那么需要按需修改CobaltStrikeParser里的脚本进行适配

#### Stageless

![image](https://image.3001.net/images/20220701/1656659087_62be9c8f472b129a39f78.png!small)

对于stageless的beacon会扫描进程内存空间狩猎符合beacon程序内存特征的进程

![image](https://image.3001.net/images/20220701/1656659102_62be9c9e21b04e60441e2.png!small)

### MemHunter

MemHunter主要扫描进程内存中是否被注入可疑PE文件，如果是会dump出可疑文件所在内存dmp文件供分析。还是用绕过了上述扫描手段的beacon程序为例。

![image](https://image.3001.net/images/20220701/1656659116_62be9cac05df0ba02eaf9.png!small)

![image](https://image.3001.net/images/20220701/1656659126_62be9cb6cc8fdac88c984.png!small)

#### Inject

![image](https://image.3001.net/images/20220701/1656659141_62be9cc56fead0c173b8f.png!small)

![image](https://image.3001.net/images/20220701/1656659166_62be9cde5213fd1287554.png!small)

转储文件拖至IDA分析

![image](https://image.3001.net/images/20220701/1656659179_62be9ceb71cdc8f49700b.png!small)

## Q&A

Q：一些正常文件、进程被扫出来威胁？

A：由于是威胁狩猎工具，所以会存在一些误报，总体来说除了webshell扫描模块，误报还是比较可控的

## TO-DO

  * 命令行版本

  * 支持syslog外发告警信息

  * MemHunter导出PE文件时自动修复IAT

下载地址：[GitHub](https://github.com/10000Tigers/BlueHound/releases/tag/v1.0.0-beta)


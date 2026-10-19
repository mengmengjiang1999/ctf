NetWire 是一种公开可用的多平台远控木马（RAT），可以针对 Windows、MacOS 和 Linux 发起攻击。通过 Office
文档、嵌入下载链接的 PDF 文档利用网络钓鱼进行传播，其暗网售价在 40 美元到 140 美元不等。

NetWire 能够记录键盘击键、捕获屏幕截图、窃取密码、控制网络摄像头和麦克风等。

## 操作系统

![](https://image.3001.net/images/20210921/1632213438_614999bef151d7ddd46f5.png!small)

## 技术分析

2012 年 NetWire 首次在野被发现，一直被网络犯罪分子和 APT 组织使用。

该 Windows 可执行文件经过 UPX 加壳阻止分析，并且两次调用
`GetCursorPos`函数比较鼠标位置，不同才会运行。![](https://image.3001.net/images/20210921/1632213441_614999c16b8b223398a4a.png!small)

执行时，程序会创建一个子进程，然后将代码写入该进程。父进程将子进程写入 `User/AppData/Roaming/Install`并自行退出，文件名为
`Host.exe`。![](https://image.3001.net/images/20210921/1632213443_614999c3191cd36da1826.png!small)

NetWire
通过注册表自启动实现持久化：![](https://image.3001.net/images/20210921/1632213444_614999c4be89f125c3656.png!small)

通过分析内存中的字符串，可以看到 NetWrie
尝试通过浏览器收集用户登录数据。![](https://image.3001.net/images/20210921/1632213446_614999c69d956e886ebce.png!small)

恶意软件还会是扫描失陷主机的 Outlook 配置目录收集凭据，也会收集和记录击键和鼠标移动。这些信息可能在地下论坛和暗网中获得很好的售价。

NetWire 在失陷主机上的
`User/Analyst/AppData/Roaming/Logs`目录中创建一个日志文件，存储所有捕获的数据。日志文件使用 DAY-MONTH-YEAR
格式命名，与失陷主机被感染的日期相同。![](https://image.3001.net/images/20210921/1632213448_614999c8401e47d617c82.png!small)

日志文件通过 RC4 进行加密，NetWrie 还使用这种混淆技术来隐藏注册表、API、DLL 和其他字符串。

加密日志文件的内容如下所示，恶意软件在失陷主机上保持的时间越长，收集的数据越多，文件越大。![](https://image.3001.net/images/20210921/1632213449_614999c9e6a8bc27c3893.png!small)

恶意软件通过名为
`OqvAvPni`互斥量防止二次感染。![](https://image.3001.net/images/20210921/1632213451_614999cb8b02a85daeadb.png!small)

NetWire 尝试与远程 C&C 服务器创建连接，通过 3382 端口与 192.169.69.25 创建链接。从内存中可以发现，访问的 DNS 是
`love82.duckdns.org`。![](https://image.3001.net/images/20210921/1632213452_614999ccccdad1787d391.png!small)

示例中的 C&C
服务器可能不在线。![](https://image.3001.net/images/20210921/1632213454_614999ce4f9fe080951ee.png!small)

## Yara

    
    
    import "pe"
    rule NetWire_RAT {
    meta:
    description = "Detects NetWire Remote Access Trojan"
    author = "BlackBerry Threat Research Team"
    date = "2021-09-06"
    SHA256 = "021323e02e618769aab03cd9d5dea602ff684c2ff64ef592d69b119e78502fd9"
    
    strings:
    s2 = "key_dtor_list"
    s4 = "./mingw-w64-crt/crt/natstart.c"
    s6 = "./mingw-w64-crt/crt/tlsmcrt.c"
    s8 = "tagCOINITBASE"
    s10 = "winnt.h"
    $s11 = "fwrite"
    
    condition:
    ( uint16(0) == 0x5a4d and filesize < 1500KB and
    pe.imphash() == "084fafd5fea9d39b4ff35f2d82f0908b" and pe.number_of_sections == 15 and ( all of them )
    )
    }

## IOC

> 021323e02e618769aab03cd9d5dea602ff684c2ff64ef592d69b119e78502fd9  
> love82.duckdns.org  
> 192.169.69.25

## 参考来源

> [BlackBerry](https://blogs.blackberry.com/en/2021/09/threat-thursday-> netwire-rat-is-coming-down-the-line)


# **背景**

    
    
    电脑病毒 incaseformat在国内大面积爆发，该蠕虫病毒会删除用户特定盘符的所有文件，造成用户数据信息大量丢失。incaseformat 蠕虫病毒发现至今已有10多年历史，一般通过 U 盘进行传播，该蠕虫病毒会遍历删除系统盘以外的文件，并在根目录下创建名为 incaseformat.txt的空文件，由于病毒代码中设置变量值的错误，导致计算当前系统时间出错，所以直到 2021 年 1 月 13 日才被触发。
        工程师分析发现，此次的病毒与常见的蠕虫病毒不同，除了具有伪装文件夹图标，隐藏原始文件夹，将自身复制 到 C 盘 Windows 目录下，并创建注册表自启动，还设置了定时删除文件的逻辑。当用户重启计算机后，将病毒将自启动，遍历除系统盘之外的盘符并删除所有文件。不仅如此，该病毒设定的删除日期不止今天（1月13日），距离最近的下一次删除时间为1月23日。如果用户电脑中还有残留的病毒，将面临再次被删除的危害。
    

# **威胁分析**

    
    
    incaseformat 蠕虫病毒运行后，会首先判断是否在系统盘目录下和自身文件名，随后进行自复制和设置注册表自启动，启动后判断自身文件路径是否为 "C:\windows\tsay.exe" 或者 "C:\windows\ttry.exe"，当路径名为 "C:\windows\ttry.exe" 才会下一步运行。
    

![图片.png](https://image.3001.net/images/20210121/1611215272_600931a852e71272143c4.png!small)

    
    
    同时修改注册表键值实现自启动，涉及注册表项为：
    

HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce\msfsa  
![图片.png](https://image.3001.net/images/20210121/1611215334_600931e6f28a1262f206c.png!small)

    
    
    该病毒由于编写时对某时间判断变量赋值错误，导致在今天（2021年1月13日）才触发并执行文件删除的代码逻辑，实际该病毒可能已在感染主机上驻留多年，但由于缺少主机防病毒软件或白名单设置错误等原因，一直未能被发现。该病毒所使用的delphi库中的 DateTimeToTimeStamp 函数中 IMSecsPerDay 变量的值错误，最终导致 DecodeDate 计算转换出的系统当前时间错误。也因为上述原因，该样本作为一个老病毒。直到2021年1月13日才触发删除用户文件的代码逻辑。
    

![图片.png](https://image.3001.net/images/20210121/1611215355_600931fb9554bfb2b26b3.png!small)

# 处置建议

  1. 检测是否存在以下文件：  
C:\Windows\tsay.exe C:\Windows\ttry.exe  
![图片.png](https://image.3001.net/images/20210121/1611215365_600932058974781c9eead.png!small)  
2.检测注册表路径  
“HKEY_LOCAL_MACHINE\SOFTWARE\Wow6432Node\Microsoft\Windows\CurrentVersion\RunOnce”是否存在“msfsa”项。  
3.数据恢复  
切勿对被删除文件的分区执行写操作，以免覆盖原有数据，然后使用常见的数据恢复软件即可恢复被删除数据。


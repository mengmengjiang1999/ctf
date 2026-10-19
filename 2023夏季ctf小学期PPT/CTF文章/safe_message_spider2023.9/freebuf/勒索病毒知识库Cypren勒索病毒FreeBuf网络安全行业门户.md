## **勒索信息**

![图片1.png](https://image.3001.net/images/20190709/1562633660_5d23e5bcd730b.png!small)

![图片12_副本.png](https://image.3001.net/images/20190709/1562633664_5d23e5c0e9e27.png!small)

 **加密后缀** ：.ENCRYPTED。

![图片2_副本.png](https://image.3001.net/images/20190709/1562633687_5d23e5d77f6a2.png!small)

 **解密工具** ：该勒索病毒暂无解密工具。

 **其他特征** ：运行后弹框。

![图片3.png](https://image.3001.net/images/20190709/1562633695_5d23e5dfdd31b.png!small)

##  **详细分析**

1.获取主机相应的文件目录，如下所示：

![图片4_副本.png](https://image.3001.net/images/20190709/1562633710_5d23e5ee5e0a0.png!small)相应的目录列表：

    
    
    C:\Users\用户名\Desktop
    
    C:\Users\用户名\Downloads
    
    C:\Users\用户名\Documents

2.设定磁盘的名称列表，如下所示：

![图片5_副本.png](https://image.3001.net/images/20190709/1562633714_5d23e5f29f906.png!small)

磁盘名列表：

    
    
    B、D、E、F、G、H、I、J、K、L、M、N、O、P、C

3.循环遍历磁盘，如下所示：

![图片6_副本.png](https://image.3001.net/images/20190709/1562633723_5d23e5fb90270.png!small)

4.枚举目录下的文件，如下所示：

![图片7_副本.png](https://image.3001.net/images/20190709/1562633727_5d23e5ff369d8.png!small)

5.判断相应的目录或文件名包含如下字符串则跳过，如下所示：

![图片8_副本.png](https://image.3001.net/images/20190709/1562633732_5d23e60489ae9.png!small)

相应的字符串为：ENCRYPTED、READ_THIS、.sys等。

6.判断文件名后缀是否为如下后缀则跳过，如下所示：

![图片9_副本.png](https://image.3001.net/images/20190709/1562633739_5d23e60b2c9a5.png!small)

相应的后缀列表：vhd、vhdx、vdi。

7.然后遍历之前获取的目录列表：

    
    
    C:\Users\用户名\Desktop
    
    C:\Users\用户名\Downloads
    
    C:\Users\用户名\Documents

如下所示：![图片10.png](https://image.3001.net/images/20190709/1562633746_5d23e612efbf3.png!small)

8.如果遍历的磁盘目录为C盘，则跳过C盘下的特定目录，如下所示：

![图片11_副本.png](https://image.3001.net/images/20190709/1562633753_5d23e6197ee73.png!small)

跳过以下目录和文件，如下:

    
    
    PerfLogs
    
    Program Files
    
    Program Files (x86)
    
    ProgramData
    
    Users
    
    Windows
    
    System Volume Information
    
    $Recycle.Bin
    
    . (当前目录)
    
    .. (上一级目录)
    
    bootmgr
    
    BOOTNXT
    
    Documents and Settings
    
    hiberfil.sys
    
    MSOCache
    
    pagefile.sys
    
    swapfile.sys

![图片22.png](https://image.3001.net/images/20190709/1562633977_5d23e6f9205f5.png!small)![图片23.png](https://image.3001.net/images/20190709/1562633983_5d23e6ff34ac8.png!small)

9.如果文件为以下后缀名，则加密文件，如下所示：

![图片14.png](https://image.3001.net/images/20190709/1562633996_5d23e70c266f8.png!small)

会加密的文件的后缀名列表，如下：

    
    
    txt、jpg、png、xml、doc、docx、xls、xlsx、ppt、pptx、gif、bmp、sql、php、html、cs、cpp、docm、docb、rar、zip、xlm、xml、py、rb、mp3、mp4、xlsb、xla、xlam、xll、xlw、pdf、pps、pot、accdb、accde、accdt、accdr、cert、swf、mdb、rtf、gzip、tar、css。

10.创建线程，加密文件，如下所示：

![图片16.png](https://image.3001.net/images/20190709/1562634097_5d23e7713014b.png!small)

11.加密后的文件后缀名为ENCRYPTED，如下所示：

![图片16.png](https://image.3001.net/images/20190709/1562634102_5d23e776adb86.png!small)

加密文件过程，如下所示：

![图片17.png](https://image.3001.net/images/20190709/1562634109_5d23e77d1662c.png!small)

12.在内存中解密出相应的勒索信息，如下所示：

![图片18.png](https://image.3001.net/images/20190709/1562634113_5d23e78172927.png!small)

生成相应的勒索超文本信息READ_THIS_TO_DECRYPT.html，如下所示：

![图片19_副本.png](https://image.3001.net/images/20190709/1562634117_5d23e78571f31.png!small)

13.加密完成之后，弹出相应的勒索信息，如下所示：

![图片20_副本.png](https://image.3001.net/images/20190709/1562634134_5d23e7961a73d.png!small)

##  **病毒防御**

再次提醒广大用户，勒索病毒以防为主，目前大部分勒索病毒加密后的文件都无法解密，注意日常防范措施：

1.及时给电脑打补丁，修复漏洞；

2.对重要的数据文件定期进行非本地备份；

3.不要点击来源不明的邮件附件，不从不明网站下载软件；

4.尽量关闭不必要的文件共享权限；

5.更改账户密码，设置强密码，避免使用统一的密码，因为统一的密码会导致一台被攻破，多台遭殃；

6.如果业务上无需使用RDP的，建议关闭RDP。

 ***本文作者：深信服千里目安全实验室，转载请注明来自FreeBuf.COM**


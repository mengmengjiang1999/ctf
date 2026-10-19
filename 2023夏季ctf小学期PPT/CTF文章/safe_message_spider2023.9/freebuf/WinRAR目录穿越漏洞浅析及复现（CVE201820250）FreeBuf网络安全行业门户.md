***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

 ***本文原创作者：ERFZE，本文属FreeBuf原创奖励计划，未经许可禁止转载**  

## 0x00 前言

**我是于2月21号看见各大安全网站都发布了"WINRAR曝出严重漏洞，影响全球5亿用户"的文章，才了解到这个漏洞。等到真正去研究它，是backlion师傅已经将exp发出来之后了。这是本菜研究及复现的第一个漏洞，其中若有分析不到位或者错误的地方烦请各位师傅指正，谢谢。**

## 0x01 本文结构概览

![下载.jpeg](https://image.3001.net/images/20190310/1552194329_5c849b1921861.jpeg!small)

## 0x02 漏洞描述

该漏洞由Check
Point团队爆出，是一个关于WinRAR存在了19年的漏洞，用它来可以获得受害者计算机的控制。攻击者只需利用此漏洞构造恶意的压缩文件，当受害者使用WinRAR解压该恶意文件时便会触发漏洞。

> 其实不只是WinRAR，凡是使用了UNACE2.dll动态链接库的解压软件就会受影响，具体可参考0x03中受该漏洞影响的解压软件及版本号。

该漏洞是由 WinRAR 所使用的一个陈旧的动态链接库UNACEV2.dll所造成的，该动态链接库在 2006 年被编译，没有任何的基础保护机制(ASLR,
DEP 等)。动态链接库的作用是处理 ACE
格式文件。而WinRAR解压ACE文件时，由于没有对文件名进行充分过滤，导致其可实现目录穿越，将恶意文件写入任意目录,甚至可以写入文件至开机启动项，导致代码执行。

## 0x03 漏洞影响

> WinRAR < 5.70 Beta 1
>
> Bandizip < = 6.2.0.0(笔者没有测试Bandzip，有兴趣的师傅可以自行测试)
>
> 好压(2345压缩) < = 5.9.8.10907
>
> 360压缩 < = 4.0.0.1170

## 0x04 漏洞危害

> 通过该漏洞攻击者可以向用户的开机启动项中植入恶意程序，实现监控受害者主机的目的。
>
> DLL劫持

## 0x05 漏洞原理浅析

### 0x05-1 CleanPath

先来看看Check Point团队发布的文章中给出的CleanPath的伪代码：

    
    
    Bool CleanPath(PCHAR Path)
    {
     char *PathTraversalPos=NULL;
     if(Path[1]==':' && Path[2]=='\\')
      strcpy(Path,&Path[3]);
     if(Path[1]==':' && Path[2]!='\\')
      strcpy(Path,&Path[2]);
     PathTraversalPos=strstr(Path,"..\\");
     while(PathTraversalPos)
     {
      if(PathTraversalPos==Path || *(PathTraversalPos-1)=='\\')
      {
       strcpy(Path,&Path[3]);
       PathTraversalPos=strstr(Path,"..\\");
      }
      else
      {
       PathTraversalPos=strstr(Path+1,"..\\");
      }
     }
     return Path;
    }
    

在执行GetDevicePathLen这个函数之前，CleanPath会清除path中的一些简单的目录遍历序列，比如：

> \\..\
>
> 盘符名:\
>
> 盘符名:
>
> 盘符名:\盘符名:
>
> ..\\(只有它在path的开始处才会被清除)

这段伪代码的大概流程描述如下：

> 1.如果Path的第2、3个字符为":"、"\"，那么将Path第4个字符之前的部分清除。
>
> 2.如果Path的第2个字符为":"，第3个字符不为"\"，那么将Path第3个字符之前的部分清除。
>
> 3.在Path中寻找"..\"出现的位置，PathTraversalPos将指向此位置。若找到，执行4；否则执行7。
>
>
> 4.如果PathTraversalPos指向的位置正是Path开始的位置(e.g.`..\some_folder\some_file.ext`)或者PathTraversalPos指向位置的前一个字符是"\"，执行5；否则，执行6。
>
> 5.将Path第4个字符之前的部分清除,继续在Path中寻找"..\"出现的位置，若找到，执行4；否则，执行7。
>
> 6.在Path+1处向后寻找"..\"出现的位置，若找到，执行4；否则，执行7。
>
> 7.返回Path。

通过上述分析我们可以看出`盘符名:\`是在步骤1被清除掉的，`盘符名:`是在步骤2被清除掉的；`盘符名:\盘符名:`是通过步骤1和步骤2两个步骤清除掉的；而`\..\`是在步骤5被清除掉的。

### 0x05-2 GetDevicePathLen

GetDevicePathLen的伪代码：

    
    
     INT GetDevicePathLen(PCHAR Path)
     {
      PCHAR SlashPos;
      INT Result;
      Result=0;
      if(Path[0]=="\\")
      {
       if(Path[1]=="\\")
       {
        if(!(SlashPos=strchr(&Path[2],"\\")))
        {
         return 0;
        }
        if(!(SlashPos=strchr(SlashPos+1,"\\")))
        {
         return 0;
        }
        Result=(UINT)SlashPos-(UINT)Path+1;
       }
       else
       {
        Result=1;
       }
      }
      else
      {
       if(Path[1]=":";
       {
        Result=2;
        if(Path[2]="\\")
        {
         Result++;
        }
       }
      }
      return Result;
     }
    

GetDevicePathLen会返回一个Result，Result取值有两种情况：非0和0。可以看看Check Point团队给出的例子：

> C:\folder\file.ext`return:3`
>
> \folder\file.ext`return:1`
>
> \\\LOCALHOST\C$\folder\file.ext`return:15`
>
> \\\?\Harddisk0Volume1\folder\file.ext`return:21`
>
> folder\file.ext`return:0`

这段伪代码的大概流程描述如下：

> 1.如果Path中第1个字符为"\"，执行2；否则，执行7。
>
> 2.如果Path中第2个字符为"\"，执行3；否则，执行6。
>
> 3.如果在Path第3个字符之后没有找到"\"，返回0；否则将SlashPos指向此位置。
>
> 4.如果在SlashPos+1之后没有找到"\"，返回0；否则将SlashPos指向此位置。
>
>
> 5.将SlashPos指向位置减去Path指向位置再加1赋值给Result(e.g.`\\?\Harddisk0Volume1\folder\file.ext`)，然后执行9。
>
> 6.Result赋值为1，然后执行9。
>
> 7.如果Path第2个字符为":"，Result赋值为2。
>
> 8.如果Path第3个字符为"\"，Result值加1。
>
> 9.返回Result。

这样我们就可以知道例子中的返回值是如何计算出来的了。

### 0x05-3 WinRAR Validators / Callbacks

![下载
\(1\).jpeg](https://image.3001.net/images/20190310/1552194392_5c849b5877b4a.jpeg!small)

这段伪代码的功能很简单，执行以下检查：

1.第一个字符不等于"\"或"/"。

2.文件名不以以下字符串"..\"或"../"开头。

3.字符串中不存在：

> \\..\
>
> \\../
>
> /../
>
> /..\

### 0x05-4 触发目录遍历漏洞的sprintf

![下载
\(2\).jpeg](https://image.3001.net/images/20190310/1552194415_5c849b6fdbf5f.jpeg!small)

如果调用GetDevicePathLen，返回的结果为0，则执行

    
    
    sprintf（final_file_path，“％s％s”，destination_folder，file_relative_path）;
    

即图中蓝色箭头指向的部分。

如果调用GetDevicePathLen，返回的结果不为0，则执行

    
    
    sprintf（final_file_path，“％s％s”，“”，file_relative_path）;
    

即图中红色箭头指向的部分，这就是触发目录遍历漏洞的错误代码。

## 0x06 构造路径

思路如下所示：

> 1.GetDevicePathLen函数的结果应不为0；
>
> 2.执行 `sprintf（final_file_path，“％s％s”，“”，file_relative_path）;` 代替
> `sprintf（final_file_path，“％s％s”，destination_folder，file_relative_path）;`
>
> 3.绕过CleanPath函数；
>
> 4.绕过WinRAR Validators / Callbacks。

通过上述思路来分析Check Point团队给出的最强攻击向量：

    
    
    C:\C:C:../AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\some_file.exe
    

> 1.开始字符不在WinRAR Validators / Callbacks的黑名单中；
>
> 2.CleanPath函数将清除掉开头的"C:\C:"；
>
> 3.GetDevicePathLen函数的结果为2；
>
> 4.执行 `sprintf（final_file_path，“％s％s”，“”，file_relative_path）;`

成功！！最终路径为：

    
    
    C：../ AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\some_file.exe
    

如果我们在桌面解压文件，那么"当前目录"为：

    
    
    C:\Users\<user name>\Desktop
    

![下载
\(3\).jpeg](https://image.3001.net/images/20190310/1552194448_5c849b901247c.jpeg!small)![下载
\(4\).jpeg](https://image.3001.net/images/20190310/1552194468_5c849ba43aff0.jpeg!small)

经过上面的操作我们的路径将会变为：

    
    
    C:\Users\<user name>\Desktop../AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\some_file.exe
    

这样"../"会返回到上一层文件夹，即

    
    
    C:\Users\<user name>\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\some_file.exe
    

这样就将`some_file.exe`添加到启动目录了。

其他"当前目录"的例子比如：`C：\Program Files\WinRAR`、`C:\Users\<user
name>\Downloads`就不再上图了。

## 0x07 UNACEV2.dll校验CRC引发漏洞

漏洞主要是由Winrar用来解压ACE文件时使用的动态链接库UNACEV2.dll引起的，UNACEV2.dll在处理filename时只校验了CRC。故我们可以通过使用HxD修改filename（也就0x06中的最强攻击向量，我们无法直接去修改filename，所以要用HxD去修改ACE二进制文件）将恶意文件解压到启动目录，但是在修改完成后，CRC校验会失败，所以我们还要再去修改CRC，具体过程请见下面的分析。

### 0x07-1 建立ACE文件

这里要使用WinACE这个工具:

![下载
\(5\).jpeg](https://image.3001.net/images/20190310/1552194516_5c849bd478200.jpeg!small)

建立一个ACE格式文件：

![下载
\(6\).jpeg](https://image.3001.net/images/20190310/1552194528_5c849be06fba3.jpeg!small)

注意红色框中要选取"store full path"：

![下载
\(7\).jpeg](https://image.3001.net/images/20190310/1552194541_5c849bedbfd84.jpeg!small)

使用HxD工具来查看一下example.ace这个文件，可以看到下图中蓝色选中部分的路径是我们上图中绿色框中的路径：

### ![下载
\(8\).jpeg](https://image.3001.net/images/20190310/1552194553_5c849bf9ce751.jpeg!small)0x07-2
ACE文件的header信息

使用github上的工具acefile.py来查看我们创建的ACE文件的header信息。

![下载
\(9\).jpeg](https://image.3001.net/images/20190310/1552194624_5c849c4031208.jpeg!small)

结果中有两个header（红色划线部分），重点在第二个header。

> hdr _ crc：CRC校验后的结果
>
> filename：文件路径
>
> hdr _ size:头部大小（我没有在图片中框出来，抱歉）
>
> filename _ size：文件名的大小（acefile.py没有把这个列出来，可以见下图中我的标示）

修改filename后CRC校验的结果与hdr_size都会发生变化，所以我们还要再修改hdr_crc与hdr _ size。

### 0x07-3 修改ACE的header

![下载
\(10\).jpeg](https://image.3001.net/images/20190310/1552194650_5c849c5a9a973.jpeg!small)

> 绿色：hdr _ crc
>
> 红色：hdr _ size
>
> 紫色：filename _ size

 **P.S.** filename没有标出，但在右侧可以看到：`Users\Administrator\Desktop\example.txt`

 **0x07-3.1 修改filename**

在右侧选中`Users\Administrator\Desktop\example.txt`，将其修改为`C:\ProgramData\Microsoft\Windows\Start
Menu\Programs\example.txt`

 **0x07-3.2 修改filename_size**

![下载
\(1\).jpg](https://image.3001.net/images/20190310/1552194796_5c849cece4817.jpg!small)

将蓝色选中部分前面2字节的`27 00`改为`40 00`，因为是小端序，所以是从后向前。

 **0x07-3.3 修改hdr_size**

![下载.jpg](https://image.3001.net/images/20190310/1552194832_5c849d10760e3.jpg!small)

将蓝色选中部分前面2字节的`71 00`改为`5F
00`。（这一步的截图，由于我中间操作失误，所以与上面的图片不是一个文件，但修改的位置是正确的，hdr_crc后面接着的就2字节的hdr
_size，所以比较好找。）

 **0x07-3.4 修改hdr_crc**

这一步需要使用acefile.py重新查看一下这个文件，得到下图：

![下载\(2\).jpg](https://image.3001.net/images/20190310/1552194894_5c849d4e70055.jpg!small)

可以看到给出的信息上面部分是正确的hdr_crc：`4766`

而下面部分是现在的hdr_crc：`cda9`。在HxD中修改掉它（注意是小端序）：

![下载\(3\).jpg](https://image.3001.net/images/20190310/1552194951_5c849d87783b6.jpg!small)

 **0x07-3.5 再次查看头部信息**

修改完成后再使用acefile.py去查看一下头部信息：

![下载\(4\).jpg](https://image.3001.net/images/20190310/1552194966_5c849d96c2a82.jpg!small)

修改成功。

## 0x08 演示

我这里使用的是winrar 5.50.0.0破解版，可以去安装目录中看到存在UNACEV2.dll

[](http://www.example.com/)![下载.gif](https://image.3001.net/images/20190310/1552194996_5c849db49585f.gif!small)

我在桌面放了一个文件example（最强攻击向量）.ace的文件，其实后缀改成rar也是可以的，winrar在解压的时候检验的是格式而非后缀。（说明：我这个文件中的filename是Check
Point团队给出的最强攻击向量，而非0x07中我修改的filename，请大家在测试的时候注意一下，我会在最后把需要用到文件都放出来）

![下载
\(1\).gif](https://image.3001.net/images/20190310/1552195020_5c849dcc33747.gif!small)

对好压的测试就不放图了，测试结果是同样存在这个漏洞。360zip在测试的时候，它会提示格式损坏，但是在它的安装目录中确实存在UNACEV2.dll，如果有师傅测试成功，可以指导一下，谢谢。

## 0x09 参考链接及用到的文件

> <https://research.checkpoint.com/extracting-code-execution-from-winrar/>
>
> <https://www.cnblogs.com/backlion/p/10417985.html>

用到的文件百度网盘链接: <https://pan.baidu.com/s/1rQF7ha1O-xoy5gOQF0tNYw> 提取码: eus4
（有无后门及木马请各位自查）

## 0x10 修复建议

1.升级到最新版本的 WinRAR ，目前版本是 5.70 Beta 1。下载地址如下：

> 32 位：<http://win-rar.com/fileadmin/winrar-versions/wrar57b1.exe>
>
> 64 位：<http://win-rar.com/fileadmin/winrar-versions/winrar-x64-57b1.exe>

2.删除UNACEV2.dll。

## 0x11 exp 链接

> <https://github.com/WyAtu/CVE-2018-20250/>  
>
>
> <https://www.freebuf.com/articles/network/197025.html>  
>

***本文原创作者：ERFZE，本文属FreeBuf原创奖励计划，未经许可禁止转载**


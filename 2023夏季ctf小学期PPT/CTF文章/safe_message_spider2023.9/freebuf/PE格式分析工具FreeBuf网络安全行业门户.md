**HW期间，为防范钓鱼，即日起FreeBuf将取消投稿文章的一切外部链接。给您带来的不便，敬请谅解~**

经过大半个月参考和学习网上各位大神的文案， **做了一款*.dll和*.exe的PE格式分析工具，此工具可以分析32位和64位系统下可执行文件。**
1.0版本略显粗造，请各路大神多多指导，也欢迎大家多多交流。

目前有5大板块: **【DOS头信息】、【NT头信息】、【节表信息】、【数据目录表】、【地址计算】** 。（*含中文注解，底部有工具下载链接）

![](https://image.3001.net/images/20210420/1618902212_607e7cc404887af12cf9e.png!small)

 **第一板块：【DOS头信息】：DOS头表的所有信息，显示DOS表下各成员**

![](https://image.3001.net/images/20210420/1618902224_607e7cd0a74115186281d.png!small)

**第二板块：【NT头信息】：分为【文件头信息】和【可选映像头信息】；**![](https://image.3001.net/images/20210420/1618902240_607e7ce08ee500b438306.png!small)

### 一：【文件头信息】：所含可执行文件的运行平台，文件生成时间，文件属性等文件信息，简单明了的了解文件所有信息；  
![](https://image.3001.net/images/20210420/1618902251_607e7ceb8d4a49c6b8039.png!small)

###

###
二：【可选映像头信息】：信息量较大，映像头包含可执行文件程序执行入口的RVA，文件类型，函数何时被调用等等；![](https://image.3001.net/images/20210420/1618902261_607e7cf50494edcccddc3.png!small)

**第三板块【节表信息】：使用下拉选项来显示每一个节的内存偏移地址，属性等等；**![](https://image.3001.net/images/20210420/1618902271_607e7cffdab7a81d4c893.png!small)

 **第四板块【数据目录表】：可执行文件的各种表的RVA，以及Size；含【导出表】、【导入表】、【重定位表】的详细信息；**

![](https://image.3001.net/images/20210420/1618902280_607e7d08cf6213223597f.png!small)

### 一：【导出表】:可执行文件所导出的函数、地址信息等。

![](https://image.3001.net/images/20210420/1618902292_607e7d14327ec5ad18398.png!small)

IMAGE_EXPORT_DIRECTORY 结构的重要成员：  
DWORD NumberOfFunctions; // 所有的导出函数的个数  
DWORD NumberOfNames; // 以名字导出的函数的个数  
DWORD AddressOfFunctions; // 导出的函数地址表的RVA  
DWORD AddressOfNames; // 导出的函数名称表的RVA  
DWORD AddressOfNameOrdinals // 导出的函数序号表的RVA  
找出所有的导出函数:  
![](https://image.3001.net/images/20210420/1618902302_607e7d1e2a1ce18b1a8a0.png!small)

1.以NumberOfFunctions导出函数的个数为准，循环遍历函数地址表的RVA;  
2.当找到函数地址表不为零时，嵌套循环以NumberOfNames 名字导出的函数的个数循环遍历函数的序号的 RVA；  
3.如果函数地址的ＲＶＡ 和 函数的序号的 RVA相同的话，那么这就是函数名称的RVA，即可找到该地址的函数;

### 二：【导入表】：简单来说就是代表了该模块调用了哪些外部的API

![](https://image.3001.net/images/20210420/1618902326_607e7d36e210f2a77a34a.png!small)

IMAGE_IMPORT_DESCRIPTOR结构的重要成员：  
DWORD OriginalFirstThunk; //导入名称表  
DWORD FirstThunk; //导入地址表  
//OriginalFirstThunk和FirstThunk都指向的是_IMAGE_THUNK_DATA32结构体  
_IMAGE_THUNK_DATA32  
{  
DWORD ForwarderString; // PBYTE  
DWORD Function; // PDWORD，导入函数的地址  
DWORD Ordinal; // 序号  
DWORD AddressOfData;
//PIMAGE_IMPORT_BY_NAME，假如是函数名导入的，它指向另外一个结构体：PIMGE_IMPORT_BY_NAME  
}  
_IMAGE_IMPORT_BY_NAME  
{  
WORD Hint ; // 序号  
BYTE Name[1]; // 函数名  
}

找出所有的导入函数：  
![](https://image.3001.net/images/20210420/1618902344_607e7d48780249c12ddb9.png!small)

1.通过IMAGE_IMPORT_DESCRIPTOR结构的OriginalFirstThunk导入名称表参数，从RvaToOffset找到名称表_IMAGE_THUNK_DATA32的RVA  
2.如果名称表的AddressOfData值不为零，增加名称表和地址表本身值大小，循环查找下一个，直到为0则退出。  
3.在循环体本身判断：如果序号超出最大范围值，说明是以序号导入的；不然则是以函数名导入，将AddressOfData的RvaToOffset，便得到该函数名。

### 三：【重定位表】:地址的重定向表

![](https://image.3001.net/images/20210420/1618902360_607e7d583d46d326ff528.png!small)

IMAGE_BASE_RELOCATION结构的重要成员：  
DWORD VirtualAddress； //要修正的数据的基地址，RVA  
DWORD SizeOfBlock; //大小

获取所有的重定位信息：  
![](https://image.3001.net/images/20210420/1618902371_607e7d6325078f33a79cb.png!small)

1\. 找到重定位表的地址后；  
2.当表地址和大小不为零时，循环遍历重定位信息，找到首个重定位信息，以该重定位的大小为主嵌套循环，找到该重定位的地址和重定位类型,
再将重定位信息加上SizeOfBlock，继续循环遍历下一块重定位信息;

 **第五板块【地址计算】： VA，RVA，OFFSET之间值的计算，显示此值的所在区块和字节内容**

![](https://image.3001.net/images/20210420/1618902382_607e7d6e9b1ccda0c7a56.png!small)

 **工具下载地址：**  
 **https://pan.baidu.com/s/1HKhs2_te4cllE3RQ5UPaig?_at_=1618891328986**  
 **提取码：1234；**

>  **参考链接：**  
>  PE格式概述：  
>
> [url=https://www.cnblogs.com/2f28/p/9800992.html]https://www.cnblogs.com/2f28/p/9800992.html[/url]  
>
> [url=https://blog.csdn.net/qq_36746738/article/details/74171292]https://blog.csdn.net/qq_36746738/article/details/74171292[/url]  
> DOS头学习资料:  
>
> [url=https://blog.csdn.net/pxm2525/article/details/39895487]https://blog.csdn.net/pxm2525/article/details/39895487[/url]  
> NT头学习资料：  
>
> [url=https://blog.csdn.net/chy_chenyang/article/details/80768654]https://blog.csdn.net/chy_chenyang/article/details/80768654[/url]  
> 文件头学习资料：  
>
> [url=https://blog.csdn.net/jiangqin115/article/details/79757041]https://blog.csdn.net/jiangqin115/article/details/79757041[/url]  
>
> [url=https://blog.csdn.net/u011513939/article/details/73496402]https://blog.csdn.net/u011513939/article/details/73496402[/url]  
>
> [url=https://blog.csdn.net/chy_chenyang/article/details/80768654]https://blog.csdn.net/chy_chenyang/article/details/80768654[/url]  
> 可选映像头学习资料：  
>
> [url=https://blog.csdn.net/chy_chenyang/article/details/80768654]https://blog.csdn.net/chy_chenyang/article/details/80768654[/url]  
>
> [url=https://www.cnblogs.com/kuangke/p/5393514.html]https://www.cnblogs.com/kuangke/p/5393514.html[/url]  
> 节表信息学习资料：  
>
> [url=https://www.cnblogs.com/IMyLife/p/4826090.html]https://www.cnblogs.com/IMyLife/p/4826090.html[/url]  
>
> [url=https://www.cnblogs.com/ruingking/p/10867778.html]https://www.cnblogs.com/ruingking/p/10867778.html[/url]  
> 导入表学习资料：  
>
> [url=https://www.cnblogs.com/SunsetR/p/11192555.html]https://www.cnblogs.com/SunsetR/p/11192555.html[/url]  
>
> [url=https://blog.csdn.net/weixin_42489582/article/details/84800464]https://blog.csdn.net/weixin_42489582/article/details/84800464[/url]  
> 导出表学习资料：  
>
> [url=https://www.cnblogs.com/iBinary/p/9739031.html]https://www.cnblogs.com/iBinary/p/9739031.html[/url]  
>
> [url=https://blog.csdn.net/with_dream/article/details/81144496]https://blog.csdn.net/with_dream/article/details/81144496[/url]  
> 重定位表学习资料：  
>
> [url=https://bbs.pediy.com/thread-246759.htm]https://bbs.pediy.com/thread-246759.htm[/url]  
>
> [url=https://blog.csdn.net/qq_40890756/article/details/90080880]https://blog.csdn.net/qq_40890756/article/details/90080880[/url]


## **情报背景**

继Bumblebee通过使用ISO内组合恶意LNK+DLL的方式进行网络钓鱼活动被曝光之后，研究人员对落地的DLL文件进行了深入分析，原文中对恶意软件防御规避的技术部分做了重点分析，并指出BumbleBee可能与被观察到使用该技术的Trickbot有相关性。

 **关联组织**

|

BumbleBee  
  
---|---  
  
 **战术标签**

|

防御规避  
  
 **技术标签**

|

HOOK DLL  
  
 **情报来源**

|

https://elis531989.medium.com/the-chronicles-of-bumblebee-the-hook-the-bee-and-the-trickbot-connection-686379311056  
  
##  **01** 攻击技术分析

 **亮点: 挂钩NT函数来劫持LoadLibrary**

dopper的导出函数通过一系列的内存分配和解密操作后，最终从内存中解密出一个新的PE载荷。

![1655175149_62a7f7ed44f8a12b1e7a3.png!small?1655175150937](https://image.3001.net/images/20220614/1655175149_62a7f7ed44f8a12b1e7a3.png!small?1655175150937)

图:内存中的新载荷文件

dopper接下来通过GetProcAddress分别获取NtOpenFile、NtCreateSection、NtMapViewOfSection的函数地址并挂钩。

![1655175172_62a7f8041d2c5eeb3b346.png!small?1655175173775](https://image.3001.net/images/20220614/1655175172_62a7f8041d2c5eeb3b346.png!small?1655175173775)

图:获取NT函数

完成挂钩后，dropper将尝试使用LoadLibrary加载GdiPlus.dll并从中获取SetPath的导出函数。

![1655175187_62a7f813512648864837d.png!small?1655175188919](https://image.3001.net/images/20220614/1655175187_62a7f813512648864837d.png!small?1655175188919)

图:LoadLibrary加载GdiPlus.dll

GdiPlus.dll
作为系统DLL，并没有SetPath导出函数呢，这一步是Bumblebee偷梁换柱，挂钩的NTCreateSection会将系统DLL的内容替换成恶意DLL，具体操作如下：

1\. 使用CreateSection创建可执行的Section

2\. 将解密后的恶意内容写入此部分

3\. 返回NTSTATUS_SUCCESS给LoadLibrary，因此看起来像是GdiPlus.dll已经被成功映射

![1655175200_62a7f820f3a1145d07d07.png!small?1655175202663](https://image.3001.net/images/20220614/1655175200_62a7f820f3a1145d07d07.png!small?1655175202663)

图:NtMapViewOfSection的钩子函数

完成后恶意模块将占据合法gdiplus.dll的空间。

![1655175244_62a7f84c38b35b2b5a3af.png!small?1655175246770](https://image.3001.net/images/20220614/1655175244_62a7f84c38b35b2b5a3af.png!small?1655175246770)

图:从processhacker中观察被替换的gdiplus.dll

缺陷: 通过EXPORTS暴露的原始DLL名称

文章中分别使用PEstudio和PE-Bear对Bumblebee的初始DLL进行了分析，PEstudio的图中展示出droper的编译时间是2022年3月（compiler-stamp、debugger-stamp、exports-stamp都有相同的时间戳），entropy项演示该droper的熵值为6.561，熵值较高通常表明该程序包含很多随机数据，可能会在运行时进行加密解密。

PE-bear的分析图则表明该droper包含两个导出函数IternalJob和SetPath,
内部的编译名称似乎为“lodqcbw041xd9.dll”。不管这个奇怪名称的真实性，可以从EXPORTS中获取编译名称还是较少被注意到。

![1655175265_62a7f8611e22fba0a7bcd.png!small?1655175266767](https://image.3001.net/images/20220614/1655175265_62a7f8611e22fba0a7bcd.png!small?1655175266767)

图:PEstudio展示的时间戳和熵值信息

![1655175293_62a7f87d6cbd839cf1154.png!small?1655175295089](https://image.3001.net/images/20220614/1655175293_62a7f87d6cbd839cf1154.png!small?1655175295089)

图:PE-Bear展示的导出函数和疑似的编译名称

##  **02** 总结

本次攻击中出现的恶意载荷隐藏方法与DLL
Hollowing技术具有相似的目的，都是为了让恶意内容隐藏于系统合法DLL的内存空间之中。不同于直接覆写已完成加载DLL时SizeOfImage的大小限制，劫持LoadLibrary过程通过NtCreateSection可以获得更大的内存空间。但这也更改了劫持DLL的映射属性与内存执行权限，增加了暴露的风险。


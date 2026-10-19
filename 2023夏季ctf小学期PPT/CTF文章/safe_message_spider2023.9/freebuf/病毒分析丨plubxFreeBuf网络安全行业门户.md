作者丨黑蛋

# 一、基本信息

文件名称  
00fbfaf36114d3ff9e2c43885341f1c02fade82b49d1cf451bc756d992c84b06  
文件格式  
RAR  
文件类型(Magic)  
RAR archive data, v5  
文件大小  
157.74KB  
SHA256  
00fbfaf36114d3ff9e2c43885341f1c02fade82b49d1cf451bc756d992c84b06  
SHA1  
1c251974b2e6f110d96af5b23ad036954ba15e4e  
MD5  
c1c9624b21f71e4565b941a37db3815a  
CRC32  
59832D3D  
SSDEEP  
3072:c8BHz/pBz9AycS0lEm2DchuhmE62duNkKa2W75u57cXehC9v:cgz/pnUS5chuHfu/aTI4Xeha  
TLSH  
T1A8F323A63B4FFB50C74C35A6EC2B4D09068B929D14CBB6093F14C7722F5A0667D1BB92  
Tags  
rar,contains_pe

# 二、环境准备

系统版本  
  
---  
  
Win7x86SP1  
  
# 三、动态分析

用火绒剑观察一下：  
图1：

![](https://image.3001.net/images/20230525/1684982495_646ecadf0f43827c3b394.png!small)

图2：

![](https://image.3001.net/images/20230525/1684982496_646ecae0740b11f93f3ab.png!small)

图3：

![](https://image.3001.net/images/20230525/1684982497_646ecae14dd85cc0a55ef.png!small)

图4

![](https://image.3001.net/images/20230525/1684982497_646ecae1d1920a28c5a13.png!small)

可以看到主要是释放了三个资源，一个自身exe，一个dat文件，一个dll。随后就是设置自启动，进行网络链接，进行释放模块的一个加载。

# 四、静态分析

exe没有什么东西，很简单一个加载dll,然后调用run函数：

![](https://image.3001.net/images/20230525/1684982498_646ecae26d829454c19ae.png!small)

分析dll，直接搜索run，找到run跟进去到了sub_10001BF0:

![](https://image.3001.net/images/20230525/1684982499_646ecae371f7f2c87d423.png!small)

接下来是一部分代码注释：

![](https://image.3001.net/images/20230525/1684982500_646ecae44992910ed610c.png!small)

![](https://image.3001.net/images/20230525/1684982500_646ecae4eb919ac1e845e.png!small)

最后return的函数里面是一个virtualproject。  
我们动态抠出解密文档，调试exe，跟进run，在申请空间那里下断点：

![](https://image.3001.net/images/20230525/1684982501_646ecae5ae117bc0ea7a9.png!small)

完事直接在数据那里找到解密数据，是一个pe文件：

![](https://image.3001.net/images/20230525/1684982503_646ecae7141e153da6db2.png!small)

抠出来，放入010Editor生成文件，直接拖入ida，是一个dll文件，找到dllmain：

![](https://image.3001.net/images/20230525/1684982504_646ecae8b9dfcbba729a1.png!small)

进入标记函数，一直跟进去，到了如下地方：

![](https://image.3001.net/images/20230525/1684982505_646ecae94857c60730407.png!small)

这里就是关键地方。  
接下来有三个case，直接看注释：  
case1：

![](https://image.3001.net/images/20230525/1684982505_646ecae9e2188f0cd220f.png!small)

![](https://image.3001.net/images/20230525/1684982506_646ecaead476ceeb8ef7b.png!small)

![](https://image.3001.net/images/20230525/1684982507_646ecaeb93bad95bbc9fe.png!small)

  
case2：

![](https://image.3001.net/images/20230525/1684982508_646ecaec3feb3d66edef7.png!small)

![](https://image.3001.net/images/20230525/1684982509_646ecaed1003e6f002f18.png!small)

  
sub_100153A0()：

![](https://image.3001.net/images/20230525/1684982509_646ecaed9beb8f758565c.png!small)

![](https://image.3001.net/images/20230525/1684982510_646ecaee317d866c6dc08.png!small)

  
  
case3：

![](https://image.3001.net/images/20230525/1684982510_646ecaeedc121ea29c269.png!small)

五、总结

很简单的一次分析，基本所有函数都不需要自行猜测，都是通过GetProcAddress函数获取，所以没有太详细分析，修改了函数名。大概流程就是这样。


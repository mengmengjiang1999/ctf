**最近比较热门的WannaRen勒索病毒，今天（应该是昨天）测试了一堆，死活都不加密我的文件。最终总算找到原因，原来下载的是解密程序。**

> **病毒名称：** WannaRen
>
> **威胁等级：** 高
>
> **威胁范围：** Windows10/2008r2/win7（已确认） XP未知
>
> **威胁类别：** 勒索病毒
>
> **传播途径：** 未知（未分析到外连行为）

##  **具体情况：**

###  **时间线**

文件最早生成时间可以推到4月3日

其本体存在位置：C:\ProgramData

通过添加系统服务WINWORDC开机自启动

![](https://image.3001.net/images/20200408/1586292318_5e8ce65ecda35.png!small)

然后运行WINWORD.EXE并调用wwlib.dll

![](https://image.3001.net/images/20200408/1586292336_5e8ce6702dbd5.png!small)

随后开始加密文件，出现勒索信与解密本体

![](https://image.3001.net/images/20200408/1586292349_5e8ce67d73c76.png!small)

加密文件以.wannaren为后缀名

![](https://image.3001.net/images/20200408/1586292291_5e8ce6437d20f.png!small)

###  **病毒本体**

类型  |  值  
---|---  
文件名  |  WINWORD.EXE  
SHA256  |  6c959cfb001fbb900958441dfd8b262fb33e052342948bab338775d3e83ef7f7  
  
![](https://image.3001.net/images/20200408/1586291210_5e8ce20acc2d3.png!small)

类型  |  值  
---|---  
文件名  |  wwlib.dll  
SHA256  |  22a49fd2468178e5b33cad08985adde50f0530a33260affc58bee6b2401005a9  
  
###
![](https://image.3001.net/images/20200408/1586291278_5e8ce24e5aa53.png!small)**解密本体**

类型  |  值  
---|---  
文件名  |  @WannaRen@.exe  
SHA256  |  a18ad572ca6b8b53d45eef810fc116f9ea1e820528af97f2fbd970f252296fe5  
  
![](https://image.3001.net/images/20200408/1586291604_5e8ce3944a878.png!small)

  

![3.jpg](https://image.3001.net/images/20200408/15863293228010.jpg!small)

> 样本自提处
>
> 样本：<https://pan.baidu.com/s/1R2qISDdaEIiFzS4pDzJcaw>
>
> 提取码：eyhb
>
> 密码：wannaren

希望可以给各位师傅一些研究的思路。

 ***本文作者：CyAnogeN，转载请注明来自FreeBuf.COM**


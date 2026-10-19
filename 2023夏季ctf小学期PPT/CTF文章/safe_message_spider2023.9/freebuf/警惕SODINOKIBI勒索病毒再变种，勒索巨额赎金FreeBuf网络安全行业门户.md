**近日，亚信安全截获SODINOKIBI勒索病毒最新变种文件，与以往不同的是，本次截获的勒索病毒的payload是一个DLL文件（以往样本是EXE可执行文件），通过进程注入方式加载，从而逃避检测。其首先通过.net外壳程序启动一个正常的
vbc.exe进程，然后将勒索模块注入到该进程中，最后加载执行数据加密。另外一个值得注意的是，本次勒索病毒的勒索赎金最高达4万美金。亚信安全将该勒索病毒命名为Ransom.MSIL.SODINOKIBI.A。**

##  **病毒详细分析**

###  **外壳程序分析**

该样本是由.Net编写，并且进行了混淆处理。样本信息如下图所示：

![](https://image.3001.net/images/20191203/1575356237_5de6074d388b8.png!small)![](https://image.3001.net/images/20191203/1575356244_5de60754cb102.png!small)

去除相关混淆后，我们可以清楚地看到具体程序流程，其首先使用base64解密数据到数组中，通过动态调试可知，解密后的数据就是核心勒索payload
DLL（我们dump出为payload.dll），用于后续的进程注入：

![](https://image.3001.net/images/20191203/1575356268_5de6076cac3bc.png!small)![](https://image.3001.net/images/20191203/1575356274_5de607722bc9f.png!small)![](https://image.3001.net/images/20191203/1575356279_5de60777468d6.png!small)

然后启动Windows的正常进程vbc.exe：

![](https://image.3001.net/images/20191203/1575356294_5de6078625c7a.png!small)![](https://image.3001.net/images/20191203/1575356299_5de6078b858b3.png!small)![](https://image.3001.net/images/20191203/1575356304_5de6079019781.png!small)

通过进程内存修改和恢复线程的方式进行注入操作：

![](https://image.3001.net/images/20191203/1575356314_5de6079a4eb0a.png!small)![](https://image.3001.net/images/20191203/1575356320_5de607a05cb52.png!small)

进程注入操作用到的库函数列表：

![](https://image.3001.net/images/20191203/1575356329_5de607a953d2a.png!small)

###  **payload.dll** **文件分析**

此文件是勒索病毒主体文件，与以往SODINOKIB勒索样本基本类似，需要在内存中解密出核心加密主程序，然后跳转至入口执行：

![](https://image.3001.net/images/20191203/1575356348_5de607bcd0931.png!small)

加密后的文件后缀名为.gt0w210：

![](https://image.3001.net/images/20191203/1575356374_5de607d6ae835.png!small)

勒索提示信息文件：

![](https://image.3001.net/images/20191203/1575356385_5de607e11c380.png!small)

修改桌面背景图片：

![](https://image.3001.net/images/20191203/1575356393_5de607e9377c5.png!small)

##  **解决方案**

> 不要点击来源不明的邮件以及附件；
>
> 不要点击来源不明的邮件中包含的链接；
>
> 采用高强度的密码，避免使用弱口令密码，并定期更换密码；
>
> 打全系统及应用程序补丁；
>
> 尽量关闭不必要的文件共享；
>
> 请注意备份重要文档。备份的最佳做法是采取3-2-1规则，即至少做三个副本，用两种不同格式保存，并将副本放在异地存储。

##  **IOC**

> SHA-1:
>
> c25a1eeea09a17c44fd6969b4107980c8fffa29c

 ***本文作者： 亚信安全，转载请注明来自FreeBuf.COM**  


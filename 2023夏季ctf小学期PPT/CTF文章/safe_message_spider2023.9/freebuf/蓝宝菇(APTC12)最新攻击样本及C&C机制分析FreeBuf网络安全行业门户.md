## 背景  

**继360公司披露了蓝宝菇(APT-C-12)攻击组织的相关背景以及更多针对性攻击技术细节后，360威胁情报中心近期又监测到该组织实施的新的攻击活动，本文章是对其相关技术细节的详细分析。**

## 样本分析

### 诱饵文件

在APT-C-12组织近期的攻击活动中，其使用了伪装成"中国轻工业联合会投资现况与合作意向简介"的诱导文件，结合该组织过去的攻击手法，该诱饵文件会随鱼叉邮件进行投递。

如下图所示该诱饵文件伪装成文件夹的图标，执行后会打开包含有诱饵文档和图片的文件夹，而此时实际的恶意载荷已经在后台执行。

![image.png](https://image.3001.net/images/20180723/15323161665250.png)

当该诱饵文件运行时，其会解密释放4个文件，其中两个为上述的诱导文档和图片，另外为两个恶意的tmp文件。

![image.png](https://image.3001.net/images/20180723/153231618033.png!small)

释放的恶意tmp文件路径为：

%temp%\unicode32.tmp

%appdata%\WinRAR\update.tmp

最后通过LoadLibraryW加载释放的unicode32.tmp文件。

![image.png](https://image.3001.net/images/20180723/15323161896505.png!small)

### unicode32.tmp

unicode32.tmp为一个loader，其主要用于加载update.tmp，如下图所示其通过rundll32.exe加载update.tmp，并调用其导出函数jj。

![image.png](https://image.3001.net/images/20180723/1532316199409.png!small)

当加载了update.tmp后，会删除装载exe程序文件和自身。

![image.png](https://image.3001.net/images/20180723/15323162073863.png!small)

![image.png](https://image.3001.net/images/20180723/15323162145656.png!small)

### update.tmp

该文件为一个DLL,并有一个名为jj的导出函数。

![image.png](https://image.3001.net/images/20180723/15323162243979.png!small)

![image.png](https://image.3001.net/images/20180723/15323162311824.png!small)

其首先会对目标主机进行信息收集。

获取系统版本信息：

![image.png](https://image.3001.net/images/20180723/15323162392198.png!small)

调用CreateToolhelp32Snapshot获取系统进程信息：

![image.png](https://image.3001.net/images/20180723/15323162486559.png!small)

调用GetAdaptersInfo获取网卡MAC地址：

![image.png](https://image.3001.net/images/20180723/15323162581447.png!small)

判断当前系统环境是32位或64位：

![image.png](https://image.3001.net/images/20180723/15323162652619.png!small)

通过注册表获取已安装的程序信息，获取的安装程序信息加上前缀”ISL”格式化：

![image.png](https://image.3001.net/images/20180723/15323162735456.png!small)

![image.png](https://image.3001.net/images/20180723/15323162893124.png!small)

通过注册表获取DisplayName和DisplayVersion的信息，并将DisplayName
和DisplayVersion格式化为”%s”:{“ND”:”%s”,”DV”:”%s”}。

![image.png](https://image.3001.net/images/20180723/15323163036749.png!small)

![image.png](https://image.3001.net/images/20180723/1532316307665.png!small)信息收集后会首先向远程控制服务器发送上线信息。

![image.png](https://image.3001.net/images/20180723/15323163187412.png!small)

![image.png](https://image.3001.net/images/20180723/15323163262352.png!small)

获取tmp目录, 创建AdobeNW目录,并从控制服务器上下载AdobeUpdate.tmp作为第二阶段的载荷，其实际为一个DLL文件。

![image.png](https://image.3001.net/images/20180723/15323163348026.png!small)

![image.png](https://image.3001.net/images/20180723/15323163423134.png!small)

![image.png](https://image.3001.net/images/20180723/15323163497013.png!small)

最终调用rundll32启动DLL文件的导出函数MainFun，如果进程创建成功给服务器返回信息。

![image.png](https://image.3001.net/images/20180723/15323163571605.png!small)

### AdobeUpdate.tmp

AdobeUpdate.tmp为DLL文件，其导出方法MainFun由第一阶段木马DLL调用执行。

![image.png](https://image.3001.net/images/20180723/15323163669843.png!small)

其首先遍历%USERPROFILE%\AppData路径下tmp后缀文件，并删除。

![image.png](https://image.3001.net/images/20180723/15323163766026.png!small)

然后从文件自身尾部读取配置信息并解密，其格式如下：

加密的配置信息，包括标识ID，控制服务器地址，加密IV和KEY，以及Mutex信息；

4字节加密配置信息长度；

17字节解密密钥；

![image.png](https://image.3001.net/images/20180723/15323163887262.png!small)

例如上图所示的解密配置文件的KEY为sobcsnkciatwiffi，其解密算法如下：

![image.png](https://image.3001.net/images/20180723/15323163962540.png!small)

![image.png](https://image.3001.net/images/20180723/15323164061692.png!small)

解密之后的配置文件如下所示：

![image.png](https://image.3001.net/images/20180723/15323164153662.png!small)

查询HKEY_CURRENT_USER下的MyApp注册表查看是否有FirstExec, 通过字符串”no”来判断该DLL是否是第一次执行。

![image.png](https://image.3001.net/images/20180723/15323164212876.png!small)

若DLL不为首次执行，则轮询获取控制服务器命令，否则遍历磁盘C：到F：中的文档文件信息，并保存在temp文件夹下的list_tmp.txt中。

![image.png](https://image.3001.net/images/20180723/15323164281402.png!small)

![image.png](https://image.3001.net/images/20180723/15323164399584.png!small)

其中查找的文档类型包括.ppt .pptx .pdf.xls .xlsx .doc .docx .txt .wps
.rtf的文档，将文档文件路径、创建时间以及文件大小信息进行保存。

![image.png](https://image.3001.net/images/20180723/15323164496291.png!small)

下图为示例的写入数据格式(文件路径 创建时间文件大小)：

![image.png](https://image.3001.net/images/20180723/15323164578699.png!small)

并将list_tmp.txt进行aes加密后上传到控制服务器：

![image.png](https://image.3001.net/images/20180723/15323164643621.png!small)

接着设置注册表FirstExec标志：

![image.png](https://image.3001.net/images/20180723/1532316477703.png!small)

AdobeUpdate.dll木马实现了丰富的命令控制指令，其通过访问控制域名获取包含有控制命令的文件，并在本地解密解析后执行。

![image.png](https://image.3001.net/images/20180723/15323164865195.png!small)

其指令以***和对应指令数字组成，以下为控制指令功能列表：

*****1** |  执行cmd命令  
---|---  
*****2** |  更新AppName配置  
*****3** |  文件上传  
*****4** |  文件下载  
*****5** |  更新控制域名  
*****7** |  上传文档文件列表信息  
*****8** |  执行dll文件或exe  
*****9** |  文件删除  
*****10** |  指定文件列表信息上传  
*****11** |  保留  
  
## 控制基础设施

APT-C-12组织近期活动中使用的恶意代码利用了applinzi.com域名下的二级域名作为控制域名，该域名为Sina App Engine的云服务托管。

![image.png](https://image.3001.net/images/20180723/15323165087113.png!small)

我们测试注册了SAE的账户，其默认创建应用可以免费使用十多天，并支持多种开发语言的环境部署。

![image.png](https://image.3001.net/images/20180723/153231652382.png!small)

![image.png](https://image.3001.net/images/20180723/15323165331299.png!small)![image.png](https://image.3001.net/images/20180723/153231654024.png!small)

我们尝试对其控制服务器进行连接，但其后台处理程序已经出错，通过返回的错误信息我们可以发现该组织使用Python部署的后台应用，并使用了flask作为其Web服务实现。

![image.png](https://image.3001.net/images/20180723/15323165489628.png!small)

### SAE控制协议

该组织针对SAE的部署应用实现了一套访问协议，其分为put，info，get，del四个功能。

其中put用于上传文件：

![image.png](https://image.3001.net/images/20180723/15323165939137.png!small)

get用于获取文件：

![image.png](https://image.3001.net/images/20180723/15323166002751.png!small)

info用于获取信息：

![image.png](https://image.3001.net/images/20180723/15323166063453.png!small)

del用于删除文件：

![image.png](https://image.3001.net/images/20180723/15323166145883.png!small)

## 总结

继360威胁情报中心发现该组织利用Digital
Ocean云服务作为命令控制和回传通信渠道以后，我们又发现该组织使用国内的云服务SAE构建其控制回传基础设施，利用这种方式一定程度上减少了攻击利用的成本，也增加了分析回溯的难度。

## IOC

crecg.applinzi.com

costbank.applinzi.com

## 参考链接

<https://sae.sina.com.cn/>

## 原文链接：

<https://ti.360.net/blog/articles/latest-sample-and-c2-mechanism-of-apt-c-12/>  

***本文作者：360天眼实验室，转载请注明来自FreeBuf.COM**  


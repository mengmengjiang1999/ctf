**样本一：dump2.bin**  
MD5: 4B99184764B326B10640A6760111403D

 **样本概述：**  
该样本是c#编写的窃密木马，从VT研判可知是massLogger家族。massLogger是一个相当新的凭证窃取软件。采用了一种复杂的技术，该技术在运行时取代了Microsoft中间语言（MSIL），从而阻碍了静态分析，而且代码中用到的字符串都被加密放到了资源节。

样本执行细节：  
入口点函数，非常简洁，调用yd.bx, 然后在初始化会调用pC(4).Fvq方法返回值为函数类型，然后调用该函数。  
![image.png](https://image.3001.net/images/20210619/1624110408_60cdf5489d24becf3ce1f.png!small)  
![image.png](https://image.3001.net/images/20210619/1624110415_60cdf54fb823fc4aa944e.png!small)  
![image.png](https://image.3001.net/images/20210619/1624110423_60cdf557a3af6dbe49c95.png!small)  
上面调用过程就是massLogger的主要混淆技术，把方法声明和方法体分开，通过一张映射表做关联，而这张表就是通过LR4Cc这个资源节数据解密获取的，key值对应方法声明的token，value对应方法体的token  
![image.png](https://image.3001.net/images/20210619/1624110432_60cdf5608fd89c48c424c.png!small)  
下面是[0x40001E2，0x60001E2]对应关系为aP.cB对应kW0.PWX的w6R方法  
![image.png](https://image.3001.net/images/20210619/1624110442_60cdf56ab8da6fbeadb89.png!small)  
![image.png](https://image.3001.net/images/20210619/1624110457_60cdf5798152d996c15a8.png!small)  
有了这个映射表，我可以通过Token的RID在储存流中找到名字（主要是dnspy没办法搜索token），每个token的最高字节代表了类型，后面的几位代表序号，找到名字之后就能通过搜索找到定义的地方了  
![image.png](https://image.3001.net/images/20210619/1624110464_60cdf58041e72fd035901.png!small)  
![image.png](https://image.3001.net/images/20210619/1624110476_60cdf58c5ffc1b9f239f5.png!small)  
![image.png](https://image.3001.net/images/20210619/1624110480_60cdf590e90a123917676.png!small)  
在“-“模块中，有很多类都是通过这种方式调用方法  
![image.png](https://image.3001.net/images/20210619/1624110485_60cdf595e0f0c8be13b5a.png!small)  
由于混淆基本只能动态跟踪，刚看到资源节中加载了数据，然后看了下有4个资源  
![image.png](https://image.3001.net/images/20210619/1624110493_60cdf59d1f80b649dfa96.png!small)  
在加载资源的地方下断点，通过后面的调试，这4个资源都会被加载，但能力有限只看出两个有用的数据，后面的不知道干啥的。  
![image.png](https://image.3001.net/images/20210619/1624110499_60cdf5a33f4b325d2a2f5.png!small)  
![image.png](https://image.3001.net/images/20210619/1624110504_60cdf5a88b8850f10938f.png!small)  
![image.png](https://image.3001.net/images/20210619/1624110508_60cdf5acc33103d6d8188.png!small)  
![image.png](https://image.3001.net/images/20210619/1624110515_60cdf5b3e918423c5e2b6.png!small)  
从b7XmD中解密出了程序所需要的字符串，每个字符串第1个字节标识长度，00因该是结束符，后面才是字符串内容，然后程序会通过w4.bx获取指定index的字符串  
![image.png](https://image.3001.net/images/20210619/1624110521_60cdf5b90fb1811a8441a.png!small)  
![image.png](https://image.3001.net/images/20210619/1624110524_60cdf5bceb0fd4537cc8d.png!small)  
![image.png](https://image.3001.net/images/20210619/1624110528_60cdf5c0655a2ecccb041.png!small)  
生成的字符串大部分是没有加密的，有些关键的配置开关和数据传输地址进行了加密处理，还是有很多有用信息，我们可以通过字符串在内存中的偏移index在程序中搜索，以得到获取该字符串的位置  
下面是Ohlz资源名字通过22482搜索到的使用处位置  
![image.png](https://image.3001.net/images/20210619/1624110536_60cdf5c8a81e39ad331fa.png!small)  
通过该方法找到了配置数据所在的文件，在XWr这个类中包含了所有配置信息，Ftp的账号和密码，反调试开关等  
![image.png](https://image.3001.net/images/20210619/1624110544_60cdf5d0017ed649a881d.png!small)  
这个是用户配置信息  
![image.png](https://image.3001.net/images/20210619/1624110549_60cdf5d53f4150eed2a6b.png!small)  
然后在这些地方下断点，就能解密很多数据  
![image.png](https://image.3001.net/images/20210619/1624110554_60cdf5dae971eb9cb5c7c.png!small)  
![image.png](https://image.3001.net/images/20210619/1624110562_60cdf5e2df2c20081cb6b.png!small)  
![image.png](https://image.3001.net/images/20210619/1624110567_60cdf5e7a31c49e335a4e.png!small)  
然后根据这些开关和调试信息可以找到使用他们的地方，然后改写数据就能跳过一些限制，比如可以把反调试给关闭，OlnySendOnPassword字段关闭

基本的通过上面的方法就能获取到有用的信息，现在可以在w4.bx处下断点，跟踪用到了哪些字符串，可以看出木马执行了那些功能  
检测有无AVGUI进程，杀软的进程  
![image.png](https://image.3001.net/images/20210619/1624110588_60cdf5fc60a0c47c9530b.png!small)  
窃取浏览器和邮箱凭证  
![image.png](https://image.3001.net/images/20210619/1624110592_60cdf600c9931d09b91b2.png!small)  
![image.png](https://image.3001.net/images/20210619/1624110598_60cdf6060efe8ee36c04e.png!small)  
获取设备的HWID  
![image.png](https://image.3001.net/images/20210619/1624110605_60cdf60dd07cbd08bf7a3.png!small)  
获取本机ip地址  
![image.png](https://image.3001.net/images/20210619/1624110610_60cdf612935c26e9827ef.png!small)  
通过FTP协议发送数据  
![image.png](https://image.3001.net/images/20210619/1624110616_60cdf618f141c1d24eb3c.png!small)  
键盘记录功能  
![image.png](https://image.3001.net/images/20210619/1624110622_60cdf61e055669e600734.png!small)  
网络抓取的数据  
![image.png](https://image.3001.net/images/20210619/1624110626_60cdf622a18ed7acd03d5.png!small)  
![image.png](https://image.3001.net/images/20210619/1624110633_60cdf629082e83ababcf8.png!small)

 **分析总结：**  
在分析中有时会遇到调试到某个地方就会终止了，后面发现程序开启了互斥体，但它不是一启动就检测的，在跑完很长一大段才检测。还有调试时一直没有发送FTP请求，但看anyRun上面有请求，使得一直觉得是有哪个反虚拟机指令没有过掉，但后面仔细看了配置字段发现OlnySendOnPassword才知道我的环境里面没有配置账号密码，导致一直不发送。

 **IOCs：**  
nankasa.com.ar

 **参考资料：**  
关于masslogger反混淆技术，火眼有篇文章讲了破解方法，但试了下并没有成功  
<https://www.4hou.com/posts/o7lj>


***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

## 写在前面的话

**在这篇文章中，我将跟大家讨论一个我在Panda反病毒产品中发现的一个安全漏洞（CVE-2019-12042），这是一个本地提权漏洞，该漏洞将允许攻击者在目标设备上将非特权账户提权至SYSTEM。**

受影响的产品包括Panda Dome（版本< 18.07.03）、Panda InternetSecurity、Panda Antivirus
Pro、PandaGlobal Protection、Panda Gold Protection和旧版本的Panda Antivirus（版本 <=
15.0.4）。

目前，厂商已经在v18.07.03版本中修复了该漏洞。

## 漏洞分析

存在漏洞的系统服务为AgentSvc.exe这个服务可以创建一个全局Section对象和一个对应的全局事件，每当一个进程尝试向共享内存写入数据并需要服务进程去处理这些数据时，它们便会发出信号。由于这个过程中的权限验证机制存在缺陷，因此该漏洞将影响那些允许“Everyone”和非特权用户修改共享内存和事件的对象。

![1.jpg](https://image.3001.net/images/20190707/1562510245_5d2203a5cd53d.jpg!small)

![1.png](https://image.3001.net/images/20190707/1562510264_5d2203b813572.png!small)

## 逆向工程与漏洞利用

这个服务会创建一个线程，该线程会无限期等待内存更改事件，并在收到事件信号时解析内存中的内容。当共享内存中的第二个“值”不为零时，它会使用一个指针来调用如下所示的函数，指针指向的地址为列表头部的值：

![3.PNG](https://image.3001.net/images/20190707/1562510274_5d2203c2c479e.png!small)

### 列表元素的结构如下所示：

    
    
    typedef struct StdList_Event
    
    {
    
           struct StdList_Event* Next;
    
           struct StdList_Event* Previous;
    
           struct c_string
    
          {
    
               union
    
              {
    
                     char* pStr;
    
                     char str[16];
    
               };
    
               unsigned int Length;
    
               unsigned intInStructureStringMaxLen;
    
           }DipsatcherEventString;
    
           //..
    
    };

如下图所示，代码期望在共享内存中偏移量为2的位置有一个unicode字符串，它会使用这个字符串来初始化一个wstring对象，并将其转换为ANSI字符串。除此之外，在第50行代码，使用了"3sa342ZvSfB68aEq"来初始化一个字符串，并将它和攻击者可控制的ANSI字符串以及一个指针（指向一个输出字符串对象）传递给函数"DecodeAndDecryptData"。

![4.PNG](https://image.3001.net/images/20190707/1562510299_5d2203db92c75.png!small)

该函数会对这个base64字符串进行解码，然后使用RC2和密钥“3sa342ZvSfB68aEq”揭密出结果值。所以，我们向共享内存中写入的内容必须是经过RC2加密并且使用Base64编码的值。

![5.PNG](https://image.3001.net/images/20190707/1562510304_5d2203e06906d.png!small)

当函数返回结果时，解码后的数据会被转换为“wstring”对象，而do-while循环会根据分隔符“|”来提取子字符串，并将它们分别插入到列表中，最后将它们以参数进行传递。

![6.PNG](https://image.3001.net/images/20190707/1562510309_5d2203e5adc5d.png!small)

我们回到线程的主函数，如下所示，代码会遍历列表，并将字符串传递给Dispatcher.dll中CDispatcher类的InsertEvent方法：

![7.PNG](https://image.3001.net/images/20190707/1562510314_5d2203ea7e678.png!small)

我们对Dispatcher.dll文件中的CDispatcher::InsertEvent方法进行了分析，发现它会向一个CQueue队列中插入事件字符串：

![8.PNG](https://image.3001.net/images/20190707/1562510320_5d2203f0384ee.png!small)

CDispatcher::Run方法会运行一个单独的线程来处理这个队列中的元素：

![9.PNG](https://image.3001.net/images/20190707/1562510327_5d2203f7286ae.png!small)

CRegisterPlugin::ProcessEvent方法会解析攻击者控制的字符串，查看错误调试消息，我们会发现我们面对的是一个开源的JSON解析器：【[json-parser](https://github.com/udp/json-parser)】。

![10.PNG](https://image.3001.net/images/20190707/1562510333_5d2203fd60065.png!small)

既然我们已经知道了这个服务需要我们传入哪种数据，但我们还需要知道数据的JSON属性。CDispatcher::Initialize方法会调用CRegisterPlugins::LoadAllPlugins方法来从注册表中读取Panda的安装路径，然后访问插件目录，然后加载其中所有的DLL文件。

其中一个DLL名叫Plugin_Commands.dll，它的功能貌似是执行命令行指令。

![11.png](https://image.3001.net/images/20190707/1562510338_5d2204027e647.png!small)

由于这些DLL都可以提供错误调试消息，这样我们就可以轻松定位目标方法了。我们也迅速找到了Plugin_Commands.dll中的Run方法：

![12.PNG](https://image.3001.net/images/20190707/1562510344_5d22040854dbb.png!small)

在这个函数中，我们从输入数据中找到了目标JSON属性：

![13.PNG](https://image.3001.net/images/20190707/1562510349_5d22040d37213.png!small)

我们还可以从内核调试器中拦截部分JSON消息：

![14.png](https://image.3001.net/images/20190707/1562510355_5d22041315e3b.png!small)

至此，我想看看是否能够执行硬盘中的某些东西。通过对Run方法的反编译结果进行分析，我们发现了一个函数可以解析相关的属性值，并判断其是否指向的是URL或是磁盘中的文件。这里，我们就可以使用file://URI来执行硬盘中的文件了。

![15.PNG](https://image.3001.net/images/20190707/1562510360_5d220418a800e.png!small)

在查找强制属性时，我们发现至少要提供这两个值：ExeName和SourcePath：

![16.png](https://image.3001.net/images/20190707/1562510366_5d22041eed507.png!small)

![17.png](https://image.3001.net/images/20190707/1562510372_5d22042450f6a.png!small)

但是，当我们在设置了这两个值之后将事件"CmdLineExecute"加入队列，我们的进程并没有创建成功。调试之后，我发现“ExeMD5”也是一个强制属性，它应该包含待运行的可执行程序的有效MD5哈希。

CheckMD5Match函数会动态计算文件哈希，并与我们提供的JSON属性进行对比。

![18.png](https://image.3001.net/images/20190707/1562510378_5d22042a70088.png!small)

### 成功执行后的进程流：

![19.png](https://image.3001.net/images/20190707/1562510384_5d2204303248e.png!small)

测试如下JSON数据（RC2+Base64编码），我们可以看到cmd.exe成功以SYSTEM权限运行了：

    
    
    {
    
        "CmdLineExecute":        
    
        {
    
            "ExeName":"cmd.exe",                           
    
            "SourcePath":"file://C:\\Windows\\System32",                
    
            "ExeMD5":"fef8118edf7918d3c795d6ef03800519"
    
        }
    
    }

![20.png](https://image.3001.net/images/20190707/1562510397_5d22043d0fea7.png!small)

当我们尝试提供自己的可执行程序时，Panda会将其检测为恶意软件并删除之，即使该文件不是恶意软件。此时，我们可以让cmd.exe来启动我们的进程，最终的JSON数据如下所示：

    
    
    {
    
        "CmdLineExecute":                                   
    
        {
    
            "ExeName":"cmd.exe",                          
    
            "Parameters": "/c startC:\\Users\\VM\\Desktop\\run_me_as_system.exe",
    
            "SourcePath":"file://C:\\Windows\\System32",               
    
            "ExeMD5":"fef8118edf7918d3c795d6ef03800519" //MD5 hash of CMD.EXE
    
        }
    
    }

最后的漏洞利用代码会在目标磁盘中存放一个文件，并计算cmd.exe的MD5哈希，构建JSON数据，对其加密并编码，最终将其写入共享内存。

还需要注意的是，这个PoC漏洞利用代码可以在不需要任何重新编译操作的情况下在所有的Windows版本中正常工作。

![21.png](https://image.3001.net/images/20190707/1562510407_5d2204476e3d7.png!small)

## PoC代码

漏洞利用代码：【[GitHub传送门](https://github.com/SouhailHammou/Panda-Antivirus-LPE)】

 *** 参考来源：[rce4fun](https://rce4fun.blogspot.com/2019/05/panda-antivirus-local-privilege.html)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**


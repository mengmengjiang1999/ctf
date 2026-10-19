原文地址：[《"BLIND" Reversing - A Look At The Blind iOS
App》](https://exceptionlevelone.blogspot.tw/2017/10/blind-reversing.html
"《"BLIND" Reversing - A Look At The Blind iOS App》")  
译者：hello1900@知道创宇404实验室

#### 前言

[“Blind是一款用于工作场合的匿名社区应用。” ](https://us.teamblind.com/about
"“Blind是一款用于工作场合的匿名社区应用。”
")换句话说，作为一名员工，如果有“畅所欲言”或以匿名方式抨击雇主或同事的打算（当然这种情况极为常见），那么Blind可能是你的不二之选。这款有趣的小应用能够帮助我们透过事物表象了解真实情况。

#### 范围与环境

我重点关注应用本身，因此使用Linkedin账户而非工作邮件注册。这样一来就产生了一些访问限制。此外，我也并未花时间了解所有功能，仅考虑一些自己看来具有核心功能的组件，所以难免存在局限性。

环境搭建如下：

-运行iOS 9.3.3的越狱iPhone 5S  
-jtool  
-IDA Pro  
-Hopper  
-BurpSuite Pro  
-Frida 

#### 越狱检测

首先，这款应用不具备任何越狱检测例行程序。对于你的不屑一顾我暂时保持缄默。我开始也不认为缺少此类检查本身是安全问题，但从更宽泛、深入的防御观点来看却不尽然。

#### 证书固定

第二个观察结果是该应用没有通过SSL证书验证（证书固定）检查远程端点的真实性，因此可以通过中间人（MiTM）攻击监听并篡改数据。事实上，情况并不像听起来那么糟。原因如下：1.
攻击者必须欺骗用户在设备上安装恶意证书；2. 该应用对发送至后端的数据进行加密。

另一方面，攻击者大多数情况下需要先欺骗用户安装恶意证书。对此，我表示赞同，因为确实存在旨在简化流程的工具。Sensepost上的博客文章（<https://sensepost.com/blog/2016/too-easy-adding-root-cas-to-ios-devices/>）就是一个很好的例子。

最后，该应用程序提供两种登录选项：工作电子邮件与LinkedIn验证（见下图）。如上所述，我倾向使用后者。副作用是攻击者可在证书未固定的情况下捕获LinkedIn登陆凭据，当然是在安装恶意证书的前提下。

![](https://images.seebug.org/content/images/2017/11/dd09edaa-926a-4a9c-b434-c484f0cb14ec.png-w331s)
登录选项

#### 获取二进制文件

解决这些问题后就可以获得二进制文件、开始逆向了。我使用 [dumpdecrypted
dylib](https://github.com/stefanesser/dumpdecrypted "dumpdecrypted dylib")，仅需
ssh登录设备并运行以下代码：

    
    
    root@Jekyl (/var/root)# su mobile  
     mobile@Jekyl (/var/mobile/Documents)# DYLD_INSERT_LIBRARIES=/var/root/dumpdecrypted.dylib /private/var/containers/Bundle/Application/3C411AB3-6018-4604-97D2-DC2A546EAB85/teamblind.app/teamblind  
     mach-o decryption dumper  
     DISCLAIMER: This tool is only meant for security research purposes, not for application crackers.  
     [+] detected 64bit ARM binary in memory.  
     [+] offset to cryptid found: @0x1000d4f28(from 0x1000d4000) = f28  
     [+] Found encrypted data at address 00004000 of length 7995392 bytes - type 1.  
     [+] Opening /private/var/containers/Bundle/Application/3C411AB3-6018-4604-97D2-DC2A546EAB85/teamblind.app/teamblind for reading.  
     [+] Reading header  
     [+] Detecting header type  
     [+] Executable is a plain MACH-O image  
     [+] Opening teamblind.decrypted for writing.  
     [+] Copying the not encrypted start of the file  
     [+] Dumping the decrypted data into the file  
     [+] Copying the not encrypted remainder of the file  
     [+] Setting the LC_ENCRYPTION_INFO->cryptid to 0 at offset f28  
     [+] Closing original file  
     [+] Closing dump file  

应注意使用root权限在iOS 9.3.3版本运行`DYLD_INSERT_LIBRARIES=dumpdecrypted.dylib`可杀掉被注入进程：

    
    
     root@Jekyl (/var/root)# DYLD_INSERT_LIBRARIES=dumpdecrypted.dylib /private/var/containers/Bundle/Application/3C411AB3-6018-4604-97D2-DC2A546EAB85/teamblind.app/teamblind  
     zsh: killed   DYLD_INSERT_LIBRARIES=dumpdecrypted.dylib   
     root@Jekyl (/var/root)# 

解决办法是先切换至手机再cd至上图/var/mobile/Document。还应注意我们之所以能够注入自己的 dylib 是因为Blind应用没有
__RESTRICT Segment。

    
    
     LC_SEGMENT_64     Mem: 0x100008000-0x100008000     __RESTRICT  
          Mem: 0x100008000-0x100008000          __RESTRICT.__restrict 

这是个null segment (size 0)，用于通知 DLYD 不要相信任何 DLYD* 环境变量。

#### 识别端点

我在查看二进制文件时通常会转储字符串并搜索URL端点，然后用该列表确认Burpsuite流量。

    
    
     macho-reverser:BLIND macho-reverser$ jtool -d __TEXT.__cstring teamblind.decrypted | grep "http"  
     Address : 0x1006dcfd0 = Offset 0x6dcfd0  
     0x1006df366: https://api.linkedin.com/v1/people/~:(id,email-address,first-name,last-name,headline,num-connections,industry,summary,specialties,positions:(id,title,summary,start-date,end-date,is-current,company:(id,name,universal-name,type,size,industry,ticker,email-domains)),educations:(id,school-name,field-of-study,start-date,end-date,degree,activities,notes),associations,interests,num-recommenders,date-of-birth,publications:(id,title,publisher:(name),authors:(id,name),date,url,summary),patents:(id,title,summary,number,status:(id,name),office:(name),inventors:(id,name),date,url),languages:(id,language:(name),proficiency:(level,name)),skills:(id,skill:(name)),certifications:(id,name,authority:(name),number,start-date,end-date),courses:(id,name,number),recommendations-received:(id,recommendation-type,recommendation-text,recommender),honors-awards,three-current-positions,three-past-positions,volunteer)?format=json  
     0x1006df80e: http://us.teamblind.com  
     0x1006e19ad: https://api.linkedin.com/v1/people/~:(id,email-address)?format=json  
     0x1006e75df: https://m.facebook.com/settings/email  
     0x1006e760c: https://www.linkedin.com/m/settings/email  
     0x1006ea5ec: https://docs.google.com/forms/d/e/1FAIpQLSc_J26TtkDL7HXcLeFXC2jy6lb1PmJSPnh51_ng7fr1638p_Q/viewform  
     0x1006ee9c3: https://www.linkedin.com/uas/oauth2/authorization?response_type=code&client_id=%@&scope=%@&state=%@&redirect_uri=%@  
     0x1006f4865: https://krapi.teamblind.com  
     0x1006f4881: https://usapi.teamblind.com  
     0x1006f489d: http://kr.stage.teamblind.com:8080  
     0x1006f48c0: http://us.stage.teamblind.com:8080  
     0x1006f48e3: http://dev.teamblind.com:8080  
     0x1006f4901: http://us.dev.teamblind.com:8080  
     0x1006f4922: https://kr.teamblind.com  
     0x1006f493b: https://us.teamblind.com  
     0x1006f4954: https://krnotifier.teamblind.com  
     0x1006f4975: https://usnotifier.teamblind.com  
     ----
也可以用它获取其他潜在目标列表。于是，启动Burpsuite并检查流量。如前文所述，Blind应用能否实现证书固定并没有那么重要，因为该应用对发送至后端的数据进行加密。下图为常用请求示例。

![](https://images.seebug.org/content/images/2017/11/b08f21ec-1391-4e1a-b6c0-4dc8e54393fe.png-w331s)
请求样本

唯一能够确定的是早前识别的链接。所以说我们实际上处于“盲”状态。但如果数据经过加密，那么加密秘钥的存储或生成的方式与位置是什么？能否看到应用发送至服务器的明文数据？

#### 提取类

为了回答这些问题，首先转储类，看看是否存在有价值的内容。列出代码段后发现关于Objective-C的引用：

    
    
    macho-reverser:BLIND macho-reverser$ jtool -l teamblind.decrypted   
     LC 00: LC_SEGMENT_64     Mem: 0x000000000-0x100000000     __PAGEZERO  
     LC 01: LC_SEGMENT_64     Mem: 0x100000000-0x1007a4000     __TEXT  
          Mem: 0x100007a90-0x100663f18          __TEXT.__text     (Normal)  
          Mem: 0x100663f18-0x10066723c          __TEXT.__stubs     (Symbol Stubs)  
          Mem: 0x10066723c-0x10066a560          __TEXT.__stub_helper     (Normal)  
          Mem: 0x10066a560-0x100671ec0          __TEXT.__const       
          Mem: 0x100671ec0-0x1006dcfc9          __TEXT.__objc_methname     (C-String Literals)  
          Mem: 0x1006dcfd0-0x10074ca58          __TEXT.__cstring     (C-String Literals)  
          Mem: 0x10074ca58-0x100754bb2          __TEXT.__objc_classname     (C-String Literals)  
          Mem: 0x100754bb2-0x100767daa          __TEXT.__objc_methtype     (C-String Literals)  
          Mem: 0x100767daa-0x100768e18          __TEXT.__ustring       
          Mem: 0x100768e18-0x100788c4c          __TEXT.__gcc_except_tab       
          Mem: 0x100788c50-0x10078b967          __TEXT.__swift3_typeref       
          Mem: 0x10078b968-0x10078c6a0          __TEXT.__swift3_capture       
          Mem: 0x10078c6a0-0x10078d720          __TEXT.__swift3_fieldmd       
          Mem: 0x10078d720-0x10078e67d          __TEXT.__swift3_reflstr       
          Mem: 0x10078e680-0x10078edc8          __TEXT.__swift3_assocty       
          Mem: 0x10078edc8-0x10078f3c8          __TEXT.__swift2_proto       
          Mem: 0x10078f3c8-0x10078f478          __TEXT.__swift2_types       
          Mem: 0x10078f478-0x10078f4dc          __TEXT.__swift3_builtin       
          Mem: 0x10078f4dc-0x1007a3d20          __TEXT.__unwind_info       
          Mem: 0x1007a3d20-0x1007a4000          __TEXT.__eh_frame       
     LC 02: LC_SEGMENT_64     Mem: 0x1007a4000-0x100980000     __DATA  
          Mem: 0x1007a4000-0x1007a4ba8          __DATA.__got     (Non-Lazy Symbol Ptrs)  
          Mem: 0x1007a4ba8-0x1007a6dc0          __DATA.__la_symbol_ptr     (Lazy Symbol Ptrs)  
          Mem: 0x1007a6dc0-0x1007a6e00          __DATA.__mod_init_func     (Module Init Function Ptrs)  
          Mem: 0x1007a6e00-0x1007cfd20          __DATA.__const       
          Mem: 0x1007cfd20-0x10080f300          __DATA.__cfstring       
          Mem: 0x10080f300-0x100811498          __DATA.__objc_classlist     (Normal)  
          Mem: 0x100811498-0x1008114d0          __DATA.__objc_nlclslist     (Normal)  
          Mem: 0x1008114d0-0x100811890          __DATA.__objc_catlist     (Normal)  
          Mem: 0x100811890-0x1008118e8          __DATA.__objc_nlcatlist     (Normal)  
          Mem: 0x1008118e8-0x1008123b0          __DATA.__objc_protolist       
          Mem: 0x1008123b0-0x1008123b8          __DATA.__objc_imageinfo       
          Mem: 0x1008123b8-0x10092bf38          __DATA.__objc_const       
          Mem: 0x10092bf38-0x100944b20          __DATA.__objc_selrefs     (Literal Pointers)  
          Mem: 0x100944b20-0x100944c88          __DATA.__objc_protorefs       
          Mem: 0x100944c88-0x100946ee0          __DATA.__objc_classrefs     (Normal)  
          Mem: 0x100946ee0-0x100948918          __DATA.__objc_superrefs     (Normal)  
          Mem: 0x100948918-0x10094ee80          __DATA.__objc_ivar       
          Mem: 0x10094ee80-0x100965188          __DATA.__objc_data  
     ------
我们可以通过`jtool - JCOLOR=1 jtool -v -d objc teamblind.decrypted`的 objc 选项转储类与方法。

![](https://images.seebug.org/content/images/2017/11/3ce79213-9792-475c-83de-324454bf4844.png-w331s)
用jtool提取类信息

还需要说明一点，虽然本文使用IDA，读者完全可以根据自身反汇编需要使用jtool，例如研究某个特殊类时输入`jtool -d
UserControl:getSecretUserDefaultString: teamblind.decrypted`。

![](https://images.seebug.org/content/images/2017/11/6a67aa14-3754-4170-846c-fc06753663a0.png-w331s)
拆分类信息

#### 破解加密值

现在，我们已经成功拦截流量，但如何破解加密流量成为难题。不妨先找出加密实现方法。如上文所述，Blind允许通过工作邮件或LinkedIn账户登录。登录后将看到创建账户选项：

![](https://images.seebug.org/content/images/2017/11/9f1f89d3-73fe-4639-b41f-2207cdbd59a8.png-w331s)
登录界面

应用设置可在`com.teamblind.blind.plist`中查找，具体位置在
`/private/var/mobile/Containers/Data/Application/<app_id>/Library/Preferences/com.tea
mblind.blind.plist`。此时，检查文件就会发现其中包含明文电子邮件以及登录时填写的公司信息。可以使用plutil实用程序读取文件。

![](https://images.seebug.org/content/images/2017/11/fee490ca-481d-4410-86af-4b72b1b7237b.png-w331s)
plist代码段

一旦输入密码、用户名，点击“开始”后就是另一番景象了。

![](https://images.seebug.org/content/images/2017/11/0bf308a9-afd3-4855-a6b2-9b84e09459cf.png-w331s)

现在，你的电子邮件不再以明文存储而是经过加密，新增了密码与其他几个值。牢记千万不要在plist文件中存储密码等敏感信息。敏锐的读者可能会注意到我并没有隐藏`password_enc`值。秘钥名称以`_enc`结尾表示该值可能被加密，但事实是否果真如此？另外，应注意该值是加密过程必不可少的一部分，具体原因将在后文介绍。接下来，我们将继续探索关于这个值的更多细节。

“加密”密码仅是一个md5哈希值，可以在AuthCompleteViewController的requestPassword中看到。

![](https://images.seebug.org/content/images/2017/11/c0ea41e3-645e-4583-84e0-70ec0974fee6.png-w331s)
创建密码哈希值

在 0x000000010004EB50 位置得到用户提供值后计算 0x000000010004EB8C 位置的md5
哈希值。为了证实这一点，我们在与上文plist取值相同处使用Python。现在，我的超级密码一目了然。

    
    
     >>> import hashlib  
     >>> m = hashlib.md5()  
     >>> m.update("password#1")  
     >>> print m.hexdigest()  
     5486b4af453c7830dcea12f347137b07  
     >>> 

#### 识别ViewControllers

为了确定需要检查的类，我首先来到账户创建页面，用cycript 确定ViewController外观：

    
    
     root@Jekyl (/var/root)# ps aux | grep blind  
     mobile  4136  0.1 5.8  815696 59532  ?? Ss  4:10PM  0:06.85 /var/containers/Bundle/Application/3C411AB3-6018-4604-97D2-DC2A546EAB85/teamblind.app/teamblind  
     root   4139  0.0 0.0  657104  212 s000 R+  4:11PM  0:00.01 grep blind  
     root@Jekyl (/var/root)# cycript -p 4136  
     cy# [[[UIWindow keyWindow] rootViewController] _printHierarchy].toString()  
     "<UINavigationController 0x15615d000>, state: appeared, view: <UILayoutContainerView 0x157415a30>\n  | <RootViewController 0x1570db260>, state: disappeared, view: <UIView 0x157337ab0> not in the window\n  | <AuthCompleteViewController 0x155f587c0>, state: appeared, view: <UIView 0x155da07a0>"  
     cy#  

别忘了你的电子邮件经过加密处理。加密惯例也在requestPassword 方法中呈现。你的电子邮件首先通过 plist(NSUserDefaults)
找回，然后传输至NSString ([NSString encryptHES256:]) encryptHES256 方法。

![](https://images.seebug.org/content/images/2017/11/80f31001-fee0-4bcd-8afa-a0d6dacc34f3.png-w331s)
读取用户电子邮件

encryptHES256方法在过渡至AES256EncryptWithKey方法（涵盖加密过程）前生成带有密码简单异或的加密秘钥和一些“随机”值。从技术角度看，此方法调用另一个功能，但整体情况已趋向明朗，不难发现“随机性”。

![](https://images.seebug.org/content/images/2017/11/090ccafe-9337-4bf0-8290-7bb3f98414e9.png-w331s)

#### Frida

稍微借助[Frida](https://www.frida.re/ "Frida")就可以看到实际效果。对于还不了解
Frida的读者，我强烈建议您将这款工具添加至兵器库并在使用go脚本前检查[Frida
CodeShare](https://codeshare.frida.re/ "Frida
CodeShare")。当然，代码运行前的例行检查无论何时都是必要步骤。

通过Frida与CodeShare ObjC method observer脚本，我们能够观察到AES256EncryptWithKey方法起到的作用：

    
    
     macho-reverser:BLIND macho-reverser$ frida -U --codeshare mrmacete/objc-method-observer -f com.teamblind.blind  
        ____  
       / _ |  Frida 10.6.15 - A world-class dynamic instrumentation framework  
       | (_| |  
       > _ |  Commands:  
       /_/ |_|    help   -> Displays the help system  
       . . . .    object?  -> Display information about 'object'  
       . . . .    exit/quit -> Exit  
       . . . .  
       . . . .  More info at http://www.frida.re/docs/home/  
     Spawned `com.teamblind.blind`. Use %resume to let the main thread start executing!  
     [iPhone::com.teamblind.blind]-> %resume  
     [iPhone::com.teamblind.blind]-> observeSomething('*[* *AES256EncryptWithKey:*]');  
     (0x125fcdca0) -[NSData AES256EncryptWithKey:]  
     AES256EncryptWithKey: password#1^0123456789abcdefghijk  
     0x1001b25cc teamblind!0x11e5cc  
     0x1000e2c7c teamblind!0x4ec7c  
     ---- 

现在，密码与电子邮件加密方式已知。基本说来，重复以上步骤就能找到其他加密值。接下来，了解实际流量。

如上文所述，设备出口流量监控结果显示，所有请求均包括一个载荷。在IDA中搜索字符串后发现多数请求参数在[NetworkControl
encRequestWithParams:showAlert:completionBlock:failBlock:] 方法中设置。

![](https://images.seebug.org/content/images/2017/11/80126721-93b3-4943-a8f4-1ef23a5465bf.png-w331s)

#### encRequestWithParams

此方法首先尝试找回之前生成的加密秘钥与初始化向量（IV），如果失败则调用 EncriptControl 类 `makeKeyAndIvForEnc
(-[EncriptControl makeKeyAndIvForEnc])` 方法。没错，是带有IV的Encript。 或许可称之为隐匿式安全……:)

![](https://images.seebug.org/content/images/2017/11/e1c9cd19-e1df-4da7-8ed9-d7acd733294d.png-w331s)

#### makeKeyAndIvForEnc

这种做法的有趣之处在于加密秘钥通过用户密码与硬编码值组合生成。还记得之前提到的加密密码（password_enc）吗？该方法首先尝试将其找回：

![](https://images.seebug.org/content/images/2017/11/67d8721b-784e-49bb-bbce-4bb372c32fc9.png-w331s)

根据硬编码值生成另一个md5哈希值：

![](https://images.seebug.org/content/images/2017/11/a30f9bd9-f8e2-41fc-80a5-76bbabd4ebb6.png-w331s)
生成静态值

如果涉及用户密码找回问题，则再生成一个哈希值：

![](https://images.seebug.org/content/images/2017/11/79e92036-c180-459d-ab5d-36b026757882.png-w331s)

最后，秘钥设置完毕，以 hash1+hash2 或 hash1+password_enc 组合结尾。

![](https://images.seebug.org/content/images/2017/11/024f4bd1-5297-4484-a0ab-9b7e20e3693f.png-w331s)
生成实际秘钥

在此例中，加密秘钥应为 md5("QkdEhdk") + md5(“password#1")，并由此得到“c07bcdc2 3522ed81
fb76db0c 0c4387cf 5486b4af 453c7830 dcea12f3 47137b07”。

该方法的其余部分用于设置初始向量（IV）：

![](https://images.seebug.org/content/images/2017/11/79091246-a4d0-469e-8c05-8db3b17875ab.png-w331s)
生成 IV

#### 冲破黑暗

NetworkControl 类 encRequestWithParams 方法通过调用EncriptControl
类makeKeyAndIvForEnc设置加密。设置完毕后使用encRequestWithParams 方法调用 EncriptControl
类makePayloadDataWithJsonString。该方法使用之前提及的加密秘钥与IV调用CocoaSecurity
aesEncryp，结果返回base64 编码密文，也就是Burp呈现的内容。

![](https://images.seebug.org/content/images/2017/11/ba2df566-9dba-440b-8e0a-cfcb11ae84c8.png-w331s)
加密载荷

暂时返回 jtool -d objc dump，注意 EncriptControl 类实例变量：

![](https://images.seebug.org/content/images/2017/11/48887274-6aa8-47d6-84db-f51cb74f6643.png-w331s)
Encript实例变量

收集到所有线索后编写Frida脚本，获得实例变量，即加密秘钥、明文数据与相应密文：

    
    
    if(ObjC.available){  
       var makeKandIv = ObjC.classes.EncriptControl["- makePayloadDataWithJsonString:"];  
         Interceptor.attach(makeKandIv.implementation, {  
          onEnter: function(args) {  
            /* Get Class/Params */  
            var obj = ObjC.Object(args[0]);  
            var params = ObjC.Object(args[2]);  
            /* Get ivars */  
            var ivar = obj.$ivars;  
            // Print ivars values   
            console.log("-----------------------------------------------------------\n");  
            console.log("_encKey: " + ivar["_encKey"] + "\n");  
            console.log("_encIv: " + ivar["_encIv"] + "\n");  
            console.log("_encIvStr: " + ivar["_encIvStr"] + "\n");   
            console.log("_encKeyForDM: " + ivar["_encKeyForDM"] + "\n");   
            console.log("_encKeyForDM: " + ivar["_encIvForDM"] + "\n");   
            console.log("-----------------------------------------------------------\n");   
            console.log("PARAMS: " + params);  
           },  
          onLeave: function onLeave(retval) {  
             console.log("Encrypted Payload: " + new ObjC.Object(retval).toString() + "\n");  
          }  
       });  
     }  

![](https://images.seebug.org/content/images/2017/11/a5faa1c3-62b4-4739-9fb6-0d13d1c8d90e.png-w331s)
一次加密的burp流量

现在变成：
![](https://images.seebug.org/content/images/2017/11/d9ac0508-a0ab-4e6c-af8c-ac90039a400f.png-w331s)
具有加密秘钥的明文数据

此外，连接EncriptControl 类convertDictionaryEncWithResultStr:
方法后打印出服务器响应明文。这时需要考虑将[Brida](https://github.com/federicodotta/Brida "Brida")
Burpsuite 插件用于其他选项。

#### 结语

Ok，今天就到此为止。如前文所述，我没有注册Blind
账户，因此无法使用会员功能。但这些都无妨，我只对Burp上的一些数据感兴趣。考虑到应用程序性质与要求，我打算探索更多内容。因此，并无恶意流量发送至Blind服务器。

Happy hacking!!!

本文可用于围绕Blind应用开展进一步调研。对于提供信息的采用，本博客不承担任何责任。

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/440/>


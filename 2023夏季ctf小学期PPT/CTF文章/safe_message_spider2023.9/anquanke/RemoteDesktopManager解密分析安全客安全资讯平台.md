# Remote Desktop Manager 解密分析

阅读量 **161130**

|评论 **2**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2022-01-11 10:00:41

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p1.ssl.qhimg.com/t01abedabf76ad133ff.png)

## 前言

Remote Desktop Manager
是一款远程桌面管理器工具，主要应用场景在，IT部门负责管理和控制对不断增长的现场和异地服务器、计算机和设备库存的访问。然而，依赖多个远程连接工具和密码管理器效率低下、令人沮丧且不安全。IT
专业人员、系统管理员和帮助台技术人员没有得到简化的清晰度处理，而是在持续的混乱中挣扎。解决方案是将远程连接技术、远程机器数据、密码管理和访问控制集中在一个安全、可扩展且易于使用的平台上。

在内网横向中，我们经常会遇到运维的机器，当我们可以解密Remote Desktop Manager
工具的密码时，可以获取更多的凭据，有助于我们在内网渗透中横向移动。

类似于我们常常去解密Xshell 是一个道理的，由于我项目中遇到，在 google 等搜索引擎并没有找到解密办法，尝试自己解密。

## 0x1 基本信息获取

根据启动时，所加载的DLL 确定大概分析范围

RemoteDesktopManager.Core.dll

RemoteDesktopManager.Business.dll

Devolutions.dll

![](https://p3.ssl.qhimg.com/t01f6bb0797a250ea64.png)

对查看密码功能进行点击测试，观察Operation 是否读取本地文件、注册表等信息

发现在
**%LOCALAPPDATA%\AppData\Local\Devolutions\RemoteDesktopManagerFree\Connections.log**
进行连接记录

![](https://p4.ssl.qhimg.com/t01b75ad29faa9c7f97.png)

![](https://p3.ssl.qhimg.com/t0126f2802cf1569cf1.png)

**%LOCALAPPDATA%\AppData\Local\Devolutions\RemoteDesktopManagerFree\Connections.db**  
在DB中发现了加密的密码

  * RDP

    
    
    <RDP>
        <SafePassword>UJbKx4lffJM=</SafePassword>
        <UserName>administrator</UserName>
      </RDP>
    

  * SSH

    
    
    <Terminal>
        <Host>cc</Host>
        <PrivateKeyPromptForPassPhrase>false</PrivateKeyPromptForPassPhrase>
        <SafePassword>WqYhDbiAsH8=</SafePassword>
        <Username>aa</Username>
      </Terminal>
    

![](https://p2.ssl.qhimg.com/t013fcc28cb67894d92.png)

现在我们已经获取了加密后的密码，和基础的连接信息，接下来我们只要分析出加密方式，即可解密、获取明文密码。

## 0x2 加密方式获取

根据上0x1的基础分析，我们现在对 RemoteDesktopManager.Core.dll 进行反编译，查看代码，尝试找到加密方式。

在FreRemoteDesktopConnectionSetings 发现了连接配置信息，

![](https://p3.ssl.qhimg.com/t01b8e88540ea65ce5b.png)

根据连接信息进行回溯

找到 **DecryptBasic** 方法

![](https://p5.ssl.qhimg.com/t010733b10d6b9b91f6.png)

继续跟 **UnsafeEncryptionManager.Deobfuscate**

![](https://p0.ssl.qhimg.com/t0161acc086bbb3f9aa.png)

**Deobfuscate** 中发现 当满足 **!UnsafeEncryptionManager.IsEncrypted(cipherText)**
条件 进入 **ObfuscationUtils.Deobfuscate**

![](https://p5.ssl.qhimg.com/t017db71478f7a52f4f.png)

Deobfuscate 方法 接收参数为 string **encryptedString** , string **key** 那么这里
**encryptedString** 接收的内容 可能就是我们在sqlite中看到的Safepassword ，key为 软件所生成的，

![](https://p0.ssl.qhimg.com/t01237401d16d92142f.png)

回溯上面的调用，下断点。

![](https://p4.ssl.qhimg.com/t01abbd312af6191ce2.png)

通过逐语句，来到了我们刚刚自己找的这块，确认了我们猜测的流程没有问题。

![](https://p5.ssl.qhimg.com/t018bf3d61bc183e952.png)

在到了 **Deobfuscate** 方法中时，我们所接收的key 已经有了

![](https://p0.ssl.qhimg.com/t01cfaf2e9b6c13139a.png)

在继续跟上图103 行,GetDecryptorTransform 方法时，我们看到了加密方法。

    
    
            public static ICryptoTransform GetDecryptorTransform(string key)
            {
                Dictionary<string, ICryptoTransform> obj = ObfuscationUtils.decryptorTransforms;
                ICryptoTransform cryptoTransform;
                lock (obj)
                {
                    if (!ObfuscationUtils.decryptorTransforms.TryGetValue(key, out cryptoTransform))
                    {
                        TripleDESCryptoServiceProvider tripleDESCryptoServiceProvider = new TripleDESCryptoServiceProvider();
                        byte[] key2 = ObfuscationUtils.MD5CryptoServiceProvider.ComputeHash(Encoding.ASCII.GetBytes(key));
                        tripleDESCryptoServiceProvider.Key = key2;
                        tripleDESCryptoServiceProvider.Mode = CipherMode.ECB;
                        cryptoTransform = tripleDESCryptoServiceProvider.CreateDecryptor();
                        ObfuscationUtils.decryptorTransforms.Add(key, cryptoTransform);
                    }
                }
                return cryptoTransform;
    

![](https://p1.ssl.qhimg.com/t01dc362d23a9079021.png)

当reurn result 的时，我们就已经看到了密码

![](https://p5.ssl.qhimg.com/t01545b96bc1fa4c682.png)

**Deobfuscate** 对应加密的 **key** 和 **encryptedString** , text 为我们的明文密码，由刚刚的bytes
result 转字符串

![](https://p4.ssl.qhimg.com/t0102478da8a335dd78.png)

那么现在具体的解密流程，我们就已经大概了解了，接下来我们怎么解密目标机器的呢？

  * 1.离线解密

回溯key的生成，找到key生成的方法和存储位置

  * 2.反编译对应的DLL文件

在DLL文件添加记录 encryptedString 、key、 text(password)

## 0x3 获取明文凭据

这里我们以反编译对应的DLL，演示获取明文凭据，在此处进行反编译DLL，最后保存生成替换即可。

![](https://p1.ssl.qhimg.com/t013c692af87bbd9fbd.png)

    
    
        string[] array2 = new string[]
        {
            "encryptedString:" + encryptedString,
            "key:" + key,
            "result:" + text + "\n"
        };
        using (StreamWriter streamWriter = new StreamWriter("C:\\\\Windows\\\\temp\\\\log.txt", true))
        {
            foreach (string text2 in array2)
            {
                if (!text2.Contains("second"))
                {
                    streamWriter.WriteLine(text2);
                }
            }
        }
    

![](https://p1.ssl.qhimg.com/t01f5a180f871f0a540.png)

最后实现效果，成功记录了SSH、RDP 的 password ，想详细的记录连接信息，可继续往上层跳。

拿到encryptedString 直接就可以在数据库中比对了。

![](https://p5.ssl.qhimg.com/t015010db183ada919d.png)

![](https://p0.ssl.qhimg.com/t01c8443b4cf135c77e.png)

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **0xdd** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/264191](/post/id/264191)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [Remote Desktop Manager](/tag/Remote Desktop Manager)

 **+1** __7赞

 __收藏

![](https://p2.ssl.qhimg.com/t01fbe6b3f3ba6fed28.png) 0xdd

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)


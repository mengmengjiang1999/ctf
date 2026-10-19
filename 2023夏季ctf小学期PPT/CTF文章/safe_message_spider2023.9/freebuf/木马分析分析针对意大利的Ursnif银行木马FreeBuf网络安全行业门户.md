***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

![1.png](https://image.3001.net/images/20190216/1550314564_5c67ec44e17a0.png!small)

## 介绍

 **近期，又有一波Ursnif攻击席卷了意大利！**

Ursnif是目前活动最为频繁的银行木马，它也被称为GOZI。实际上，它是Gozi-ISFB银行木马的一个变种版本，自从该木马在2014年泄露了其源代码之后，攻击者这些年来一直都在升级和更新Gozi的功能。而且在这个变种版本中，Ursnif还嵌入了针对Office文档的攻击“武器”，即恶意VBA宏，它可以作为Dropper或经过混淆的PowerShell脚本来隐藏真正的Payload。除此之外，Ursnif还使用了隐写术来隐藏恶意代码并躲避AV检测。

当然了，这个变种还使用了QueueUserAPC进程注入技术来向explorer.exe注入恶意代码，这种技术的隐蔽性更强，因为不需要在目标进程中创建远程线程。

## 技术分析

初始感染向量以一个无法打开的Excel文件呈现，并要求用户启用宏来查看恶意文档的内容，文件标题通常都是采购订单或者发票等等。

![2.png](https://image.3001.net/images/20190216/1550314583_5c67ec57f0a2d.png!small)

在对样本的分析过程中，我们提取出了恶意宏代码，我们发现代码回使用Application.International MS
Office属性来检查用户的所属国家。如果返回的国家代码为意大利（代码39），恶意宏将会使用Shell函数来执行下一条攻击指令：

![3.png](https://image.3001.net/images/20190216/1550314591_5c67ec5fa7120.png!small)

恶意宏剩下的函数主要用来准备Shell命令的执行，并使用各种方法来拼接和编码字符串。最终的命令代码包含大量二进制字符串，它们需要使用下列函数来转化为新的PowerShell命令：

    
    
    [Convert]::ToInt16()-as[char]

![4.png](https://image.3001.net/images/20190216/1550314602_5c67ec6ad50fa.png!small)

如上图所示，恶意软件会尝试从至少1到2个嵌入的URL地址去下载一张图片：

[](https://images2.imgbox)

    
    
    <https://images2.imgbox>[.]com/55/c4/rBzwpAzi_o.png
    
    <https://i.postimg>[.]cc/PH6QvFvF/mario.png?dl=1

这个看似合法的图片实际上包含了新的PowerShell命令，攻击者使用了Invoke-PSImage脚本来制作这张恶意图片，而这个脚本一般用来向PNG文件的像素中嵌入字节或脚本代码。

![5.png](https://image.3001.net/images/20190216/1550314616_5c67ec78621b0.png!small)

Et voilà是另一段经过混淆的PowerShell代码，Payload采用Base64编码，所以很好处理：

![6.png](https://image.3001.net/images/20190216/1550314634_5c67ec8ac4f9b.png!small)

代码看似为十六进制编码，可以通过之前的[Convert]::ToInt16函数进行解码。

最终的代码如下：

![7.png](https://image.3001.net/images/20190216/1550314642_5c67ec927b091.png!small)

代码会再次检查用户是否位于意大利，信息由下列命令返回：

    
    
    Get-Culture| Format-List -Property *

如果检测结果为假，脚本会从<http://fillialopago>[.]info/~DF2F63下载一个EXE
Payload，然后将其存储在%TEMP%\Twain001.exe并执行。

在分析的过程中，大多数反病毒软件都无法检测到恶意文件：

![8.png](https://image.3001.net/images/20190216/1550314659_5c67eca3eebbe.png!small)

其中的可执行文件是典型的Ursnif加载器，它负责跟后台服务器交互并下载需要注入到explorer.exe进程中的恶意代码。它使用了IWebBrowser.Navigate函数来从其恶意服务器felipllet[.]info下载恶意数据，其中URI路径会伪造成一个视频文件（.avi）。

![9.png](https://image.3001.net/images/20190216/1550314670_5c67ecaeb5597.png!small)

服务器响应的数据为加密数据，如下图所示：

![10.png](https://image.3001.net/images/20190216/1550314681_5c67ecb94320b.png!small)

解密后，全部有用的数据都会存储在下面这个注册表键中：

    
    
    HKCU\Software\AppDataLow\Software\Microsoft\{GUID}

![11.png](https://image.3001.net/images/20190216/1550314698_5c67ecca16c39.png!small)

注册表键“defrdisc”中包含了下一步需要执行的恶意命令，目标主机启动之后命令会自动执行：

![12.png](https://image.3001.net/images/20190216/1550314707_5c67ecd37ac7a.png!small)

命令的主要目的就是通过PowerShell引擎来执行“cmiftall”注册表键中的数据：

    
    
    C:\Windows\system32\wbem\wmic.exe/output:clipboard process call create “powershell -w hiddeniex([System.Text.Encoding]::ASCII.GetString((get-itemproperty‘HKCU:\Software\AppDataLow\Software\Microsoft\94502524-E302-E68A-0D08-C77A91BCEB4E’).cmiftall))”

“cmiftall”注册表键中的数据是一个以十六进制编码的PowerShell脚本，所以我们可以轻松重构出它所要进行的操作：

![13.png](https://image.3001.net/images/20190216/1550314725_5c67ece579920.png!small)

Ursnif会使用PowerShell脚本来把恶意代码存储到注册表键中，Ursnif能够通过其恶意字节数组来分配空间，其中包含了最终的恶意Payload，并通过调用QueueUserAPC和SleepEx来嵌入到合法进程之中。

### Ursnif的完整工作机制如下图所示：

![14.png](https://image.3001.net/images/20190216/1550314734_5c67eceeb0438.png!small)

## 入侵威胁指标IoC

### 哈希：

    
    
    630b6f15c770716268c539c5558152168004657beee740e73ee9966d6de1753f(老样本)
    
    f30454bcc7f1bc1f328b9b546f5906887fd0278c40d90ab75b8631ef18ed3b7f(新样本)
    
    93dd4d7baf1e89d024c59dbffce1c4cbc85774a1b7bcc8914452dc8aa8a79a78(最终代码)

### Dropurls：

[](https://images2.imgbox)

    
    
    <https://images2.imgbox>[.]com/55/c4/rBzwpAzi_o.png
    
    <https://i.postimg>[.]cc/PH6QvFvF/mario.png?dl=1
    
    <https://fillialopago>[.]info/~DF2F63
    
    <http://felipllet>[.]info

### C&C：

    
    
    pereloplatka[.]host
    
    roiboutique[.]ru
    
    uusisnfbfaa[.]xyz
    
    nolavalt[.]icu
    
    sendertips[.]ru

### IP：

    
    
    185.158.248.142
    
    185.158.248.143

### 攻击组件：

    
    
    HKCU:\Software\AppDataLow\Software\Microsoft\94502524-E302-E68A-0D08-C77A91BCEB4E

## Yara规则

    
    
    import "pe"
    
    rule Ursnif_201902 {
    
    meta:
    
           description = "Yara rule for Ursnifloader - January version"
    
           author = "Yoroi - ZLab"
    
           last_updated = "2019-02-06"
    
           tlp = "white"
    
           category = "informational"
    
    strings:
    
           $a1 = "PADDINGXX" 
    
           $a2 = { 66 66 66 66 66 66 66 }
    
    condition:
    
           all of ($a*) and pe.number_of_sections ==4 and (pe.version_info["OriginalFilename"] contains"Lumen.exe" or pe.version_info["OriginalFilename"] contains"PropositionReputation.exe")
    
     }

 ***参考来源：[yoroi](https://blog.yoroi.company/research/ursnif-long-live-the-steganography/)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**


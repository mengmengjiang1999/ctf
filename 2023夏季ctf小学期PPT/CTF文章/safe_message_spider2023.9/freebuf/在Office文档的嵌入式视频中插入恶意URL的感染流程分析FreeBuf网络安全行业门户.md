**10月底，Cymulate的安全研究人员公布了利用office在线视频特征逻辑漏洞来传播恶意软件的POC。最近，研究人员发现一款利用该漏洞传播URSNIF信息窃取器的在野样本。**

##  **什么是恶意软件的感染媒介？**

因为这类攻击中使用了刻意伪造的word文档，研究人员假设可以通过其他恶意软件或垃圾邮件中的附件、链接到达用户系统。该漏洞影响Microsoft Word
2013及更高版本。PoC和恶意软件使用Microsoft
Word中使用的DOCX文件类型，这是一种可扩展标记语言（XML）文件，可以包含文本，对象，样式，格式和图像。它们存储为单独的文件，并打包在ZIP压缩/存档的DOCX文件中。

##
![1.jpg](https://image.3001.net/images/20190218/1550496482_5c6ab2e2b24c3.jpg!small)**PoC和野外恶意软件如何工作？**

 ****PoC和野外样本滥用了Microsoft
Office在线视频嵌入功能中的逻辑错误，该功能允许用户从外部来源（如YouTube和其他类似媒体平台）嵌入在线视频。PoC是通过在文档中嵌入在线视频然后修改文档包中的XML文件来完成的。如Cymulate所示，它涉及：

> 修改文档的文件扩展名（DOCX到ZIP）。
>
> 提取文档存档中的文件。
>
> 在XML文件中定位标记（embeddedHtml），可以附加恶意脚本或URL。请注意，一旦修改了embeddedHtml参数下的URL
> ，它就会在单击文档内部视频帧的任何位置后自动将用户重定向到指定URL。
>
> 通过修改embeddedHtml中的脚本来初始化和部署payload。仔细研究一下野外样本，可以看出它只是修改了在src参数下编写的URL
> ，将其替换为一个包含在成功重定向时加载和运行的脚本的Pastebin URL。反过来，该脚本访问另一个恶意URL以下载并执行URSNIF恶意软件的版本。

![2.jpg](https://image.3001.net/images/20190218/1550496489_5c6ab2e9adb4e.jpg!small)

## **PoC与在野恶意软件有何不同**

PoC使用的是[msSaveorOpenBlob](a%20href=).aspx)方法来解码嵌入到video
tag中的base64编码的二进制文件，msSaveorOpenBlob可以为文件或blob对象加载应用。点击视频框也可以触发。解码后，会弹出IE下载管理器询问是否运行或者手动保存可执行文件，如图3。真实的恶意软件样本更加简单有效。点击video框后可以直接访问恶意URL。然后加载可以自动下载final
payload的恶意脚本。如图4所示，然后弹出下载管理器保存或运行payload的用户弹窗，伪装为Flash Player更新。

![3.jpg](https://image.3001.net/images/20190218/1550496496_5c6ab2f0438a2.jpg!small)

图3：IE下载管理器询问用户运行或保存可执行文件

##  **总结**

目前还没有为该漏洞分配CVE编号。用户可以拦截XML文件中含有embeddedHtml
tag的文档或关闭嵌入视频的文档。因为URL是可修改的，所以恶意软件可能会给用户和企业传播不同的恶意软件。

###  **IoC** **哈希值(SHA-256)：**

03634e2eab2f61ab1d7359c4038c7042f7eb294d9d5c855560468b8824702c47 —
TROJ_EXPLOIT.AOOCAI

d01b6f839b233ce9d6834a58d9d832ad824b73dd3dd1f399639fe5326faf783b —
TSPY_URSNIF.OIBEAO

###  **相关恶意URL：**

hxxp://wetnosesandwhiskers[.]com/driverfix30e45vers[.]exe

 ***参考来源：[trendmicro](https://blog.trendmicro.com/trendlabs-security-intelligence/hide-and-script-inserted-malicious-urls-within-office-documents-embedded-videos/)，由周大涛编译，转载请注明来自FreeBuf.COM**


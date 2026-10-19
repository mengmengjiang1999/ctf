近日，微软披露 Microsoft Office 存在远程代码执行漏洞 CVE-2022-30190。Avast 的研究人员发现澳大利亚通信公司 VOIPS
Telecom 帕劳分公司已经被攻陷，用于分发恶意软件。受害者打开恶意文档后，将会通过恶意网站下载并执行恶意软件。

## 复杂攻击

攻击分为多个阶段，相对复杂。攻击者使用 LOLBAS（Living off the Land Binaries And Scripts）技术，利用
CVE-2022-30190
漏洞恶意代码，无需将可执行文件落地，尽量降低端点检出可执行文件的可能性。为了最大限度保持隐蔽，攻击者在多个阶段中都使用了合法签名。

## 第一阶段

失陷的网站上部署了一个名为
`robots.txt`的可执行文件，这样在日志中即使被发现也能够尽可能不引起管理人员的注意。调用微软支持诊断工具程序（msdt.exe），下载
`robots.txt`并保存为 `Sihost.exe`，最后执行恶意程序。

![image.png-89.8kB](https://image.3001.net/images/20220609/1654744781_62a166cdb5bc13f48f5fa.png!small)下载文件

![image.png-1421.1kB](https://image.3001.net/images/20220609/1654744782_62a166ce5b9384ae73f61.png!small)网络流量

![image.png-129kB](https://image.3001.net/images/20220609/1654744786_62a166d22e4e0d5a4ebac.png!small)解码命令

## 第二阶段

当 msdt.exe 执行 Sihost.exe 时，样本会下载第二阶段的
Loader（b63fbf80351b3480c62a6a5158334ec8e91fecd057f6c19e4b4dd3febaa9d447）。下载的
Loader 用于下载和解密第三阶段的恶意文件，该文件为也在相同 Web 服务器上部署的加密文件 favicon.svg。

![image.png-76.9kB](https://image.3001.net/images/20220609/1654744786_62a166d2c059ca0cff833.png!small)解密操作

![image.png-35.4kB](https://image.3001.net/images/20220609/1654744787_62a166d36f13c4fa2e408.png!small)样本下载

## 第三阶段

加密文件 favicon.svg 被解密后，会下载第四阶段的样本。

![image.png-462.5kB](https://image.3001.net/images/20220609/1654744787_62a166d3d4a315f0f9962.png!small)解密样本示例

![image.png-323.9kB](https://image.3001.net/images/20220609/1654744789_62a166d58ddf6c733a9ac.png!small)样本下载

这些样本也是部署在 `palau.voipstelecom.com.au`上的，被命名为 `Sevntx64.exe`与 `Sevntx.lnk`。

## 第四阶段

恶意样本执行时，会加载一个长为 66kb 的 Shellcode 程序。该程序名为 `Sevntx64.exe`，是 AsyncRAT 家族的恶意程序，且与
`Sihost.exe`使用相同的证书进行签名。

![image.png-561.4kB](https://image.3001.net/images/20220609/1654744790_62a166d658210baf15249.png!small)加载
Shellcode

## 第五阶段

感染链的最后，攻击者部署 AsyncRAT
远控木马（aba9b566dc23169414cb6927ab5368b590529202df41bfd5dded9f7e62b91479）。木马与
palau.voipstelecom.com.au 的 443 端口进行 C&C 通信。

![image.png-1081.9kB](https://image.3001.net/images/20220609/1654744792_62a166d86b644e8f0e7a4.png!small)AsyncRAT
配置信息

## 回溯

研究人员也发现了恶意软件的早期版本：

文件| 哈希| 首次发现  
---|---|---  
Grievance Against Lawyers, Judge or Justice.doc.exe (signed)|
87BD2DDFF6A90601F67499384290533701F5A5E6CB43DE185A8EA858A0604974| 26.05.2022  
Grievance Against Lawyers, Judge or Justice (1).zip\Grievance Against Lawyers,
Judge or Justice.doc.exe|
0477CAC3443BB6E46DE9B904CBA478B778A5C9F82EA411D44A29961F5CC5C842| 18.05.2022  
  
## IOC

> 0af202af06aef4d36ea151c5a304414a67aee18c3675286275bd01d11a760c04  
> b63fbf80351b3480c62a6a5158334ec8e91fecd057f6c19e4b4dd3febaa9d447  
> ed4091700374e007ae478c048734c4bc0b7fe0f41e6d5c611351bf301659eee0  
> 9651e604f972e36333b14a4095d1758b-50decda893e8ff8ab52c95ea89bb9f74  
> f3ccf22db2c1060251096fe99464002318baccf598b626f8dbdd5e7fd71fd23f  
> 33297dc67c12c7876b8052a5f490cc6a4c50a22712ccf36f4f92962463eb744d  
> 7d6d317616d237ba8301707230abbbae64b2f8adb48b878c528a5e42f419133a  
> aba9b566dc23169414cb6927ab5368b590529202df41bfd5dded9f7e62b91479

## 参考来源

> [Avast](https://decoded.avast.io/threatintel/outbreak-of-follina-in-> australia/)


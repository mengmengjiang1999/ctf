## Shade光顾 ？

**2014年底，国外安全人员首次发现Shado勒索软件，其目标主要是俄罗斯，但近期，这个历史悠久的勒索软件已经开始“光顾”俄罗斯以外的国家，这表明，开发商正在增加其受害者集的广度。**

**Shade又名“Ransom.Troldesh”，通过钓鱼邮件进行传播。从2018年第四季度到2019年第一季度，Shade攻击事件数量飙升，其感染企业多数是高科技类别组织，教育和电信也是他们青睐的目标。​“袭击就像鲨鱼一样，它们的攻击尽可能多而有效，当它们达到不需要进一步攻击的水平时，才会停止。”鉴于此，深信服安全团队将会持续关注Shade攻击活动。**

## 勒索特征

勒索病毒运行之后，桌面背景被改变，如下所示：

![](https://image.3001.net/images/20190806/1565091351_5d4966170987e.png!small)

勒索病毒生成10个勒索信息文本文件README1.txt...README10.txt，如下所示：

![](https://image.3001.net/images/20190806/1565091358_5d49661e72497.png!small)

勒索病毒加密后的文件后缀名为crypted000007,如下所示：

![](https://image.3001.net/images/20190806/1565091365_5d4966252123e.png!small)

## 详细分析

1.解密出相应的注册表健值，如下所示：

![](https://image.3001.net/images/20190806/1565091373_5d49662d28a17.png!small)

打开相应的注册表健值，如下所示：

![](https://image.3001.net/images/20190806/1565091391_5d49663fb3348.png!small)

2.分配相应的内存空间，解密Payload代码，如下所示：

![](https://image.3001.net/images/20190806/1565091398_5d49664619c05.png!small)

3.然后跳转到Payload代码，继续执行，如下所示：

![](https://image.3001.net/images/20190806/1565091405_5d49664d04a09.png!small)

4.分配相应的内存空间，解密出勒索病毒核心代码数据，如下所示：

![](https://image.3001.net/images/20190806/1565091412_5d49665464e8f.png!small)

5.再次解密出勒索病毒核心PE代码，如下所示：

![](https://image.3001.net/images/20190806/1565091419_5d49665b06a64.png!small)

6.解密出Payload中的勒索信息数据，如下所示：

![](https://image.3001.net/images/20190806/1565091446_5d496676b96aa.png!small)

7.获取Payload核心函数地址，如下所示：

![](https://image.3001.net/images/20190806/1565091453_5d49667d00f09.png!small)

8.获取勒索病毒的版本号等信息，如下所示：

![](https://image.3001.net/images/20190806/1565091463_5d4966874c81d.png!small)

9.打开注册表项HKEY_LOCAL_MACHINE\SOFTWARE\System32\Configuration\，查询相应的注册表项，如下所示：

![](https://image.3001.net/images/20190806/1565091469_5d49668dbff09.png!small)

然后将相应的勒索信息数据，写入到注册表项，如下所示：

![](https://image.3001.net/images/20190806/1565091490_5d4966a29980e.png!small)

xcnt 未知

xi主机用户ID号

xmode 未知

xpk 勒索病毒加密公钥

xstate 未知

xVersion 勒索病毒版本号

10.获取主机计算机名，如下所示：

![](https://image.3001.net/images/20190806/1565091499_5d4966ab2f088.png!small)

11.获取系统磁盘目录以及磁盘信息，如下所示：

![](https://image.3001.net/images/20190806/1565091507_5d4966b375406.png!small)

12.创建事件对象Local\\\\{C15730E2-145C-4c5e-B005-3BC753F42475}-once-flag，如下所示：

![](https://image.3001.net/images/20190806/1565091513_5d4966b9910f6.png!small)

13.拷贝自身到C:\ProgramData\Windows下csrss.exe，如下所示：

![](https://image.3001.net/images/20190806/1565091519_5d4966bfe8328.png!small)

拷贝完成之后，生成的文件，如下所示：

![](https://image.3001.net/images/20190806/1565091527_5d4966c7a6d05.png!small)

并设置自启动注册表项，如下所示：

![](https://image.3001.net/images/20190806/1565091533_5d4966cd53595.png!small)

设置完成之后，如下所示：

![](https://image.3001.net/images/20190806/1565091542_5d4966d6aa636.png!small)

14.在加密磁盘的根目录下生成勒索信息文本文件README1.txt...README10.txt，如下所示：

![](https://image.3001.net/images/20190806/1565091554_5d4966e2b797e.png!small)

写入相应的勒索信息，如下所示：

![](https://image.3001.net/images/20190806/1565091570_5d4966f2b26ad.png!small)

一共循环生成十个勒索信息文本文件，如下所示：

![](https://image.3001.net/images/20190806/1565091577_5d4966f9ece9d.png!small)

15.解密出需要加密的文件后缀列表，如下所示：

![](https://image.3001.net/images/20190806/1565091722_5d49678a9e9bb.png!small)

需要加密的文件后缀名列表，如下所示：

>
> wb2、cdr、srw、p7b、odm、mdf、p7c、3fr、der、odb、arw、rwl、cer、xlk、pdd、rw2、crt、dx、r3d、pem、bay、ptx、pfx、indd、nrw、p12、bd、backup、torrent、kwm、pwm、safe、xl、xls、xlsx、xlsm、xlsb、xltm、xlt、xlam、xla、mdb、rtf、txt、xml、csv、pdf、prn、dif、slk、ods、xltx、xlm、odc、xlw、uxdc、pm、udl、dsn、iqy、dqy、rqy、oqy、cub、bak、xsn、xsf、xtp、xtp2、accdb、adb、adp、mda、accda、mde、accde、accdw、accdt、accdc、mdw、dbf、tab、asc、frm、opt、myd、myi、db、onetoc2、one、onepkg、vcs、ics、pst、oft、msg、pptx、ppt、pptm、pps、ppsm、pot、potx、potm、odp、thmx、wpd、wps、ppa、ppam、wmf、emf、pub、ps、xps、vsd、vdx、vss、vsx、vst、vtx、vsw、vdw、emz、dwg、dxf、docx、doc、docm、dotx、dot、dotm、djvu、chm、htm、html、mht、mhtml、shtml、shtm、asp、aspx、dwt、stm、cs、css、psd、pdd、3ds、max、crw、nef、raf、orf、mrw、dcr、mos、pef、srf、dng、x3f、cr2、erf、sr2、kdc、mfw、mef、cin、sdpx、dpx、fido、dae、dcm、dc3、dic、eps、kmz、iff、tdi、exr、pcx、pdp、pxr、sct、u3d、obj、ai3、ai4、ai5、ai6、ai7、ai8、ai、epsp、epsf、hdr、rgbe、xyze、flm、pbm、pgm、ppm、pnm、pfm、pam、pct、pict、psb、fxg、swf、hta、htc、ssi、as、asr、xsl、xsd、dtd、xslt、rss、rdf、lbi、asa、ascx、asmx、config、cfm、cfml、cfc、tld、phtml、jsp、wml、tpl、lasso、jsf、vb、vbs、vtm、vtml、edml、raw、jpg、jpeg、jpe、bmp、png、tif、tiff、dib、gif、svg、svgz、rle、tga、vda、icb、wbm、wbmp、jpf、jpx、jp2、j2k、j2c、jpc、avi、mkv、mov、mp4、wmv、3gp、mpg、mpeg、m4v、divx、mpv、m1v、dat、anim、m4a、qt、3g2、f4v、mkidx、mka、avs、vdr、flv、bin、mp3、wav、asx、pls、zip、7z、rar、tar、gz、bz2、wim、xz、c、h、hpp、cpp、php、php3、php4、php5、py、pl、sln、js、json、inc、sql、java、class、ini、asm、clx、tbb、tbi、tbk、pst、dbx、cbf、crypted、tib、eml、fld、vbm、vbk、vib、vhd、mtr、vault、1cd、dt、cf、cfu、mxl、epf、vrp、grs、geo、elf、lgf、lgp、log、st、pff、mft、efd、md、dmp、fdb、lst、fbk

16.分离出不加密的文件列表，如下所示：

![](https://image.3001.net/images/20190806/1565091730_5d49679247c28.png!small)

相应的文件列表，如下所示：

desktop.ini、boot.ini、Bootfont.bin、ntuser.ini、NTUSER.DAT、IconCache.db

17.遍历磁盘目录，如下所示：

![](https://image.3001.net/images/20190806/1565091739_5d49679bed30e.png!small)

18.遍历目录下的文件，如下所示：

![](https://image.3001.net/images/20190806/1565091746_5d4967a2a3c31.png!small)

19.加密文件，打开文件，读取文件数据，如下所示：

![](https://image.3001.net/images/20190806/1565091755_5d4967ab3c3b8.png!small)

然后加密文件，加密算法，使用RSA+AES算法，如下所示：

![](https://image.3001.net/images/20190806/1565091766_5d4967b6d55b9.png!small)

最后用加密后的文件替换原文件，如下所示：

![](https://image.3001.net/images/20190806/1565091774_5d4967be8386b.png!small)

加密后的文件名为[原文件名Base64编码]+[主机ID]+crypted000007

20.创建桌面背景，如下所示：

![](https://image.3001.net/images/20190806/1565091782_5d4967c6ddeb4.png!small)

设置修改桌面背景，如下所示：

![](https://image.3001.net/images/20190806/1565091789_5d4967cd91fc0.png!small)

生成背景图片，如下所示：

![](https://image.3001.net/images/20190806/1565091797_5d4967d57f8e3.png!small)

21.使用TOR进行CC通信连接，如下所示：

![](https://image.3001.net/images/20190806/1565091804_5d4967dc7dbf0.png!small)

22.DNS通信域名为：whatismyipaddress.com、whatsmyip.net，捕获到的相关数据包，如下所示：

![](https://image.3001.net/images/20190806/1565091810_5d4967e2b5fbf.png!small)

## 解决方案

针对已经出现勒索现象的用户，由于暂时没有解密工具，建议尽快对感染主机进行断网隔离。深信服提醒广大用户尽快做好病毒检测与防御措施，防范该病毒家族的勒索攻击。

## 病毒检测查杀

1、深信服为广大用户免费提供查杀工具，可下载如下工具，进行检测查杀。

64位系统下载链接：

<http://edr.sangfor.com.cn/tool/SfabAntiBot_X64.7z>

32位系统下载链接：

<http://edr.sangfor.com.cn/tool/SfabAntiBot_X86.7z>

2、深信服EDR产品、下一代防火墙及安全感知平台等安全产品均具备病毒检测能力，部署相关产品用户可进行病毒检测，如图所示：

![](https://image.3001.net/images/20190806/1565091817_5d4967e930f84.jpg!small)

3、深信服EDR官网提供勒索病毒搜索功能，支持勒索病毒家族名或加密后缀查询，快速找到相关信息。

搜索链接：[https://edr.sangfor.com.cn](https://edr.sangfor.com.cn/)

## 病毒防御

深信服安全团队再次提醒广大用户，勒索病毒以防为主，目前大部分勒索病毒加密后的文件都无法解密，注意日常防范措施：

> 1、及时给电脑打补丁，修复漏洞。
>
> 2、对重要的数据文件定期进行非本地备份。
>
> 3、不要点击来源不明的邮件附件，不从不明网站下载软件。
>
> 4、尽量关闭不必要的文件共享权限。
>
> 5、更改账户密码，设置强密码，避免使用统一的密码，因为统一的密码会导致一台被攻破，多台遭殃。
>
>
> 6、如果业务上无需使用RDP的，建议关闭RDP。当出现此类事件时，推荐使用深信服防火墙，或者终端检测响应平台（EDR）的微隔离功能对3389等端口进行封堵，防止扩散！
>
>
> 7、深信服防火墙、终端检测响应平台（EDR）均有防爆破功能，防火墙开启此功能并启用11080051、11080027、11080016规则，EDR开启防爆破功能可进行防御。
>
> 8、深信服防火墙客户，建议升级到AF805版本，并开启人工智能引擎Save，以达到最好的防御效果。
>
> 9、使用深信服安全产品，接入安全云脑，使用云查服务可以即时检测防御新威胁。
>
>
> 10、深信服推出安全运营服务，通过以“人机共智”的服务模式帮助用户快速扩展安全能力，针对此类威胁安全运营服务提供设备安全设备策略检查、安全威胁检查、相关漏洞检查等服务，确保第一时间检测风险以及更新策略，防范此类威胁。

最后，建议企业对全网进行一次安全检查和杀毒扫描，加强防护工作。推荐使用深信服安全感知+防火墙+EDR，对内网进行感知、查杀和防护。

 ***本文作者：深信服千里目安全实验室，转载请注明来自FreeBuf.COM**


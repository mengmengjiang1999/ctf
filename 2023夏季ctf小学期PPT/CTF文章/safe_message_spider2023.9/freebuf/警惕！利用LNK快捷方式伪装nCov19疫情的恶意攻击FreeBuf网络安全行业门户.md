自新冠肺炎疫情发生以来，人们时刻都在关心着各项数据，尤其是各个国家及地区的感染和死亡人数等。攻击组织正是看中了这一点，利用疫情相关报告作为诱饵，使得用户在阅读此类文档时也悄然执行了恶意程序。（更多可见:
http://blog.nsfocus.net/netwire-ncov-19-0318/）

近期，攻击组织开始使用快捷方式加白名单文件的手段来投放恶意软件，较之前普遍利用文档漏洞的方式有所不同。

# 事件简述

## 攻击流程

伏影实验室发现，3月份的疫情相关攻击事件中，出现了一种恶意快捷方式，当用户点击后，虽然打开了一个正常无害的文档，但同时也运行了恶意软件。整个流程如下图所示：

![1.png](https://image.3001.net/images/20200413/1586771384_5e9435b8ad5e3.png!small)

  

诱饵lnk  

快捷方式的名称为20200308-sitrep-48-covid-19.pdf.lnk。点击后会打开一个PDF报告（如果有阅读器的话），由世界卫生组织发布，内容为疫情相关数据，如下图所示：

![2.png](https://image.3001.net/images/20200413/1586771350_5e94359615946.png!small)

可知，该文件位于AppData/Local/Temp目录下，找到后验证MD5，知其与外网地址下载的PDF的MD5相同，链接如下：

https://www.who.int/docs/default-source/coronaviruse/situation-reports/20200308-sitrep-48-covid-19.pdf?sfvrsn=16f7ccef_4

然而该快捷方式疑点重重，其创建时间太早，文件大小也不合理，而且命令行太长。

![3+4.png](https://image.3001.net/images/20200413/1586771350_5e9435960d28f.png!small)

完整的命令行如下，会提取快捷方式中暗藏的恶意组件并执行：

![5.png](https://image.3001.net/images/20200413/1586771350_5e94359653544.png!small)
命令首先将快捷方式本身和系统目录下的certutil.exe复制到Temp目录下并重命名，然后在快捷方式（副本）中查找包含”TVNDRgAAAA”的Base64编码数据并存入文件，如下图所示：

![6.png](https://image.3001.net/images/20200413/1586771350_5e94359662808.png!small)
接着，命令使用certutil.exe（副本）对数据进行解码，再使用expand命令对解码后的CAB数据进行解压，得到若干文件，包含真正的疫情报告PDF、白名单工具和恶意组件，最后会执行其中的恶意JS脚本。释放的文件如下图所示：

![7.png](https://image.3001.net/images/20200413/1586771350_5e943596860fb.png!small)

## 白名单利用与劫持

恶意JS脚本会执行cmd命令，后者会执行其它脚本，以启动真正的恶意软件Wordcnvpxy.exe。

命令行会将所需文件复制到指定目录下。此处使用了MSOSTYLE.EXE这个白名单程序来加载恶意软件。该文件为Microsoft Office
2007的组件，必须加载另一个组件Oinfo12.ocx才能执行，而后者恰好被替换为恶意组件，从而实现了白名单劫持。

为了让MSOSTYLE.EXE驻留在用户主机上，命令会通过XLS脚本间接执行一段VBS脚本，后者会在Startup目录下创建用来执行MSOSTYLE.EXE的快捷方式。此处用到了另一个白名称文件url.dll，通过调用其函数FileProtocolHandler来执行MSOSTYLE.EXE。VBS脚本中的相关内容如下图所示：

![8.png](https://image.3001.net/images/20200413/1586771350_5e943596a3013.png!small)

为了更好执行这段VBS脚本，攻击者使用到了第三个白名单文件winrm.vbs。该脚本为Windows自带，并具有Windows的签名，可执行其他XSL脚本。当接收到参数”-format:pretty”或”-format:text”时，winrm.vbs会在cscript.exe所在目录下寻找并执行名为WsmPty.xsl或Wsmtxt.xsl的XSL脚本。

此处，JS执行的cmd命令会将恶意XSL脚本重命名为WsmPty.xsl，并将其与cscript.exe（重命名为msproof.exe）置于同一目录下，通过cscript.exe执行winrm.vbs，从而达到了利用白名单程序执行未签名脚本的目的。相关cmd命令如下图所示：

![9.png](https://image.3001.net/images/20200413/1586771581_5e94367daf1dd.png!small)恶意的WsmPty.xsl代码如下图所示，其作用为解码并执行一段VBS脚本，包含了上文所述中为MSOSTYLE.EXE创建持久性的内容：

![10.png](https://image.3001.net/images/20200413/1586771544_5e943658d612b.png!small)

VBS脚本的第二个功能是生成PE文件头部前三个字节，随后由JS执行的cmd命令将这三个字节与之前释放的MiZl5xsDRylf0W.tmp文件组合，得到完整的Wordcnvpxy.exe。

![11.png](https://image.3001.net/images/20200413/1586771544_5e943658db246.png!small)![12.png](https://image.3001.net/images/20200413/1586771544_5e943658e0dc5.png!small)
最终的恶意组件最终被释放到C:\User\username\Office12下。

![13.png](https://image.3001.net/images/20200413/1586771545_5e9436592326a.png!small)

##  

## 恶意软件

MSOSTYLE.EXE加载Oinfo12.ocx后直接启动了Wordcnvpxy.exe。

![14.png](https://image.3001.net/images/20200413/1586771545_5e943659296a3.png!small)

Wordcnvpxy.exe会每隔60秒向motivation.*****.site发起一次HTTP请求，以下载后续恶意软件并执行。

![15.png](https://image.3001.net/images/20200413/1586771545_5e94365935c82.png!small)![16.png](https://image.3001.net/images/20200413/1586771545_5e9436596c0f8.png!small)  

下载后的文件经过需经过Base64解码和R**解密。  

其中，Base64解码与标准有所不同，编码表和填充字符串均被替换。编码表如下所示：

”z2bqw7k90rJYALIQUxZK%sO=hd5**piVMFlaRucWy31GTNH-mED8fnXtPvSojeB6g”

最后一个字符串’g’为填充字符，替代了原版的’=’。

解码后的数据尾部包含要创建的文件名，以’$’开头。剩余数据经过R**解密后保存在当前登录用户的temp目录下。R**解密中初始密钥为64个字节，生成方式如下：

![17.png](https://image.3001.net/images/20200413/1586771545_5e94365975522.png!small)

##  

## 事件影响

同某些长期活跃的攻击链域名不同，本次事件，C&C较为孤立且不活跃，也未显示出攻击者准备利用疫情来长期“经营”的迹象，故可能是定向发起，或由小团体所为。

在众多涉及新型肺炎疫情恶意诱饵的安全事件中，此次攻击中使用了多个白名单文件，使得恶意行为更加难以检测。而利用快捷方式释放无害文档和恶意组件的手段，与以往利用文档漏洞有显著区别，需引起高度警惕。

  

# 关于绿盟科技伏影实验室

伏影实验室专注于安全威胁研究与监测技术，包括但不限于威胁识别技术，威胁跟踪技术，威胁捕获技术，威胁主体识别技术。研究目标包括：僵尸网络威胁，DDOS对抗，WEB对抗，流行服务系统脆弱利用威胁、身份认证威胁，数字资产威胁，黑色产业威胁
及 新兴威胁。通过掌控现网威胁来识别风险，缓解威胁伤害，为威胁对抗提供决策支撑。

  

# 关于绿盟威胁中心NTI

绿盟威胁情报中心（NSFOCUS Threat Intelligence center,
NTI）是绿盟科技为落实智慧安全2.0战略，促进网络空间安全生态建设和威胁情报应用，增强客户攻防对抗能力而组建的专业性安全研究组织。其依托公司专业的安全团队和强大的安全研究能力，对全球网络安全威胁和态势进行
持续观察和分析，以威胁情报的生产、运营、应用等能力及关键技术作为核心研究内容，推出了
绿盟威胁情报平台以及一系列集成威胁情报的新一代安全产品，为用户提供可操作的情报数据、专业的情报服务和高效的威胁防护能力，帮助用户更好地了解和应对各类网络威胁。

绿盟威胁情报中心NTI网址：https://nti.nsfocus.com/

  


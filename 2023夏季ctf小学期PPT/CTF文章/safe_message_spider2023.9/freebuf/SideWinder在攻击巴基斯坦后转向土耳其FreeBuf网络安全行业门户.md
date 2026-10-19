SideWinder，也称为 Razor Tiger、Rattlesnake 与 T-APT-04，至少从 2012
年以来一直在针对巴基斯坦政府组织发动攻击。SideWinder 被认为是印度支持的 APT
组织，特别关注巴基斯坦、阿富汗、中国与尼泊尔，一直针对军事、政府与商业公司发起攻击。研究人员近日发现 SideWinder
使用了服务器端多态技术，绕过传统基于签名的反病毒软件的检测，来部署下一阶段的 Payload。

## 服务器端多态技术

服务器端多态技术是攻击者用于逃避反病毒程序扫描检测的一种技术。顾名思义，多态恶意软件是通过加密与混淆改变外在形态的，主要用于确保没有任何两个样本看起来相同。传统基于签名的反病毒软件很难检测此类恶意软件，尽管听起来十分炫酷，但其实这是一种自从上世纪九十年代就被攻击者使用的成熟技术。

## 攻击分析

从 2022 年 11 月下旬开始，SideWinder 利用服务器端多态技术部署下一阶段
Payload。诱饵文档是针对巴基斯坦政府官员创建的，通过利益相关的文档引诱受害者上钩。诱饵文档名为 BEACON JOURNAL – 2023
PAKISTAN NAVY WAR COLLEGE (PNWC)（意为：期刊指南-2023巴基斯坦海军学院）。

![image.png-307kB](https://image.3001.net/images/20230510/1683730955_645bb20b04919fc26a895.png!small)针对巴基斯坦的诱饵文档

2022 年 12 月初，攻击者使用的另一个诱饵文档名为
PK_P_GAA_A1_Offerred.docx。文件内容长达八页，伪装成要购买国防物品、国防服务的交易邀约与承诺书。

![image.png-288.8kB](https://image.3001.net/images/20230510/1683730956_645bb20c60fc96f51fe13.png!small)针对巴基斯坦的诱饵文档

诱饵文档并没有使用嵌入恶意宏代码的方式投递下一阶段的 Payload，而是利用了远程模板注入漏洞（CVE-2017-0199）。

诱饵文档 Guidelines FOR JOURNAL - 2023 PAKISTAN NAVY WAR COLLEGE (PNWC).doc 通过
hxxps[:]//pnwc[.]bol-north[.]com/5808/1/3686/2/0/0/0/m/files-a2e589d2/file[.]rtf 加载远程模板。该域名
pnwc[.]bol-north[.]com 解析的 IP 地址为 5.230.73[.]106。

![image.png-321.8kB](https://image.3001.net/images/20230510/1683730957_645bb20d574d83dd64ac1.png!small)下一阶段的
URL

诱饵文档 PK_P_GAA_A1_Offerred.docx 通过 hxxps[:]//paknavy-gov-pkp[.]downld[.]net/14578/1/6277/2/0/0/0/m/files-75dc2b1e/file[.]rtf 加载远程模板。该域名
paknavy-gov-pk[.]downld[.]net 解析的 IP 地址为 185.205.187[.]234。

![image.png-402.5kB](https://image.3001.net/images/20230510/1683730958_645bb20eda95a0667dccc.png!small)下一阶段的
URL

攻击活跃期间，攻击者将受害者重定向到合法的巴基斯坦海军学院。目前，恶意服务器已经不再活跃。

![image.png-405.6kB](https://image.3001.net/images/20230510/1683730959_645bb20fc08f9d5af84a1.png!small)合法巴基斯坦海军学院网站

3 月初，研究人员发现了同样通过钓鱼邮件传播的新恶意软件。该文档的特殊之处在于，受害者来自土耳其。

### 武器化

下一阶段的 Payload 文件 file.rtf 是一个 RTF
文件，只能由巴基斯坦境内的用户下载。该地址下载的文件名与文件类型都是相同的，但文件内容、文件大小与文件哈希都不相同。这表明使用了服务器多态技术，每次会响应不同的文件。

如果用户不在巴基斯坦境内，服务器只会返回 8 字节的 RTF 文件。而如果用户在巴基斯坦境内，服务器会返回大小在 406KB 到 414KB 之间的 RTF
文件。

![image.png-716.2kB](https://image.3001.net/images/20230510/1683730960_645bb210aa05d4881d83d.png!small)file.rtf

### Loader

通过 paknavy-gov-pk[.]downld[.]net 下载的 file.rtf 文件，可以从中解析出 1.a 对象以供进一步分析：

![image.png-468.5kB](https://image.3001.net/images/20230510/1683730962_645bb21224df3e2bcf968.png!small)1.a
对象概览

在恶意软件执行链中，该对象保存在失陷主机的 C:\Users\user\AppData\Local\Temp\1.a 路径下。与此同时，1.a
文件是经过混淆处理的 JavaScript 代码。

![image.png-665.6kB](https://image.3001.net/images/20230510/1683730963_645bb2135956c37975bf1.png!small)反混淆字符串

base64 编码的数据可以为解码为 DLL 文件 App.dll，而 URL 则是用于与攻击者进行进一步通信：

![image.png-236.3kB](https://image.3001.net/images/20230510/1683730964_645bb21450f830dc45fef.png!small)用于进一步通信的
URL

### Agent

前文提到的 base64 编码数据是一个名为 App.dll 的 DLL 文件，该文件由 .NET 开发。

为了避免基于静态签名的检测，App.dll 与其他文件都使用相同的方式进行混淆。

![image.png-459.3kB](https://image.3001.net/images/20230510/1683730965_645bb2152004145f7b4d7.png!small)App.dll
文件

App.dll 文件由 JavaScript 代码启动，反序列化 .NET 二进制文件并将 URL 传递给可执行文件的 Work() 函数。该函数通过
URL 发起请求并尝试解密然后执行响应，以此检索下一阶段的 Payload 并执行它。

## 网络基础设施

通常来说，SideWinder 的 C&C 服务器只在短期有效。至少从 2021 年 1 月开始，部署 RTF
文件的服务器对于非巴基斯坦来源请求的响应一直是相同的（仅有八字节的文件）。在野一共发现了 28 个域名下部署了这个空的 RTF 文件，这些域名对应的 URL
也是相似的。

如下所示，SideWinder 部署恶意文件的 URL 结构是可预测的。该特征已经持续超过两年，研究人员相信其可能会继续使用下去。

  * 第一阶段：/2/0/0//files-*/(hta|file.rtf)
  * 第二阶段：/3/1/1//files-*/

2023 年 3 月中旬，研究人员发现了新配置的服务器来投递恶意 Payload。该服务器的不同之处是针对土耳其的受害者投递第二阶段的
Payload，这说明土耳其也是该组织的攻击目标。

## 攻击目标

SideWinder 组织的主要目标仍然是巴基斯坦，新增的攻击目标是土耳其。

![image.png-206.7kB](https://image.3001.net/images/20230510/1683730966_645bb2167287038ea6764.png!small)攻击对象分布

## 总结

本文介绍了 SideWinder 组织的针对性攻击，尤其是针对土耳其的新攻击动向。从地缘政治角度来说，土耳其对巴基斯坦的支持可能引起了印度的警惕。

## IOC

> b7e63b7247be18cdfb36c1f3200c1dba  
> 8af93bed967925b3e5a70d0ad90eae1f13bc6e362ae3dac705e984f8697aaaad  
> 5efddbdcf40ba01f1571140bad72dccb  
> a45258389a3c0d4615f3414472c390a0aabe77315663398ebdea270b59b82a5c  
> 3b853ae547346befe5f3d06290635cf6  
> bc9d4eb09711f92e4e260efcf7e48906dca6bf239841e976972fd74dac412e2f  
> 666b2b178ce52e30be9e69de93cc60a9  
> cd09bf437f46210521ad5c21891414f236e29aa6869906820c7c9dc2b565d8be  
> ef00004a1ebc262ffe0fb89aa5524d42  
> a3283520e04d7343ce9884948c5d23423499fa61cee332a006db73e2b98d08c3  
> 6c7d24b90f3c6b4383bd7d08374a0c6f  
> 4db0a2d4d011f43952615ece8734ca4fc889e7ec958acd803a6c68b3e0f94eea  
> 73750f08265bbe80c3f235318bcef6fe  
> bc3c6f9d51e2bdb37e03b01e2949f72836ecee4230e2320c5dc33a83b55b062f  
> 16341fcff1bc7388387fd17b4b3a7a50  
> cf1f4ec1d7db6cf1fe8e15687b348a279889689fa9c387de4a2c310c34336f9f  
> 1c62441de076eb5a5b2e1f8146767777  
> 75079e408ca9517825ffac396680a2d2169d691be3f1adbbd797e05e665c6fde  
> dacdb33b6e9de4c1fe8591bb5a65c55c  
> cde768a4cf95e58f0e98e2bcca0663fd2c1a36510f6010065b4f54169a92e207  
> 709e6a64735432c25cafb89951cc149c  
> a2a9fd1db7f1dc196fa8af0669ea72d1f8ae48bf4775108ee746e0f83c5a7498  
> hxxps[:]//paknavy-gov-> pkp[.]downld[.]net/14578/1/6277/2/0/0/0/m/files-75dc2b1e/file[.]rtf  
> hxxps[:]//pnwc[.]bol-> north[.]com/5808/1/3686/2/0/0/0/m/files-a2e589d2/file[.]rtf  
> 185.205.187[.]234  
> 5.230.73[.]106  
> https[:]//cstc-spares-> vip-163.dowmload[.]net/14668/1/1228/2/0/0/0/m/files-403a1120/file[.]rtf  
> https[:]//mtss.bol-> south[.]org/5974/1/8682/2/0/0/0/m/files-b2dff0ca/file[.]rtf  
> https[:]//paknavy-gov-> pk[.]downld[.]net/14578/1/6277/2/0/0/0/m/files-75dc2b1e/file[.]rtf  
> hxxts[:]//paknavy-gov-> pk[.]downld[.]net/14578/1/6277/2/0/0/0/m/files-75dc2b1e/file[.]rtf  
> hxxts[:]//pnwc[.]bol-> north[.]com/5808/1/3686/2/0/0/0/m/files-a2e589d2/file[.]rtf  
> hxxts[:]//sl-navy[.]office-drive[.]live/45/1/334/2/0/0/0/m/files-> fe9dade2/file[.]rtf  
> hxxts[:]//forecast[.]comsats-net[.]com/5760/1/5041/2/0/0/0/m/files-> dd96433f/file[.]rtf  
> https[:]//forecast[.]comsats-> net[.]com/5760/1/5039/2/0/0/0/m/files-d7c7dda1/file[.]rtf  
> hxxts[:]//forecast[.]comsats-> net[.]com/5760/1/5035/2/0/0/0/m/files-4a0480ae/file[.]rtf  
> hxxts[:]//moma[.]comsats-> net[.]com/5753/1/4375/2/0/0/0/m/files-8062311a/file[.]rtf  
> hxxts[:]//forecast[.]comsats-> net[.]com/5760/1/5040/2/0/0/0/m/files-f3b20b30/file[.]rtf  
> hxxts[:]//forecast[.]comsats-> net[.]com/5760/1/5036/2/0/0/0/m/files-2ad09cbd/file[.]rtf  
> hxxts[:]//moma[.]comsats-> net[.]com/5753/1/4371/2/0/0/0/m/files-b62d382f/file[.]rtf  
> hxxts[:]//srilanka-> navy[.]lforvk[.]com/135/1/334/2/0/0/0/m/files-4fdaf6c7/file[.]rtf  
> hxxts[:]//promotionlist[.]comsats-> net[.]com/5756/1/8887/2/0/0/0/m/files-3d1dff0f/file[.]rtf  
> hxxts[:]//dgms[.]paknavy-> gov[.]com/5733/1/5051/2/0/0/0/m/files-73bdca4d/file[.]rtf  
> hxxts[:]//mofadividion[.]ptcl-> gov[.]com/5724/1/3268/2/0/0/0/m/files-11e30891/file[.]rtf  
> hxxts[:]//ksew[.]kpt-> gov[.]org/5663/1/3275/2/0/0/0/m/files-937950ad/file[.]rtf  
> hxxts[:]//ministryofforeignaffairs-mofa-gov-> pk[.]dytt88[.]org/14444/1/2454/2/0/0/0/m/files-9ba90b7f/file[.]rtf  
> hxxt[:]//bdmil[.]alit[.]live/3398/1/50073/2/0/0/0/m/files-> ac995f17/file[.]rtf  
> hxxt[:]//navy-mil-> bd[.]jmicc[.]xyz/5625/1/8145/2/0/0/0/m/files-b11074b7/file[.]rtf  
> hxxts[:]//navy-mil-> bd[.]jmicc[.]xyz/5625/1/8145/2/0/0/0/m/files-b11074b7/file[.]rtf  
>
> hxxts[:]//paknavy[.]jmicc[.]xyz/5627/1/4367/2/0/0/0/m/files-9e0912cc/file[.]rtf  
>
> hxxt[:]//bdmil[.]alit[.]live/3398/1/54346/2/0/0/0/m/files-491dc489/file[.]rtf  
>
> hxxts[:]//paknavy[.]comsats[.]xyz/5552/1/5037/2/0/0/0/m/files-1b5c7556/file[.]rtf  
> hxxts[:]//mofa-gov[.]interior-> pk[.]org/14419/1/6/2/0/0/0/m/files-07b01f9b/file[.]rtf  
> hxxt[:]//mofa-gov[.]interior-> pk[.]org/14419/1/6/2/0/0/0/m/files-07b01f9b/file[.]rtf  
> hxxts[:]//paknavy[.]paknavy[.]live/5516/1/4367/2/0/0/0/m/files-> db71f6b3/file[.]rtf  
>
> hxxts[:]//mofabn[.]ksewpk[.]com/5511/1/4993/2/0/0/0/m/files-18e5db65/file[.]rtf  
> hxxt[:]//srilankanavy[.]ksew[.]org/5471/1/1101/2/0/0/0/m/files-> cd6e6dbd/file[.]rtf  
> hxxts[:]//srilankanavy[.]ksew[.]org/5471/1/1101/2/0/0/0/m/files-> cd6e6dbd/file[.]rtf  
> hxxt[:]//maritimepakistan[.]kpt-pk[.]net/5434/1/3694/2/0/0/0/m/files-> ce32ed85/file[.]rtf  
> hxxts[:]//maritimepakistan[.]kpt-pk[.]net/5434/1/3694/2/0/0/0/m/files-> ce32ed85/file[.]rtf  
> hxxt[:]//dgmp-paknavy[.]mod-> pk[.]com/14325/1/10/2/0/0/0/m/files-5291bef6/file[.]rtf  
> hxxts[:]//dgmp-paknavy[.]mod-> pk[.]com/14325/1/10/2/0/0/0/m/files-5291bef6/file[.]rtf  
> hxxt[:]//dgpr[.]paknvay-> pk[.]net/5330/1/1330/2/0/0/0/m/files-4d9d0395/file[.]rtf  
> hxxts[:]//cabinet-gov-pk[.]ministry-> pk[.]net/14300/1/1273/2/0/0/0/m/files-68ebf815/file[.]rtf  
> hxxts[:]//dgpr[.]paknvay-> pk[.]net/5330/1/1330/2/0/0/0/m/files-4d9d0395/file[.]rtf  
> hxxts[:]//careitservices[.]paknvay-> pk[.]net/5359/1/4586/2/0/0/0/m/files-266ad911/file[.]rtf  
>
> hxxts[:]//defencelk[.]cvix[.]live/3023/1/54082/2/0/0/0/m/files-0c31ed2d/file[.]rtf  
>
> hxxt[:]//mohgovsg[.]bahariafoundation[.]live/5320/1/13/2/0/0/0/m/files-1ddf5195/file[.]rtf  
>
> hxxts[:]//mohgovsg[.]bahariafoundation[.]live/5320/1/13/2/0/0/0/m/files-1ddf5195/file[.]rtf  
> hxxts[:]//sppc[.]moma-> pk[.]org/5281/1/4265/2/0/0/0/m/files-d2608a99/file[.]rtf  
>
> hxxps[:]//mailrta.mfagov[.]org/3818/1/53382/2/0/0/0/m/files-c78a6966/file[.]rtf  
> http[:]//mailnavybd.govpk[.]net/5845/1/12/2/0/0/0/m/files-> ca78574e/file[.]rtf  
>
> hxxts[:]//mailaplf[.]cvix[.]live/2968/1/50390/2/0/0/0/m/files-7630e91a/file[.]rtf  
> hxxt[:]//slpa[.]mod-gov[.]org/5946/1/5775/2/0/0/0/m/files-> fca3cc50/file[.]rtf  
> hxxt[:]//slpa[.]mod-> gov[.]org/5946/1/5780/2/0/0/0/m/files-20bba5af/file[.]rtf  
> hxxt[:]//slpa[.]mod-> gov[.]org/5946/1/5795/2/0/0/0/m/files-c9dddc54/file[.]rtf  
> hxxt[:]//slpa[.]mod-> gov[.]org/5946/1/5797/2/0/0/0/m/files-875e140b/file[.]rtf  
> hxxt[:]//slpa[.]mod-> gov[.]org/5946/1/5771/2/0/0/0/m/files-5995311a/file[.]rtf  
> hxxt[:]//slpa[.]mod-> gov[.]org/5946/1/5784/2/0/0/0/m/files-94153639/file[.]rtf  
> hxxt[:]//slpa[.]mod-> gov[.]org/5946/1/5770/2/0/0/0/m/files-2d21c32e/file[.]rtf  
> hxxt[:]//slpa[.]mod-> gov[.]org/5946/1/5778/2/0/0/0/m/files-27d5c7d3/file[.]rtf  
>
> hxxt[:]//mailnavymilbd[.]govpk[.]net/5848/1/13/2/0/0/0/m/files-57d837e4/file[.]rtf  
> hxxts[:]//slpa[.]mod-gov[.]org/5946/1/5792/2/0/0/0/m/files-> da7756e4/file[.]rtf  
> hxxts[:]//slpa[.]mod-> gov[.]org/5946/1/5776/2/0/0/0/m/files-175c56e7/file[.]rtf  
> hxxts[:]//slpa[.]mod-> gov[.]org/5946/1/5783/2/0/0/0/m/files-a26663eb/file[.]rtf  
> hxxts[:]//slpa[.]mod-> gov[.]org/5946/1/5780/2/0/0/0/m/files-20bba5af/file[.]rtf  
> hxxts[:]//slpa[.]mod-> gov[.]org/5946/1/5785/2/0/0/0/m/files-76f11745/file[.]rtf  
> hxxts[:]//slpa[.]mod-> gov[.]org/5946/1/5788/2/0/0/0/m/files-3acec3be/file[.]rtf  
> hxxts[:]//slpa[.]mod-> gov[.]org/5946/1/5782/2/0/0/0/m/files-78d7e141/file[.]rtf  
> hxxts[:]//slpa[.]mod-> gov[.]org/5946/1/5796/2/0/0/0/m/files-97e02960/file[.]rtf  
> hxxts[:]//slpa[.]mod-> gov[.]org/5946/1/5795/2/0/0/0/m/files-c9dddc54/file[.]rtf  
> hxxts[:]//slpa[.]mod-> gov[.]org/5946/1/5790/2/0/0/0/m/files-a3d0041a/file[.]rtf  
> hxxts[:]//slpa[.]mod-> gov[.]org/5946/1/5773/2/0/0/0/m/files-5a31d681/file[.]rtf  
> hxxts[:]//slpa[.]mod-> gov[.]org/5946/1/5799/2/0/0/0/m/files-03dd18bd/file[.]rtf  
> hxxts[:]//slpa[.]mod-> gov[.]org/5946/1/5781/2/0/0/0/m/files-62caea91/file[.]rtf  
> hxxts[:]//slpa[.]mod-> gov[.]org/5946/1/5804/2/0/0/0/m/files-c43dece3/file[.]rtf  
> hxxts[:]//slpa[.]mod-> gov[.]org/5946/1/5794/2/0/0/0/m/files-60cb1621/file[.]rtf  
> hxxts[:]//slpa[.]mod-gov[.]org/5946/1/5775/2/0/0/0/m/files-> fca3cc50/file[.]rtf  
> hxxts[:]//slpa[.]mod-> gov[.]org/5946/1/5778/2/0/0/0/m/files-27d5c7d3/file[.]rtf  
> hxxts[:]//slpa[.]mod-gov[.]org/5946/1/5787/2/0/0/0/m/files-> fb528413/file[.]rtf  
> hxxts[:]//slpa[.]mod-> gov[.]org/5946/1/5786/2/0/0/0/m/files-5def1d52/file[.]rtf  
> hxxts[:]//slpa[.]mod-> gov[.]org/5946/1/5798/2/0/0/0/m/files-c3178f3d/file[.]rtf  
> hxxts[:]//slpa[.]mod-> gov[.]org/5946/1/5779/2/0/0/0/m/files-2f2e186d/file[.]rtf  
> hxxts[:]//slpa[.]mod-> gov[.]org/5946/1/5789/2/0/0/0/m/files-8822f8ff/file[.]rtf  
> hxxts[:]//slpa[.]mod-> gov[.]org/5946/1/5777/2/0/0/0/m/files-7f2e758b/file[.]rtf  
> hxxts[:]//slpa[.]mod-gov[.]org/5946/1/5791/2/0/0/0/m/files-> bda6f896/file[.]rtf  
> hxxts[:]//slpa[.]mod-> gov[.]org/5946/1/5769/2/0/0/0/m/files-2f6b9c9a/file[.]rtf  
> hxxts[:]//slpa[.]mod-> gov[.]org/5946/1/5774/2/0/0/0/m/files-12eca223/file[.]rtf  
> hxxts[:]//slpa[.]mod-> gov[.]org/5946/1/5772/2/0/0/0/m/files-84c4942a/file[.]rtf  
> hxxts[:]//slpa[.]mod-> gov[.]org/5946/1/5771/2/0/0/0/m/files-5995311a/file[.]rtf  
> hxxts[:]//slpa[.]mod-> gov[.]org/5946/1/5797/2/0/0/0/m/files-875e140b/file[.]rtf  
> hxxts[:]//slpa[.]mod-> gov[.]org/5946/1/5784/2/0/0/0/m/files-94153639/file[.]rtf  
> hxxts[:]//slpa[.]mod-> gov[.]org/5946/1/5770/2/0/0/0/m/files-2d21c32e/file[.]rtf  
> hxxts[:]//slpa[.]mod-> gov[.]org/5946/1/5793/2/0/0/0/m/files-f2d0617e/file[.]rtf  
>
> hxxts[:]//mailrta[.]mfagov[.]org/3818/1/53382/2/0/0/0/m/files-c78a6966/file[.]rtf  
> hxxt[:]//promotionlist[.]comsats-> net[.]com/5756/1/8887/2/0/0/0/m/files-3d1dff0f/file[.]rtf  
>
> hxxts[:]//mailnavymilbd[.]govpk[.]net/5848/1/13/2/0/0/0/m/files-57d837e4/file[.]rtf  
> hxxt[:]//mailnavybd[.]govpk[.]net/5845/1/12/2/0/0/0/m/files-> ca78574e/file[.]rtf  
> slpa.mod-gov[.]org  
> 62.113.255[.]80  
> mailrta.mfagov[.]org  
> 194.61.121[.]216  
> promotionlist.comsats-net[.]com  
> 5.255.104[.]32  
> mailnavybd.govpk[.]net  
> 5.255.112[.]194  
> mailnavymilbd.govpk[.]net

## 参考来源

> [BlackBerry](https://blogs.blackberry.com/en/2023/05/sidewinder-uses-server-> side-polymorphism-to-target-pakistan)


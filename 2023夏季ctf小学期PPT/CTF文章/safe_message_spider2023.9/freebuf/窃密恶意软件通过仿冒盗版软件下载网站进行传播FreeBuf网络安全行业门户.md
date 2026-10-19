攻击者正在针对寻求下载盗版软件的用户进行攻击，由于用户自己知道获取与使用盗版软件是违法的，许多下载盗版软件的用户都不会对下载来源进行安全审查，这些用户最终可能会付出更大的代价。

## 介绍

自从 Napster
在互联网上发布盗版已经有二十余年，海盗湾种子下载站出现也近十年。尽管许多国家都针对此发布了相关的法律与禁令，但是盗版依旧屡禁不止，许多人都会下载与使用。互联网上也有很多宣传破解软件的的广告，出现在
Google 的搜索结果与网站的广告位中。

![image.png-133.1kB](https://image.3001.net/images/20220827/1661602124_630a094cd63e8e9a9d3b9.png!small)Google
搜索结果中的仿冒盗版下载网站

安全研究人员最近发现了通过仿冒盗版软件下载网站进行恶意软件传播的攻击行动。如上所示，Google
的搜索结果中就包含此类虚假网站，这些网站看起来与真正的盗版下载网站差不多。

## 案例一分析

### 阶段一：重定向分发

用户访问仿冒盗版下载网站时，会被多次重定向到最终部署恶意软件的网站，多次重定向则是为了规避搜索引擎和其他扫描程序的检测。如下所示，此类重定向在正常网站上可能会引起受害者的警觉，但是在盗版下载网站上，受害者可能会认为这是网站运行的正常方式。

![image.png-123.3kB](https://image.3001.net/images/20220827/1661602125_630a094d960ad389b488a.png!small)多次重定向

如下所示，恶意文件都部署在开放目录中，其中包含 3000 余个伪装成常见破解软件的恶意 ZIP 压缩文件，用户下载的文件通常是一个小于 10MB 的 ZIP
压缩文件。

![image.png-477.6kB](https://image.3001.net/images/20220827/1661602126_630a094e70031cda5f418.png!small)开放目录

分发方式也并不单一，攻击者会还使用 Mediafire 与 Discord 等受信任的公共网站部署恶意软件。

![image.png-631.6kB](https://image.3001.net/images/20220827/1661602127_630a094f8c622f303ff06.png!small)钓鱼网站

### 阶段二：Loader

下载的压缩文件中包含一个受密码加密的 ZIP 压缩文件和另一个伪装成包含密码的文本文件。

![image.png-39.3kB](https://image.3001.net/images/20220827/1661602129_630a09511e2f9dee1fc40.png!small)压缩文件与密码

加密的 ZIP 文件中还包含一个名为 setup.zip 的文件，大小为 1.3MB。提取压缩文件会出现一个 0x20 与 0x00
字节填充的可执行文件，大小超过 600MB，如下所示：

![image.png-204kB](https://image.3001.net/images/20220827/1661602129_630a0951bdd3153d04ba7.png!small)填充文件

研究人员认为填充字节只是为了逃避检测，该样本还具备反虚拟机与反调试功能。删除无关字节后，样本大小从 600MB 下降到 78KB，如下所示。

![image.png-354.4kB](https://image.3001.net/images/20220827/1661602130_630a09529a3bbff6fb66e.png!small)实际大小

文件被执行，就会生成一个被编码的 PowerShell 命令，解码后为 `(Start-Sleep-s10;Remove-Item-Path"C:\Users\User\Desktop\Setupfinal.exe"-Force)`。连接远程服务器，下载名为
`windows.decoder.manager.form.fallout15_Uwifqzjw.jpg`的文件，如下所示：

![image.png-74.4kB](https://image.3001.net/images/20220827/1661602131_630a0953d74b813099204.png!small)下载文件

![image.png-169.3kB](https://image.3001.net/images/20220827/1661602132_630a0954931627a19e468.png!small)下载文件

下载的文件看起来是加密的，但实际上只是倒序存储。将其翻转过来可以发现，这是一个 DLL 文件。

### 阶段三：RedLine Stealer

DLL 为一个 RedLine 窃密恶意软件，会窃取受害者的隐私信息，例如浏览器历史记录。

## 案例二分析

研究人员还发现仿冒盗版下载网站还分发 RecordBreaker 窃密恶意软件，样本文件通过 Themida、VMprotect 和 MPRESS
等进行加壳，如下所示。

![image.png-156.4kB](https://image.3001.net/images/20220827/1661602133_630a09555eb234fd1c735.png!small)加壳文件

攻击者常常使用加壳来躲避检测，并且在壳中融合反虚拟机与反调试技术，如下所示。

![image.png-99.1kB](https://image.3001.net/images/20220827/1661602134_630a095615cf84ebd3868.png!small)反调试技术

![image.png-101.2kB](https://image.3001.net/images/20220827/1661602134_630a0956bee9431b54d9b.png!small)反调试技术

![image.png-83.5kB](https://image.3001.net/images/20220827/1661602135_630a0957769c8590d17dd.png!small)反调试技术

![image.png-24.1kB](https://image.3001.net/images/20220827/1661602136_630a095869201576ee448.png!small)关闭安全软件的提示

样本与 C&C 服务器通信，并回传机器 ID 与配置 ID：

![image.png-382.8kB](https://image.3001.net/images/20220827/1661602137_630a0959119ea2e373f44.png!small)C&C
通信

通过浏览器窃取的信息包括
MetaMask、TronLink、BinanceChain、Ronin、MetaMask、MetaX、XDEFI、WavesKeeper、Solflare、Rabby、CyanoWallet、Coinbase、AuroWallet、KHC、TezBox、Coin98、Temple、
ICONex、Sollet、CloverWallet、PolymeshWallet、NeoLine、Keplr、TerraStation、Liquality、SaturnWallet、GuildWallet、Phantom、TronLink、Brave、MetaMask、Ronin、MEW_CX、TON、Goby
和 TON。

收集到的失陷主机上的相关信息回传给 C&C 服务器：

![image.png-429.9kB](https://image.3001.net/images/20220827/1661602137_630a0959e2e01e2a2c4ea.png!small)窃密信息

恶意软件还能够将屏幕截图回传给攻击者，如下所示：

![image.png-239.7kB](https://image.3001.net/images/20220827/1661602139_630a095be0f0003daf251.png!small)发送屏幕截图

RecordBreaker 收集用户的 Cookie 也会回传给 C&C 服务器，如下所示：

![image.png-905.6kB](https://image.3001.net/images/20220827/1661602140_630a095cb4ab22b64fd0b.png!small)窃取浏览器
Cookie

## 结论

攻击者通过盗版软件的渠道分发恶意软件，窃取受害者的信息进行获利。用户能够通过使用合法网站下载的正版软件来规避此类，由于非法行为造成的感染。

## IOC

> 45[.]150[.]67[.]175  
> 94[.]158[.]244[.]119  
> 45[.]135[.]134[.]211  
> 194[.]180[.]174[.]180  
> 185[.]250[.]148[.]76  
> 37[.]221[.]67[.]219  
> 45[.]140[.]146[.]169  
> 94[.]140[.]114[.]231  
> 94[.]158[.]244[.]213  
> 45[.]142[.]212[.]100  
> 194[.]180[.]174[.]187  
> 194[.]180[.]174[.]186  
> 135[.]181[.]105[.]89  
> 77[.]91[.]102[.]88  
> 77[.]91[.]103[.]31  
> 94[.]158[.]247[.]24  
> 85[.]239[.]34[.]235  
> 45[.]67[.]34[.]234  
> 45[.]67[.]34[.]238  
> 45[.]142[.]215[.]92  
> 45[.]153[.]230[.]183  
> 45[.]152[.]86[.]98  
> 74[.]119[.]193[.]57  
> 77[.]91[.]74[.]67  
> 146[.]19[.]247[.]28  
> 77[.]91[.]102[.]115  
> 45[.]159[.]251[.]21  
> 146[.]19[.]247[.]52  
> 45[.]142[.]215[.]50  
> 45[.]133[.]216[.]170  
> 193[.]43[.]146[.]22  
> 193[.]43[.]146[.]26  
> 146[.]70[.]124[.]71  
> 193[.]43[.]146[.]17  
> 146[.]19[.]75[.]8  
> 45[.]84[.]0[.]152  
> 45[.]133[.]216[.]249  
> 45[.]67[.]34[.]152  
> 45[.]133[.]216[.]145  
> fullcrack4u[.]com  
> activationskey[.]org  
> xproductkey[.]com  
> saifcrack[.]com  
> crackedpcs[.]com  
> allcracks[.]org  
> aryancrack[.]com  
> prolicensekeys[.]com  
> apps-for-pc[.]com  
> bagas3-1[.]com  
> seostar2[.]xyz  
> keygenwin[.]com  
> cloud27[.]xyz  
> allpcsoftwares[.]info  
> deepprostore[.]com  
> serialfull[.]info  
> steamunlocked[.]one  
> file-store2[.]xyz  
> reallkeys[.]com  
> fullcrackedz[.]com  
> softwaresdaily[.]com  
> officials-kmspico[.]com  
> hotbuckers[.]com  
> mycrackfree[.]com  
> procfullcracked[.]com  
> idmfullcrack[.]info  
> drake4[.]xyz  
> crackedsofts[.]info  
> getintopc[.]digital  
> piratespc[.]net  
> apxsoftwares[.]com  
> crackfullpro[.]com  
> allcrackhere[.]info  
> kuyhaa-me[.]pw  
> crackplaced[.]com  
> freepccrack[.]com  
> proapkcrack[.]com  
> crackfullpc[.]com  
> Free-4paid[.]com  
> crackedlink[.]com  
> crackpropc[.]com  
> cracktube[.]net  
> getmacos[.]org  
> getwindowsactivator[.]info  
> playzipgames[.]co  
> proactivationkey[.]com  
> procrackfree[.]com  
> showcrack[.]com  
> file-store2[.]xyz  
> seostar2[.]xyz  
> drake4[.]xyz  
> cloud27[.]xyz  
> kirov1[.]xyz  
> unixfilesystem2[.]xyz  
> file-store4[.]xyz  
> cloud25[.]xyz  
> clubfiletyc[.]com  
> ihgatms[.]cfd  
> notbeexcluded[.]cfd  
> andslideasco[.]cfd  
> sonarsurveyof[.]cfd  
> butvelocities[.]cfd  
> herihed[.]cfd  
> largerinscale[.]cfd  
> itsdebri[.]cfd  
> lditsdebriisar[.]cfd  
> eeorderso[.]cfd  
> psestwotothr[.]cfd  
> uptomscan[.]cfd  
> fmagnitude[.]cfd  
> byasdebrisfie[.]cfd  
> ticlewesimulate[.]cfd  
> ergyfrommo[.]cfd  
> sup7podthee[.]cfd  
> heirreplacem[.]cfd  
> hthecrown[.]cfd  
> entbymo[.]cfd  
> ctswasprimarilyd[.]cfd  
> adsharedwi897th[.]cfd  
> mershadclo[.]cfd  
> aptersandt[.]cfd  
> nkstherefor[.]cfd  
> iruiotish[.]cfd  
> itishindia[.]cfd  
> theyt786ku[.]cfd  
> theritishind[.]cfd  
> edbythe67ak[.]cfd  
> panyruld[.]cfd  
> uslimsofbr[.]cfd  
> sputrey567rik[.]cfd  
> shatheg[.]cfd  
> istanmove[.]cfd  
> menhichs[.]cfd  
> upta16theu[.]cfd  
> andelect[.]cfd  
> oughtme[.]cfd  
> ionvictoriesin[.]cfd  
> anwasthere[.]cfd  
> ateofakist[.]cfd  
> egiontheh[.]cfd  
> ahthegha[.]cfd  
> mayyadc[.]cfd  
> emodernst[.]cfd  
> almofmultiple[.]cfd  
> ofth546ebr[.]cfd  
> znavidsde[.]cfd  
> mprisesth[.]cfd  
> ionthatco[.]cfd  
> onzeage[.]cfd  
> indush[.]cfd  
> low-lyingwh[.]cfd  
> nalhajarm[.]cfd  
> iesandb[.]cfd  
> helandsca[.]cfd  
> tsofhormuz[.]cfd  
> rhighest[.]cfd  
> rategicstrai[.]cfd  
> undimangen[.]cfd  
> ani453las[.]cfd  
> anceovarec[.]cfd  
> dcommerc[.]cfd  
> condandthi[.]cfd  
> resonherse[.]cfd  
> ordsexecutiv[.]cfd  
> oundandk[.]cfd  
> quezachieve[.]cfd  
> undertheguid[.]cfd  
> domainxnewma[.]com

## 参考来源

> [Zscaler](https://www.zscaler.com/blogs/security-research/making-victims-> pay-infostealer-malwares-mimick-pirated-software-download)


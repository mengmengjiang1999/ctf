本文主要分析了一次非国家性质的针对伊朗基础设施的攻击事件，此次攻击事件虽然发生在伊朗，但他同样可以发生在其他国家城市。接下来我们会对攻击的技术细节进行分析，找到网络攻击事件背后的黑客，并将其与前几年的攻击事件进行关联分析。

## 主要发现

2021年7月9日和10日，伊朗铁路道路与城市发展系统部成为网络攻击的目标。黑客在全国各地车站的信息板上显示火车延误或取消的信息，并敦促乘客拨打电话以获取更多信息，此电话号码属于该国领导人的办公室。

![1630498918_612f706622cea97b38339.png!small?1630498920833](https://image.3001.net/images/20210901/1630498918_612f706622cea97b38339.png!small?1630498920833)

第二天，伊朗道路和城市化部的网站出现“网络中断”后停止服务。

![1630498978_612f70a22079a8f6f781f.png!small?1630498979160](https://image.3001.net/images/20210901/1630498978_612f70a22079a8f6f781f.png!small?1630498979160)

几天后，伊朗网络安全公司 Amnpardaz Software 发布了技术分析，该恶意软件被称为 Trojan.Win32.BreakWin。

此次对伊朗的攻击在战术和技术上与叙利亚私营公司遭到的攻击类似，攻击活动至少从2019年已经开始看，可与自称为政权反对派组织Indra联系起来。攻击者在受害者网络中开发并部署了至少3种不同版本的工具（Meteor、Stardust、Comet）。从工具的质量、运作方式来看，Indra不太可能属于国家层面。

### 攻击流程分析

![1630499318_612f71f6a4cc6790bf6ca.png!small?1630499318183](https://image.3001.net/images/20210901/1630499318_612f71f6a4cc6790bf6ca.png!small?1630499318183)

### 过滤目标机器

setup.bat检查机器是否为：PIS-APP, PIS-MOB, WSUSPROXY,PIS-DB。如果是，它会停止执行并从这台机器中删除恶意脚本文件。

### 下载恶意文件

同一个批处理文件下载名为 env.cab 的 cab
文件：\\\railways.ir\sysvol\railways.ir\scripts\env.cab。特定主机名和内网路径说明攻击者事先了解环境。

### 释放运行工具

update.bat，由 setup.bat 提取并启动，使用密码提取下一个阶段：cache.bat、msrun.bat 和 bcd.bat。

### 断开机网络连接

cache.bat 脚本使用以下命令禁用所有网络适配器："Get-WmiObject -class Win32_NetworkAdapter |
ForEach { If ($.NetEnabled) { $.Disable() } }" > NUL

### 反病毒检查

cache.bat 还会检查计算机上是否安装了卡巴斯基，如果没有，它会将与攻击相关所有文件和文件夹添加到 Windows Defender 排除列表中。

### 破坏引导

bcd.bat 用于破坏引导过程。首先，它尝试覆盖启动文件，然后使用 Windows 内置 BCDEdit 工具删除不同的启动标识符：for /F
"tokens=2" %%j in ('%comspec% /c "bcdedit -v | findstr identifier"') do
bcdedit /delete %%j /f

### 消除痕迹

bcd.bat 还会使用 wevtutil 从系统中删除安全、系统和应用程序事件日志。

### 释放负载

msrun.bat 负责释放
Wiper。它将wiper相关文件移动到“C:\temp”，并创建一个名为mstask的计划任务，在23:55:00执行wiper。

## Wiper分析

攻击主要有效载荷是msapp.exe，其目的是锁定受害者机器并擦除其内容使其停止服务。执行时恶意软件会隐藏此可执行文件的控制台窗口。

配置文件各个字段：

![1630550041_613038193f86f7dd402aa.png!small?1630550040517](https://image.3001.net/images/20210902/1630550041_613038193f86f7dd402aa.png!small?1630550040517)

该工具不是专门为此次攻击创建的，配置解析成功，程序会将字符串“Meteor has
started.”写入加密日志文件。在整执行过程中，它不断将其操作记录到同一个加密日志文件中。

### 感染步骤

首先，使用WinAPI或WMI将计算机从Active
Directory域中删除，使远程修复更加困难。接下来，恶意软件会破坏计算机的启动配置：在Windows
7之前的版本中，恶意软件会覆盖c:\boot.ini文件；在Windows 7及更高版本中，删除BCD条目。最后更改本地用户的密码。

所有操作执行完成后，用户无法获得机器的访问权限。恶意软件禁用Windows屏幕保护程序，然后将桌面壁纸和锁屏图像更改为自定义图像。

![1630550541_61303a0d8a655f7a24359.png!small?1630550541182](https://image.3001.net/images/20210902/1630550541_61303a0d8a655f7a24359.png!small?1630550541182)

完成上述操作后，恶意软件将注销所有用户，并在新线程中执行一个“锁定器”。mssetup.exe将阻止键盘和鼠标设备的输入来阻止用户与机器交互。最后，恶意软件会创建一个计划任务，计划任务将在每次系统启动时执行。

### Wiper功能

首先，wiper恶意软件从遍历config中paths_to_wipe路径下的文件和目录，用零字节填充它们，然后删除它们。擦除后执行：
vssadmin.exe delete shadows /all /quiet **and
**C:\\\Windows\\\system32\\\wbem\\\wmic.exe shadowcopy delete。最后，恶意软件进入无限循环。

## 关联分析

和近期伊朗被攻击的目标进行关联分析发现，攻击流程几乎相同，文件具有相似的结构、相同的名称和相同的功能。但仍然存在一些差异，update.bat脚本没有被早期的样本使用，
执行的是nti.exe—一个基于NotPetya的MBR感染程序。

![1630551189_61303c957592e61d2878b.png!small?1630551188977](https://image.3001.net/images/20210902/1630551189_61303c957592e61d2878b.png!small?1630551188977)

根据目前收集到的信息，需要确定伊朗被攻击目标是否是攻击者第一次使用这些工具。结果发现在叙利亚这些工具被上传到了Virus
Total三次，比最近针对伊朗的攻击早了一年多。这些发现的攻击都是基于VBS脚本，其中还包括了一些攻击目标的身份信息。

![1630551731_61303eb3179535539f2bc.png!small?1630551730423](https://image.3001.net/images/20210902/1630551731_61303eb3179535539f2bc.png!small?1630551730423)

初始有效负载是VBS脚本resolve.VBS，它将受密码保护的RAR提取到C:\\\Program Files\\\Windows
NT\\\Accessories\\\，其中包含另一个RAR文件和三个其他VBS文件。然后按以下顺序运行脚本：

第一个脚本遍历已安装的程序并检查是否安装了卡巴斯基防病毒软件。

第二个脚本首先检查卡巴斯基的avp.exe进程是否正在运行。如果正在运行，它将尝试删除卡巴斯基许可证。

最后一个脚本提取第二阶段RAR文件，并运行可执行文件。

在对叙利亚攻击活动分析中，检查到的多个目标公司：卡特吉集团及其关联公司Arfada Petroleum。

![1630553611_6130460b76d4ef22f4ad3.png!small?1630553610679](https://image.3001.net/images/20210902/1630553611_6130460b76d4ef22f4ad3.png!small?1630553610679)

这些行动背后的组织的身份为“Indra”的组织。事实上，Indra并没有隐瞒他们的身份，而是在多个地方留下了他们的签名。攻击者在受害者锁定的计算机上显示自己的身份，并对袭击卡特吉集团负责。

![1630553758_6130469e40ab5606686e2.png!small?1630553759070](https://image.3001.net/images/20210902/1630553758_6130469e40ab5606686e2.png!small?1630553759070)

所有样本都多次出现字符串“INDRA”。

![1630553792_613046c0a03eb91fc4b38.png!small?1630553791869](https://image.3001.net/images/20210902/1630553792_613046c0a03eb91fc4b38.png!small?1630553791869)

他们在不同的平台上运营多个社交网络账户，包括Twitter、Facebook、Telegram和Youtube。这些账户披露了对上述公司的攻击：

![1630553833_613046e9084d000258920.png!small?1630553832354](https://image.3001.net/images/20210902/1630553833_613046e9084d000258920.png!small?1630553832354)

2019年和2020年针对叙利亚目标的攻击与针对伊朗网络的行动有许多相似之处。比如在工具、战术、技术和程序（TTP）以及攻击的高度针对性方面存在相似之处，因此可以认定Indra应对最近在伊朗的攻击负责。

这些攻击都是针对伊朗相关目标的，无论是2021年伊朗铁路公路部，还是2019年的卡特尔吉、阿尔法达、阿尔法德莱克斯和其他叙利亚公司。Indra的推特清楚地表明，他们的目标是他们认为与伊朗有联系的实体。

他们的攻击流依赖于早期对目标网络的侦察信息。在对伊朗入侵攻击时，攻击者确切地知道他们需要让哪些机器不受影响，以便公开传递他们的信息；此外，他们还可以访问铁路的Active
Directory服务器，该服务器用于传播恶意文件。

## 附录

> md5,sha1,sha256  
> Executables:  
> 5e3e9ac6e280d8f7fa0e29707d32ce63, 6dc64e916faaf7cb26c7019e3d1e9c423550e2bd,
> 6709d332fbd5cde1d8e5b0373b6ff70c85fee73bd911ab3f1232bb5db9242dd4  
> 685632a50d8c514a09882f24165741c3, 864667b969b7b31e8975700c4e9236390a250118,
> d71cc6337efb5cbbb400d57c8fdeb48d7af12a292fa87a55e8705d18b09f516e  
> 04633656756847a79c7a2a02d62e5522, 86e4f73c384d84b6ecd5ad9d7658c1cc575b54df,
> 2aa6e42cb33ec3c132ffce425a92dfdb5e29d8ac112631aec068c8a78314d49b  
> bd5acbbfc5c2c8b284ec389207af5759, c71b6cd6a46494e9132da20a6bacfe0b870a460e,
> 9b0f724459637cec5e9576c8332bca16abda6ac3fbbde6f7956bc3a97a423473  
> Other Artifacts:  
> aad0e2a996a0b1602f5716f1b9615631, acc58db9a430be2a385d046634b26c5f88b839a0,
> 7ad16dab6f066ec559e11ead2d9da8755d03273b1c5d374a3f59dd421c417f5a  
> f034755abb5ba85c7d24660668f8e710, b3f5cc0288dce893cb5b4716f30b535e862dd3e6,
> 0f941dea21337420610164da04fa2c3c929b2685363e79e5b70818cd43b3aa13  
> 8420afcab941d1fdf78acd1795c7119a, b21bde15f12e30f9b8c167716da2d3d46c33f71b,
> b75a962528123df9d773baa86215d9b9c6d0b85bf8364e4e553d7b64a4a9f532  
> e1cd6d256f1eb0670f3149f5beb56ee6, 296c1c077d00eeca273fdb8bd3dc79fd32ed20b4,
> eb5237d56c0467b5def9a92e445e34eeed9af2fee28f3a2d2600363724d6f8b0  
> 8c14e57367fa096afebb94260301ed48, b4fed320516ae5f64bb1e02890e866e0533ee649,
> 62a984981d14b562939294df9e479ac0d65dfc412d0449114ccb2a0bc93769b0  
> 877a992716d13e47a52f4cdf00e51c02, ca942726a3b262b98a5fddb1b2e4734246cdf9cf,
> 2872da0355c441cedba1e5f811e99b56ea5517fe86fdebb4e579a49baf0bdee0  
> 5d70cc279156c425101e51bfa92e61ea, ae4bb25557eaca1ce03ec392b27d2afb712c815a,
> 3099deb8c06fb8d188863f0c861de0c5bef657abdb9920a***1d9e165e495381  
> 73b0bca9d0dfb45492475f39ab54b735, 86194d936776050ca4d7f1236badc9df872122f6,
> 571468214c11e5c76ae524b730b26b02872d8987cc67ce2d7faaabeceb1f5e52  
> 2be09527a2acc1906a4f77d42cae315c, 2dabc8a869dced67b9ce6308628441f826b17d*f,
> 5cd6e3e2c2c7313de5acc5b9a4ca4a7680b0d667951627038e5df348f61aacea  
> 86faa0db5*b4443270c505e561b77eb5, c304aed1735814c4614f5367cb12e9f89ce00a99,
> 8929380c7ea52659e0f7cacfde2e01011b9fb895db0e52cea388db901e1e668f  
> 3cba53cda9ace7ab1a7beeb0f401047d, 0a725efee682999a2a27a827f7abd19b85fdbf27,
> 78a8134a53fa2c541dcc8fbb8a122addf0f855a86dd041bd75ff845c34e43913  
> 20db704469ae59c75a76cf36c84e8d9f, ec65cd56f5c79df62c01ae16e474d8d218f2e957,
> 948febaab71727217303e0aabb9126f242aa51f89caa7f070a3da76c4f5699ed  
> 1d9ae3af3503a087a4f942cacf2a7b75, 706918a9a551e506333fc84e89189b126bff6fd1,
> 74cdb71236c63343428ed61d578a0d048fa9ec46929413726542e2f7e02311ce  
> 6f78d83ef0471cc783e29d8051e24f67, 08727eb2ebcd8e46aff094c611e806df3dba20f9,
> 5553ba3dc141cd63878a7f9f0a0e67fb7e887010c0614efd97bbc6c0be9ec2ad  
> 1551eaf7f1935ec3bcbde64f09c77d4c, b84a60f800bbd06e778ffc09e28abe38b3573903,
> 22627df09a7d68e99f4682d9442755de38c71f53af22c80f92def91823af1466  
> bab43b4e0df5b64ab0f053c813497610, 03e6a0b9afe4346ff0e5bc2c3a4ff05e6a4eb6bd,
> 341e5d7fab4e6b5a16ab2c5***6d00e49b1b3aa214fb930a371637a1813382c6  
> 4c1636d7036a9b4bfea421b25f73691e, 40faadf37fc6bace3a304f572b1f2892e8147820,
> 342fb340dc518faa5811d2b9701f83a14d409310da32e0b8c451a85200e08832  
> db07dd687b32c50a0aa51359fb8cce09, 8249491393ffe07ffb3f987e8199f889579d0826,
> 68e95a3ccde3ea22b8eb8adcf0ad53c7993b2ea5316948e31d9eadd11b5151d7  
> cfb7b988cc5dc257987635646e86172b, dd01819d9ce6853927c000cc8de598d8030ab27c,
> 38a419cd9456e40961c781e16ceee99d970be4e9235ccce0b316efe68aba3933  
> 26f49957eaa56a82ad20492919cc6c22, d7e2e40825e262e4bb884111d7ba13fd867c3c0f,
> 4d994b864d785abccef829d84f91d949562d0af934114b65056315bf59c1ef58  
> 81d3fcbe0dca0f47f780fcf22ebb3f5e, 8531d06c2cc36af8f65f558932e2c09dec4fa3e4,
> 2d35bb7c02062ff2fba4424a267c5c83351405281a1870f52d02f3712a547a22  
> d85a211793e9cb1cb8c24be22c24b30f, 1b90dafc4a34491f64e62d63c82f1b44ca138887,
> 67920ff26a18308084679186e18dcaa5f8af997c7036ba43c2e8c69ce24b9a1a  
> eef87eea468b7ac6055b49dafc86502f, 75bb2bb1ea3cd4b726f5a1bc4fab20edbeb08238,
> ac7dd1048e1705e07e4d21dc25c58441f9eb86b37b9969b423ff6ca241871586  
> 29adef27d040405cd22d5b36aae3e00f, db82ef80f28bdca0821a616a1ba8db1d79287a67,
> e9b70bf93f1b396be02feb35af5445985e3429461b195de881e0483361e57049  
> 6833338cc5a96826cef926703753f10e, 62f36c0eba49ee73d8751e721fdd0acb61ef1304,
> 342070940aa3b46486cb458eb13545101b49d4eebe2c93c608948dbb7ce463bc  
> bfb51ec459eaafb7a50ee646d49ecd4d, 579330d75f5fce52b1bab475bd77cf347fc404e4,
> f8139c0f5bab5d7b1624f1ac55e84d451fe1fa01f2903f269f56e5bfa3a40548

> C&C servers:
>
> 68.183.79.77  
> 167.172.177.158  
> 139.59.89.238  
> 172.105.42.64

## 原文链接

> [research.checkpoint](https://research.checkpoint.com/2021/indra-hackers-> behind-recent-attacks-on-iran/)


**译者：知道创宇404实验室翻译组**  
**原文链接：<https://seguranca-informatica.pt/threat-analysis-the-emergent-ursa-trojan-impacts-many-countries-using-a-sophisticated-loader/#.X2LUXWgzbIV>**

## 前言

2020年6月以来，新一波URSA木马程序（ESET称之为mispadu恶意软件）已影响到多个国家的用户，包括玻利维亚、智利、墨西哥、阿根廷、厄瓜多尔、秘鲁、哥伦比亚、巴拉圭、哥斯达黎加、巴西、西班牙、意大利和葡萄牙。此软件是恶意木马，当安装在受害者的设备上时，它从浏览器和流行软件（如FTP和电子邮件服务）收集密码，并执行银行浏览器覆盖，以诱使受害者介绍银行凭证，这些流程由攻击者在后台逐步执行。

下表1显示了2020年6月至9月中旬全球感染数量的地理分布。
![](https://images.seebug.org/content/images/2020/09/5b83abf1-34c6-4e6c-b694-ad8a1f1c91b3.png-w331s)
表1:URSA木马——2020年6月至9月中旬按国家分列的感染情况。

从一些C2s获得的数据可以看出，从2020年6月到9月中旬，共有3379名用户受到该威胁的影响。墨西哥共有1977例，是受感染人数最多的国家，其次是西班牙631例，葡萄牙514例，智利331例。

实际感染的数量可能要比上面高得多，因为这些指标只与文章末尾部分C2s中存在的数据有关。

### URSA木马如何传播

URSA恶意软件是一种相对较新的木马程序，旨在窃取受害者机器的凭证，并在受害者访问其家庭银行门户网站时创建银行覆盖窗口。URSA通过社会工程模式传播，即网络钓鱼/恶意欺诈活动。在葡萄牙，这种威胁已经在野外传播，并冒充了四个受欢迎的组织，即沃达丰、EDP（葡萄牙能源公司）、MEO（Serviços
de Comunicaões e Multimédia，S.A）和Polícia Judicíaria——葡萄牙负责刑事调查的警察组织之一。

电子邮件通常是通过过期发票诱使受害者下载恶意文件（从互联网下载的.zip文件）来进行影响用户的。这些电子邮件通常在每个月底和月初之间发送。

![](https://images.seebug.org/content/images/2020/09/eb4041e9-6523-449b-a52b-4fa00dadb734.png-w331s)
图1：URSA模仿沃达丰、EDP和Polícia Judíciaria的电子邮件模板-葡萄牙。

### URSA装载细节分析

乍一看，通过电子邮件诈骗犯罪分子发送的恶意URL下载的文件是一个zip文件，里面有一个MSI（微软安装程序）。通过分析MSI文件，可以观察到另一个文件在内部可用，并且可能在MSI执行时被删除。名为px3q8x.vbs的文件是一个VBscript文件，负责加载和执行下一个阶段。有趣的是，这个文件有一个低检测率绕过。

> 威胁名称：554S2000A2S144D1S4111D.zip  
>  MD5:2d2f3500836ed60303103bafac6357a3  
>  威胁名称：554S2000A2S144D1S4111D.msi  
>  MD5:3be539aa8d421d09cef27723a98d2d83  
>  威胁名称：px3q8x.vbs (initial payload – VBScript)  
>  MD5: a4f066196b1009c42c1dea74f857180d

![](https://images.seebug.org/content/images/2020/09/0bf2bda8-6201-4dad-bbb6-fbc8760015ba.png-w331s)
图2:MSI文件中包含另一个文件–名为px3q8x.vbs的VBScript–Ursa木马VBScript加载程序。

在本文中，我们可以看到URSA木马有两个加载程序。首先是VBScript加载程序，然后是几轮模糊处理和兔子洞。最后VBScript负责启动和删除磁盘上的文件，并执行AutoIt加载程序/注入器。该二进制文件通过进程注入技术将一些DLL注入内存，包括与银行覆盖窗口相关的Delphi二进制文件，以及与C2服务器建立所有通信的DLL。

下图显示了URSA木马程序工作原理的高级图表。

![](https://images.seebug.org/content/images/2020/09/3007239a-22b6-4e60-a44a-77d6ce4f9897.png-w331s)
图3:URSA木马/Mispadu 2020-高级图表。

### VBScript

在提取VBscript加载程序之后，我们发现它非常混乱，如图4所示。

![](https://images.seebug.org/content/images/2020/09/fb417979-ca61-4155-9617-e05e4b86d918.png-w331s)
图4:URSA VBScript加载程序-代码模糊化以绕过AV并使其难以分析。

几轮之后，我们得到了一个更可读的版本。注意，一些与无用代码相关的部分被删除了。具体来说，VBscript分为两部分。第一部分是Installer对象的方法，该方法返回一个新的记录对象，其中包含请求的字段数（下面突出显示的代码）。

![](https://images.seebug.org/content/images/2020/09/648dee47-d7b8-4861-a68b-64ce11b2fa5d.png-w331s)
图5:URSA加载程序VBScript分析-第一部分-记录对象部分。

第二部分是下一个有效载荷编码的代码。然后执行该有效载荷，并负责解码另一个有效载荷（图5–步骤5中的第二个有效载荷）。

![](https://images.seebug.org/content/images/2020/09/40d36ad2-3d25-4fc2-b098-ee2df61f123a.png-w331s)
图6:URSA加载程序VBScript分析-第二部分-有效负载2。

这个新的有效载荷（在去除代码并重命名一些函数和变量之后）是另一个VBScript，最后一个有效载荷从C2服务器请求下一个阶段。

![](https://images.seebug.org/content/images/2020/09/872917bc-54e3-42ca-968d-a626c7242aa1.png-w331s)
图7：分析URSA加载程序VBScript—第三部分—有效负载3—步骤8。

![](https://images.seebug.org/content/images/2020/09/a0a94fec-969a-4cd2-8ad0-546961546c96.png-w331s)
图8：从C2下载下一个恶意软件阶段时的网络流量。

最后，我们得到了c2ip地址（191.235.99.]13）和本阶段来自C2服务器的最终有效负载。

### URSA木马程序–VBscript加载程序/删除程序（最终的VBscript）

> 威胁名称：最终有效载荷（VBScript）  
>  MD5:bda287c97d9373052f347ac0ccedfdf8

在经历了几次兔子洞之后，我们终于从C2服务器上完全除掉了URSA
VBScript加载程序。只需对恶意软件配置进行加密，C2服务器和特洛伊木马客户端之间的所有通信都是使用相同的算法执行的，即使是在这个恶意软件的最后阶段——一个Delphi
PE文件，负责创建银行覆盖窗口，从受害者的机器收集凭证，并将所有数据发送到C2在线。

![](https://images.seebug.org/content/images/2020/09/bbe620c8-e3a5-42c6-a7b1-087d444f5c92.png-w331s)
图9:URSA最终VBScript加载程序及其配置。

从图9中，我们可以观察到以下内容：

  * 来自C2服务器的一些路径（SRoleX和sRoleXW2）。
  * 从C2下载二进制文件到（cRaiz1）的路径。
  * 一些用于构建最终阶段的部分（一个AutoIT二进制文件，负责将恶意软件final stage注入并执行到内存中，即所提到的Delphi文件）。

如前所述，恶意软件和C2服务器之间的所有通信都是加密的。为了解密恶意软件通信，我们可以使用GitHub上的下一个脚本。

通过执行脚本，可以解密恶意软件配置，如下所示。

![](https://images.seebug.org/content/images/2020/09/0b181020-2a2f-431c-b72d-e2e75f48990c.png-w331s)
图10:Ursa木马配置解密。

变量“#wp#”是在恶意软件执行期间发送受害者信息的最终C2端点。同时，还发现了几种寄主重复。这是一个潜在的C2，当一个新的受害者受到影响时会通知攻击者。尽管如此，下一阶段的恶意软件是从IP地址（191.235.99.]13）下载的，如上所述。

在VBScript代码分析过程中，发现了一些函数：

    
    
    Function GetWmiPropertyValue(strNameSpace, strClassName, strPropertyName)
    function crypt(cText, cCod) 
    function decrypt(cText, cCod)
    Function UnZip(ZipFile, ExtractTo)
    Function StringGetURL(sUrl)
    Function BinaryGetURL(strURL)
    Function StringGetURL(strURL)
    Function SaveBinaryData(arrByteArray, strFileName)
    Sub writeBinary(bstr, path)
    Function makeArray(n) ' Small utility function
    Function TrocaEntry(strFileName1, strFileName, sSenhaVelha, sSenhaNova)
    function cr1pt(x, c)

一般来说，下一个恶意软件阶段分几个部分从C2服务器检索，然后动态构建。这些文件在恶意软件执行期间被加密和解密。接下来，在这个过程中生成一个最终的PE文件。下面介绍一些有趣的函数。值得注意的是，用于下载文件的用户代理是：“strusagentstring=“binary-getter/1.0””。

![](https://images.seebug.org/content/images/2020/09/74a9ea55-9c13-43d3-853f-ba246acc4b6d.png-w331s)
图11:VBScript文件的一些部分和函数。

在受害者启动下一个阶段后，对其进行初步验证，然后将检索操作系统（OS）版本，如果是虚拟环境，则脚本将终止其执行。按照这个逻辑，最终的有效载荷就不会从C2上加载和下载，这使得它至少不会被防病毒引擎标记。

![](https://images.seebug.org/content/images/2020/09/4e758f0f-619a-4016-a1ca-6a1794f28e45.png-w331s)
图12:URSA加载程序上发现的反VM技术。

接下来，脚本验证受害者设备是否位于攻击者定义的目标位置，即：

  * Spanish – Spain (Traditional) 1034
  * Portuguese – Brazil – 1046
  * Spanish – Mexico – 2058
  * Portuguese – Portugal – 2070
  * Spanish – 58378, 3082

![](https://images.seebug.org/content/images/2020/09/c86917c6-a030-4231-9ea1-b3e292ae4cef.png-w331s)
图13：受URSA恶意软件影响的目标位置。

如果受害者的计算机以不同于硬编码的语言ID执行，或者计算机名等于“JOHN-PC”，则感染过程停止。将计算机名改为“JOHN-PC”是避免URSA感染的潜在杀手锏。

此时，下一阶段从C2服务器下载。这些文件存储在C:\Users\Public文件夹（tmp文件）中，然后移动到在C:\驱动器上创建的随机文件夹中。此文件夹的名称基于计算机名。

![](https://images.seebug.org/content/images/2020/09/b3e2d693-d953-49f8-a1f2-b271790072a8.png-w331s)
图14：从C2服务器下载下一个二进制文件（AutoIT–injector/loader）和URSA木马（一个注入内存的Delphi二进制文件）。

在此过程中，还下载了另外两个dll。一个是SSL的DLL，另一个是SQLite3的DLL。它们可能是恶意软件中打包的依赖项，如果目标计算机上没有安装这些DLL/资源，则可以避免失败。我们将观察到最终的二进制文件——ursadelphi——里面有两个工具并打包了。这些工具是在凭证获取过程中使用的合法软件。

在这个复杂的过程之后，最后的文件被移到C:\“artibrary_name”文件夹中。

![](https://images.seebug.org/content/images/2020/09/e9a9a820-2eb0-437f-9007-b76d4b92cd0a.png-w331s)
![](https://images.seebug.org/content/images/2020/09/6697d6a9-cefc-47eb-b02a-f17145f29896.png-w331s)
图15:Final stage被移动到在C:\（本例中为o0t）上创建的随机文件夹中。

接下来，执行另一个加载器/注入器，AutoIT文件。它负责将最终有效负载（包含木马代码和恶意进程的Delphi文件）加载到内存中。

![](https://images.seebug.org/content/images/2020/09/8668a580-f91e-471e-9aba-05c31c3c2b94.png-w331s)
图16：执行最终有效载荷。

Ursa木马程序–AutoIT loader/injector

> 威胁名称：n11ai.exe  
>  MD5:c56b5f0201a3b3de53e561fe76912bfd  
>  威胁名称：n111.11n  
>  MD5:7396051fd6575180166d66ddf0a9295b  
>  威胁名称：winx86.dll  
>  MD5:87f9e5a6318ac1ec5ee05aa94a919d7a  
>  威胁名称：libeay32.dll  
>  MD5:f3e6c0d52bab27289db2a70e4aab628c  
>  威胁名称：n11  
>  MD5:71fdf07084a741b553b97b0d0815fa0e

AutoIT二进制文件受保护，可以使用GitHub上的以下脚本进行反编译。该脚本是myAut2Exe的一个构建版本，它是在2.12版本的基础上修改而来的。

![](https://images.seebug.org/content/images/2020/09/c130cd08-98b9-403b-afec-5ec8c6ab5b90.png-w331s)
图17:AutoIT反编译代码（n11ai.exe).

如前所述，为了执行进程注入技术，从kernel32.dll导入了一些调用。

    
    
    LOCAL $KERNELHANDLE=DLLCALL($_MDKERNEL32DLL,"ptr","LoadLibrary","str","kernel32.dll")
    
    $_MFHOOKBAK=DLLSTRUCTCREATE("ubyte[7]")
    DLLCALL($_MDKERNEL32DLL,"int","WriteProcessMemory","ptr",-1,"ptr",DLLSTRUCTGETPTR($_MFHOOKBAK),"ptr",$_MFHOOKPTR,"uint",7,"uint*",0)
    DLLCALL($_MDKERNEL32DLL,"int","WriteProcessMemory","ptr",-1,"ptr",$_MFHOOKPTR,"byte*",184,"uint",1,"uint*",0)
    DLLCALL($_MDKERNEL32DLL,"int","WriteProcessMemory","ptr",-1,"ptr",$_MFHOOKPTR+5,"ushort*",57599,"uint",2,"uint*",0)

具体来说，文件n111.11n是导入的dll之一–Delphi
PE文件。根据传递的参数注入所有DLL文件。这些命令在图17中VBScript加载程序的末尾执行。

    
    
    "C:\o0t\n11ai.exe" n11 @
    "C:\o0t\n11ai.exe.exe" n11 ##1
    "C:\o0t\n11ai.exe.exe" /stext "WWy1"
    "C:\o0t\n11ai.exe.exe" n11 ##3
    "C:\o0t\n11ai.exe.exe" /stext "WWy0"

在细节上，这个自动装载机按部件加载恶意软件，即：

  * n11@–AutoIT内部的DLL，用于将Delphi二进制文件加载到内存中。
  * n11/stext“WWy1”–执行从浏览器收集密码的模块。
  * n11/stext“WWy0”–执行从流行软件（FTP、email等）收集凭据的模块。

![](https://images.seebug.org/content/images/2020/09/e43e984c-1fb7-4a3c-b976-ee195493b106.png-w331s)
图18：注入内存的DLL（Delphi二进制文件和其他）。

另一方面，这两个dll似乎引用SSL和SQLite3，它们可能是执行delphipe文件（winx86.dll和libeay32.dll）中可用工具的依赖项。

![](https://images.seebug.org/content/images/2020/09/4a19e112-f9b3-4bf9-a68f-c6db1de177c1.png-w331s)
图19:dll存储在AutoIT二进制文件的同一路径中（Delphi加载程序）。

挖掘URSA的最后阶段（Delphi木马）

> 威胁名称：36f0000.rec.dll (extracted from memory)  
>  MD5:309335fe1e4f27029a8ec6087e0de1f4

最后一个阶段是一个Delphi二进制文件，负责执行浏览器覆盖来控制和窃取受害者访问其家庭银行门户网站的数据。这里观察到的活动和代码相似性与在葡萄牙和拉丁美洲运行的其他经过分析和流行的木马非常接近，例如Grandoreiro和Lampion[1,2]。根据ESET的分析，最终的有效载荷是Mispadu，一种雄心勃勃的拉丁美洲银行业木马，它将攻击面扩展到web浏览器。

Delphi二进制文件中还有两个合法的工具。这些工具用于收集存储在受害者设备上的凭据。

![](https://images.seebug.org/content/images/2020/09/33cbf1de-dc81-49cd-bb4f-0331d09209ba.png-w331s) 图20:Delphi二进制文件中可用的二进制文件。

这些工具在最后阶段开始时执行，数据存储在下面突出显示的标记“F1”和“F2”之间。

![](https://images.seebug.org/content/images/2020/09/1acc1f28-17bf-495c-9bfd-2c58c3217005.png-w331s)
图21：执行凭证窃取模块的代码块。

具体来说，这些工具是合法的，来自Nir-Sofer。第一个是在内存中启动WebBrowserPassView，用于从流行的web浏览器中过滤凭证。另一方面，Mail
PassView用于从多个位置收集数据。

![](https://images.seebug.org/content/images/2020/09/4a4210bd-6d01-4ee0-8778-aa6c3b89f8e8.png-w331s)
图22：嵌入在木马文件中并用于从受感染设备收集数据的工具。

在快结束时，数据被发送到C2服务器。

![](https://images.seebug.org/content/images/2020/09/5acb341f-f63b-4d05-ba91-bdcefdf10fcd.png-w331s)
![](https://images.seebug.org/content/images/2020/09/6a620f30-916d-477e-9fbf-fc67c98d4596.png-w331s) 图23：收集受害者的凭证并发送到C2服务器。

木马同时监听和监视受害者访问的窗口和网站（它将焦点窗口放在web浏览器上）。访问目标银行门户时，将根据访问的银行门户在合法的web浏览器窗口上创建覆盖窗口。
简而言之，下一个数字显示了一些目标银行被URSA木马攻击者“操纵”情况。

![](https://images.seebug.org/content/images/2020/09/96cefdf2-35d8-4698-bd48-1c448ec53198.png-w331s)
图24:URSA木马攻击者运营的目标银行组织。

完整的列表可以在下面找到。

    
    
    .text:039E67D0 00000010 unicode BMSC_BO          
    .text:039E67EC 0000001C unicode BANCOUNION_BO    
    .text:039E6814 0000000E unicode BNB_BO           
    .text:039E6830 00000010 unicode BISA_BO          
    .text:039E684C 0000000E unicode BCP_BO           
    .text:039E6868 00000014 unicode FASSIL_BO        
    .text:039E6888 00000018 unicode BANCOFIE_BO      
    .text:039E68AC 00000018 unicode BANCOSOL_BO      
    .text:039E68D0 0000000C unicode BG_BO            
    .text:039E68E8 00000014 unicode BANECO_BO        
    .text:039E6908 0000001A unicode CORPBANCA_CH     
    .text:039E6930 00000010 unicode BBCA_CH          
    .text:039E694C 00000024 unicode BANCOFALABELLA_CH
    .text:039E697C 00000020 unicode BANCOEDWARDS_CH  
    .text:039E69A8 0000001E unicode BANCORIPLEY_CH   
    .text:039E69D4 00000018 unicode TBANCWLS_CH      
    .text:039E69F8 00000014 unicode BANEFE_CH        
    .text:039E6A18 0000001C unicode SCOTIABANK_CH    
    .text:039E6A40 00000010 unicode BICE_CH          
    .text:039E6A5C 0000001C unicode BANCOINTER_CH    
    .text:039E6A84 00000024 unicode BANCOCONSORCIO_CH
    .text:039E6AB4 00000010 unicode BITCOIN          
    .text:039E6AD0 0000000E unicode PAYPAL           
    .text:039E6AEC 00000014 unicode BANKIA_ES        
    .text:039E6B0C 00000018 unicode SABADELL_ES      
    .text:039E6B30 0000001A unicode BANKINTER_ES     
    .text:039E6B58 00000018 unicode IBERCAJA_ES      
    .text:039E6B7C 0000001A unicode LIBERBANK_ES     
    .text:039E6BA4 00000014 unicode ABANCA_ES        
    .text:039E6BC4 0000001C unicode KUTXABANCA_ES    
    .text:039E6BEC 00000016 unicode UNICAJA_ES       
    .text:039E6C10 00000012 unicode GERAL_PT         
    .text:039E6C30 0000000E unicode BPI_PT           
    .text:039E6C4C 0000001A unicode NOVOBANCO_PT     
    .text:039E6C74 0000000E unicode BCP_PT           
    .text:039E6C90 0000000E unicode CGD_PT           
    .text:039E6CAC 00000014 unicode ACTIVO_PT        
    .text:039E6CCC 00000018 unicode MONTEPIO_PT      
    .text:039E6CF0 0000001C unicode CREDITOAGR_PT    
    .text:039E6D18 0000000E unicode BPM_IT           
    .text:039E6D34 00000010 unicode BPER_IT          
    .text:039E6D50 00000016 unicode UNICRED_IT       
    .text:039E6D74 00000018 unicode SAMPAOLO_IT      
    .text:039E6D98 0000000E unicode BNL_IT           
    .text:039E6DB4 00000018 unicode BANCAMPS_IT      
    .text:039E6DD8 0000001A unicode SANTANDER_CH     
    .text:039E6E00 0000001A unicode SANTANDER_ES     
    .text:039E6E28 00000010 unicode BBVA_ES          
    .text:039E6E44 0000001A unicode CAIXABANK_ES     
    .text:039E6E6C 0000001A unicode SANTANDER_PT     
    .text:039E6E94 00000010 unicode BBVA_MX          
    .text:039E6EB0 00000014 unicode AZTECA_MX        
    .text:039E6ED0 00000016 unicode BANAMEX_MX       
    .text:039E6EF4 00000016 unicode BANORTE_MX       
    .text:039E6F18 00000012 unicode SANTA_MX         
    .text:039E6F38 00000010 unicode HSBC_MX          
    .text:039E6F54 00000014 unicode SCOTIA_MX        
    .text:039EA11C 0000000A unicode bbva                    
    .text:039EA134 0000000A unicode xico                    
    .text:039EA15C 00000008 unicode 99_                     
    .text:039EA170 00000006 unicode 99                      
    .text:039EA184 0000000A unicode BBVA                    
    .text:039EA1AC 0000000C unicode banco                   
    .text:039EA1C4 0000000E unicode azteca                  
    .text:039EA1E0 0000001A unicode Banco Azteca            
    .text:039EA208 0000001C unicode banconacional           
    .text:039EA230 00000010 unicode agrcola                 
    .text:039EA24C 00000032 unicode Banco Nacional de México
    .text:039EA28C 00000010 unicode banorte                 
    .text:039EA2A8 00000010 unicode Banorte                 
    .text:039EA2C4 00000014 unicode santander               
    .text:039EA2E4 0000001E unicode bancadeempresa          
    .text:039EA310 0000000C unicode mxico                   
    .text:039EA328 00000012 unicode gobierno                
    .text:039EA348 0000000A unicode pyme                    
    .text:039EA360 00000020 unicode Banco Santander         
    .text:039EA38C 00000014 unicode caixabank               
    .text:039EA3AC 00000008 unicode bpi                     
    .text:039EA3C0 00000014 unicode CaixaBank               
    .text:039EA3E0 00000016 unicode scotiabank              
    .text:039EA404 0000000E unicode Scotia                  
    .text:039EA420 0000000A unicode hsbc                    
    .text:039EA438 0000000A unicode HSBC                    
    .text:039EA450 0000000A unicode solu                    
    .text:039EA468 00000010 unicode advance                 
    .text:039EA484 00000012 unicode investor                
    .text:039EA4A4 00000012 unicode Santader                
    .text:039EA4C4 00000016 unicode blockchain              
    .text:039EA4E8 00000010 unicode bitcoin                 
    .text:039EA504 00000010 unicode binance                 
    .text:039EA520 00000012 unicode coinbase                
    .text:039EA540 0000000E unicode kraken                  
    .text:039EA55C 0000000E unicode crypto                  
    .text:039EA578 00000012 unicode primebit                
    .text:039EA598 0000000C unicode bitso                   
    .text:039EA5B0 0000000E unicode paypal                  
    .text:039EA5CC 0000000E unicode bankia                  
    .text:039EA5E8 0000001C unicode bancosabadell           
    .text:039EA610 00000014 unicode bankinter               
    .text:039EA630 00000012 unicode ibercaja                
    .text:039EA650 00000014 unicode liberbank               
    .text:039EA670 0000000E unicode abanca                  
    .text:039EA68C 00000014 unicode kutxabank               
    .text:039EA6AC 0000001A unicode unicajabanco            
    .text:039EA6D4 00000012 unicode bancobpi                
    .text:039EA6F4 00000014 unicode novobanco               
    .text:039EA714 0000001C unicode millenniumbcp           
    .text:039EA73C 0000001A unicode caixadirecta            
    .text:039EA764 00000016 unicode activobank              
    .text:039EA788 00000012 unicode montepio                
    .text:039EA7A8 00000014 unicode crditoagr               
    .text:039EA7C8 0000002C unicode bancapopolaredemilano   
    .text:039EA800 00000012 unicode bancobpm                
    .text:039EA820 0000000A unicode bper                    
    .text:039EA838 00000014 unicode unicredit               
    .text:039EA858 00000010 unicode banking                 
    .text:039EA874 00000028 unicode bancaintesasanpaolo     
    .text:039EA8A8 00000008 unicode bnl                     
    .text:039EA8BC 0000000C unicode banca                   
    .text:039EA8D4 00000012 unicode bancamps

在恶意软件分析过程中，我们得到了一些有趣的覆盖窗口。更多的细节和完整的图片在文章的最后展示。

![](https://images.seebug.org/content/images/2020/09/a61393b5-5112-485d-ac62-45229568159a.png-w331s)
图25:URSA木马的银行覆盖窗口。

当恶意软件检测到受害者访问了一个目标银行门户时，就会建立到恶意软件运营商（C2服务器）的套接字连接。攻击者控制着每一步，在后台门户中一步一步地请求特定数据。图26显示了恶意软件中硬编码的一些命令。

![](https://images.seebug.org/content/images/2020/09/62ad9322-2f35-4649-a7a6-745820ec68aa.png-w331s)
图26:URSA木马的内部命令。

### 指挥控制中心的细节和受害者的数据

在恶意软件执行期间，受害者的数据被发送到C2。在我们的分析过程中，我们有可能收集到在这波浪潮（6月至9月中旬）中受影响的受害者人数的信息，以及从受害者设备中过滤出的所有数据。

![](https://images.seebug.org/content/images/2020/09/df623aeb-46b8-4ffa-963f-e9761fba099c.png-w331s)
图27：一些受影响的用户和安装并运行在受感染设备中的AV引擎。

有趣的是，至少在收集凭证的阶段，这个恶意软件逃避了AV检测。我们可以在图28中看到，许多受影响的计算机正在运行流行的防病毒软件，并受到这种威胁的感染。所有的数据都存储在另一侧的服务器上。文件以id语言（Portugal
– 2070）开头，后跟计算机名、木马编译id，最后是C2数据库中的受害者id。

![](https://images.seebug.org/content/images/2020/09/b4317cd6-5514-45f1-9a67-4426407c8b0d.png-w331s)
图28:Ursa木马-受害者的详细信息。

本文中最初提到的地理地图是基于以下可用的C2s，并基于在那里发现的可用感染的数量。

### URSA木马–银行覆盖窗口

![](https://images.seebug.org/content/images/2020/09/2fe4f73f-ab7e-4fa1-b32d-89522cae1f54.png-w331s)
![](https://images.seebug.org/content/images/2020/09/62edc70c-7953-4b81-819f-3987da8017fc.png-w331s)
![](https://images.seebug.org/content/images/2020/09/5a4c875c-492d-4ea4-b9fd-d7119b9df6ab.png-w331s)
![](https://images.seebug.org/content/images/2020/09/aae195fd-e8e1-4112-a3aa-29f6f7934b14.png-w331s)
![](https://images.seebug.org/content/images/2020/09/5c5965af-3a86-4ecf-b06d-ce0ed096f3bc.png-w331s)
![](https://images.seebug.org/content/images/2020/09/3d3c6ca4-3d33-4960-abd0-fd5d2e5d522b.png-w331s)

### IOCs

    
    
    ---- Phishing URLs Portugal #0xSI_f33d --- 
    hxxps://medeiros-boatworks.]com/wp-content/!/https:/my.vodafone.pt/?client=xxx
    hxxps://publichealth.msu.ac.]th/eng/wp-content/languages/--/my.vodafone.pt/?client=xxx
    hxxps://kresna.co.]id/sarikresnakimia/wp-content/!/www.edp.pt/?client=xxx
    hxxps://robyn-plombier-chauffagiste.fr/wp-admin/css/--/https:/www.policiajudiciaria.pt/?cliente=xxxx
    
    ---- URLS -----    hxxp://191.235.99.]13/lp1a.php
    hxxp://191.235.99.]13/m/

#### \---- C2 -----
191.235.99.]13（[ZoomEye搜索结果](https://www.zoomeye.org/searchResult?q=191.235.99.13
"ZoomEye搜索结果")）  
52.91.227.]152（[ZoomEye搜索结果](https://www.zoomeye.org/searchResult?q=52.91.227.152
"ZoomEye搜索结果")）  
87.98.137.]173（[ZoomEye搜索结果](https://www.zoomeye.org/searchResult?q=87.98.137.173
"ZoomEye搜索结果")）  
144.217.32.]24（[ZoomEye搜索结果](https://www.zoomeye.org/searchResult?q=144.217.32.24
"ZoomEye搜索结果")）  
51.81.104.]17（[ZoomEye搜索结果](https://www.zoomeye.org/searchResult?q=51.81.104.17
"ZoomEye搜索结果")）  
104.44.143.]28（[ZoomEye搜索结果](https://www.zoomeye.org/searchResult?q=104.44.143.28
"ZoomEye搜索结果")）  
51.143.39.]80（[ZoomEye搜索结果](https://www.zoomeye.org/searchResult?q=51.143.39.80
"ZoomEye搜索结果")）  
45.132.242.]89（[ZoomEye搜索结果](https://www.zoomeye.org/searchResult?q=45.132.242.89
"ZoomEye搜索结果")）  
13.58.123.]122（[ZoomEye搜索结果](https://www.zoomeye.org/searchResult?q=13.58.123.122
"ZoomEye搜索结果")）  
51.222.39.]127（[ZoomEye搜索结果](https://www.zoomeye.org/searchResult?q=51.222.39.127
"ZoomEye搜索结果")）  
66.70.237.]175（[ZoomEye搜索结果](https://www.zoomeye.org/searchResult?q=66.70.237.175
"ZoomEye搜索结果")）  
54.233.78.]131（[ZoomEye搜索结果](https://www.zoomeye.org/searchResult?q=54.233.78.131
"ZoomEye搜索结果")）  
51.222.39.]128（[ZoomEye搜索结果](https://www.zoomeye.org/searchResult?q=51.222.39.128
"ZoomEye搜索结果")）  
54.39.33.]188（[ZoomEye搜索结果](https://www.zoomeye.org/searchResult?q=54.39.33.188
"ZoomEye搜索结果")）

### 联机沙盒URL

554S2000A2S144D1S4111D.msi:  
<https://www.virustotal.com/gui/file/23892054f9494f0ee6f4aa8749ab3ee6ac13741a0455e189596edfcdf96416b3/details>

px3q8x.vbs initial VBScript:  
<https://www.virustotal.com/gui/file/d1fb8a5061fc40291cc02cec0f1c2d13168b17d22ffcabea62816e14ed58e925/>

final payload (VBScript):  
<https://www.virustotal.com/gui/file/5b91c8acffe1980653718a493e24bde7211ee825ea2947df54c03e9733d61a70/details>

n11ai.exe (AutoIt loader/injector):  
<https://www.virustotal.com/gui/file/237d1bca6e056df5bb16a1216a434634109478f882d3b1d58344c801d184f95d/details>

6f0000.dll (Delphi trojan):  
<https://www.virustotal.com/gui/file/93488eab403fafb3d8e10d38c80f0af745e3fa4cf26228acff24d35a149f6269/detection>

Samples MalwareBazaar:  
<https://bazaar.abuse.ch/browse/tag/URSA%20trojan/>

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1338/>


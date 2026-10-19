**作者：[启明星辰ADLab](https://mp.weixin.qq.com/s/KAbrmrFe41tDYHkHfsK-mQ
"启明星辰ADLab")**

#### 漏洞描述

2018年8月27日，安全研究人员在Twitter上披露了Windows
10系统中的一个0day漏洞。该漏洞是一个本地提权漏洞，存在于Windows的任务调度服务中，允许攻击者从USER权限提权到SYSTEM权限。微软官方目前还没有提供相应的补丁。

#### 漏洞影响范围

Windows 10  
Windows Server 2016

#### 漏洞分析

Microsoft
Windows系统的任务调度服务中高级本地过程调用（ALPC）接口存在本地提权漏洞，该漏洞存在于`schedsvc.dll`模块中的`SchRpcSetSecurity`函数，`SchRpcSetSecurity`函数定义如下，函数功能是设置安全描述符。

    
    
     HRESULT SchRpcSetSecurity(
       [in, string] const wchar_t* path,
       [in, string] const wchar_t* sddl,
       [in] DWORD flags
     );

`SchRpcSetSecurity`第一个参数为路径path，第二个参数为安全描述符定义语言 (SDDL)
字符串sddl，该函数内部调用了`SetSecurity::RpcServer`函数。

![](https://images.seebug.org/content/images/2018/08/b7f8bfd3-6cae-4ae3-8ceb-7ba15ce6dbb5.png-w331s)

`SetSecurity::RpcServer`函数首先调用`ConvertStringSecurityDescriptorToSecurityDescriptor`
将`SchRpcSetSecurity`函数传入的sddl字符串转换为安全描述符`SecurityDescriptor`。并调用`TaskPathCanonicalize`函数对传入path参数路径规范化为Dst。

![](https://images.seebug.org/content/images/2018/08/2e06ec00-ec4f-4792-b4e4-6fafc11453ae.png-w331s)

然后获取Dst路径的JobSecurity安全描述符`pSecurityDescriptor`，继而调用`JobSecurity::Update`函数，传入`SecurityDescriptor`参数，更新`pSecurityDescriptor`。

![](https://images.seebug.org/content/images/2018/08/133c8c1f-5740-48a5-a208-333b06c302c9.png-w331s)

![](https://images.seebug.org/content/images/2018/08/039303da-2231-42bd-a33b-bfe7f86ee16e.png-w331s)

最后，调用`JobSecurity::AddRemovePrincipalAce`函数设置DACL。

![](https://images.seebug.org/content/images/2018/08/22e05403-e717-41d0-99ad-53f3cd5642f4.png-w331s)

![](https://images.seebug.org/content/images/2018/08/44a8fcbd-e4ab-443f-96d9-0ba44e8789ae.png-w331s)

![](https://images.seebug.org/content/images/2018/08/4429f943-7c44-41e7-978a-203fc7799216.png-w331s)

那么如何修改指定目标文件的DACL属性呢？首先，使用`ZwSetInformationFile`函数为目标文件创建硬链接。然后，调用`_SchRpcSetSecurity`函数设置硬链接文件的DACL，等同于修改目标文件的DACL。通过设置SchRpcSetSecurity的第3个参数，可以为用户Administrators(BA)、Authenticated
Users（AU）添加对硬链接文件的写入权限。

以`PrintConfig.dll`文件为例，调用`SchRpcSetSecurity`函数前，文件访问权限如下，此时Administrators不具有对文件的写入权限。

![](https://images.seebug.org/content/images/2018/08/e904746d-88e9-460b-bcc1-9a3b42a6fa78.png-w331s)

调用`SchRpcSetSecurity`函数后，文件的权限如下，此时Administrators和Authenticated
Users都拥有对文件写入权限。

![](https://images.seebug.org/content/images/2018/08/63fdff47-e7a6-40de-9bff-440046da8b65.png-w331s)
![](https://images.seebug.org/content/images/2018/08/b5e13d99-576d-41ec-b245-a89bd493593b.png-w331s)

由于`SchRpcSetSecurity`函数存在安全验证缺陷，使得当前用户可修改只读文件的DACL，添加写入权限。成功利用该漏洞的结果如下图。

![](https://images.seebug.org/content/images/2018/08/cb4a2c15-74a8-44e2-a5bf-f042a0af6422.png-w331s)

#### 安全建议

  * 不要运行未知来源的程序
  * 在微软更新补丁后，及时安装补丁

#### 参考链接

  * <https://thehackernews.com/2018/08/windows-zero-day-exploit.html>
  * <https://www.kb.cert.org/vuls/id/906424>

* * *

**启明星辰积极防御实验室（ADLab）**

ADLab成立于1999年，是中国安全行业最早成立的攻防技术研究实验室之一，微软MAPP计划核心成员。截止目前，ADLab通过CVE发布Windows、Linux、Unix等操作系统安全或软件漏洞近400个，持续保持国际网络安全领域一流水准。实验室研究方向涵盖操作系统与应用系统安全研究、移动智能终端安全研究、物联网智能设备安全研究、Web安全研究、工控系统安全研究、云安全研究。研究成果应用于产品核心技术研究、国家重点科技项目攻关、专业安全服务等。
![](https://images.seebug.org/content/images/2017/05/adlab.png-w331s)

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/688/>


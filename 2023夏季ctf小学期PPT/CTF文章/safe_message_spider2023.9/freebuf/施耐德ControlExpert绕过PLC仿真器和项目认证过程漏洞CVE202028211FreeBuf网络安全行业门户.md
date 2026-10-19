  

Schneider Electric EcoStruxure Control Expert（前称Unity Pro）是法国施耐德电气（Schneider
Electric）公司的一套用于Schneider Electric逻辑控制器产品的编程软件。该软件的V14.1以下的版本存在一个不正确的授权漏洞-CVE-2020-28211，可导致项目的身份验证被绕过。

## Part1 漏洞状态

漏洞细节| 漏洞POC| 漏洞EXP| 在野利用  
---|---|---|---  
有| 有| 有| 无  
  
## Part2 漏洞描述

EcoStruxure Control Expert上存在不正确的授权漏洞，当使用调试器或其他方法覆盖内存时，该漏洞可能导致绕过身份验证。

‍漏洞名称| 绕过PLC仿真器和项目认证过程漏洞  
---|---  
CVE编号| CVE-2020-28211  
漏洞类型| 绕过身份验证  
漏洞等级| 7.8 高危  
公开状态| 公开  
时间线| 2020-11-05 - 分配 CVE2020-11-08 - 公开发布  
影响范围| ‍Schneider Electric EcoStruxure Control Expert version <= v14.1  
复现环境| Windows 10Schneider Electric EcoStruxure Control Expert v14.1  
  
## Part3 漏洞复现

\- 安装Schneider Electric EcoStruxure Control Expert v14.1

\- 启动Control Expert 14.1

![v2-35abe3b8cafd6887fafbb286c2ccc8cc_720w.jpg](https://image.3001.net/images/20220913/1663048055_632019773516d09953e52.jpg!small)

新建任意项目并添加密码(这里我们先暂时设置hellovuleye):

![v2-fe097acd01a28e70c054b7c30cecb364_720w.jpg](https://image.3001.net/images/20220913/1663048055_63201977b8e35dfbba9dd.jpg!small)

无需其他操作，直接保存项目到任意目录下:

![v2-4b8c04d878fe872c38a5f7720385fc90_720w.jpg](https://image.3001.net/images/20220913/1663048056_632019783ce3f8979af4c.jpg!small)

项目生成两个文件 **.stu **.ztx其中stu是主要工程文件，双击打开就会提示输入密码。

![v2-638109521756210d6cf3237fd186b744_720w.jpg](https://image.3001.net/images/20220913/1663048056_63201978a83b7c8ce90d4.jpg!small)

这里我们使用xdbg附加进程。然后在 关键函数位置下断点。

![v2-4ed70f1644ad0ac5c36498fadec209f8_720w.png](https://image.3001.net/images/20220913/1663048057_63201979322cf563bdc77.png!small)

输入任意错误密码我这里输入9个6 (666666666

)然后点击确定。

![v2-abd35553bf49512808a9e15f82a9cbc6_720w.png](https://image.3001.net/images/20220913/1663048057_63201979b127439f71e4b.png!small)

断点断下，我们不做任何处理，直接运行。

![v2-950d2fb015babf9c5d6051d07bc1d4f8_720w.jpg](https://image.3001.net/images/20220913/1663048058_6320197a3e5a9d16b64d5.jpg!small)

提示密码错误。再次输入9个6->确定。断点再次断下，我们进行内存覆盖，F9执行。

![v2-782c906d16a0e0ae8e3d290213423d77_720w.jpg](https://image.3001.net/images/20220913/1663048058_6320197abe781f45d45cf.jpg!small)

项目被打开。

 **复现成功！**

## Part4 漏洞细节

此漏洞出现的原因是最终验证身份的关键点只是一个函数的返回值，很容易被绕过，如果使用一些加密方式来加密工程文件，首先验证密码，然后通过密码解密工程，这样就不容易被绕过。

## Part5 修复缓解建议

1\. 软件升级至最新版本。

2\. 安装主机卫士，开启实时防护。


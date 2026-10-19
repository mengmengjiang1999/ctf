## 概述

Donot“肚脑虫”（APT-C-35）是疑似具有南亚背景的APT组织，其主要以周边国家的政府机构为目标进行网络攻击活动，通常以窃取敏感信息为目的。该组织具备针对Windows与Android双平台的攻击能力。

据奇安信红雨滴团队与奇安信APT实验室监测发现，Donot
APT组织近期攻击频繁。其利用恶意宏样本以及公式编辑漏洞利用样本对周边国家地区开展了多次攻击活动，同时，其在移动端攻击活动也并未停息。根据红雨滴及APT实验室研究人员跟踪分析，Donot此次的攻击活动有如下特点。

l RTF文档中嵌入Excel流，Excel流中包含恶意宏。

l 在文档单元格中写入长段语句，通过宏代码从语句特定位置获取字符拼接为恶意Payload远程服务器地址。

l
增加Loader模块，将恶意木马分割成为Loader以及加密数据两个模块，最终恶意木马由Loader解密数据模块释放执行，目前，Loader模块在VirusTotal上无杀软报毒。

l 在最新的攻击活动中，最终恶意木马不落地，在内存中解密执行，从而绕过杀软检测。

l 托管模板注入资源的恶意服务器上存在着多个测试样本。

![图片.png](https://image.3001.net/images/20200630/1593484877_5efaa64d3be75.png!small)

目前，奇安信威胁情报中心云沙箱（[https://sandbox.ti.qianxin.com/sandbox](https://sandbox.ti.qianxin.com/sandbox/page/detail?type=file&id=c39a48fa9df4fd1cc3253b0ffede0bfaad603be9)）注册用户通过集成红雨滴团队自研RedDrip
APT Scanner（红雨滴高级威胁检测引擎），已支持部分APT样本的精准检测。

## 样本分析

### 样本摘要

近期，奇安信红雨滴团队及奇安信APT实验室捕获多起Donot攻击活动相关样本。基于样本在VirusTotal上的首次提交地区以及部分诱饵信息内容，我们判断此次攻击活动攻击目标为斯里兰卡等地区，部分捕获到的攻击样本信息如下。

**文件名** |  **MD5**  
---|---  
**Letter 11 Jun 20.docx** |  7e484c7eed8990d2f4fc4bb0028dcc49  
**Incident Report.xls** |  248323b43a58d226536202a649f88a83  
**31PN.xls** |  94a48c8430c69baca1ee704a1306d75d  
**** |  8702385f0a64bf1aa8e202430692a9e6  
**vcallnchat-24.5.18-aligned-signed.apk** |  e7fdc332***18d5b21f05324be027f01  
**secchat.apk** |  e5811485b2185e4cebb60425b6a63c99  
**Protection Plan.xls** |  4428912f168f3f1f0554126de7b4eced  
**** |  1d1fb7aba66794303afc6b5420068231  
  
### 宏利用类样本

样本以事故报告为诱饵，诱导受害者点击执行，打开文档后提示用户启用宏。

![图片.png](https://image.3001.net/images/20200630/1593484935_5efaa687f2cc4.png!small)

当用户选择启用宏后，恶意宏代码将被执行。样本宏经过简单加密处理，无法直接查看

![图片.png](https://image.3001.net/images/20200630/1593484946_5efaa6922fd9f.png!small)

通过奇安信威胁情报中心自研深度文件解析引擎OWL解析得到的宏代码如下

![图片.png](https://image.3001.net/images/20200630/1593484951_5efaa69714383.png!small)

攻击者在单元格**以及C10中写入长语句，并将其字体颜色设置为白色，使受害者无法直接看见该语句

![图片.png](https://image.3001.net/images/20200630/1593484956_5efaa69cd42a1.png!small)

而恶意宏代码将从长语句中特定位置获取字符组成URL，并从URL下载后续Loader
dll以及加密的恶意木马数据保存%temp%目录下，并加载Loader模块执行。

![图片.png](https://image.3001.net/images/20200630/1593484964_5efaa6a499594.png!small)

**DLL下载地址** |  **<http://filepage.icu/f>**  
---|---  
**DLL MD5** |  20E20211648F**E60A65EE2FD3A1825E  
**数据下载地址** |  <http://filepage.icu/p>  
**数据 MD5** |  7CFF1A66099A48A9BB7B551BC768927A  
  
下载的Loader
dll执行起来后，将尝试读取加密的数据，若读取成功则解密该数据，并将解密的数据写入到%Roaming%\logical\mentn.dll

![图片.png](https://image.3001.net/images/20200630/1593484977_5efaa6b12de27.png!small)

之后将在logical目录下创建js文件用于启动mentn.dll,并在启动项目录下创建lnk文件启动js文件，从而实现持久驻留

![图片.png](https://image.3001.net/images/20200630/1593484986_5efaa6ba97296.png!small)

**文件名** |  **MD5**  
---|---  
**mentn.dll** |  24C3355E080887DC987CD8ADAF2B3475  
  
Mentn.dll加载执行后，将在内存中异或解密最终的恶意木马程序执行

![图片.png](https://image.3001.net/images/20200630/1593485014_5efaa6d60dced.png!small)

内存加载的恶意程序执行后，首先通过一些特定路径检查受害者计算机中是否存在相应杀软

![图片.png](https://image.3001.net/images/20200630/1593485020_5efaa6dcbaf08.png!small)

之后创建线程，进入主功能函数StartAdress执行

![图片.png](https://image.3001.net/images/20200630/1593485027_5efaa6e391f5f.png!small)

样本中大量字符串采用加密处理，增加分析师分析难度，经红雨滴安全研究员分析研究后，还原解密算法如下:

![图片.png](https://image.3001.net/images/20200630/1593485035_5efaa6eb1fdfe.png!small)

进入StartAddress执行后，首先通过0x5658端口检测虚拟机，当处于虚拟机状态时，执行命令后EBX寄存器值将0x564D5868（”VMXh”）

![图片.png](https://image.3001.net/images/20200630/1593485040_5efaa6f095355.png!small)

之后检测是否存在特定的文件，若存在则将其删除

![图片.png](https://image.3001.net/images/20200630/1593485048_5efaa6f81d10e.png!small)

检测运行环境是否处于虚拟机状态，若处于虚拟机则退出，否则进入主功能流程

![图片.png](https://image.3001.net/images/20200630/1593485054_5efaa6fe7b562.png!small)

之后获取受害者计算机信息，包括磁盘剩余容量，文件列表，操作系统等信息

![图片.png](https://image.3001.net/images/20200630/1593485059_5efaa703b8425.png!small)

以“|||“为分割符拼接获取的信息

![图片.png](https://image.3001.net/images/20200630/1593485064_5efaa708a242c.png!small)

与C2通信，并发送加密后的信息

![图片.png](https://image.3001.net/images/20200630/1593485069_5efaa70d74e8f.png!small)

并尝试从C2获取其他功能插件执行

![图片.png](https://image.3001.net/images/20200630/1593485078_5efaa71680806.png!small)

遗憾的是，在分析过程中未获取到其他功能插件执行。

### 模板注入样本

**文件名** |  **MD5**  
---|---  
**Letter 11 Jun 20.docx** |  7e484c7eed8990d2f4fc4bb0028dcc49  
  
该样本在文档中嵌入了一个远程模板文件，受害者打开文档后，则会从外部链接下载公式编辑漏洞利用文档执行

![图片.png](https://image.3001.net/images/20200630/1593485094_5efaa7261b10d.png!small)

远程模板信息如下

**远程模板地址** |  **MD5**  
---|---  
**<http://datasecure.icu/KB4209T/10068P>** |  033F4D56F1273A555028225D74CDE177  
  
获取的文档是公式编辑漏洞利用文档，执行后将释放Loader
dll与加密的木马数据到本地磁盘，执行后将解密完成的恶意木马DLL释放到%appdata%\uppdown\eupol.dll.

![图片.png](https://image.3001.net/images/20200630/1593485100_5efaa72ce4d48.png!small)

之后创建计划任务，利用rundll32.exe执行eupol.dll并调用其导出函数csytu，计划任务信息如下

![图片.png](https://image.3001.net/images/20200630/1593485107_5efaa733932e4.png!small)

其功能流程与宏样本后续木马基本一致，不再赘述

## 溯源关联

奇安信威胁情报中心红雨滴团队通过对此次捕获样本的木马特征，基础设施等方向关联发现，此次攻击活动幕后黑手疑似是南亚APT组织Donot

### 与Donot的关联

与2019年Donot组织攻击活动一致，均通过特定文件路径检测计算机是否存在杀软

![图片.png](https://image.3001.net/images/20200630/1593485116_5efaa73c1109c.png!small)

样本中均包含大量VS2010调试信息，都尝试通过检测端口0x5658检测虚拟机。且主功能函数冗长，字符均通过加密处理。

![图片.png](https://image.3001.net/images/20200630/1593485123_5efaa7439c430.png!small)

同时，其c2命名方式也与donot基本一致，且奇安信ALPHA威胁分析平台已有Donot相关标签

![图片.png](https://image.3001.net/images/20200630/1593485134_5efaa74e16e30.png!small)

### 拓展

在分析模板注入样本过程中，安全研究员发现该托管服务器还存在多个Donot组织样本

![图片.png](https://image.3001.net/images/20200630/1593485142_5efaa75643c5a.png!small)

经分析发现，其中多个样本为测试样本，释放执行的最终恶意文件弹框显示测试消息

![图片.png](https://image.3001.net/images/20200630/1593485148_5efaa75c4c20c.png!small)

由此可见该组织团体在发起正式攻击前，曾经过多次测试。

## 总结

Donot是一个长期活跃的APT组织，同时具有Windows与Andorid双平台攻击能力，且持续更新其武器库，此次将恶意木马分割成Loader与加密的数据，已能起到极好的免杀效果，奇安信威胁情报中心将持续追踪该组织攻击活动。

奇安信威胁情报中心再次提醒各企业用户，加强员工的安全意识培训是企业信息安全建设中最重要的一环，如有需要，企业用户可以建设态势感知，完善资产管理及持续监控能力，并积极引入威胁情报，以尽可能防御此类攻击。

目前，基于奇安信威胁情报中心的威胁情报数据的全线产品，包括威胁情报平台（TIP）、天眼高级威胁检测系统、NGSOC、奇安信态势感知等，都已经支持对此APT攻击团伙攻击活动的精准检测。

![图片.png](https://image.3001.net/images/20200630/1593485159_5efaa7670927a.png!small)

## 参考

<https://ti.qianxin.com/blog/articles/donot-apt-group-recent-attacks-on-nei***oring-countries-and-regions/>

## IOC

7e484c7eed8990d2f4fc4bb0028dcc49

248323b43a58d226536202a649f88a83

94a48c8430c69baca1ee704a1306d75d

8702385f0a64bf1aa8e202430692a9e6

e7fdc332***18d5b21f05324be027f01

e5811485b2185e4cebb60425b6a63c99

4428912f168f3f1f0554126de7b4eced

1d1fb7aba66794303afc6b5420068231

<http://filepage.icu/f>

<http://filepage.icu/p>


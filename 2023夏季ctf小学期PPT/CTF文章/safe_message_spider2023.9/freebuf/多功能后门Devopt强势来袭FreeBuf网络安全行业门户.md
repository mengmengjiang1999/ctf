近年来，恶意软件攻击变得越来越复杂，攻击者会不断寻找新的方法来进行攻击与窃取敏感数据。研究人员近日发现了一个名为 Devopt
的后门，提供按键记录、浏览器凭据窃取等功能。短短几日，后门的多个版本就轮番出现，这表明攻击者仍然在积极开发中。

## 攻击活动

研究人员在寻找新的恶意软件时发现了使用 Free Pascal
创建的后门，该后门能够从失陷主机中窃取数据。调查中发现一个俄语网站，用户在网站上完成涉及恶意软件下载的任务后会获得经济奖励。通过进一步分析，下载的恶意软件是压缩文件的图标，并且引诱用户双击执行。网络犯罪分子也会使用经济激励等策略来引诱用户下载恶意软件，其
URL 通常遵循如下结构：`wdfiles-download[.]siteme[.]org/arxiv[digit].exe`。

![image.png-332.5kB](https://image.3001.net/images/20230424/1682348136_64469868c9af52c4b608f.png!small)诱使用户下载恶意样本

## 技术分析

最早发现的后门包含图形界面且没有经过混淆，大约为 20MB。新变种约为 2MB，且使用编码来混淆字符串。

旧版本后门使用 HTTP 协议，而新版本后门使用 HTTPS 协议。为了建立网络连接，后门依赖
libcrypto-1_1.dll、libeay32.dll、libssl-1_1.dll、libssl32.dll 与 ssleay32.dll 这几个
DLL 文件。如果缺少这些依赖，恶意软件将不会感染系统。

混淆字符串| 原始字符串| 描述  
---|---|---  
5494-4756-7544-6970-9430-8282-9348-9430-7544| C:\Users\| 失陷主机用户目录  
7544-5576-8282-9430-8774-9512-9102-9184-7544| \Desktop\| 失陷主机桌面目录  
7544-5576-9102-8118-9594-8938-8282-9020-9512-9430-7544| \Documents\| 失陷主机文档目录  
7544-5576-9102-9758-9020-8856-9102-7954-8200-9430-7544| \Downloads\| 失陷主机下载目录  
8200-8282-9676-9102-9184-9512-3444-3772-8282-9840-8282| devopt*.exe| 创建副本文件持久化  
7544-7134-8610-9020-8774-8282-9922-6068-8282-9512-3772-8610-9020-8610|
\WinkeyJet.ini| 配置文件名  
8528-9512-9512-9184-9430-4756-3854-3854-8938-9676-8200-3690-8774-3690-9512-9594-8856-7954-3772-9430-8610-9512-8282-8938-8282-3772-9102-9348-8446-3854|
https[:]//mvd-k-tula[.]siteme[.]org/| C&C 服务器  
7544-5330-9184-9184-5576-7954-9512-7954-7544-6724-9102-7954-8938-8610-9020-8446-7544-6314-8610-8118-9348-9102-9430-9102-8364-9512-7544-7134-8610-9020-8200-9102-9758-9430-7544-6806-9512-7954-9348-9512-2624-6314-8282-9020-9594-7544-6560-9348-9102-8446-9348-7954-8938-9430-7544-6806-9512-7954-9348-9512-9594-9184-7544|
\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\| 启动路径  
6314-9102-10004-8610-8856-8856-7954-3854-4346-3772-3936-2624-3280-7134-8610-9020-8200-9102-9758-9430-2624-6396-6888-2624-4428-3772-4100-4838-2624-9348-9676-4756-4018-3936-4264-3772-3936-3362-2624-5822-8282-8118-8774-9102-3854-4100-3936-4018-3936-3936-4018-3936-4018-2624-5740-8610-9348-8282-8364-9102-9840-3854-4018-3936-4264-3772-3936|
Mozilla/5.0 (Windows NT 6.2; rv:104.0) Gecko/20100101 Firefox/104.0| User-Agent  
8856-8610-9430-9512-8282-9020-8282-9348-3772-9184-8528-9184| listener.php|
回传地址  
  
早期版本的后门需要用户点击提交，新版本的后门则无需交互即可静默运行。

![image.png-59.7kB](https://image.3001.net/images/20230424/1682348137_64469869de7f5eeb15f05.png!small)早期版本的后门

## 其他分析

### 持久化

样本文件会在启动文件夹中进行复制，使其在计算机开机时保持启动，其路径为：`C:\Users\User\AppData\Roaming\Microsoft\Windows\Start
Menu\Programs\Startup\devopt[random 2 digits].exe`。

![image.png-375kB](https://image.3001.net/images/20230424/1682348138_6446986a91b2841c37875.png!small)持久化机制

### 剪贴板复制

样本文件会创建名为 `C:\User\[User]\clippa.dan`的文件，其中记录了剪贴板中的所有信息。

![image.png-49.2kB](https://image.3001.net/images/20230424/1682348139_6446986baed05bc1d3c55.png!small)获取剪贴板数据

### 信息窃密

在 `C:\User\[User]\`中的 `cdck.bin`与 `bdck.bin`，窃取特定浏览器的凭据、Cookie、历史记录和版本信息：

从 Chrome 浏览器收集的数据：

  * [C:\Users\User\AppData\Local\Google\Chrome\User Data\Default\Network\Cookies]
  * [C:\Users\User\AppData\Local\Google\Chrome\User Data\Default\History]
  * [C:\Users\User\AppData\Local\Google\Chrome\User Data\Default\Login Data]
  * [C:\Users\User\AppData\Local\Google\Chrome\User Data\Last Version]

从 Yandex 浏览器收集的数据：

  * [C:\Users\User\AppData\Local\Yandex\YandexBrowser\User Data\Default\Network\Cookies]
  * [C:\Users\User\AppData\Local\Yandex\YandexBrowser\User Data\Default\Network\History]
  * [C:\Users\User\AppData\Local\Yandex\YandexBrowser\User Data\Default\Ya Passman Data]
  * [C:\Users\User\AppData\Local\Yandex\YandexBrowser\User Data\Default\Ya Autofill Data]

### 按键记录

恶意软件会创建 C:\User[User]\Kebba.dan 文件来存储用户的按键记录。

![image.png-71.8kB](https://image.3001.net/images/20230424/1682348140_6446986c5cd3185e1d8fd.png!small)按键记录

### 数据收集

![image.png-404kB](https://image.3001.net/images/20230424/1682348141_6446986d60a449325bb94.png!small)遍历文件目录

恶意软件会查找存储在文档文件夹、下载文件夹与桌面文件夹的各种文件，窃取的文件会保存在 C:\User[User]\grb.bin。

![image.png-101.8kB](https://image.3001.net/images/20230424/1682348142_6446986e6c7d2184c5089.png!small)窃取内容

### 释放的文本文件

早期版本的后门使用名为 unpacked.dt 的文件，其中包含随机生成的字符串。新版本中，该文件名为 0.txt。

![image.png-1847.8kB](https://image.3001.net/images/20230424/1682348143_6446986f483560c7ecba3.png!small)随机字符串

该文件可能是为了旨在干扰恶意软件分析人员，并没有实际作用。

### 配置文件

名为 Winkeyjet.ini 的配置文件中，包含有关失陷主机的相关信息，例如操作系统名、设备 ID
与操作系统版本号等。此外，文件中还包含恶意软件的硬编码版本号。配置文件中还指定了 C&C 服务器：

![image.png-60.9kB](https://image.3001.net/images/20230424/1682348145_6446987100d8a9c70feb1.png!small)配置文件

早期版本的恶意软件会显示消息框，文本是嘲笑俄罗斯总统普京的标语。

![image.png-30.8kB](https://image.3001.net/images/20230424/1682348145_6446987193a15b868d4e6.png!small)消息框

### 网络通信

![image.png-646.2kB](https://image.3001.net/images/20230424/1682348146_644698724ed84f99128c1.png!small)网络通信

### 命令

后门所支持的命令如下所示：

![image.png-67.1kB](https://image.3001.net/images/20230424/1682348147_644698736f38150d23dc4.png!small)命令列表

旧版本的恶意软件不支持收集驱动器和进程信息的 DRLS 和 PRLS 命令。

## 结论

该恶意软件是一种多功能的后门，可以窃取机密信息、记录按键、窃取文件以及建立对失陷主机的持久访问权限。攻击者也在不断为该后门增加新功能使其更加隐蔽，并且使用了各种检测逃避技术来改进恶意软件。Devopt
后门将命令进行编码，并且使用了误导性名称文件来欺骗恶意软件分析人员。

## IOC

> db14d40d780853f80b93e21e92617680  
> 94df2e4aa0f432ef992893d7b994ce84  
> 391c894616dd0e8b372b801cbbc0a790  
> e42198e7c0647238b999a2b2133daac2  
> mvd-k-tula[.]siteme[.]org  
> mvd-k-tula[.]ru  
> wdfiles-download[.]siteme[.]org/arxiv5.exe

## 参考来源

> [Zscaler](https://www.zscaler.com/blogs/security-research/introducing-> devopt-multifunctional-backdoor-arsenal)


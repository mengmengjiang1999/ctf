## 一、事件背景

**近期深信服EDR安全团队接到客户应急需求，称服务器被勒索病毒加密，经过深入分析，提取到相关的样本信息，发现此样本为SamSam勒索病毒最新的变种样本，加密的流程与之前发现的SamSam的变种基本一致。**

SamSam勒索病毒最早于2016年4月左右被首次发现，主要通过服务器网站漏洞、垃圾邮件，RDP爆破等方式感染服务器，此勒索病毒主要用于攻击企业服务器，主要活跃在北美地区，之前曾对北美多个国家医院服务器进行攻击，破坏医院的正常业务，最近此勒索病毒变种在北美等地区非常活跃，已有多家企业中招，此次发现的最新变种加密后的文件后缀为：weapologize，它会通过PSEXEC.EXE工具感染其它主机，勒索病毒采用RSA2048加密算法加密相应的文件，加密后的文件无法还原。

## 二、样本分析

1.此勒索病毒涉及到的相关文件，如下：

![图片.png](https://image.3001.net/images/20180730/1532922154_5b5e892a47859.png!small)

2.此勒索病毒执行流程(与之前发现的变种加密流程基于一致)，如下：

![图片.png](https://image.3001.net/images/20180730/1532922167_5b5e89378f4a6.png!small)

3.启动此勒索病毒的BAT脚本g04inst.bat，如下：

![图片.png](https://image.3001.net/images/20180730/1532922183_5b5e89477498e.png!small)

通过传递一个解密key参数，启动此BAT脚本，执行加密操作，最后删除相关文件。

4.此勒索病毒加密使用的RSA公钥KEY文件NTAARFOIP02_publicKey.keyxml，如下：

![图片.png](https://image.3001.net/images/20180730/1532922191_5b5e894f07ee3.png!small)

5.此勒索病毒母体winupdateini.exe会读取BAT脚本传递进来的四个参数，然后执行相应的操作，如果参数不对，则退出程序，如下：

![图片.png](https://image.3001.net/images/20180730/1532922198_5b5e8956b9999.png!small)

6.查找相应的加密payload文件*.sophos，如果发现则读取payload文件内容，然后删除相应的payload文件，如下：

![图片.png](https://image.3001.net/images/20180730/1532922207_5b5e895fcca92.png!small)

7.对读取的加密payload文件进行解密，通过BAT传入到解密参数，如下：

![图片.png](https://image.3001.net/images/20180730/1532922216_5b5e896811549.png!small)

会调用dellerrrtonimon.dll的解密函数，如下：

![图片.png](https://image.3001.net/images/20180730/1532922223_5b5e896fd3d4b.png!small)

8.解密函数的过程，如下：

![图片.png](https://image.3001.net/images/20180730/1532922238_5b5e897e2b0bf.png!small)

通过AES解密算法进行解密，解密的Key和IV是通过参数进行传递，然后从如下数组中选取的，如下：

![图片.png](https://image.3001.net/images/20180730/1532922245_5b5e8985cff57.png!small)

相应的数组列表如下：

![图片.png](https://image.3001.net/images/20180730/1532922253_5b5e898d854cd.png!small)

9.加载解密出来的加密payload，执行加密操作，如下：

![图片.png](https://image.3001.net/images/20180730/1532922262_5b5e899624d32.png!small)

加密payload的实例对象，如下：

![图片.png](https://image.3001.net/images/20180730/1532922270_5b5e899e41082.png!small)

调用加密的payload，执行相应的加密操作，如下：

![图片.png](https://image.3001.net/images/20180730/1532922278_5b5e89a6a16f8.png!small)

通过Invoke执行加密操作，如下：

![图片.png](https://image.3001.net/images/20180730/1532922287_5b5e89afc7fc3.png!small)

10.母体样本和解密函数DLL里面都包含大量的垃圾代码，如下：

![图片.png](https://image.3001.net/images/20180730/1532922297_5b5e89b99478c.png!small)

攻击者通过传入解密参数key，启动执行BAT脚本，并传入相应的四个参数，调用母体EXE解密出相应的加密payload，然后对主机中的相应文件进行加密，并在桌面生成多个包含勒索信息的HTML超文件文件。

## 三、解决方案

深信服EDR产品能有效检测及防御此类勒索病毒家族样本及其变种，同时深信服EDR安全团队提醒广大用户：

1.不要点击来源不明的邮件附件，不从不明网站下载软件；

2.及时给主机打补丁，修复相应的高危漏洞；

3.对重要的数据文件定期进行非本地备份；

4.尽量关闭不必要的文件共享权限以及关闭不必要的端口，如：445,135,139,3389等；

5.RDP远程服务器等连接尽量使用强密码，不要使用弱密码；

6.此勒索病毒会通过PSEXEC.EXE工具感染其它主机，建议卸载禁用此工具；

7.安装专业的终端安全防护软件，为主机提供端点防护和病毒检测清理功能；

## 四、相关IOC

758274028C49227A779E3A7812F526D5 g04inst.bat

69FCB82C35C67CAB0F9C877B489C8D69 dellerrrtonimon.dll

20487336761EDD9537318C7A139E32AD winupdateini.exe

F547DE1E1346042E138CF2D465EBB07C NTAARFOIP02_publicKey.keyxml

 ***本文作者千里目安全实验室，转载注明来自FreeBuf.COM**  


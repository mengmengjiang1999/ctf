## **一、样本简介**  

**Globelmposter家族首次出现在2017年5月份，2018年2月全国各大医院受Globelmposter2.0勒索病毒攻击，导致医院系统被加密，严重影响了医院的正常业务，此勒索病毒在今年8月份变种出Globelmposter3.0版本，导致全国多家法院等政企事业单位被勒索加密。**

此次，在2018年12月份，深信服EDR安全团队又第一时间跟踪发现一例新的Globelmposter勒索病毒变种，加密后缀".fuck"。

Globelmposter勒索病毒今年的安全威胁热度一直居高不下，攻击手法极其丰富，可以通过社会工程，RDP爆破，恶意程序捆绑等方式进行传播，其加密的后缀名也不断变化，Globelmposter2.0后缀：TECHNO、DOC、CHAK、FREEMAN、TRUE，ALC0、ALC02、ALC03、RESERVE等。Globelmposter3.0变种后缀为以*4444结尾，Globelmposter3.0家族的变种，采用RSA+AES算法加密，目前该勒索样本加密的文件暂无解密工具，文件被加密后会被加上Ox4444、China4444、Help4444、Rat4444
、Tiger4444 、Rabbit4444 、Dragon4444 、Snake4444 、Horse4444、Goat4444 、Monkey4444
、Rooster4444、Dog4444等后缀。在被加密的目录下会生成一个名为“HOW_TO_BACK_FILES”的txt文件，显示受害者的个人ID序列号以及黑客的联系方式等。

深信服EDR安全团队一直持续关注并跟踪此勒索病毒家族，多次发布此勒索病毒相应的预警报告，如下：

> Globelmposter勒索样本分析报告
>
> <https://mp.weixin.qq.com/s/iy9bGvS8ls2eBM2J_gCDXA>
>
> 紧急预警：Globelmposter勒索最新变种爆发，用户怒怼黑客！
>
> <https://mp.weixin.qq.com/s/Rx3QCJZ5cqWayBOwuO82lg>
>
> 紧急预警：Globelmposter再爆3.0变种，大型医院已中招
>
> <https://mp.weixin.qq.com/s/nm_B04qDr6TGv-qmU5t6FQ>

此次深信服EDR安全团队又第一时间跟踪发现一例新的Globelmposter勒索病毒变种，样本编译时间为2018年12月5号，可能是此勒索病毒的最新变种，如下所示：

![1.png](https://image.3001.net/images/20190109/1547026076_5c35be9c8de25.png!small)

##  **二、详细分析**

1.样本经过多层payload解密，运行后先弹出控制台窗口输出几组随机数对，并且创建窗口以混淆视听：

![2.png](https://image.3001.net/images/20190109/1547026086_5c35bea6a7b8d.png!small)

在创建窗体的代码中隐藏了解密payload的代码，通过virtualalloc函数申请内存，随后解密出第一层payload代码，如下所示：

![3.png](https://image.3001.net/images/20190109/1547026096_5c35beb0776f8.png!small)

第一层payload解密出第二层payload代码，如下所示：

![4.png](https://image.3001.net/images/20190109/1547026106_5c35bebad5bc1.png!small)

第二层payload代码循环解密核心的PE代码，如下所示：

![5.png](https://image.3001.net/images/20190109/1547026116_5c35bec44a446.png!small)

并将解密出来的PE文件内容替换到当前进程内存：

![6.png](https://image.3001.net/images/20190109/1547026123_5c35becb59ab6.png!small)

然后跳转到被替代的当前进程，执行加密勒索操作，如下所示：

![7.png](https://image.3001.net/images/20190109/1547026134_5c35bed60a0cf.png!small)

2.样本在"HKEY_CURRENT_USER\Software\FUCK"下创建注册表项PERSONALID保存用户ID：

![8.png](https://image.3001.net/images/20190109/1547026144_5c35bee014c04.png!small)

并设置自启动注册表项：

![9.png](https://image.3001.net/images/20190109/1547026153_5c35bee9b4de6.png!small)

添加后的自启动项，如下所示：

![10.png](https://image.3001.net/images/20190109/1547026163_5c35bef32742d.png!small)

3.进行加密之前，样本先遍历进程列表，查找并终止以下进程：

![11.png](https://image.3001.net/images/20190109/1547026172_5c35befcde9b1.png!small)

相应的进程列表，如下所示：

teamviewer、sql、google、cloud、photoshop、torrent、backup等。

4.启动cmd执行删除卷影副本的命令：

![12.png](https://image.3001.net/images/20190109/1547026185_5c35bf09576f0.png!small)

5.获取所有驱动器并判断类型：

![13.png](https://image.3001.net/images/20190109/1547026194_5c35bf12b5ea9.png!small)

6.遍历磁盘加密文件，跳过文件后缀为dll、htm、lnk、ini、exe、fuck、gsg的文件：

![14.png](https://image.3001.net/images/20190109/1547026204_5c35bf1c39ab1.png!small)

跳过"Program Files"和"Windows"目录：  

![15_3.png](https://image.3001.net/images/20190109/1547026214_5c35bf2609d0c.png!small)![16.png](https://image.3001.net/images/20190109/1547026214_5c35bf26d04bc.png!small)

在每个目录下释放勒索信息文件"README_BACK_FILES.htm"：

![17.png](https://image.3001.net/images/20190109/1547026224_5c35bf309b4da.png!small)

相应的勒索信息超文本文件，如下所示：  

![18.png](https://image.3001.net/images/20190109/1547026234_5c35bf3ab1811.png!small)![19.png](https://image.3001.net/images/20190109/1547026237_5c35bf3d4dae1.png!small)

7.样本使用了AES+RSA的方式对文件进行加密，首先生成AES密钥：

![20.png](https://image.3001.net/images/20190109/1547026247_5c35bf470359a.png!small)

使用RSA公钥对AES密钥进行加密：

![21.png](https://image.3001.net/images/20190109/1547026258_5c35bf5292dee.png!small)

再使用AES加密文件，并重命名文件，添加加密后缀".fuck"：

![22.png](https://image.3001.net/images/20190109/1547026268_5c35bf5c1eaab.png!small)

加密之后的文件，如下所示：

![23.png](https://image.3001.net/images/20190109/1547026279_5c35bf677d1ac.png!small)

8.加密完成后释放bat文件进行自删除：

![24.png](https://image.3001.net/images/20190109/1547026289_5c35bf71456c0.png!small)

##  **三、解决方案**

深信服EDR产品能有效检测及防御此类勒索病毒家族样本及其变种，如下所示：

![25.png](https://image.3001.net/images/20190109/1547026300_5c35bf7cdc3e0.png!small)

深信服EDR安全团队再次提醒广大用户，勒索病毒以防为主，目前大部分勒索病毒加密后的文件都无法解密，注意日常防范措施：

1.不要点击来源不明的邮件附件，不从不明网站下载软件。

2.及时给主机打补丁(永恒之蓝漏洞补丁)，修复相应的高危漏洞。

3.对重要的数据文件定期进行非本地备份。

4.尽量关闭不必要的文件共享权限以及关闭不必要的端口，如：445,135,139,3389等。

5.RDP远程服务器等连接尽量使用强密码，不要使用弱密码。

6.安装专业的终端安全防护软件，为主机提供端点防护和病毒检测清理功能。

 ***本文作者：千里目安全实验室，转载请注明来自FreeBuf.COM**


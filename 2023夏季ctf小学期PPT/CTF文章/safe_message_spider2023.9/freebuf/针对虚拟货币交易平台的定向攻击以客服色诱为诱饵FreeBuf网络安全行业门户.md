## **概述** ****

近期，奇安信病毒响应中心在日常的样本运营中，发现了一起针对区块链虚拟货币交易平台的定向攻击，鉴于诱饵极具诱惑性，并且该定向攻击幕后团伙此前也被曝光过，鉴于攻击手法已经升级，我们对此进行了分析，并披露了此次攻击。

## **样本分析** ****

Excel的文件名为：mxc客服人员色诱客户侵吞平台财产.xls

该样本的VT报毒结果如下：

![图片.png](https://image.3001.net/images/20191115/1573793059_5dce2d238a28b.png!small)

刚打开的界面如下：

![图片.png](https://image.3001.net/images/20191115/1573793065_5dce2d298fa7e.png!small)

点击后的截图：

![图片.png](https://image.3001.net/images/20191115/1573793073_5dce2d312408a.png!small)

通过mshta执行hta文件：

Null.hta的内容如下，被执行起来后会请求一个github的地址：

<https://raw.githubusercontent.com/pick90/hit/master/1.txt>获取数据并通过InstallUtil.exe执行下载的C#编译的exe文件：

![图片.png](https://image.3001.net/images/20191115/1573793082_5dce2d3a64e93.png!small)

该文件的文件描述为age.png，编译时间为：2019-10-30 11:37:12

会通过powershell执行下面的恶意代码：

![图片.png](https://image.3001.net/images/20191115/1573793088_5dce2d4014478.png!small)

恶意代码解密后，会去请求<https://n-trip.com/index.png>，下载下一阶段的脚本执行：

![图片.png](https://image.3001.net/images/20191115/1573793092_5dce2d447df36.png!small)

该png是一个加密的文件，经过 base64解码后，在进行rc4解密，rc4的密钥是前16字节：

![图片.png](https://image.3001.net/images/20191115/1573793098_5dce2d4a5de9f.png!small)

解密后的数据是powershell：

![图片.png](https://image.3001.net/images/20191115/1573793103_5dce2d4fa0bd5.png!small)

如果有360和QQ电脑管家，会通过事件过滤的形式实现开机启动，创建的filter的名字为：TimerFilter；如果不存在上述杀毒软件，就直接通过系统dll劫持实现持久化，劫持的dll名字为“wlbsctrl.dll”：

![图片.png](https://image.3001.net/images/20191115/1573793109_5dce2d550832d.png!small)

通过wusa的方式bypass UAC，然后释放wlbsctrl.dll”到system32下的：

![图片.png](https://image.3001.net/images/20191115/1573793113_5dce2d59a8a35.png!small)

下图是wlbsctrl.dll的代码，

在dllmain里会通过InstallUtil.exe加载A164C0BF-67AE-3C7E-BC05-BFE24A8CDB62.dat这个文件，而这个文件就是rat变量的内容解密后释放的文件：

![图片.png](https://image.3001.net/images/20191115/1573793122_5dce2d62aed19.png!small)![图片.png](https://image.3001.net/images/20191115/1573793130_5dce2d6ad89a8.png!small)  

Rat的变量经过2层base64解密后，是一个C#编译的exe文件，该exe文件也是通过InstallUtil.exe加载：

![图片.png](https://image.3001.net/images/20191115/1573793136_5dce2d70f35d5.png!small)

该exe文件会执行powershell命令：

![图片.png](https://image.3001.net/images/20191115/1573793141_5dce2d756ff46.png!small)

执行的powershell命令解密后如下：

![图片.png](https://image.3001.net/images/20191115/1573793146_5dce2d7a55e3c.png!small)

最后会加载cobaltstrike的Loader，请求url（[https://slay.008ex.com/NhRT）获取beacon.dll](https://slay.008ex.com/NhRT%EF%BC%89%E8%8E%B7%E5%8F%96beacon.dll)
实现远程控制。

![图片.png](https://image.3001.net/images/20191115/1573793152_5dce2d80645bf.png!small)

回联的地址：

这次攻击者出现的所有的exe文件，整理表格如下：

![图片.png](https://image.3001.net/images/20191115/1573793244_5dce2ddce93ee.png!small)  

  

  
  
  
  
  
  
  
  

##  **域名信息** ****

域名注册时间：

![图片.png](https://image.3001.net/images/20191115/1573793310_5dce2e1ec274d.png!small)  

  

  
  
  
  
  
  

承载第一阶段的Github账号的注册时间是2019年9月25日，在9月26号开始提交一些webshell相关的代码，怀疑攻击者是想通过网站的漏洞下载webshell到服务的web目录下；为了避免被发现，才使用了github的方式。

![图片.png](https://image.3001.net/images/20191115/1573793344_5dce2e407f401.png!small)

9月26号曾多次提交名字为1.txt的webshell代码：

![图片.png](https://image.3001.net/images/20191115/1573793349_5dce2e45e9e23.png!small)

而10月29号，攻击者把一直提供webshell下载服务的1.txt，修改成了木马使用的payload：

![图片.png](https://image.3001.net/images/20191115/1573793354_5dce2e4addeae.png!small)

攻击者应该是平时做渗透的，最近想通过定向攻击的方式拿到一些重要的目标。

而就在刚刚（2019年11月14日），攻击者又更新了下木马使用的payload：

![图片.png](https://image.3001.net/images/20191115/1573793363_5dce2e53cc18b.png!small)

从该payload里解密出来的木马的编译时间就在11月14日，而该样本在VT上是0检出的：

![图片.png](https://image.3001.net/images/20191115/1573793386_5dce2e6aeb20a.png!small)![图片.png](https://image.3001.net/images/20191115/1573793428_5dce2e9454983.png!small)  

  

  
  

##  **关联分析** ****

在对域名bill.008ex.com解析的IP: 192.52.167.189进行关联分析的过程中；

![图片.png](https://image.3001.net/images/20191115/1573793440_5dce2ea03f869.png!small)  

我们发现在该ip端的同一网段存在另一个可疑ip 192.52.167.185 。  

![图片.png](https://image.3001.net/images/20191115/1573793445_5dce2ea5c331f.png!small)

从平台来看，其恰好关联到了腾讯御见威胁情报中心的一篇《针对某区块链数字加密币交易平台的APT攻击》报告

[
_https://mp.weixin.qq.com/s/F7A9hxucQS-82VcE7xCVmg_](https://mp.weixin.qq.com/s/F7A9hxucQS-82VcE7xCVmg)

其中

![图片.png](https://image.3001.net/images/20191115/1573793466_5dce2ebac581c.png!small)

使用的IP地址。

![图片.png](https://image.3001.net/images/20191115/1573793472_5dce2ec09a794.png!small)  

但是当时该团伙没有使用github的形式进行样本获取，而且本次的域名都是动态域名，该团伙被曝光后，8月30日就申请了008ex.com这个域名作为下次攻击的C2，并于9月25日注册github账号，而且这次攻击中使用的2个非动态域名都申请了隐私保护。

## **总结** ****

本次针对区块链平台的针对性攻击，并结合此前的攻击，不难认为，该攻击组织具备黑产属性，并且在隐藏自身做的非常到位，无论是使用Github进行木马下载，还是最后释放的Cobaltstrike远控都让人难以进一步追踪。

奇安信病毒响应中心将持续追踪该黑产团伙，相关载荷和木马均可被奇安信全线产品查杀。

值得一提的是，奇安信威胁情报中心Alpha威胁分析平台企业版目前解锁新功能，可以查询关于每个IOC对象(域名，IP，URL，Hash)对应的TTP信息中的Technologic，只为了更方便客户知晓整个域名的具现化描述。

有需求请发邮件联系ti_support@qianxin.com

![图片.png](https://image.3001.net/images/20191115/1573793483_5dce2ecbaf628.png!small)

## **IOCs** ****

<https://download.008ex.com/auth.log>

<https://n-trip.com/index.png>

<https://slay.008ex.com/NhRT>

slay.008ex.com,/c/msdownload/update/others/2016/12/29136388_,

bill.008ex.com,/c/msdownload/update/others/2016/12/29136388_,

jan.008ex.com,/c/msdownload/update/others/2016/12/29136388_

bill.008ex.com

download.008ex.com

download.008ex.com

jan.008ex.com

slay.008ex.com

gfem.n-trip.com

sbar.n-trip.com


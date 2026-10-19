## ****事件背景****

近日，深信服安全云脑捕获到一起H2Miner黑产组织的最新攻击事件。该组织使用新的C2服务器，通过 ** **Weblogic 远程执行漏洞****
，同时向主机植入Linux和Windows恶意脚本，最终执行门罗币挖矿程序。

H2Miner黑产组织（Kinsing挖矿僵尸网络）最早活跃在2019年底和2020年初，并一直持续更新活跃，主要是针对Linux服务器进行攻击，因守护进程kinsing而得名。该挖矿组织
** **擅长使用RCE漏洞进行攻击**** ， 曾在2020年5月和7月之间使用SaltStack RCE(CVE-2020-11651),
ThinkPHP5 RC, Solr dataimport RCE(CVE-2019-0193), Redis未授权RCE, Confluence
未授权RCE(CVE-2019-3396) 等高危漏洞进行攻击。本次捕获的攻击使用了Weblogic RCE
漏洞，攻击时间在10月30日前后，综合payload和攻击时间判断， ** **疑似利用了最新的漏洞 CVE-2020-14882/14883****
。和以往攻击目标相比，还 ** **增加了对Windows主机的攻击**** ，以恶意powershell脚本的方式实现Windows主机的挖矿。

##  ** **攻击流程****

![1605001333_5faa60751c21f8433f344.png!small?1605001332830](https://image.3001.net/images/20201110/1605001333_5faa60751c21f8433f344.png!small?1605001332830)

  

##  ** **详细分析****

###  ** **本次**** ** **攻击**** ** **事件**** ** **涉及的样本整理****

![1605001372_5faa609c033bbdeb743d2.png!small?1605001371609](https://image.3001.net/images/20201110/1605001372_5faa609c033bbdeb743d2.png!small?1605001371609)

###  ** **Windows挖矿样本的矿池和钱包地址****

![1605001381_5faa60a547cb3f7e05daa.png!small?1605001380849](https://image.3001.net/images/20201110/1605001381_5faa60a547cb3f7e05daa.png!small?1605001380849)

###  ** **Weblogic RCE 样本分析****

攻击者向主机发送一个构造好的数据包，将该数据包中的payload部分设在远程服务器xml文件中，漏洞成功触发后，主机会请求远程服务器的xml文件，并解析执行。本次攻击事件中，攻击组织同时向目标主机发送Linux和Windows的payload，漏洞利用成功后，对应的系统的payload的会被执行。

根据后台系统匹配的攻击时间分析，Oracle官方发布十月份补丁安全公告，以及近期的对此漏洞利用的威胁情报，判断出攻击者利用了CVE-2020-14882/14883漏洞：

![1605001437_5faa60dd83710c146919b.png!small?1605001437123](https://image.3001.net/images/20201110/1605001437_5faa60dd83710c146919b.png!small?1605001437123)

Windows的漏洞利用payload （wbw.xml）：

![1605001444_5faa60e42a0fc92c106bb.png!small?1605001443769](https://image.3001.net/images/20201110/1605001444_5faa60e42a0fc92c106bb.png!small?1605001443769)

Linux的漏洞利用payload (wb.xml)：

![1605001461_5faa60f50d8180827527c.png!small?1605001460593](https://image.3001.net/images/20201110/1605001461_5faa60f50d8180827527c.png!small?1605001460593)

###  ** **Windows 样本分析--1.ps1****

门罗币挖矿程序和配置文件的下载路径和保存路径：

![1605001474_5faa6102435a383db4685.png!small?1605001473851](https://image.3001.net/images/20201110/1605001474_5faa6102435a383db4685.png!small?1605001473851)

下载函数：

![1605001483_5faa610b62133dd474ad9.png!small?1605001482934](https://image.3001.net/images/20201110/1605001483_5faa610b62133dd474ad9.png!small?1605001482934)

下载挖矿程序：

![1605001491_5faa6113b380ba212842d.png!small?1605001491279](https://image.3001.net/images/20201110/1605001491_5faa6113b380ba212842d.png!small?1605001491279)

下载挖矿配置文件：

![1605001497_5faa611958fdb2cf8fe37.png!small?1605001496977](https://image.3001.net/images/20201110/1605001497_5faa611958fdb2cf8fe37.png!small?1605001496977)

更新程序和添加到计划任务：

![1605001515_5faa612b16cbcd1a25ddb.png!small?1605001514655](https://image.3001.net/images/20201110/1605001515_5faa612b16cbcd1a25ddb.png!small?1605001514655)

###  ** **Windows 样本分析--xmrig.exe****

编译时间为10月18日：

![1605001531_5faa613b30cf3e1c576c0.png!small?1605001530934](https://image.3001.net/images/20201110/1605001531_5faa613b30cf3e1c576c0.png!small?1605001530934)

为64位的门罗币，版本位6.4.0：

![1605001556_5faa615460605c928fb31.png!small?1605001555926](https://image.3001.net/images/20201110/1605001556_5faa615460605c928fb31.png!small?1605001555926)

###  ** **Windows 样本分析--config.json****

配置文件中有4个矿池地址，钱包地址都为4ASk4RhUyLL7sxE9cPyBiXb82ofekJg2SKiv4MKtCbzwHHLQxVVfVr4D4xhQHyyMTieSM5VUFGR9jZVR5gp6sa1Q2p8SahC：

![1605001583_5faa616fa57b2f484cbbe.png!small?1605001583303](https://image.3001.net/images/20201110/1605001583_5faa616fa57b2f484cbbe.png!small?1605001583303)

截止分析时该钱包的收益为0.0052XMR，从算力和收益来看，目前Windows主机上的感染量还不大：

![1605001599_5faa617f113e708043355.png!small?1605001598699](https://image.3001.net/images/20201110/1605001599_5faa617f113e708043355.png!small?1605001598699)

###  ** **Linux 样本分析--wb.sh****

对比了今年批露的威胁情报，针对Linux的恶意脚本在功能上没有太大的变化，主要是更新了C2服务器地址，主要功能为：禁用Selinux；卸载主机的安全软件阿里云骑士和腾讯云镜；清除挖矿竞品；下载执行恶意木马kinsing；添加到计划任务。kinsing主要功能为挖矿，爆破横向移动和远控。

其中，kinsing的样本没有做更新，md5校验值和7月批露的威胁情报一致（详情见参考链接），都为52ca5bc47c84a748d2b349871331d36a，而下载的服务器地址做了改变：

![1605001628_5faa619c166ae44a9a34e.png!small?1605001627895](https://image.3001.net/images/20201110/1605001628_5faa619c166ae44a9a34e.png!small?1605001627895)

VT 上的查询结果为7月的样本：

![1605001655_5faa61b7d72ee19eabe56.png!small?1605001655535](https://image.3001.net/images/20201110/1605001655_5faa61b7d72ee19eabe56.png!small?1605001655535)

添加到计划任务的部分，该部分的远程服务器地址也做了更新：

![1605001672_5faa61c85e352be9aebf8.png!small?1605001671997](https://image.3001.net/images/20201110/1605001672_5faa61c85e352be9aebf8.png!small?1605001671997)

卸载主机的安全软件阿里云骑士和腾讯云镜：

![1605001682_5faa61d23f3b4c10b008a.png!small?1605001681849](https://image.3001.net/images/20201110/1605001682_5faa61d23f3b4c10b008a.png!small?1605001681849)

清除竞品的挖矿程序：

![1605001703_5faa61e77953654b9759c.png!small?1605001703215](https://image.3001.net/images/20201110/1605001703_5faa61e77953654b9759c.png!small?1605001703215)![1605001711_5faa61ef9402fd1cd07bf.png!small?1605001711198](https://image.3001.net/images/20201110/1605001711_5faa61ef9402fd1cd07bf.png!small?1605001711198)清除竞品的计划任务：

![1605001849_5faa62798b98bcd3ef8f7.png!small?1605001849155](https://image.3001.net/images/20201110/1605001849_5faa62798b98bcd3ef8f7.png!small?1605001849155)

##  ** **IOC****

### url:

> http[:]//95.142.39.135/wb.xml
>
> http[:]//95.142.39.135/wbw.xml
>
> 95.142.39.135/wb.sh
>
> http[:]//95.142.39.135/1.ps1
>
> http[:]//95.142.39.135/kinsing
>
> http[:]//95.142.39.135/xmrig.exe
>
> http[:]//95.142.39.135/config.json
>
> http[:]//195.3.146.118/wb.sh
>
> http[:]//45.10.89.187/kinsing
>
> https[:]//bitbucket.org/tromdiga1/git/raw/master/kinsing
>
> https[:]//bitbucket.org/tromdiga1/git/raw/master/for
>
> http[:]//93.189.43.3/kinsing
>
> http[:]//93.189.43.3/kinsing2
>
> http[:]//93.189.43.3/spr.sh
>
> http[:]//93.189.43.3/spre.sh
>
> http[:]//93.189.43.3/a.sh
>
> http[:]//93.189.43.3/cron.sh
>
> http[:]//93.189.43.3/d.sh
>
> http[:]//93.189.43.3/ex.sh
>
> http[:]//93.189.43.3/h2.sh
>
> http[:]//93.189.43.3/j.sh
>
> http[:]//93.189.43.3/lf.sh
>
> http[:]//93.189.43.3/p.sh
>
> http[:]//93.189.43.3/pa.sh
>
> http[:]//93.189.43.3/s.sh
>
> http[:]//93.189.43.3/t.sh
>
> http[:]//93.189.43.3/tf.sh
>
> http[:]//93.189.43.3/al.sh

### ip:

> 95.142.39[.]135
>
> 195.3.146[.]118
>
> 45.10.89[.]187
>
> 93.189.43[.]3

### md5：

> 11e3bac0c37ed0bc89563b6a7106bcf9
>
> fe0f332ed847a25a18cd63dfdaf69908
>
> 19a43cb3d3518c71a8616e75890882eb
>
> 70000d52dc3ad153464dc41891c10439
>
> 57f0fdec4d919db0bd4576dc84aec752
>
> 8c6681daba966addd295ad89bf5146af
>
> 52ca5bc47c84a748d2b349871331d36a
>
> e3af308c4a4130dd77dc5772d801ebab
>
> bd405b37e69799492a58a50f5efc2725
>
> be17040e1a4eaf7e2df8c0273ff2dfd2
>
> 7f469ccecbf9d0573f0efd456e8e63a7
>
> 1b34c5bb3a06c4439b5da77c49f14cf7
>
> 41640173ddb6a207612ee052b48dd8be
>
> bac660c7aa23f4fda6c699c75b4b89f1
>
> e040303652c05dbf6469c9c3ce68031a
>
> 18dc6621299b855793bdeaad8ef5af23
>
> 1c489a326a4d37fbf02680bbd6f38b4f
>
> 255779cf6134f3ac5133f04868e3956c
>
> 639d87d54aa57371cc0bf82409503311
>
> ae9017bbeac57bc4de1ac5f59d59c519
>
> 831093a5a825ab096c2fc73a7a52bbf1
>
> d06e2a3f52043c3a3c3ecf1f406b8241

#  ** **手动修复**** ** **建议****

针对Linux 用户：

> （1）查找路径为/tmp/kinsing, /tmp/knsing2, /tmp/kdevtmpfsi的进程，结束并删除对应的文件；
>
> （2）查找crontab任务中包含“195.3.146.118”的相关项并删除
>
> （3）修复Weblogic等现存的漏洞

针对Windows 用户：

> （1）结束sysupdate.exe进程
>
> （2）删除%TMP%\sysupdate.exe, %TMP%\config.json, %TMP%\update.ps1文件
>
> （3）删除计划任务项 "Update service for Windows Service"
>
> （4）修复Weblogic等现存的漏洞

## 参考链接

[
_https://guanjia.qq.com/news/n3/2581.html_](https://guanjia.qq.com/news/n3/2581.html)(Linux服务器遭遇挖矿蠕虫攻击，已有数千台服务器中招)

[
_https://blog.csdn.net/god_zzZ/article/details/109445728_](https://blog.csdn.net/god_zzZ/article/details/109445728)(漏洞利用介绍)

[ _https://www.oracle.com/security-alerts/cpuoct2020.html_](https://www.oracle.com/security-alerts/cpuoct2020.html)(Oracle官方发布十月份补丁安全公告)


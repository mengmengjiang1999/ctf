# 前言

红队在攻防演练中一般使用钓鱼实现突破边界，蓝队通过钓鱼实现溯源反制，但是都离不开一个好的免杀马，这里分享一下自己的免杀过程，过火绒、360杀毒、Windows
defender以及赛门铁克等主流杀软都没问题。

# 杀软工作原理

杀软的查杀方式有多种，比如特征识别，是基于各个厂商收集的病毒样本，依据病毒样本提取的病毒特征，所以杀软的能力在一定程度上也取决于病毒库的大小，这种基于特征识别一般是基于静态。启发式的工作原理基本上可以定义为动态查杀或者是机器学习方法的一种查杀手段，会依据可能执行程序或者关注应用系统重要区域行为而做出的查杀行为。

# 免杀手段

修改特征码，可以根据污点检测的方式定位到触发杀软规则的病毒样本特征，修改明显的特征在一定程度上是可以实现免杀的。

花指令免杀，在程序 `shellcode`或特征代码区域增添垃圾指令，增加的垃圾指令不会影响文件执行，在动态查杀或者文件hash对比是校验会不一致。

加壳，比如upx加壳等，一般文件落地后对比哈希值也可绕过杀软。

二次编译，一般用于对`shellcode`进行二次编译bypass杀软。

poweshell免杀，但是一般防护软件或者系统本身正常调用powershell应用程序的时候都会产生告警，一般的安全设备是过不了的，需要在命令上使用手段绕过安全设备监测。

# 免杀

CS生成payload

添加监听器，生成payload

![image-20220725164216877.png](https://image.3001.net/images/20220802/1659422526_62e8c73e466653b5b7239.png!small)

下载`go-strip.exe`,混淆二进制go编译信息

下载地址

> <https://cdn.githubjs.cf/boy-hack/go-strip/releases/download/v3.0/go-> strip_0.3.4_windows_amd64.zip>

![image-20220722172118310.png](https://image.3001.net/images/20220802/1659422527_62e8c73f06b5dfaa95aab.png!small)

运行脚本`bypass`

> go run main.go

![image-20220729094126135.png](https://image.3001.net/images/20220802/1659422527_62e8c73fc05844690eed0.png!small)

核心内容就是加密方式

![image-20220727160320295.png](https://image.3001.net/images/20220802/1659422528_62e8c7406f8d48180b8d2.png!small)

`shellcode`二层加密。

① 网安学习成长路径思维导图  
② 60+网安经典常用工具包  
③ 100+SRC漏洞分析报告  
④ 150+网安攻防实战技术电子书  
⑤ 最权威CISSP 认证考试指南+题库  
⑥ 超1800页CTF实战技巧手册  
⑦ 最新网安大厂面试题合集（含答案）  
⑧ APP客户端安全检测指南（安卓+IOS）

这里没有直接放源码，因为担心样本被打标签，这里推荐几个项目，这里的话尽量使用go不建议python

> <https://github.com/TideSec/BypassAntiVirus>
>
> <https://github.com/admin360bug/bypass>
>
> <https://github.com/hack2fun/BypassAV/blob/master/bypass.cna>

这里我修改了生成的exe。安装火绒，查杀

![image-20220727115914107.png](https://image.3001.net/images/20220802/1659422529_62e8c74130e298161858b.png!small)

![image-20220727115938733.png](https://image.3001.net/images/20220802/1659422529_62e8c741dad5f7be8f74a.png!small)

CS上线

![image-20220727115808577.png](https://image.3001.net/images/20220802/1659422530_62e8c7429c53212fc5c85.png!small)

# 加壳

另外再加壳测试。地址

> <https://upx.en.softonic.com/>

简单的压缩壳

![image-20220727151209573.png](https://image.3001.net/images/20220802/1659422531_62e8c7436068b0442bace.png!small)

> upx.exe -f Go_bypass.exe

![image-20220727152839033.png](https://image.3001.net/images/20220802/1659422532_62e8c7442d6aad847133a.png!small)

加壳后生辰的exe文件大小为`406KB`

![image-20220727152537410.png](https://image.3001.net/images/20220802/1659422532_62e8c744e60222c3f4a1f.png!small)

可以看到加壳之前的文件大小为`1011kb`

![image-20220727152715871.png](https://image.3001.net/images/20220802/1659422533_62e8c745bb7a45404de24.png!small)

修改加壳后的文件名为`upx_Go_bypass`方便确认上线状态

![image-20220727153157216.png](https://image.3001.net/images/20220802/1659422534_62e8c746726b61f11ccb0.png!small)

成功上线，继续查看加壳后的免杀效果

![image-20220727153849744.png](https://image.3001.net/images/20220802/1659422535_62e8c74730fa34f453dce.png!small)

此时火绒对于有加壳前和加壳后的文件都未报毒

![image-20220727153716346.png](https://image.3001.net/images/20220802/1659422535_62e8c747df83324fd599c.png!small)

虽然加壳前的报毒了，但是加壳后的未报毒。

![image-20220727154425252.png](https://image.3001.net/images/20220802/1659422536_62e8c748b710cf277656f.png!small)

赛门铁克也未报毒，其它杀软不放图了。但是需要注意的是别使用 **云沙箱** 检测。

# 总结

多测试总会有新发现，实践起来相对稍微容易一点儿，不过需要注意免杀之后的效果是最重要的。


## 1.简介

近期在HFish蜜罐搭建起来之后，
便不断有各种攻击蜂拥而入，其中笔者发现一起近期的通过redis蜜罐捕获的恶意挖矿活动。![1607155783_5fcb404740e921bf1ecd8.png!small?1607155781953](https://image.3001.net/images/20201205/1607155783_5fcb404740e921bf1ecd8.png!small?1607155781953)

## 2.详情分析

### 2.1样本简介

样本名称|  
  
---|---  
pm.sh| 下载ELF文件  
png| 下载miner2挖矿程序  
miner2|

挖矿程序  
  
### 2.2样本内容

### pm.sh

![1607158048_5fcb492028bd6ae927722.png!small?1607158046854](https://image.3001.net/images/20201205/1607158048_5fcb492028bd6ae927722.png!small?1607158046854)

主要为通过url http[:]//a.powerofwish.com/png 下载文件png,并保存再/var/lib/png路径下。

### png文件

png文件为upx加壳的ELF文件。

![1607158264_5fcb49f8cbe4e380fb4b0.png!small?1607158263586](https://image.3001.net/images/20201205/1607158264_5fcb49f8cbe4e380fb4b0.png!small?1607158263586)

通过upx 脱壳处理后，用ida打开如下：  
![1607158318_5fcb4a2ed18451ba0a370.png!small?1607158317572](https://image.3001.net/images/20201205/1607158318_5fcb4a2ed18451ba0a370.png!small?1607158317572)主要作用有：

1.删除var/lib目录下的相关文件，pc|cc|px|1.jpg|pm.sh等文件![1607158404_5fcb4a8409887121ca513.png!small?1607158402754](https://image.3001.net/images/20201205/1607158404_5fcb4a8409887121ca513.png!small?1607158402754)

2.ssh key

![1607158572_5fcb4b2cc93597b2538d4.png!small?1607158571557](https://image.3001.net/images/20201205/1607158572_5fcb4b2cc93597b2538d4.png!small?1607158571557)

具体内容如下(其中发现敏感词汇c4,已经使用[c][4]代替)：

>
> AAAAB3NzaC1yc2EAAAADAQABAAABAQC/cjOtl7EKcIPBchQkU/qKSGbe7A9MTvrwqBc6trso6UMBpeTWY8loM1082h4HZ4daNJ1S8yB57PtOHSUwG//SD5ahYfOTOInQpU5p7mnczql9UPXO68VXukBpbmjueEwVtXXFnd/9kZzqBroS9zMakKh53URPoKus4d/V7Ct5ecPSo2WDRJDLbewE9ojb+v4R8[C][4]xartjNLsyUXRwqgk1B6LKoLHXWUU55+LoaecFTBoBil+DP2Wxl2RhFaGCHItInwPgmtigYcOH/zMePw+aiXsYMbSzNtQswh3E0h7bpxq7hgilFTglfmrZybF45enkjwr9cfsWpkQ6NQ1nONA9

3.通过url http[:]//a.powerofwish.com/miner2下载miner2挖矿文件保存在/tmp/miner2路径下。

![1607158755_5fcb4be3a78e91de6c97f.png!small?1607158754347](https://image.3001.net/images/20201205/1607158755_5fcb4be3a78e91de6c97f.png!small?1607158754347)

4.kill相关挖矿进程

![1607158967_5fcb4cb712d7cbffb575e.png!small?1607158965800](https://image.3001.net/images/20201205/1607158967_5fcb4cb712d7cbffb575e.png!small?1607158965800)

### miner2文件

1.miner2文件同为upx加壳的挖矿文件。

![1607160501_5fcb52b56bbc5af65f0ce.png!small?1607160500231](https://image.3001.net/images/20201205/1607160501_5fcb52b56bbc5af65f0ce.png!small?1607160500231)

2.通过upx脱壳后，用ida打开后如下：其实际为挖矿软件

![1607160636_5fcb533c6c7a74ac48555.png!small?1607160635177](https://image.3001.net/images/20201205/1607160636_5fcb533c6c7a74ac48555.png!small?1607160635177)

  

3..发现糖链挖矿sugar.ss.dxpool.com:3366，其中钱包地址为

> sugar1qddpk0wgqtgufenz6z9zh4cjgrehk8ezud42p5q

![1607160244_5fcb51b4b575a02bfb4cb.png!small?1607160243470](https://image.3001.net/images/20201205/1607160244_5fcb51b4b575a02bfb4cb.png!small?1607160243470)

4.发现多个捐赠钱包的地址

> BTC donation : 36m3Gcbpn4QU4iGibZox378VdEJvjx7Z7J7Tr
>
>  
>
>
> SUGAR donation: 36msugar1qcu07vm47ceh7lec3umx7nv7e8t
>
>  
>
>
> SUGAR donation: sugar1qcu07vm47ceh7lec3umx7nv7e8tm8r8zw4l2uy
>
>  
>

![1607160659_5fcb53532b3174a7d46de.png!small?1607160657900](https://image.3001.net/images/20201205/1607160659_5fcb53532b3174a7d46de.png!small?1607160657900)

  

## 3.防护建议

1.修复redis未授权访问漏洞

2.查看/var/lib/png | var/lib/pm | /tmp/miner2
等文件是否存在，存在删除，并查看定时任务是否存在不明定时任务。因为一般挖矿脚本为了自身的保活和更新都会将自己写入到定时任务。

  

## 4.总结

在蜜罐搭建起来之后，能够抓取到一些恶意的挖矿攻击活动，近期的一些恶意攻击的总览如下：

其中redis恶意攻击所含有的信息量比较多。

![1607161444_5fcb566422615815b74b9.png!small?1607161442900](https://image.3001.net/images/20201205/1607161444_5fcb566422615815b74b9.png!small?1607161442900)

近期的top10恶意攻击者ip97%来自德国。

![1607161563_5fcb56dbd4ac964c78540.png!small?1607161562584](https://image.3001.net/images/20201205/1607161563_5fcb56dbd4ac964c78540.png!small?1607161562584)

## IOC

url|  
  
---|---  
http[:]//d.powerofwish.com/pm.sh|  
  
http[:]//a.powerofwish.com/png|  
  
http[:]//a.powerofwish.com/miner2|  
  
md5|  
  
1bd78e75628e240bca853ff7d03deb74| pm.sh  
8f6e5795ab79d72b2a12f3069001eb60| png  
a57d04bd2a3d6d1f28caa2c5a128f572| miner2  
domain|  
  
a[.]powerofwish[.]com|  
  
  
  


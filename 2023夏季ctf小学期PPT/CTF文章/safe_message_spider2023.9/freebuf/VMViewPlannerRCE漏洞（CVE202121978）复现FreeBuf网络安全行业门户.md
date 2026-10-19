## 0x00简介

View Planner是VMware官方推出的一款针对view桌面的测试工具，通过这个测试工具可以估算出在指定的应用环境下可以发布多少个view桌面。

## 0x01影响版本

VMware View Planner <= 4.6.0

## 0x02 环境搭建

1，这里我们直接下载镜像ova，地址

https://my.vmware.com/en/group/vmware/downloads/details?downloadGroup=VIEW-PLAN-460&productId=1067&rPId=53394

![1618967765_607f7cd58ecfcc8d9dce6.png!small?1618967766848](https://image.3001.net/images/20210421/1618967765_607f7cd58ecfcc8d9dce6.png!small?1618967766848)

2，这里也可以从我们的云盘下载，下载地址：

https://pan.baidu.com/s/1xtxzEtDtGNQhGXNMo5YW9A 密码为：dota

![1618967770_607f7cdab6dcd21f07ec8.png!small?1618967771919](https://image.3001.net/images/20210421/1618967770_607f7cdab6dcd21f07ec8.png!small?1618967771919)

3，直接导入到虚拟机

![1618967773_607f7cddd40f17bead27a.png!small?1618967775083](https://image.3001.net/images/20210421/1618967773_607f7cddd40f17bead27a.png!small?1618967775083)

![1618967777_607f7ce1c7261f3678814.png!small?1618967779077](https://image.3001.net/images/20210421/1618967777_607f7ce1c7261f3678814.png!small?1618967779077)

![1618967780_607f7ce49f641486c23ff.png!small?1618967782080](https://image.3001.net/images/20210421/1618967780_607f7ce49f641486c23ff.png!small?1618967782080)

![1618967783_607f7ce7aa408aa618ac2.png!small?1618967785000](https://image.3001.net/images/20210421/1618967783_607f7ce7aa408aa618ac2.png!small?1618967785000)

4，导入完成的界面

![1618967787_607f7ceb01412d5efa1be.png!small?1618967788234](https://image.3001.net/images/20210421/1618967787_607f7ceb01412d5efa1be.png!small?1618967788234)

5，访问地址

![1618967790_607f7cee24f1f938f295a.png!small?1618967791332](https://image.3001.net/images/20210421/1618967790_607f7cee24f1f938f295a.png!small?1618967791332)

## 0x03漏洞复现

1，下载exp，地址：https://github.com/skytina/CVE-2021-21978

![1618967793_607f7cf1b102c84b44f9f.png!small?1618967795049](https://image.3001.net/images/20210421/1618967793_607f7cf1b102c84b44f9f.png!small?1618967795049)

2、 运行exp

python3 CVE-2021-21978.py https://172.16.1.143/

![1618967798_607f7cf62d707ef85a5d3.png!small?1618967799392](https://image.3001.net/images/20210421/1618967798_607f7cf62d707ef85a5d3.png!small?1618967799392)

3，访问shell地址

![1618967800_607f7cf8e4b76c864b04f.png!small?1618967802089](https://image.3001.net/images/20210421/1618967800_607f7cf8e4b76c864b04f.png!small?1618967802089)

![1618967804_607f7cfc1610f0565445d.png!small?1618967805223](https://image.3001.net/images/20210421/1618967804_607f7cfc1610f0565445d.png!small?1618967805223)

## 0x04修复建议

1、升级VMware View Planner 至最新版本


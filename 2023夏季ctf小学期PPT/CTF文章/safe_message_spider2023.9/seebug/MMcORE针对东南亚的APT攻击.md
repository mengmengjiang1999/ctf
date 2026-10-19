**作者: Yenn_  
原文链接:[Wei's
Blog](https://www.weisblog.club/2020/04/22/MMcORE%E9%92%88%E5%AF%B9%E4%B8%9C%E5%8D%97%E4%BA%9A%E7%9A%84APT%E6%94%BB%E5%87%BB/#%E5%9F%BA%E6%9C%AC%E4%BF%A1%E6%81%AF)**

## 基本信息

File Name | File Size | File Type | MD5  
---|---|---|---  
| 76,800 Byte |  | bbe4ae55f828e020c32e215f4d152cc3  
  
## 查壳

[![img](https://images.seebug.org/content/images/2021/03/19/1616119912000-1gtjlu.png-w331s)](http://ww1.sinaimg.cn/large/006o5z8lgy1ge2wmym7hhj30ge09jwfm.jpg)

无壳

## 详细分析

在运行后，动态行为中未发现任何异常，可能有对抗检测的操作

[![img](https://images.seebug.org/content/images/2021/03/19/1616119912000-2lzbij.png-w331s)](http://ww1.sinaimg.cn/large/006o5z8lgy1ge2wj6bhf8j30h201b3yg.jpg)

拉进IDA，来到MAIN函数

[![img](https://images.seebug.org/content/images/2021/03/19/1616119912000-3msaoj.png-w331s)](http://ww1.sinaimg.cn/large/006o5z8lgy1ge2wnhqp6rj30bf09f3yw.jpg)

[![img](https://images.seebug.org/content/images/2021/03/19/1616119912000-4sgdfu.png-w331s)](http://ww1.sinaimg.cn/large/006o5z8lgy1ge2y5c6g31j30eb01c3yd.jpg)

### 对抗检测

先取得一次当前激活窗口名，每隔1000ms检测一次当前活动的窗口，然后比较两次是否一样，如果一样则进入死循环，一直查找窗口

[![img](https://images.seebug.org/content/images/2021/03/19/1616119912000-5asucq.png-w331s)](http://ww1.sinaimg.cn/large/006o5z8lgy1ge2y6qq76yj30ik0c6js1.jpg)

然后利用memset函数，将一片内存置0，然后在置0的一块内存中得出一个DLL名，snxhk.dll

是杀毒软件Avast的一个模块

[![img](https://images.seebug.org/content/images/2021/03/19/1616119913000-6dmyud.png-w331s)](http://ww1.sinaimg.cn/large/006o5z8lgy1ge2y7sjf4aj30ev04it8o.jpg)

[![img](https://images.seebug.org/content/images/2021/03/19/1616119913000-7icomp.png-w331s)](http://ww1.sinaimg.cn/large/006o5z8lgy1ge2y84a0gyj30370120el.jpg)

### 解密字符串

使用memset置0内存，再解密出一个url dailysync.zapto.org

[![img](https://images.seebug.org/content/images/2021/03/19/1616119913000-8azbij.png-w331s)](http://ww1.sinaimg.cn/large/006o5z8lgy1ge2yhiktpuj30fa09eq3a.jpg)

[![img](https://images.seebug.org/content/images/2021/03/19/1616119913000-9qcmdd.png-w331s)](http://ww1.sinaimg.cn/large/006o5z8lgy1ge2ygigd5ej30es021dfo.jpg)

解密出一个jpg路径，/fancycumti/combidation/scale.jpg

[![img](https://images.seebug.org/content/images/2021/03/19/1616119913000-10woupa.png-w331s)](http://ww1.sinaimg.cn/large/006o5z8lgy1ge2ylcivtuj30iv0hbt9j.jpg)

[![img](https://images.seebug.org/content/images/2021/03/19/1616119913000-11bdpeq.png-w331s)](http://ww1.sinaimg.cn/large/006o5z8lgy1ge2ym7bxd8j30go03cwee.jpg)

将前面得出的URL和jpg路径转换为宽字符

[![img](https://images.seebug.org/content/images/2021/03/19/1616119914000-12qsoqt.png-w331s)](http://ww1.sinaimg.cn/large/006o5z8lgy1ge2yy1jaffj30g3012t8m.jpg)

然后进入一个死循环，生成一个随机数，再利用生成的随机数Sleep

[![img](https://images.seebug.org/content/images/2021/03/19/1616119914000-13qtpuv.png-w331s)](http://ww1.sinaimg.cn/large/006o5z8lgy1ge2yyo1k17j30e901y0sm.jpg)

### 请求资源

加载wininet.dll，wininet.dll是windows应用程序中的网络相关模块

[![img](https://images.seebug.org/content/images/2021/03/19/1616119914000-14uvgeh.png-w331s)](http://ww1.sinaimg.cn/large/006o5z8lgy1ge2z1tzb5ej30e200vwea.jpg)

利用Getprocaddress，获取大量函数地址

[![img](https://images.seebug.org/content/images/2021/03/19/1616119914000-15ywycj.png-w331s)](http://ww1.sinaimg.cn/large/006o5z8lgy1ge2zcmo9bfj30er037t8u.jpg)

对dailysync.zapto.org/fancycumti/combidation/scale.jpg发起http请求

[![img](https://images.seebug.org/content/images/2021/03/19/1616119914000-16vcmot.png-w331s)](http://ww1.sinaimg.cn/large/006o5z8lgy1ge43rhzce4j30un0dn3zt.jpg)

### 加载资源

从远程服务器中请求一个jpg资源，然后读取jpg的数据

[![img](https://images.seebug.org/content/images/2021/03/19/1616119914000-17sdyfh.png-w331s)](http://ww1.sinaimg.cn/large/006o5z8lgy1ge43va5auqj30rz0gbwfh.jpg)

修改申请内存的页属性，然后创建新线程，执行读取到的内容

[![img](https://images.seebug.org/content/images/2021/03/19/1616119914000-18nkqtz.png-w331s)](http://ww1.sinaimg.cn/large/006o5z8lgy1ge43x10o1fj30nm0753z1.jpg)

dailysync.zapto.org/fancycumti/combidation/scale.jpg已经挂了，目前为止还没找到可下载的样本，后面的暂时分析不了。

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1517/>


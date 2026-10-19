**漏洞简介：**

 **WordPress的微信广播插件1.2.0及更早版本允许通过Image.php url参数进行目录遍历。**

 ****

 **** **漏洞环境：**

 **春秋云镜中的漏洞靶标，CVE编号为CVE-2018-16283**

 ****

 **漏洞复现：**

 **访问漏洞环境，没有发现可利用的点。**

**![1689433409_64b2b541747800be725cc.png!small](https://image.3001.net/images/20230715/1689433409_64b2b541747800be725cc.png!small)**

 ****

 **根据cve介绍，找到目录遍历的文件**

 **路径 wp-content/plugins/wechat-broadcast/wechat/Image.php?url=**

**![1689433415_64b2b54751e075d7f8546.png!small](https://image.3001.net/images/20230715/1689433415_64b2b54751e075d7f8546.png!small)**

 ****

 ****

 **开启代理，打开burpsuite抓取访问文件的数据包，放到重放器中**

**![1689433423_64b2b54f59730b173252b.png!small](https://image.3001.net/images/20230715/1689433423_64b2b54f59730b173252b.png!small)**

 ****

 ****

 **这里需要获取flag，所以利用php伪协议获取文件**

![1689433429_64b2b5559b28d74eca3ae.png!small](https://image.3001.net/images/20230715/1689433429_64b2b5559b28d74eca3ae.png!small)


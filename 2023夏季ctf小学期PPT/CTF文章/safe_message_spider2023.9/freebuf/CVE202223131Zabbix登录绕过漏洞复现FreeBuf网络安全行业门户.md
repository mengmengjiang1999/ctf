## 1.漏洞介绍

zabbix能监视各种网络参数，保证[服务器系统](https://baike.baidu.com/item/%E6%9C%8D%E5%8A%A1%E5%99%A8%E7%B3%BB%E7%BB%9F/2997788)的安全运营；并提供灵活的通知机制以让[系统管理员](https://baike.baidu.com/item/%E7%B3%BB%E7%BB%9F%E7%AE%A1%E7%90%86%E5%91%98/1503845)快速定位/解决存在的各种问题。等于说是个运维的软件，默认开放端口为10051，nmap扫描结果server项为zabbix-trapper

## 2.漏洞发现

（1）fofa资产收集语法

> app="ZABBIX-监控系统" && body="saml"

（2）2022高版本漏洞被修复，具体判断有没有漏洞看底下年限，只要不是2022一般都能复现

![](https://image.3001.net/images/20220722/1658419404_62d978cc85e03d8890e6b.png!small)

  

## 漏洞复现

（1）浏览器审查元素查看当前的cookie

![](https://image.3001.net/images/20220722/1658419506_62d97932beac0434be631.png!small)（2）用base64解密这个值，然后在解密完成的值签名添加

"saml_data": {"username_attribute": "Admin"},

变成这样

![](https://image.3001.net/images/20220722/1658419702_62d979f6c869c76ea345a.png!small)（3）把这个值重新base64编码后，用浏览器审查元素替换原来的cookie后点击登入

![](https://image.3001.net/images/20220722/1658419817_62d97a69307ccb8337e5b.png!small)（4）越权成功，无账户进入后台（码住）

![](https://image.3001.net/images/20220722/1658419847_62d97a87941cc48bf33a3.png!small)


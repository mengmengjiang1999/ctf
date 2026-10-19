****首先准备window server 2003r2 +iis6.0****

 ** **然后搭建一个网站（需要启用webDAR）****

 ** **一、搭建网站****

 ** **初始页面****

![1609938889_5ff5b7c975d013b5804c2.png!small](https://image.3001.net/images/20210106/1609938889_5ff5b7c975d013b5804c2.png!small)

 ** **选择存放路径****

![1609938999_5ff5b837bdb7d44c6d31d.png!small](https://image.3001.net/images/20210106/1609938999_5ff5b837bdb7d44c6d31d.png!small)

 ** **权限给的大一点****

![1609939019_5ff5b84ba12db9affe914.png!small](https://image.3001.net/images/20210106/1609939019_5ff5b84ba12db9affe914.png!small)

 ** **添加一个可以解析的asp文档****

![1609939034_5ff5b85aac97b9e9e5322.png!small](https://image.3001.net/images/20210106/1609939034_5ff5b85aac97b9e9e5322.png!small)

![1609939043_5ff5b863c66515cb8ad7f.png!small](https://image.3001.net/images/20210106/1609939043_5ff5b863c66515cb8ad7f.png!small)

 ** **网站添加一个erverone权限****

![1609939059_5ff5b873387605beef8b1.png!small](https://image.3001.net/images/20210106/1609939059_5ff5b873387605beef8b1.png!small)

![1609939073_5ff5b881a35515a190561.png!small](https://image.3001.net/images/20210106/1609939073_5ff5b881a35515a190561.png!small)

 ** **二、漏洞扫描****

![1609939092_5ff5b8944ecc3734932f0.png!small](https://image.3001.net/images/20210106/1609939092_5ff5b8944ecc3734932f0.png!small)

 ** **http://192.168.0.178:80|Microsoft-IIS/6.0|http://192.168.0.178/20213705113750.txt|webdva漏洞 来源模式一****

 ** **咱们到靶机中查看发现网站根目录下一个文件****

![1609939107_5ff5b8a3c7e6cb2e32e09.png!small](https://image.3001.net/images/20210106/1609939107_5ff5b8a3c7e6cb2e32e09.png!small)

 ** **然后结合另一个工具进行配合攻击****

 ** **请求该文件发现请求成功****

![1609939124_5ff5b8b47f1c134506b25.png!small](https://image.3001.net/images/20210106/1609939124_5ff5b8b47f1c134506b25.png!small)

 ** **然后再利用put方式进行上传一句话木马****

![1609939137_5ff5b8c171421feee0370.png!small](https://image.3001.net/images/20210106/1609939137_5ff5b8c171421feee0370.png!small)

 ** **咱们在网站根目录查看，发现写入的一句话存放在刚才指定访问的文件中****

![1609939153_5ff5b8d160154e4199618.png!small](https://image.3001.net/images/20210106/1609939153_5ff5b8d160154e4199618.png!small)

 ** **发现上传成功，然后再利用move协议进行更改名称****

![1609939167_5ff5b8df213f1a9572be7.png!small](https://image.3001.net/images/20210106/1609939167_5ff5b8df213f1a9572be7.png!small)

 ** **然后在我们攻击机中进行访问****

 ** **然后菜刀或者蚂蚁剑进行连接一下****

![1609939181_5ff5b8ed4db034c170e62.png!small](https://image.3001.net/images/20210106/1609939181_5ff5b8ed4db034c170e62.png!small)

 ** **发现成功连接****

![1609939193_5ff5b8f95bd64725eb503.png!small](https://image.3001.net/images/20210106/1609939193_5ff5b8f95bd64725eb503.png!small)

![1609939201_5ff5b9016e81bfb89d6b3.png!small](https://image.3001.net/images/20210106/1609939201_5ff5b9016e81bfb89d6b3.png!small)


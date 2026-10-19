![1619342939_6085365b6f27ceb8915eb.png!small?1619342939287](https://image.3001.net/images/20210425/1619342939_6085365b6f27ceb8915eb.png!small?1619342939287)

1.打开靶场即可看到S2-013的页面，访问主页字体发现有cookie，且在URL后输入/struts/webconsole.html，即可判断![1619342953_6085366949b00919d82a6.png!small?1619342953413](https://image.3001.net/images/20210425/1619342953_6085366949b00919d82a6.png!small?1619342953413)![1619342957_6085366dbbf971b6ed1a8.png!small?1619342957996](https://image.3001.net/images/20210425/1619342957_6085366dbbf971b6ed1a8.png!small?1619342957996)![1619342961_608536715b7e2641013dd.png!small?1619342961126](https://image.3001.net/images/20210425/1619342961_608536715b7e2641013dd.png!small?1619342961126)

2.可以去github上查找关于struts2漏洞的利用工具，利用工具直接进行探测

    
    
    python3 Struts2Scan.py -u http://219.153.49.228:46866/python3 Struts2Scan.py -u http://219.153.49.228:46866/ -n S2-016 -e

![1619342973_6085367da8c1d3b98da62.png!small?1619342973529](https://image.3001.net/images/20210425/1619342973_6085367da8c1d3b98da62.png!small?1619342973529)

3.执行相关命令，找到key.txt，得到我们想要的key![1619343007_6085369f5a023b165195c.png!small?1619343007161](https://image.3001.net/images/20210425/1619343007_6085369f5a023b165195c.png!small?1619343007161)

4.Struts2漏洞判断方法

> （1）通过网站页面的回显错误消息来判断，页面不回显错误消息时则无效。
>
> （2）通过网页后缀来判断，如.do .action，有可能是不准的，因为JBOSS系统也是以DO为后缀，虽然JBoss和tomcat不是一回事。
>
> （3）判断/struts/webconsole.html 是否存在来进行判断，需要devMode为true。

5.形成原理

解释一、Struts2标签库中的url标签和a标签的includeParams这个属性，代表显示请求访问参数的含义，一旦它的值被赋予ALL或者GET或者
POST，就会显示具体请求参数内容。按照正常的需求，把参数urlEncode一下也就够了，
问题在于，struts竟然多做了一步，居然把参数做了OGNL解析！

解释二、s:url和s:a标记都提供includeparams属性。该属性的主要作用域是了解包含或不包含http://request参数的内容。INCLUDEParams的允许值为：none-在URL中不包含任何参数（默认），get-仅在URL中包含get参数，all-在URL中同时包含get和post参数。当INCLUDEParams被赋予了以上参数，struts会进行OGNL解析

6.修复方法

> 1.不启用Struts2-struts1-plugin插件。
>
> 2.升级struts2的版本到最新Apache Struts 2.5.10.1版本。
>
> 3.始终使用资源键，而不是将原始消息传递给ActionMessage。
>
> 4.不使用Struts2目录下的showcase.war

## 注意：

刚使用Struts2-Scan时可能会报错，只需要修改一下就可以![1619343066_608536da6733c230f0abd.png!small?1619343066184](https://image.3001.net/images/20210425/1619343066_608536da6733c230f0abd.png!small?1619343066184)


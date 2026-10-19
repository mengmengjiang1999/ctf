靶标介绍：WSO2文件上传漏洞(CVE-2022-29464)是Orange
Tsai发现的WSO2上的严重漏洞。该漏洞是一种未经身份验证的无限制任意文件上传，允许未经身份验证的攻击者通过上传恶意JSP文件在WSO2服务器上获得RCE。

漏洞复现过程

1.开启镜像环境，访问该站WSO2https://eci-2zecky5rxu3tzqybfsu3.cloudeci1.ichunqiu.com:9443/carbon/admin/login.jsp

![1689048589_64acd60d64ac7252da843.png!small](https://image.3001.net/images/20230711/1689048589_64acd60d64ac7252da843.png!small)

2.抓包且构造漏洞利用的请求包，回应包中出现如下数字即上传文件成功（此处上传的是wavesky.jsp）

![1689048599_64acd617a14b293d59bee.png!small](https://image.3001.net/images/20230711/1689048599_64acd617a14b293d59bee.png!small)

![1689048608_64acd620cc79a84add22c.png!small](https://image.3001.net/images/20230711/1689048608_64acd620cc79a84add22c.png!small)

3.可以执行Windows命令查看根目录下的flag

![1689048614_64acd62686d3de4396b37.png!small](https://image.3001.net/images/20230711/1689048614_64acd62686d3de4396b37.png!small)

![1689048624_64acd630c1c531aa40082.png!small](https://image.3001.net/images/20230711/1689048624_64acd630c1c531aa40082.png!small)


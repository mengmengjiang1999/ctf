### 1.记得有段时间刷抖音遇见一个大师，那天开始，我悟了。谁曾想左脚踩右脚可以螺旋直接升天？

记得今年不知道几月份，火线平台放开了，但由于工作原因一直征战于召唤师峡谷，实属是太忙，上周聊胜于无的我打开了百度，发现居然“充钱了”，ok，进入一看原先刚注册时只有点点资产，现在已有许多，于是便有了捡漏洞的想法。。

### 2.Huoxian爬虫+httpscan筛选+Auto_man自动化扫描

首先是Huoxian爬虫的编写，直接调用火线直接的资产工具的json接口，通过简单的requests请求+re正则即可完成，header头部加入cookie+token验证。

![1605174230_5fad03d62a9269e5c2461.png!small?1605174229191](https://image.3001.net/images/20201112/1605174230_5fad03d62a9269e5c2461.png!small?1605174229191)

![1605174300_5fad041c20eabc412e195.png!small?1605174299102](https://image.3001.net/images/20201112/1605174300_5fad041c20eabc412e195.png!small?1605174299102)

然后就是爬取到的url资产验证筛选了，说实话，这里本带师确实花了许些时间，直到现在还是不满意，因为对于一个想捡漏洞的菜鸟来说，自然是url资产搜集的越多越好，资产筛选的越细越好，但写着写着bug越来越多，直到一天，我悟了。带师告诉我，以你现在的水平只能捡垃圾还捡不到漏洞，我问大师为什么，大师笑而不语，指了指我的上空，那一刻，我已悟了。

相信很多用子域名爆破搜集的资产用很多是重复的资产，所有我对于资产的筛选加入了标题和响应包大小的筛选，但后来我发现某些url请求后要执行js跳转才能访问最终的页面，导致遗失了很多url资产，然后我发现新大陆request_html这个新模块，然后发现方法调用的时候于多线程冲突了，然后就没有然后了，先用requests补补将就着用吧

![1605175148_5fad076c46a118ea3c8de.png!small?1605175147292](https://image.3001.net/images/20201112/1605175148_5fad076c46a118ea3c8de.png!small?1605175147292)

###
![1605175182_5fad078e023a30c37e99c.png!small?1605175181012](https://image.3001.net/images/20201112/1605175182_5fad078e023a30c37e99c.png!small?1605175181012)

然后就是auto_man这个脚本了，github上链接360爬虫和xray扫描的一款脚本，配置好文件路径

![1605175327_5fad081fc1016b436779a.png!small?1605175326881](https://image.3001.net/images/20201112/1605175327_5fad081fc1016b436779a.png!small?1605175326881)

捡垃圾开启，一个网站都捡的到洞，我直接放10000个上去，不直接起飞？听懂掌声。

![1605175292_5fad07fc7e36f2c970dd1.png!small?1605175291462](https://image.3001.net/images/20201112/1605175292_5fad07fc7e36f2c970dd1.png!small?1605175291462)

  

![timg?image&quality=80&size=b9999_10000&sec=1605188237704&di=c72f01eada2dd73a65a1d4b789836519&imgtype=0&src=http%3A%2F%2Fp3.itc.cn%2Fq_70%2Fimages03%2F20201111%2Fb9eb8d1a60144570b64265f17456ff8d.jpeg](https://image.3001.net/images/20201112/1605178542.jpeg!small)

  

github链接

<https://github.com/defaul0t/http_scan>  

<https://github.com/zhuxianjin/Auto_man>  

  

  


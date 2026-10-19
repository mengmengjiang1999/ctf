**作者：Badcode@知道创宇404实验室  
时间：2019年4月8日  
English Version: <https://paper.seebug.org/886/>**

看到官方发布了预警，于是开始了漏洞应急。漏洞描述中指出Confluence Server与Confluence Data Center中的Widget
Connector存在服务端模板注入漏洞，攻击者能利用此漏洞能够实现目录穿越与远程代码执行。

![
](https://images.seebug.org/content/images/2019/04/9bb154de-a086-4cf1-ac09-6283de9fe1d0.png-w331s)

确认漏洞点是Widget
Connector，下载最新版的比对补丁，发现在`com\atlassian\confluence\extra\widgetconnector\WidgetMacro.java`里面多了一个过滤，这个应该就是这个漏洞最关键的地方。

![
](https://images.seebug.org/content/images/2019/04/552c7a1b-4dad-4fa9-8bb0-626419b02098.png-w331s)

可以看到

    
    
    this.sanitizeFields = Collections.unmodifiableList(Arrays.asList(VelocityRenderService.TEMPLATE_PARAM));

而`TEMPLATE_PARAM`的值就是`_template`，所以这个补丁就是过滤了外部传入的`_template`参数。

    
    
    public interface VelocityRenderService {
        public static final String WIDTH_PARAM = "width";
        public static final String HEIGHT_PARAM = "height";
        public static final String TEMPLATE_PARAM = "_template";

翻了一下Widget Connector里面的文件，发现`TEMPLATE_PARAM`就是模板文件的路径。

    
    
    public class FriendFeedRenderer implements WidgetRenderer {
        private static final String MATCH_URL = "friendfeed.com";
        private static final String PATTERN = "friendfeed.com/(\\w+)/?";
        private static final String VELOCITY_TEMPLATE = "com/atlassian/confluence/extra/widgetconnector/templates/simplejscript.vm";
        private VelocityRenderService velocityRenderService;
    ......
        public String getEmbeddedHtml(String url, Map<String, String> params) {
            params.put(VelocityRenderService.TEMPLATE_PARAM, VELOCITY_TEMPLATE);
            return velocityRenderService.render(getEmbedUrl(url), params);
        }

加载外部的链接时，会调用相对的模板去渲染，如上，模板的路径一般是写死的，但是也有例外，补丁的作用也说明有人突破了限制，调用了意料之外的模板，从而造成了模板注入。

在了解了补丁和有了一些大概的猜测之后，开始尝试。

首先先找到这个功能，翻了一下官方的文档，找到了这个功能，可以在文档中嵌入一些视频，文档之类的。

![
](https://images.seebug.org/content/images/2019/04/8f35d723-2e9b-4687-aa67-ae81612461e6.png-w331s)

看到这个，有点激动了，因为在翻补丁的过程中，发现了几个参数，`url`，`width`，`height`正好对应着这里，那`_template`是不是也从这里传递进去的？

随便找个Youtube视频插入试试，点击预览，抓包。

![
](https://images.seebug.org/content/images/2019/04/b8b048e4-cdcb-46f0-9c4c-5c5291911b68.png-w331s)

在`params`中尝试插入`_template`参数，好吧，没啥反应。。

![
](https://images.seebug.org/content/images/2019/04/7eb17ac6-a1b5-4566-a709-b213482e0cd7.png-w331s)

开始debug模式，因为测试插入的是Youtube视频，所以调用的是`com/atlassian/confluence/extra/widgetconnector/video/YoutubeRenderer.class`

    
    
    public class YoutubeRenderer implements WidgetRenderer, WidgetImagePlaceholder {
        private static final Pattern YOUTUBE_URL_PATTERN = Pattern.compile("https?://(.+\\.)?youtube.com.*(\\?v=([^&]+)).*$");
        private final PlaceholderService placeholderService;
        private final String DEFAULT_YOUTUBE_TEMPLATE = "com/atlassian/confluence/extra/widgetconnector/templates/youtube.vm";
    ......
    
        public String getEmbedUrl(String url) {
            Matcher youtubeUrlMatcher = YOUTUBE_URL_PATTERN.matcher(this.verifyEmbeddedPlayerString(url));
            return youtubeUrlMatcher.matches() ? String.format("//www.youtube.com/embed/%s?wmode=opaque", youtubeUrlMatcher.group(3)) : null;
        }
    
        public boolean matches(String url) {
            return YOUTUBE_URL_PATTERN.matcher(this.verifyEmbeddedPlayerString(url)).matches();
        }
    
        private String verifyEmbeddedPlayerString(String url) {
            return !url.contains("feature=player_embedded&") ? url : url.replace("feature=player_embedded&", "");
        }
    
        public String getEmbeddedHtml(String url, Map<String, String> params) {
            return this.velocityRenderService.render(this.getEmbedUrl(url), this.setDefaultParam(params));
        }

在`getEmbeddedHtml`下断点，先会调用`getEmbedUrl`对用户传入的`url`进行正则匹配，因为我们传入的是个正常的Youtube视频，所以这里是没有问题的，然后调用`setDefaultParam`函数对传入的其他参数进行处理。

    
    
        private Map<String, String> setDefaultParam(Map<String, String> params) {
            String width = (String)params.get("width");
            String height = (String)params.get("height");
            if (!params.containsKey("_template")) {
                params.put("_template", "com/atlassian/confluence/extra/widgetconnector/templates/youtube.vm");
            }
    
            if (StringUtils.isEmpty(width)) {
                params.put("width", "400px");
            } else if (StringUtils.isNumeric(width)) {
                params.put("width", width.concat("px"));
            }
    
            if (StringUtils.isEmpty(height)) {
                params.put("height", "300px");
            } else if (StringUtils.isNumeric(height)) {
                params.put("height", height.concat("px"));
            }
    
            return params;
        }

取出`width`和`height`来判断是否为空，为空则设置默认值。关键的`_template`参数来了，如果外部传入的参数没有`_template`，则设置默认的Youtube模板。如果传入了，就使用传入的，也就是说，aaaa是成功的传进来了。

![
](https://images.seebug.org/content/images/2019/04/2349415b-a320-439f-8e5c-470348af962f.png-w331s)

大概翻了一下Widget
Connector里面的Renderer，大部分是不能设置`_template`的，是直接写死了，也有一些例外，如Youtube，Viddler，DailyMotion等，是可以从外部传入`_template`的。

能传递`_template`了，接下来看下是如何取模板和渲染模板的。

跟进`this.velocityRenderService.render`，也就是`com/atlassian/confluence/extra/widgetconnector/services/DefaultVelocityRenderService.class`里面的`render`方法。

    
    
        public String render(String url, Map<String, String> params) {
            String width = (String)params.get("width");
            String height = (String)params.get("height");
            String template = (String)params.get("_template");
            if (StringUtils.isEmpty(template)) {
                template = "com/atlassian/confluence/extra/widgetconnector/templates/embed.vm";
            }
    
            if (StringUtils.isEmpty(url)) {
                return null;
            } else {
                Map<String, Object> contextMap = this.getDefaultVelocityContext();
                Iterator var7 = params.entrySet().iterator();
    
                while(var7.hasNext()) {
                    Entry<String, String> entry = (Entry)var7.next();
                    if (((String)entry.getKey()).contentEquals("tweetHtml")) {
                        contextMap.put(entry.getKey(), entry.getValue());
                    } else {
                        contextMap.put(entry.getKey(), GeneralUtil.htmlEncode((String)entry.getValue()));
                    }
                }
    
                contextMap.put("urlHtml", GeneralUtil.htmlEncode(url));
                if (StringUtils.isNotEmpty(width)) {
                    contextMap.put("width", GeneralUtil.htmlEncode(width));
                } else {
                    contextMap.put("width", "400");
                }
    
                if (StringUtils.isNotEmpty(height)) {
                    contextMap.put("height", GeneralUtil.htmlEncode(height));
                } else {
                    contextMap.put("height", "300");
                }
    
                return this.getRenderedTemplate(template, contextMap);
            }
        }

`_template`取出来赋值给`template`，其他传递进来的参数取出来经过判断之后放入到`contextMap`，调用`getRenderedTemplate`函数，也就是调用`VelocityUtils.getRenderedTemplate`。

    
    
       protected String getRenderedTemplate(String template, Map<String, Object> contextMap){
            return VelocityUtils.getRenderedTemplate(template, contextMap);
        }

一路调用，调用链如下图，最后来到`/com/atlassian/confluence/util/velocity/ConfigurableResourceManager.class`的`loadResource`函数，来获取模板。

![
](https://images.seebug.org/content/images/2019/04/133e1155-3bb4-4bdc-96a5-a3d368b17c36.png-w331s)

这里调用了4个`ResourceLoader`去取模板。

    
    
    com.atlassian.confluence.setup.velocity.HibernateResourceLoader
    org.apache.velocity.runtime.resource.loader.FileResourceLoader
    org.apache.velocity.runtime.resource.loader.ClasspathResourceLoader
    com.atlassian.confluence.setup.velocity.DynamicPluginResourceLoader

这里主要看下Velocity自带的`FileResourceLoader`和`ClasspathResourceLoader`

`FileResourceLoader`会对用户传入的模板路径使用`normalizePath`函数进行校验

![
](https://images.seebug.org/content/images/2019/04/5e906ad6-2d09-4584-accb-10b5dc4e29af.png-w331s)

可以看到，过滤了`/../`，这样就导致没有办法跳目录了。

![
](https://images.seebug.org/content/images/2019/04/90c62d34-ba00-4594-a215-737f22d839de.png-w331s)

路径过滤后调用`findTemplate`查找模板，可看到，会拼接一个固定的`path`，这是Confluence的安装路径。

![
](https://images.seebug.org/content/images/2019/04/7496e7d2-111d-4c3f-8fc1-f7538b0878ff.png-w331s)

也就是说现在可以利用`FileResourceLoader`来读取Confluence目录下面的文件了。

尝试读取`/WEB-INF/web.xml`文件，可以看到，是成功的加载到了该文件。

![
](https://images.seebug.org/content/images/2019/04/a4c079ff-0269-4dbc-94ed-566a533797a3.png-w331s)

但是这个无法跳出Confluence的目录，因为不能用`/../`。

再来看下`ClasspathResourceLoader`

    
    
        public InputStream getResourceStream(String name) throws ResourceNotFoundException {
            InputStream result = null;
            if (StringUtils.isEmpty(name)) {
                throw new ResourceNotFoundException("No template name provided");
            } else {
                try {
                    result = ClassUtils.getResourceAsStream(this.getClass(), name);
    ......
                }

跟进`ClassUtils.getResourceAsStream`

    
    
        public static InputStream getResourceAsStream(Class claz, String name) {
            while(name.startsWith("/")) {
                name = name.substring(1);
            }
    
            ClassLoader classLoader = Thread.currentThread().getContextClassLoader();
            InputStream result;
            if (classLoader == null) {
                classLoader = claz.getClassLoader();
                result = classLoader.getResourceAsStream(name);
            } else {
                result = classLoader.getResourceAsStream(name);
                if (result == null) {
                    classLoader = claz.getClassLoader();
                    if (classLoader != null) {
                        result = classLoader.getResourceAsStream(name);
                    }
                }
            }
    
            return result;
        }

会跳到`/org/apache/catalina/loader/WebappClassLoaderBase.class`

![
](https://images.seebug.org/content/images/2019/04/05846a4d-114b-42e9-83cc-9ebf0d45bb29.png-w331s)

跟进，发现会拼接`/WEB-INF/classes`，而且其中也是调用了`normalize`对传入的路径进行过滤。。

![
](https://images.seebug.org/content/images/2019/04/4b91015d-a06e-4833-ab2e-ba96cfb2ece0.png-w331s)

这里还是可以用`../`跳一级目录。

尝试读取一下`../web.xml`，可以看到，也是可以读取成功的，但是仍然无法跳出目录。

![
](https://images.seebug.org/content/images/2019/04/7c15d73a-5622-4a26-a83d-abe051d518a2.png-w331s)

我这里测试用的版本是6.14.1，而后尝试了`file://`,`http://`，`https://`都没有成功。后来我尝试把Cookie删掉，发现在Linux环境下面还是可以读取文件，Windows的6.14.1版本是需要登陆的，但是跳不出目录。应急在这里卡住了。

而后的几天，有大佬用`file://`协议可以跳出目录限制，我惊了，我确定当时是已经试过了，没有成功的。看了大佬的截图，发现用的是6.9.0的版本，我下载了，尝试了一下，发现真的可以。而且在6.9.0版本中，Windows和Linux环境都不需要登陆。

问题还是在`ClasspathResourceLoader`上面，步骤和之前的是一样的，断到`/org/apache/catalina/loader/WebappClassLoaderBase.class`的`getResourceAsStream`方法

前面拼接`/WEB-INF/classes`获取失败后，继续往下进行。

![
](https://images.seebug.org/content/images/2019/04/d1b1f9ac-6c7d-4563-9009-2e1bc2313d29.png-w331s)

跟进`findResource`，函数前面仍然获取失败

![
](https://images.seebug.org/content/images/2019/04/da060bf3-be88-416b-9181-0bb105c3eeb9.png-w331s)

关键的地方就在这里，会调用`super.findResource(name)`，这里返回了URL，也就是能获取到对象。

![
](https://images.seebug.org/content/images/2019/04/a22374a3-7c87-46cf-a438-40f1957990d7.png-w331s)

不仅如此，这里还可以使用其他协议(https，ftp等)获取远程的对象，意味着可以加载远程的对象。

![
](https://images.seebug.org/content/images/2019/04/72b9c7e9-fa20-40bc-a359-b86e4afe5731.png-w331s)

获取到URL对象之后，继续回到之前的`getResourceAsStream`，可以看到，当返回的url不为null时，

会调用`url.openStream()`获取数据。

![
](https://images.seebug.org/content/images/2019/04/5cf69832-f084-4006-bda4-c9ac093dcd6d.png-w331s)

最终获取到数据给Velocity渲染。

尝试一下

![
](https://images.seebug.org/content/images/2019/04/55bae97d-61b1-427f-9b30-c4598b09b900.png-w331s)

至于6.14.1为啥不行，赶着应急，后续会跟，如果有新的发现，会同步上来，目前只看到`ClassLoader`不一样。

6.14.1

![
](https://images.seebug.org/content/images/2019/04/3c39c927-1787-4d8f-8a7e-16cd23aeaad6.png-w331s)

6.9.0

![
](https://images.seebug.org/content/images/2019/04/bb2e54ef-d53f-44e4-9cf3-54b10e853186.png-w331s)

这两个loader的关系如下

![
](https://images.seebug.org/content/images/2019/04/7ddcff63-d347-4825-8b1f-72611ca09ab9.png-w331s)

现在可以加载本地和远程模板了，可以尝试进行RCE。

关于Velocity的RCE，基本上payload都来源于15年blackhat的服务端模板注入的议题，但是在Confluence上用不了，因为在调用方法的时候会经过`velocity-htmlsafe-1.5.1.jar`，里面多了一些过滤和限制。但是仍然可以利用反射来执行命令。

用`python -m pyftpdlib -p 2121`开启一个简单的ftp服务器，将payload保存成rce.vm，保存在当前目录。

将`_template`设置成`ftp://localhost:2121/rce.vm`，发送，成功执行命令。

![
](https://images.seebug.org/content/images/2019/04/a29b32f0-96bb-4c69-bd77-f01fd548db82.png-w331s)

对于命令回显，同样可以使用反射构造出payload，执行`ipconfig`的结果。

![
](https://images.seebug.org/content/images/2019/04/8d6bc0ca-4636-4205-b74b-4482c0e6d6b0.png-w331s)

### 漏洞影响

根据 ZoomEye 网络空间搜索引擎对关键字 "X-Confluence" 进行搜索，共得到 61,856 条结果，主要分布美国、德国、中国等国家。

![
](https://images.seebug.org/content/images/2019/04/214dfc59-b98d-4b1e-bf1c-ef0a9798aa2e.png-w331s)

全球分布(非漏洞影响范围)

![
](https://images.seebug.org/content/images/2019/04/0be26b28-e225-4642-840c-88fbaeb7d4c7.png-w331s)

![
](https://images.seebug.org/content/images/2019/04/934c58e7-290d-4f39-9c05-19c35a653cc7.png-w331s)

中国分布(非漏洞影响范围)

![
](https://images.seebug.org/content/images/2019/04/cb862e0b-efd7-4098-b306-4941aa8e6036.png-w331s)

### 漏洞检测

2019年4月4日，404实验室公布了该漏洞的检测[PoC](https://github.com/knownsec/pocsuite3/blob/master/pocsuite3/pocs/20190404_WEB_Confluence_path_traversal.py)，可以利用这个PoC检测Confluence是否受该漏洞影响。

![ ](https://images.seebug.org/content/images/2019/04/f28e26c9-0dff-43ae-ab28-c2d562825d69.png-w331s)

### 参考链接

  * [漏洞检测PoC](https://github.com/knownsec/pocsuite3/blob/master/pocsuite3/pocs/20190404_WEB_Confluence_path_traversal.py)
  * [Remote code execution via Widget Connector macro - CVE-2019-3396](https://jira.atlassian.com/browse/CONFSERVER-57974)
  * [漏洞预警 | Confluence Server 远程代码执行漏洞](https://www.freebuf.com/news/200183.html)

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/884/>


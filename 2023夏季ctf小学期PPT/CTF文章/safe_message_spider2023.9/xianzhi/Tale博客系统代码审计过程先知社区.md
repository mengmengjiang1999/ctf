## 1、环境搭建

> 项目地址：<https://gitee.com/hellokaton/tale.git>

导入项目至idea，然后Maven->reload project即可，之后运行`Application`

![](./img/3334495140404055835.png)

## 2、项目依赖、结构

项目采用Blade框架开发

![](./img/4960933452305352775.png)

在Blade中提出 `WebHook`，你可以叫它钩子。该组件主要目的是拦截每次请求之前和之后的一些操作，在该项目中也实现了`WebHook`

![](./img/1407560919095330519.png)

![](./img/6272036232450185645.png)

判断请求URL开头是否包含`ADMIN_URI` 以及不是登录请求，如果满足条件将会判断是否登录，没有登录会跳转到登录页面

其中`ADMIN_URI` 的值为

    
    
    public static final String ADMIN_URI = "/admin";
    

Blade框架中构造 `/test/../admin/index` 无法匹配到 `/admin/index` 所以也无法绕过

## 3、代码审计

### 3.1 任意文件读取

> 路由：admin/template/content

![](./img/2953338189696218947.png)

用户可控参数`fileName` filePath直接拼接 filname并未做任何过滤，后续直接通过`Files.readAllLines`
将文件内容读出

验证：读取pom.xml文件内容

![](./img/2139179454556877693.png)

### 3.2 任意代码文件写入

> 路由：admin/api/template/save

![](./img/8575324521843649612.png)

程序首先获取了一个`TemplateParam` 对象，其中包含两个可控参数

    
    
    @Data
    public class TemplateParam {
    
        private String fileName;
        private String content;
    
    }
    

在通过`StringKit.isBlank(templateParam.getFileName())` 来判断`fileName`
是否为空，如果不为空进入下面的代码逻辑，获取`content` 并拼接filepath，在进行判断，文件是否存在，不存在则创建文件，后续进行写入操作

验证：修改桌面文件

![](./img/8974694193960996582.png)

![](./img/8217447390699257609.png)

我们也可以通过修改代码文件，来自己创建一个路由等服务器重启获取系统权限

写入一个不需要登录就能访问的路由

![](./img/1589394699855057263.png)  
写入成功

![](./img/7063543720317849029.png)

系统重启后即可执行命令

![](./img/442352730491339979.png)

### 3.3 任意文件上传

> 路由:admin/api/attach/upload

获取文件名并赋值给fname，之后进入`getFileKey` 方法中，跟进查看具体逻辑

![](./img/4213398388377374971.png)  
其作用通俗来说就是要上传到哪里去，如果没有/upload/当前日期的文件夹则创立

![](./img/5880899172954807263.png)

`StringKit.fileExt` 中主要是生成文件名，并未对后缀做任何限制

![](./img/8205653997514948906.png)

验证：文件不解析，只能打个xss了

![](./img/645552234512904957.png)

![](./img/1869697463643526177.png)

## 4、总结

如有问题，感谢各位师傅指正


**作者: Badcode@知道创宇404实验室**  
**时间: 2018/08/14  
英文版：<https://paper.seebug.org/991/>**

### 漏洞简介

2018年04月05日，Pivotal公布了Spring MVC存在一个目录穿越漏洞(CVE-2018-1271)。Spring
Framework版本5.0到5.0.4,4.3到4.3.14以及较旧的不受支持的版本允许应用程序配置Spring
MVC以提供静态资源（例如CSS，JS，图像）。当Spring MVC的静态资源存放在Windows系统上时，攻击可以通过构造特殊URL导致目录遍历漏洞。

### 漏洞影响

  * Spring Framework 5.0 to 5.0.4.
  * Spring Framework 4.3 to 4.3.14
  * 已不支持的旧版本仍然受影响

### 漏洞利用条件

  * Server运行于Windows系统上
  * 要使用file协议打开资源文件目录

### 漏洞复现

#### 复现环境

  * 操作系统Windows

  * web代码 [spring-mvc-showcase](https://github.com/spring-projects/spring-mvc-showcase)

  * 中间件jetty

#### 环境搭建

1.下载 spring-mvc-showcase

    
    
    git clone https://github.com/spring-projects/spring-mvc-showcase.git

修改`pom.xml`，使用Spring Framework 5.0.0。

![](https://images.seebug.org/content/images/2018/08/fe90b5bf-b4aa-49ad-84df-969c56768d0d.png-w331s)

2.修改 Spring MVC 静态资源配置，可参考[官方文档](https://docs.spring.io/spring-framework/docs/5.0.4.RELEASE/spring-framework-reference/web.html#mvc-config-static-resources)

通过官方文档可知有两种方式配置，可自行选择配置。此处通过重写`WebMvcConfigurer`中的`addResourceHandlers`方法来添加新的资源文件路径。在`org.springframework.samples.mvc.config.WebMvcConfig`添加以下代码即可，使用`file://`协议指定`resources`为静态文件目录。

    
    
     registry.addResourceHandler("/resources/**").addResourceLocations("file:./src/main/resources/","/resources/");

3.使用 jetty 启动项目

    
    
    mvn jetty:run

至此复现环境搭建完毕。

#### 复现过程及结果

访问以下链接

    
    
    http://localhost:8080/spring-mvc-showcase/resources/%255c%255c..%255c/..%255c/..%255c/..%255c/..%255c/..%255c/..%255c/..%255c/..%255c/windows/win.ini

![](https://images.seebug.org/content/images/2018/08/50c516bd-c1ad-449d-8e4d-c55d0b7b9fd8.png-w331s)

可以看到成功读取到`win.ini`的内容了。

### 漏洞分析

当外部要访问静态资源时，会调用`org.springframework.web.servlet.resource.ResourceHttpRequestHandler:handleRequest`来处理，在这里下断点调试。

![](https://images.seebug.org/content/images/2018/08/1c5f44e0-a8f6-4f0a-93f8-855a33727283.png-w331s)

跟进`org.springframework.web.servlet.resource.ResourceHttpRequestHandler:getResource()`。

![](https://images.seebug.org/content/images/2018/08/e4d9c406-8939-453c-afc3-b4a743adfec8.png-w331s)

在`request`中保存的路径是`/spring-mvc-showcase/resources/%255c%255c..%255c/..%255c/..%255c/..%255c/..%255c/..%255c/..%255c/..%255c/..%255c/windows/win.ini`。在`request.getAttribute()`函数取值时会进行
url
decode操作，此时`path`的值为`%5c%5c..%5c/..%5c/..%5c/..%5c/..%5c/..%5c/..%5c/..%5c/..%5c/windows/win.ini`。接下来会对path进行两次校验，将`path`和`path`解码之后的值分别使用`isInvalidPath`函数检查。看下这个函数

![](https://images.seebug.org/content/images/2018/08/f57a7143-915e-471a-96d8-7d065d4b9733.png-w331s)

当`path`包含有`..`的时候，会调用`cleanPath`函数对`path`处理。跟进

![](https://images.seebug.org/content/images/2018/08/e25741ea-e275-4c11-8907-d33d9111ad7d.png-w331s)

这个函数的作用是把包含`..`的这种相对路径转换成绝对路径。例如`/foo/bar/../`经过`cleanPath`处理后就会变成`/foo/`。

`cleanPath`的问题在于`String[] pathArray = delimitedListToStringArray(pathToUse,
"/");`这个是允许空元素存在的，也就是说`cleanPath`会把`//`当成一个目录，而操作系统是不会把`//`当成一个目录的。借用一张Orange大佬的图。

![](https://images.seebug.org/content/images/2018/08/69e2a319-176d-4173-8737-4e68b49cd481.png-w331s)

继续回到流程上，上面说到会对path进行两次校验，第一次调用`isInvalidPath`，`path`的值是`%5c%5c..%5c/..%5c/..%5c/..%5c/..%5c/..%5c/..%5c/..%5c/..%5c/windows/win.ini`，因为`path`以`/`分割之后没有元素等于`..`，所以`path`经过`cleanPath`处理后的值不变，继续之后的判断，`path`里面也不包含`../`，所以最终返回`false`，也就是通过了校验。

![](https://images.seebug.org/content/images/2018/08/9d968524-7668-455c-bb84-ba3b30bfe3f2.png-w331s)

第二次调用`isInvalidPath(URLDecoder.decode(path,
"UTF-8"))`，此时参数值是`\\..\/..\/..\/..\/..\/..\/..\/..\/..\/windows/win.ini`，经过`cleanPath`处理后的值是`//windows/win.ini`，之后继续判断，`path`里面也不包含`../`，最终返回false，也通过了校验。

![](https://images.seebug.org/content/images/2018/08/7b100e3d-6e07-43b5-a9f8-eeb3add12699.png-w331s)

通过两次校验之后，继续向下执行。获取一个`Resource`对象

![](https://images.seebug.org/content/images/2018/08/49222a99-f9bd-4042-9519-cb2237b8501a.png-w331s)

`path`的值还是之前，`getLocations()`获取到的就是之前在配置文件中配置的路径`file:./src/main/resources/`，继续跟进

![](https://images.seebug.org/content/images/2018/08/c70cd9f0-e6dd-403a-89a4-b9b8216ebaae.png-w331s)

跟进`ResourceResolver`类的`resolveResource`

![](https://images.seebug.org/content/images/2018/08/97c38ba3-87d3-49ee-94b8-2cba404462fb.png-w331s)

跟进`PathResourceResolver`的`resolveResourceInternal`

![](https://images.seebug.org/content/images/2018/08/4a3677e4-39a5-4f94-a811-8424f4256c8e.png-w331s)

进入到`org.springframework.web.servlet.resource.PathResourceResolver`的`getResource()`

![](https://images.seebug.org/content/images/2018/08/86a3d3f0-82d4-4dd8-aed1-adea855580a6.png-w331s)

此时的`resourcePath`就是之前的`path`，`location`就是之前`getLocations()`获取到的值。继续跟进`this.getResource`

![](https://images.seebug.org/content/images/2018/08/6d0ccfc6-33f4-40ea-8a54-801afaf00424.png-w331s)

调用`location.createRelativ`拼接得到文件的绝对路径，返回一个`UrlResource`对象

![](https://images.seebug.org/content/images/2018/08/cbf64073-84d9-42c1-91ae-90e20842b92c.png-w331s)

返回到`getResource`函数

![](https://images.seebug.org/content/images/2018/08/bf78aabb-d361-4985-8169-73e0501b6366.png-w331s)

此时，`resource`是一个`UrlResource`对象，可以看到值是`file:src/main/resources/%5c%5c..%5c/..%5c/..%5c/..%5c/..%5c/..%5c/..%5c/..%5c/..%5c/windows/win.ini`，之后调用`exists()`方法检查该文件是否存在，调用`isReadable()`方法检测该文件是否可读。进去`exists()`方法

![](https://images.seebug.org/content/images/2018/08/dca3e50f-ab9e-4e83-be66-cf850bb56791.png-w331s)

这里会调用`isFileURL`对`url`进行判断，是否以`file://`协议来读取文件，这也是为什么配置静态目录的时候要使用`file://`协议。

![](https://images.seebug.org/content/images/2018/08/926d1269-111f-4c39-a146-90807f10b053.png-w331s)

通过判断之后，会调用`this.getFile()`来获取这个文件对象，这个方法在`org.springframework.util.ResourceUtils`这个方法类里面，跟进

![](https://images.seebug.org/content/images/2018/08/0a73a478-afb7-4b1d-b798-748119260d29.png-w331s)

这里对是否为`file://`协议又判断了一次，之后进行了一步最重要的操作`new
File(toURI(resourceUrl).getSchemeSpecificPart());`，将`resourceUrl`转换为URL对象，最后调用`URI`类的`getSchemeSpecificPart()`获取到文件路径，而在`getSchemeSpecificPart()`里面是有一次`decode`操作的，也就是在这里把`%5c`解码成了`\`，跟进

![](https://images.seebug.org/content/images/2018/08/a0f6382f-10d0-437b-8a1c-2187e7e53f7e.png-w331s)

![](https://images.seebug.org/content/images/2018/08/820fb5e0-900d-4b14-9aec-2a7ce2e63281.png-w331s)

最后返回到`exists()`，最终返回`true`，即文件存在

之后调用`isReadable()`方法检测该文件是否可读的时候，同样会调用这个`getFile`，最终返回`true`，即文件可读。

![](https://images.seebug.org/content/images/2018/08/d75a2606-1bc5-4321-9564-b65ef12a65e5.png-w331s)

至此，对于`resource`的判断都结束了。返回到`org.springframework.web.servlet.resource.ResourceHttpRequestHandler:handleRequest()`，获取到通过校验`resource`的之后，就开始准备response的内容了，包含获取文件的类型(用于response的Content-type)，文件的大小(用于response的Content-length)等等，最后调用`this.resourceHttpMessageConverter.write(resource, mediaType,
outputMessage);`获取文件的内容并返回给用户。

![](https://images.seebug.org/content/images/2018/08/252f4ad7-f34b-4771-9931-1f002f27f5f0.png-w331s)

跟进`write()`

![](https://images.seebug.org/content/images/2018/08/26adc9b3-3405-4d6e-83c1-2629d237c37f.png-w331s)

跟进`writeInternal`，之后再跳到`writeContent`

![](https://images.seebug.org/content/images/2018/08/8de8bf8b-9f45-4cc8-93d2-d62354416996.png-w331s)

跟进`resource.getInputSream()`

![](https://images.seebug.org/content/images/2018/08/06921be8-9c93-4332-992d-47cc14f8c013.png-w331s)

可以看到，这里使用`openConnection`创建一个`URLConnection`实例，也是在`openConnection`方法内，会自动`decode`，把`%5c`解码成`\`，然后返回文件的`InputStream`对象，最终读取内容返回给用户。

### 注意事项

  1. 这个漏洞是可以在 Tomcat 下触发的，因为payload的双URL编码的。

  2. 在Spring Framework 大于5.0.1的版本(我的测试环境5.0.4)，双URL编码payload是不行的，单次URL编码的payload的却是可以的，这种情况下该漏洞就无法在Tomcat下触发了，因为在默认情况下Tomcat遇到包含`%2f(/)`、`%5c(\)`的URL直接http 400，在 jetty 下是可以触发的。

至于为什么双URL编码不行，是因为`org.springframework.web.servlet.resource.PathResourceResolver`的`getResource()`多了一个`encode`操作。

![](https://images.seebug.org/content/images/2018/08/8a8929c1-9636-4c5f-bea2-a504d105453a.png-w331s)

如果是双URL编码payload的进来，在获取`path`的时候解码一次，经过一次`isInvalidPath`判断，然后进入到`PathResourceResolver`的`getResource()`，也就是上图的位置，这里又会重新编码一次，又回到了双编码的情况了。最后在文件判断是否存在`exists()`方法的时候，`getSchemeSpecificPart()`只能解码一次，之后是无法读取到文件的，也就是文件不存在。

![](https://images.seebug.org/content/images/2018/08/d4df5f0e-bc37-40ce-89c9-674822c93e77.png-w331s)

所以这里要使用单次编码才行。

![](https://images.seebug.org/content/images/2018/08/5be1d67c-5135-4477-8c77-ff0ef7530351.png-w331s)

### 补丁分析

看官方的[补丁](https://github.com/spring-projects/spring-framework/commit/0e28bee0f155b9bf240b4bafc4646e4810cb23f8#diff-ca3a08ce8b5af11bfc5f03aa7f426cd9)，是在`ResourceHttpRequestHandler`的`getResource()`里面把`processPath`重写了

![](https://images.seebug.org/content/images/2018/08/753e8af5-a11a-49f9-8bd0-0db91398981d.png-w331s)

在进入`isInvalidPath`之前调用`processPath`函数对`path`处理，替换反斜线为斜线，删掉多余斜线，从而导致在`isInvalidPath`里面校验不通过。如果使用双编码方式的话，会经过`isInvalidEncodedPath`，里面会先对`path`解码，然后调用`processPath`处理，最后经过`isInvalidPath`，同样无法通过检查。

![](https://images.seebug.org/content/images/2018/08/0a03aedc-3e22-471c-976f-df7e473df983.png-w331s)

### 漏洞修复

  * Spring Framework 5.*（5.0到5.0.4）版本，建议更新到5.0.5版本
  * Spring Framework 4.3.*（4.3到4.3.14）版本，建议更新到4.3.15版本
  * 不再受支持的旧版本，建议更新到4.3.15版本或5.0.5版本

### 参考链接

  * [CVE-2018-1271: Directory Traversal with Spring MVC on Windows](https://pivotal.io/security/cve-2018-1271)
  * [Breaking Parser Logic! Take Your Path Normalization Off and Pop 0days Out](http://i.blackhat.com/us-18/Wed-August-8/us-18-Orange-Tsai-Breaking-Parser-Logic-Take-Your-Path-Normalization-Off-And-Pop-0days-Out-2.pdf)
  * [Directory Traversal with Spring MVC on Windows](https://bl4ck.in/vulnerability/analysis/2018/04/10/Directory-Traversal-with-Spring-MVC-on-Window.html)

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/665/>


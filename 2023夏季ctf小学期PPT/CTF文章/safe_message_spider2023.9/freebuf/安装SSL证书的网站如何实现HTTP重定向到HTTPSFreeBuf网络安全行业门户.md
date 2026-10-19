最近总有用户问：“为什么安装了SSL证书的网站仍显示不安全，需要在http后手动加小s才能正常访问呢？”这个问题的原因在于未对部署了SSL证书的网站设置HTTPS访问定向。解决方法很简单：
**只需要将** **HTTP** **访问301** **永久重定向到[HTTPS](https://www.racent.com/ssl)**
**即可。**

![](https://image.3001.net/images/20211011/1633941516_6163f80c285f21f0d7b41.jpg!small)  

## 设置HTTP重定向到HTTPS协议

下面，将以racent.com域名为例讲解如何设置HTTP重定向到HTTPS协议。

注意：将所有内部和外部链接更新为 HTTPS URL。内部链接包括导航/菜单链接、图像、CSS 引用等。如果网站在内部仍然引用 HTTP
文件，它将中断。确保将所有外部链接和本地目录列表更改为指向新的 HTTPS 网站。

此外，还需将HTTPS协议访问的https://racent.com 不带 www 的请求，也设置为301 永久重定向到带 www 的主网址
https://www.racent.com。最终效果如下：

 **请求**

|

 **端口**

|

 **HTTP** **重定向**

|

 **目标**  
  
---|---|---|---  
  
http://www.racent.com

|

80

|

永久（301）

|

https://www.racent.com  
  
http://racent.com

|

80

|

永久（301）

|

https://www.racent.com  
  
https://racent.com

|

443

|

永久（301）

|

https://www.racent.com  
  
为了网站 SEO 和
搜索引擎更加友好，对已经收录的网址，类似这样的http://yourdomain/ssl的网址，要带网址参数重定向，效果类似这样https://yourdomain/ssl，而不是重定向到首页。

接下来，我们以IIS服务器为例开始HTTP 301永久重定向到HTTPS的配置。

1\. 在IIS 服务器中添加网站，保证网站能正常响应请求，点击鼠标右键，选择“ **编辑绑定** ”，添加网站绑定。  

![](https://image.3001.net/images/20211011/1633941557_6163f835546bdf40af237.jpg!small)  

2\. 点击左侧选中网站，在右侧选择“ **HTTP** **重定向** ”双击。

![](https://image.3001.net/images/20211011/1633941580_6163f84c7bacf80adbf58.jpg!small)  

3\. 设置“ **HTTP** **重定向**
”。勾选“将请求重定向到此目标”，并填写目标地址。勾选“将所有请求重定向到确切的目标（而不是相对于目标）”。状态代码选择“永久(301)”。最后保存。

![](https://image.3001.net/images/20211011/1633941603_6163f863e7fdd5721eb85.jpg!small)  

注意：目标地址后面的【$S$Q】表示的是IIS
重定向的参数。加上【$S$Q】参数，将重定向到指定地址+请求的URL的后缀+URL中的参数，其目的就是为了更好地提高网站HTTPS排名。

4\. 通过上面的IIS 设置，您的网站目录下就多了一个 **config** 配置文件，配置内容如下：

    
    
    <?xml version="1.0" encoding="UTF-8"?>
    <configuration>
       <system.webServer>
          <httpRedirect enabled="true" destination="https://www.racent.com$S$Q" exactDestination="true" httpResponseStatus="Permanent" />
       </system.webServer>
    </configuration>

当然，您也可以选择直接在web.config配置文件中去设置301永久重定向。IIS 10 会默认加载网站根目录的 web.config
配置文件，假如您设置 IIS 10 默认不加载，那还需上面的 IIS 设置。

通过以上配置，访问HTTP的URL的时候就不再需要手动添加小s，而是会自动跳转到HTTPS协议上了。

本文转载于https://www.racent.com/blog/set-301-permanent-redirection

  


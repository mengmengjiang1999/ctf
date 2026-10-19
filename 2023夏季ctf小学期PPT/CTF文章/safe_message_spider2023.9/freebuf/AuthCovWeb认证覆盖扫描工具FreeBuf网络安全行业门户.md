**AuthCov是一个基于JavaScript的Web认证覆盖扫描工具。**

**![](https://image.3001.net/images/20190829/1567036737_5d671541a5769.jpg!small)**

## 简介

AuthCov使用Chrome headless
browser（无头浏览器）爬取你的Web应用程序，同时以预定义用户身份进行登录。在爬取阶段它会拦截并记录API请求及加载的页面，并在下一阶段，以不同的用户帐户“intruder”登录，尝试访问发现的各个API请求或页面。它为每个定义的intruder用户重复此步骤。最后，它会生成一份详细的报告，列出发现的资源以及intruder用户是否可以访问这些资源等。

以下是扫描本地Wordpress实例生成的示例报告：

![](https://image.3001.net/images/20190829/1567036890_5d6715daad17e.png!small)

##  特性

> 同时适用于单页面应用程序和传统的多页面应用程序
>
> 处理基于令牌和基于cookie的身份验证机制
>
> 生成HTML格式的深入报告
>
> 可以在报告中查看已爬取的各个页面的截图

##  安装

安装node 10。然后运行：

    
    
    $ npm install -g authcov

##  使用

为要扫描的站点生成配置：

    
    
    $ authcov new myconfig.js

更新myconfig.js中的值

运行以下命令测试配置值，以确保浏览器成功登录。

    
    
    $ authcov test-login myconfig.js --headless=false

爬取站点：

    
    
    $ authcov crawl myconfig.js

尝试intrusion在爬取阶段发现的资源：

    
    
    $ authcov intrude myconfig.js

在以下位置查看生成的报告：./tmp/report/index.html

##  配置

可以在配置文件中设置以下选项：

选项  |  类型  |  description  
---|---|---  
baseUrl  |  字符串  |  站点URL。这是爬虫开始的地方。  
crawlUser  |  对象  |  站点下要爬取的用户例如：{"username": "admin", "password": "1234"}  
intruders  |  数组  |
intrude在爬网阶段发现的api端点和页面。通常，这些用户的权限与crawlUser相同或更低。要以未登录用户身份intrude，请添加用户名为“Public”密码为null的用户。例如：[{"username":
"john", "password": "4321"}, {"username": "Public", "password": null}]  
type  |  字符串  |
这是单页应用程序（即查询API后端的javascript前端）还是更“传统”的多页应用程序？（选择“mpa”或“spa”）。  
authenticationType  |  字符串  |
网站是使用浏览器发送的cookie还是通过请求标头中发送的令牌对用户进行身份验证？对于mpa，几乎总是设置为“cookie”。在spa中，可以是“cookie”或“token”。  
authorisationHeaders  |  数组  |
需要发送哪些请求标头才能对用户进行身份验证？如果authenticationType=token，则应将其设置为["cookie"]。如果authenticationType=token，那么将是：["X-Auth-Token"]。  
maxDepth  |  整数  |  站点爬取的最大深度。建议先从1开始，然后再尝试更高的深度，以确保爬虫能够更加快速高效地完成。  
verboseOutput  |  布尔  |  详细输出，对调试很有用。  
saveResponses  |  布尔  |  从API端点保存响应正文，以便你可以在报告中查看它们。  
saveScreenshots  |  布尔  |  保存已抓取页面的浏览器屏幕截图，以便你可以在报告中查看它们。  
clickButtons  |  布尔  |
（实验性功能）在每个页面上抓取，单击该页面上的所有按钮并记录所做的任何API请求。在通过模态（modals），弹窗等进行大量用户交互的网站上非常有用。  
xhrTimeout  |  整数  |  在抓取每个页面时等待XHR请求完成的时间（秒）。  
pageTimeout  |  整数  |  在抓取时等待页面加载的时间（秒）。  
headless  |  布尔  |  将此设置为false，以便抓取工具打开Chrome浏览器，及查看实时的抓取情况。  
unAuthorizedStatusCodes  |  数组  |
HTTP响应状态代码，用于决定API端点或页面是否为请求它的用户授权。（可选）定义函数responseIsAuthorised以确定请求是否已获得授权。示例：[401,403,404]  
ignoreLinksIncluding  |  数组  |
不要抓取包含此数组中任何字符串的网址。例如，如果设置为["/logout"]，则不会抓取url：<http://localhost:3000/logout>。（可选）定义一个函数gnoreLink(url)，以确定URL是否应该被爬取。  
ignoreAPIrequestsIncluding  |  array  |
不要记录对包含此数组中任何字符串的URL所做的API记录。（可选）定义函数ignoreApiRequest(url)，以确定请求是否应被记录。  
ignoreButtonsIncluding  |  数组  |
如果clickButtons设置为true，则不单击外部HTML包含此数组中任何字符串的按钮。（可选）定义一个函数ignoreButton(url) 。  
loginConfig  |  对象  |  配置浏览器登录Web应用程序的方式。（可选）定义异步函数loginFunction(page,
username, password)。  
cookiesTriggeringPage  |  字符串  |
（可选）当authenticationType=cookie时，将设置一个页面，以便intruder浏览到该页面，然后从浏览器捕获cookie。如果站点在cookie上设置了path字段，这将非常有用。默认为options.baseUrl。  
tokenTriggeringPage  |  字符串  |
（可选）当authenticationType=token时，将设置一个页面，以便intruder浏览到该页面，然后从截获的API请求中捕获authorisationHeaders。如果站点的baseUrl没有发出任何API请求，那么这可能很有用，因此无法从该页面捕获auth标头。默认为options.baseUrl。  
  
###  **配置登录**

在配置文件中有两种配置登录的方法：

使用默认登录机制，使用puppeteer在指定的输入中输入用户名和密码，然后单击指定的提交按钮。这可以通过在配置文件中设置loginConfig选项来配置。你也可以查看此处的[示例](https://github.com/authcov/authcov/blob/master/examples/example-spa-config.js#L27-L32)。

    
    
    "loginConfig": {
      "url": "http://localhost/login",
      "usernameXpath": "input[name=email]",
      "passwordXpath": "input[name=password]",
      "submitXpath": "#login-button"
    }

如果你的登录表单较复杂并且涉及多用户交互，那么你可以在配置文件中定义自己的puppeteer函数，就像这样。同样，你可以查看此处的[示例](https://github.com/authcov/authcov/blob/master/examples/example-mpa-config.js#L25-L37)。

    
    
    "loginFunction": async function(page, username, password){
      await page.goto('http://localhost:3001/users/sign_in');
      await page.waitForSelector('input[type=email]');
      await page.waitForSelector('input[type=password]');
      await page.type('input[type=email]', username);
      await page.type('input[type=password]', password);
      await page.tap('input[type=submit]');
      await page.waitFor(500);
      return;
    }

不要忘记在headful mode下运行authcov test-login命令，以验证浏览器是否成功登录。

###  **Unit Tests**

Unit tests：

    
    
    $ npm test test/unit

###  **Integration tests：**

首先下载并运行[示例应用](https://github.com/evanrolfe/example_app)，然后运行测试：

    
    
    $ npm test test/integration

***参考来源：[GitHub](https://github.com/authcov/authcov)，FB小编secist编译，转载请注明来自FreeBuf.COM**

  


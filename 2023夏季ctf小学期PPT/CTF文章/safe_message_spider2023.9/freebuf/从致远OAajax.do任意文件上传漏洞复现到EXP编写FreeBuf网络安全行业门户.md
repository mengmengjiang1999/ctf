## **前言**

最近网上爆出致远OA ajax.do登录绕过和任意文件上传漏洞，影响部分旧版致远OA版本（致远OA V8.0，致远OA V7.1、V7.1SP1，致远OA
V7.0、V7.0SP1、V7.0SP2、V7.0SP3，致远OA V6.0、V6.1SP1、V6.1SP2，致远OA V5.x，致远OA
G6）。互联网上已经有基于Python的EXP，为了更好的发挥Goby的作用，尝试在Goby上编写EXP工具。

## 0x01 漏洞复现

漏洞复现主要分以下三个部分：

### 1.1 未授权访问

参考unicodeSec大佬的分析，通过请求eyon/thirdpartyController.do.css/…;/ajax.do判断是否存在漏洞,若出现下图异常，则可能存在漏洞。

![](https://image.3001.net/images/20210128/1611806886_601238a67f7c4b5c3f973.png!small)通过抓取数据包，可以看到如下的数据请求和返回结构：

![](https://image.3001.net/images/20210128/1611806900_601238b4a48dcae19106a.png!small)返回的状态值为200，且返回的数据包含"java.lang.NullPointerException:null"字符串。

###  **1.2 任意文件上传**

调用未授权的文件上传接口上传任意文件，以上传test.txt，上传到/seeyon目录下，内容为test123，数据包如下所示：

![](https://image.3001.net/images/20210128/1611806931_601238d337e699335d526.png!small)

返回的状态值为500，文件上传成功会返回。

    
    
    {
      "message":null,
      "code":"0844135702",
      "details":null
    }

> 其中code的值不固定。

文件上传失败会返回。

    
    
    {
      "message": "被迫下线，原因：与服务器失去连接",
      "code": "-1",
      "details": null
    }

###  **1.3 请求上传的文件**

通过请求上传的文件，查看文件是否上传成功，如下所示：

![](https://image.3001.net/images/20210128/1611807044_60123944265f1e8d8c167.png!small)

## 0x02 Goby EXP编写

###  **2.1 漏洞信息填写**

致远OA的查询规则是：app=Yonyou-Seeyon-OA（可以常规扫目标后查看该目标的资产类型以确定查询规则）

![](https://image.3001.net/images/20210128/1611807107_60123983c330a1974d6f1.png!small)填写漏洞信息，如下所示：

![](https://image.3001.net/images/20210128/1611807129_60123999a6e0e7dd04bd9.png!small)而后在高级配置中，填写标签、描述、产品、产品主页、作者、来源、漏洞危害和解决方案等信息。

###  **2.2 ScanSteps填写**

 **2.2.1 未授权访问判断**

根据漏洞复现部分，GET请求/seeyon/thirdpartyController.do.css/…;/ajax.do,根据返回数据的状态码200和返回内容中包含"java.lang.NullPointerException:null"字符串判断目标是否存在漏洞，填写对应的规则，如下所示：

![](https://image.3001.net/images/20210128/1611807180_601239cc21332c1331b24.png!small)

![](https://image.3001.net/images/20210128/1611807534_60123b2ee9d7b629a8167.png!small)

此处在header的中需要填写Accep字段。

 **2.2.2 文件上传二次判断**

和Goby团队的技术表哥交流后， **仅通过上面的未授权访问判断，可能会存在很多的误报，因此需要借助文件上传进一步判断。**

POST数据进行任意文件上传，需要带上Content-Type: application/x-www-form-urlencoded，根据返回内容是否包含message、code和details，并且排除返回内容包含-1（上传失败，返回值的code为-1）判断是否上传成功。

![](https://image.3001.net/images/20210128/1611807228_601239fccb488e5bdfe18.png!small)![](https://image.3001.net/images/20210128/1611807237_60123a0535ef5bd7fb07c.png!small)Post数据可参考互联网上已有的资源。

>  **tips小技巧：**
> 填写完测试数据后，在自定义PoC的右上角有个"单ip扫描"选项，输入ip:port，进行单ip扫描，查看定义的测试选项逻辑是否正确。

###  **2.3 ExploitSteps填写**

从生成的seeyou_OA_ajaxAction_formulaManager_File_Upload.json文件的ScanSteps中提取Post部分的数据，加入到ExploitSteps中，如下：

![](https://image.3001.net/images/20210128/1611807281_60123a31c79fc9de9dfb1.png!small)需要在ScanSteps前面加上"HasExp‘":“true”，进行设置漏洞验证。

在mojie师傅的帮助下，将上传的文件名等内容固定到ExpParams部分中，方便验证时输出文件上传的信息，如下所示：

![](https://image.3001.net/images/20210128/1611807296_60123a403496bab4f24a1.png!small)

## 0x03 Goby 验证效果

![](https://image.3001.net/images/20210128/1611807354_60123a7a69b94b3bd866d.png!small)![](https://image.3001.net/images/20210128/1611807365_60123a85800e3cda56fae.png!small)

> 文章来自Goby社区成员：bytesec，转载请注明出处。


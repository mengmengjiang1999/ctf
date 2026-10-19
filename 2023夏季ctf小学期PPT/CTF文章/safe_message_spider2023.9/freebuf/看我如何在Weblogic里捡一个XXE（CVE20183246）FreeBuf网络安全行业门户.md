***本文中涉及到的相关漏洞已报送厂商并得到修复，本文仅限技术研究与讨论，严禁用于非法用途，否则产生的一切后果自行承担。**

 ***本文作者：黑客小平哥，本文属 FreeBuf 原创奖励计划，未经许可禁止转载。**

##  前言

 **前几天空间被CVE-2018-2894刷屏，大家也都在研究和复现这个漏洞，正好我们安全团队也在玩这个漏洞，那大家就一起来玩咯。
本次的重点是复现，上传webshell，环境是内部一个测试环境，当我使用其中一个上传页面的时候，脑子突然热了一下，把文件后缀改成了.xml，结果就很6了。**

地址如下：<http://127.0.0.1:8338/ws_utc/begin.do>。

## 分析

![结果](https://image.3001.net/images/20181017/1539737226_5bc6868a1df62.jpg!small)

![结果](https://image.3001.net/images/20181017/1539737259_5bc686ab4c7c1.jpg!small)

突然看到了什么，报错了，但是错误代码里有个“Internal Exception:
org.xml.sax.SAXParseException”，这里竟然解析xml文件，这里说明一下，虽然这里是上传webshell的地方，xml文件貌似没什么用，但是当漏洞任意文件上传漏洞修复之后，这个xml文件是不会禁止的，这里既然解析了xml文件，说明这xml文件属于正常文件。

此处当然要传个payload试下了读下etc/passwd，发现还是报错，无法读取：

![试下了读下etc/passwd](https://image.3001.net/images/20181017/1539737321_5bc686e9a748d.jpg!small)

这就完了？当然不是，既然无法读取回显，那就换个payload反弹下shell试试：

![反弹下shell试试](https://image.3001.net/images/20181017/1539737344_5bc6870049a81.jpg!small)

设置本地监听：

![设置本地监听](https://image.3001.net/images/20181017/1539737361_5bc6871159c98.jpg!small)

返回包发现执行了payload代码，并且读取到服务器etc/passwd文件：

![执行payload代码](https://image.3001.net/images/20181017/1539737407_5bc6873f87a6e.jpg!small)

至此，该漏洞已经确定存在，并将及时报告给官方了，2018年10月16日，该漏洞已经在oracle发布。

### 漏洞简要分析：

根据路径，漏洞定位到ws-testpage-impl.jar文件里的“importWsTestConfig”方法：

![漏洞定位](https://image.3001.net/images/20181017/1539737481_5bc68789d9ae5.jpg!small)  

代码如下：

    
    
    @Path("/config/import")
    
     @POST
    
     @Produces({"application/xml", "application/json"})
    
     @Consumes({"multipart/form-data"})
    
     public Response importWsTestConfig(FormDataMultiPart formPartParams) {if (RequestUtil.isProductionMode()) {
    
         return Response.status(Response.Status.SERVICE_UNAVAILABLE).build();
    
        }
    
       if (TestClientRT.isVerbose()) {
    
          Logger.fine("callingWebserviceResource.importWsTestConfig");
    
        }
    
     
    
       KeyValuesMap formParams = RSDataHelper.getInstance()
    
         .convertFormDataMultiPart(formPartParams, true);
    
     
    
       ActionData ad = new ActionData();
    
       ad.put("request_form_data", formParams);
    
     
    
       ad = new ImportTestCaseAction().process(ad);
    
       if (ad.get("response_data") != null) {
    
         return Response.ok(ad.get("response_data")).build();
    
        }
    
    returnResponse.ok().build(); }

可以发现，此处使用的方法为“ImportTestCaseAction”，进去看下该方法：

![进去看下该方法](https://image.3001.net/images/20181017/1539737513_5bc687a9738c9.jpg!small)

代码如下：

    
    
    publicActionData execute(ActionData actionData)
    
      {
    
        KeyValuesMap formParams =(KeyValuesMap)actionData
    
          .get("request_form_data");
    
        try
    
        {
    
          String fileName =(String)formParams.getFirstValue("import_file_name");
    
          String importId = "" + newDate().getTime();
    
     
    
          if (TestClientRT.isVerbose()) {
    
            Logger.debug("Import ID: " +importId);
    
          }
    
     
    
          Unmarshaller Unmarshaller =context.createUnmarshaller();
    
          TTestConfig tconfig =(TTestConfig)Unmarshaller.unmarshal(new File(fileName));
    
     
    
          if (importConfigMap.size() >= 10) {
    
            importConfigMap.clear();
    
          }
    
     
    
          importConfigMap.put(importId, tconfig);
    
     
    
          actionData.put("response_data",new ImportTest(importId, tconfig.getWsdl(), null));
    
        } catch (Throwable e) {
    
          Logger.fine("[Error] Can not parsethe imported test config file.", e);
    
          WSTestRuntimeException wste = newWSTestRuntimeException(e);
    
          wste.setErrorMsgBean(newErrorMsgBean(null, UserMessages.format("error_while_importing_test",new Object[0])));
    
          throw wste;
    
        }
    
     
    
        return actionData;
    
      }

Unmarshaller接口是将XML数据转化为Java对象，此处是Unmarshaller使用不当，造成XXE，值得注意的是，经过和同事的不懈尝试，发现jdk8默认禁止外部DTD的，jdk6和jdk7是可以的，而weblogic默认的jdk是存在该问题的（详细版本范围有待进一步考证）。

### Demo介绍：

此处jdk为1.8，无法实现XXE：

![jdk为1.8](https://image.3001.net/images/20181017/1539737552_5bc687d058805.jpg!small)

此处jdk为1.6，即可执行：  

![jdk为1.6](https://image.3001.net/images/20181017/1539737720_5bc68878e48dc.jpg!small)  

本次研究结束，欢迎大佬继续研究并指正。

 ***本文作者：黑客小平哥，本文属 FreeBuf 原创奖励计划，未经许可禁止转载。**


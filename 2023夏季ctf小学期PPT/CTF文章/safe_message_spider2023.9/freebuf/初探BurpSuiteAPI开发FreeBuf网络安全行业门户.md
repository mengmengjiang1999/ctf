**0x00 环境准备**

要使用python进行BurpSuite插件的开发需要安装Jython。

下载地址：<http://www.jython.org/downloads.html>

安装完成后，加载jython的jar包到BurpSuite运行环境中。

![环境.webp.jpg](https://image.3001.net/images/20180815/1534315100_5b73ca5c3cbed.jpg!small)

 **0x01 BurpSuite API中常见的类**

 **IBurpExtender**

该类中有个registerExtenderCallbacks方法，该方法在插件被加载后会被调用，在所有扩展插件中必须实现这个接口。

java的调用方法：

    
    
    void registerExtenderCallbacks(IBurpExtenderCallbacks callbacks)
    
    Parameters:
    
    callbacks - An IBurpExtenderCallbacks object.
    

python的调用方法，python需要对这个方法传入的参数进行处理，处理的是为了更加方便的调用基本接口的方法，这里就列出了一些方法，其他的可以参考IBurpExtenderCallbacks的内容。

    
    
    def registerExtenderCallbacks(self, callbacks):
    
           # keep a reference to our callbacks object (Burp Extensibility Feature)
    
           self._callbacks = callbacks
    
           # obtain an extension helpers object (Burp Extensibility Feature)
    
           # [http://portswigger.net/burp/extender/api/burp/IExtensionHelpers.html](http://portswigger.net/burp/extender/api/burp/IExtensionHelpers.html)
    
           self._helpers = callbacks.getHelpers()
    
           # set our extension name that will display in Extender Tab
    
           self._callbacks.setExtensionName("find JSON callback")
    
           # register ourselves as an HTTP listener
    
           callbacks.registerHttpListener(self)
    

**IHttpListener**

该类是用来注册HTTP监听器，然后对获取到的请求或响应包进行处理，有个processHttpMessage的方法用于对请求和响应的数据包进行自定义操作，该方法在发送请求之前和接收响应之后会被调用。

java的调用方法：

    
    
    void processHttpMessage(int toolFlag,
    
                         boolean messageIsRequest,
    
                         IHttpRequestResponse messageInfo)
    
    Parameters:
    
    toolFlag - A flag indicating the Burp tool that issued the request. Burp tool flags are defined in the IBurpExtenderCallbacks interface.
    
    messageIsRequest - Flags whether the method is being invoked for a request or response.
    
    messageInfo - Details of the request / response to be processed. Extensions can call the setter methods on this object to update the current message and so modify Burp's behavior.
    

python的调用方法：

    
    
    def processHttpMessage(self, toolFlag, messageIsRequest, messageInfo):
    
           # determine what tool we would like to pass though our extension:
    
           if toolFlag == 64 or toolFlag == 16 or toolFlag == 8 or toolFlag == 4: #if tool is Proxy Tab or repeater
    
               # determine if request or response:
    
               if not messageIsRequest:#only handle responses
    
                   #获取响应包的数据
    
                   response = messageInfo.getResponse()
    
                   analyzedResponse = self._helpers.analyzeResponse(response) # returns IResponseInfo
    
                   response_headers = analyzedResponse.getHeaders()
    
                   response_bodys = response[analyzedResponse.getBodyOffset():].tostring()
    
                   #获取请求包的数据
    
                   resquest = messageInfo.getRequest()
    
                   analyzedRequest = self._helpers.analyzeResponse(resquest)
    
                   request_header = analyzedRequest.getHeaders()
    
                   request_bodys = resquest[analyzedResponse.getBodyOffset():].tostring()
    

......

 **IHttpRequestResponse**

该接口用来获取HTTP中请求和响应的HTTP信息，如果是响应包的HTTP信息，需要在请求被发送后才能获取到。

该接口有getComment(),getHighlight(),getHttpService(),getRequest(),getResponse(),setComment(java.lang.String
comment),setHighlight(java.lang.String color),setHttpService(IHttpService
httpService),setRequest(byte[] message),setResponse(byte[] message)

这些方法。可以直接在官方接口文档中查看。

其中getHttpService()方法会返回IHttpService的对象。如果需要获取协议，主机，端口信息的，就需要对IHttpService对象里相应的方法进行调用。

java的调用方法：

    
    
    IHttpService getHttpService()
    
    This method is used to retrieve the HTTP service for this request / response.
    
    Returns:
    
    An IHttpService object containing details of the HTTP service.
    

python的调用方法：

    
    
    #获取服务信息
    
                   httpService = messageInfo.getHttpService()
    
                   port = httpService.getPort()
    
                   host = httpService.getHost()
    

**IHttpService**

该接口用来获取可以被发送的请求包的详细内容，有getHost(),getPort(),getProtocol这个三个方法。

java的调用方法：

    
    
    java.lang.String getHost()
    
    This method returns the hostname or IP address for the service.
    
    Returns:
    
    The hostname or IP address for the service.
    
    int getPort()
    
    This method returns the port number for the service.
    
    Returns:
    
    The port number for the service.
    
    java.lang.String getProtocol()
    
    This method returns the protocol for the service.
    
    Returns:
    
    The protocol for the service. Expected values are "http" or "https".
    

python的调用方法：

#获取服务信息

    
    
                   httpService = messageInfo.getHttpService()
    
                   port = httpService.getPort()
    
                   host = httpService.getHost()
    

**IResponseInfo**

该接口是用来获取响应包的详细内容的，通过IExtensionHelpers.analyzeResponse()的方法调用该对象中的方法。

该接口有getBodyOffset(),getCookies(),getHeaders(),getInferredMimeType(),getStatedMimeType(),getStatusCode()的方法。

java的调用方法：

    
    
    java.util.List<java.lang.String> getHeaders()
    
    This method is used to obtain the HTTP headers contained in the response.
    
    Returns:
    
    The HTTP headers contained in the response.
    
    int getBodyOffset()
    
    This method is used to obtain the offset within the response where the message body begins.
    
    Returns:
    
    The offset within the response where the message body begins.
    
    short getStatusCode()
    
    This method is used to obtain the HTTP status code contained in the response.
    
    Returns:
    
    The HTTP status code contained in the response.
    
    java.util.List<ICookie> getCookies()
    
    This method is used to obtain details of the HTTP cookies set in the response.
    
    Returns:
    
    A list of ICookie objects representing the cookies set in the response, if any.
    
    java.lang.String getStatedMimeType()
    
    This method is used to obtain the MIME type of the response, as stated in the HTTP headers.
    
    Returns:
    
    A textual label for the stated MIME type, or an empty String if this is not known or recognized. The possible labels are the same as those used in the main Burp UI.
    
    java.lang.String getInferredMimeType()
    
    This method is used to obtain the MIME type of the response, as inferred from the contents of the HTTP message body.
    
    Returns:
    
    A textual label for the inferred MIME type, or an empty String if this is not known or recognized. The possible labels are the same as those used in the main Burp UI.
    

python的调用方法：

    
    
    #获取响应包的数据
    
                   response = messageInfo.getResponse()
    
                   analyzedResponse = self._helpers.analyzeResponse(response) # returns IResponseInfo
    
                   response_headers = analyzedResponse.getHeaders()
    
                   response_bodys = response[analyzedResponse.getBodyOffset():].tostring()
    

**IRequestInfo**

该接口是用来获取请求包的详细内容的，通过IExtensionHelpers.analyzeRequest()的方法调用该对象中的方法。

该接口有getBodyOffset(),getContentType(),getHeaders(),getMethod(),getParameters(),getUrl()的方法。

java的调用方法：

    
    
    java.lang.String getMethod()
    
    This method is used to obtain the HTTP method used in the request.
    
    Returns:
    
    The HTTP method used in the request.
    
    java.net.URL getUrl()
    
    This method is used to obtain the URL in the request.
    
    Returns:
    
    The URL in the request.
    
    java.util.List<java.lang.String> getHeaders()
    
    This method is used to obtain the HTTP headers contained in the request.
    
    Returns:
    
    The HTTP headers contained in the request.
    
    java.util.List<IParameter> getParameters()
    
    This method is used to obtain the parameters contained in the request.
    
    Returns:
    
    The parameters contained in the request.
    
    int getBodyOffset()
    
    This method is used to obtain the offset within the request where the message body begins.
    
    Returns:
    
    The offset within the request where the message body begins.
    
    byte getContentType()
    
    This method is used to obtain the content type of the message body.
    
    Returns:
    
    An indication of the content type of the message body. Available types are defined within this interface.
    

python的调用方法：

#获取请求包的数据

    
    
                   resquest = messageInfo.getRequest()
    
                   analyzedRequest = self._helpers.analyzeRequest(resquest)
    
                   request_header = analyzedRequest.getHeaders()
    
                   request_bodys = resquest[analyzedRequest.getBodyOffset():].tostring()
    

**0x02 示例代码**

    
    
    #-*-Thinking-*-    
    #coding=utf8
    
    from burp import IBurpExtender
    
    from burp import IHttpListener
    
    from burp import IHttpRequestResponse
    
    from burp import IResponseInfo
    
    from burp import IRequestInfo
    
    from burp import IHttpService
    
    import re
    
    # Class BurpExtender (Required) contaning all functions used to interact with Burp Suite API
    
    print 'Thinking\'s find JSON callback Bui~'
    
    class BurpExtender(IBurpExtender, IHttpListener):
    
       # define registerExtenderCallbacks: From IBurpExtender Interface 
    
       def registerExtenderCallbacks(self, callbacks):
    
           # keep a reference to our callbacks object (Burp Extensibility Feature)
    
           self._callbacks = callbacks
    
           # obtain an extension helpers object (Burp Extensibility Feature)
    
           # [http://portswigger.net/burp/extender/api/burp/IExtensionHelpers.html](http://portswigger.net/burp/extender/api/burp/IExtensionHelpers.html)
    
           self._helpers = callbacks.getHelpers()
    
           # set our extension name that will display in Extender Tab
    
           self._callbacks.setExtensionName("find JSON callback")
    
           # register ourselves as an HTTP listener
    
           callbacks.registerHttpListener(self)
    
       # define processHttpMessage: From IHttpListener Interface 
    
       def processHttpMessage(self, toolFlag, messageIsRequest, messageInfo):
    
           # determine what tool we would like to pass though our extension:
    
           if toolFlag == 64 or toolFlag == 16 or toolFlag == 8 or toolFlag == 4: #if tool is Proxy Tab or repeater
    
               # determine if request or response:
    
               if not messageIsRequest:#only handle responses
    
                   #获取响应包的数据
    
                   response = messageInfo.getResponse()
    
                   analyzedResponse = self._helpers.analyzeResponse(response) # returns IResponseInfo
    
                   response_headers = analyzedResponse.getHeaders()
    
                   response_bodys = response[analyzedResponse.getBodyOffset():].tostring()
    
                   response_StatusCode = analyzedResponse.getStatusCode()
    
                   #获取请求包的数据
    
                   resquest = messageInfo.getRequest()
    
                   analyzedRequest = self._helpers.analyzeResponse(resquest)
    
                   request_header = analyzedRequest.getHeaders()
    
                   request_bodys = resquest[analyzedRequest.getBodyOffset():].tostring()
    
                   #获取服务信息
    
                   httpService = messageInfo.getHttpService()
    
                   port = httpService.getPort()
    
                   host = httpService.getHost()
    
                   #第一种情况：url中带有callback,且返回的是json数据。
    
                   expressionA = r'.*(callback).*'
    
                   expressionB = r'.*(application/json|application/javascript).*'
    
                   expressionC = r'.*(text/html|application/javascript).*'
    
                   for rqheader in request_header:
    
                       if rqheader.startswith("Host"):
    
                           rqhost = rqheader
    
                           break
    
                   ishtml = 0        
    
                   for rpheader in response_headers:
    
                       if rpheader.startswith("Content-Type:")  and re.match(expressionC,rpheader):
    
                           ishtml = 1
    
                       if rpheader.startswith("Content-Type:")  and  re.match(expressionB,rpheader):                            
    
                           if re.match(expressionA,request_header[0]):
    
                               print '='*10,'[success|有callback且返回json数据]','='*10,'\n\n[Host]',rqhost,port,'\n\n[URI]',request_header[0],'\n\n[ResponseBody]',response_bodys[0:30],'\n\n\n'
    
                               break
    
                   #第二种情况：url中没有带callback,但是通过添加callback参数后，便返回了带方法名的json数据。
    
                   if not re.match(expressionA,request_header[0]):
    
                       new_headers = request_header
    
                       if '?' in new_headers[0]:
    
                           new_headers[0] = new_headers[0].replace('?','?callback=BuiBui&')
    
                       else:
    
                           new_headers[0] = new_headers[0][:-9] +'?callback=BuiBui'
    
                       req = self._helpers.buildHttpMessage(new_headers, request_bodys) 
    
                       ishttps = False
    
                       if port == 443:
    
                           ishttps = True
    
                       if response_StatusCode == 200 and ishtml == 1:  
    
                           rep = self._callbacks.makeHttpRequest(host, port, ishttps, req)
    
                           #TODO 在某些情况下makeHttpRequest时候会出现一些bug,得到的结果但是取不到response,很奇怪(已经解决,404页面取不到正文返回包)
    
                           #新的请求请求包
    
                           analyzedreq = self._helpers.analyzeResponse(rep)
    
                           req_headers = analyzedreq.getHeaders()
    
                           req_bodys = rep[analyzedreq.getBodyOffset():].tostring()
    
                           #新的请求响应包
    
                           analyzedrep = self._helpers.analyzeResponse(rep)
    
                           rep_headers = analyzedrep.getHeaders()
    
                           rep_bodys = rep[analyzedrep.getBodyOffset():].tostring()
    
                           if 'BuiBui' in rep_bodys:
    
                               for repheader in rep_headers:
    
                                   if repheader.startswith("Content-Type:")  and  re.match(expressionB,repheader):
    
                                       print '='*10,'[success|发现隐藏callback且返回json数据]','='*10,'\n\n[Host]',rqhost,port,'\n\n[URI]',req_headers[0],'\n\n[ResponseBody]',rep_bodys[0:30],'\n\n\n'
    
                                       break
    

**0x03 加载插件**

 **![加载
1.webp.jpg](https://image.3001.net/images/20180815/1534315380_5b73cb7488298.jpg!small)**

当请求中有callback或隐藏callback且返回包是json格式的便会在output上打印记录。

![打印.webp.jpg](https://image.3001.net/images/20180815/1534315409_5b73cb91a90ba.jpg!small)![qrcode_for_gh_223e082fe8a7_344.jpg](https://image.3001.net/images/20180815/1534315428_5b73cba451ace.jpg!small)


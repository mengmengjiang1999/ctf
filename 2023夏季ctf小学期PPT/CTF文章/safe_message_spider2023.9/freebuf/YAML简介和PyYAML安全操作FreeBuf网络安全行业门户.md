# 1、简介

YAML是一种直观的能够被电脑识别的的数据序列化格式，容易被人类阅读，并且容易和脚本语言交互，通常运用在一些数据代码分离场合：用于配置文件，但也用于数据存储（例如调试输出）或传输（例如文档标题）。YAML
的配置文件后缀为 .yml或.yaml

# 2、基本语法

1、大小写敏感；

2、使用缩进表示层级关系，缩进只可以使用空格，不允许使用tab，遵守左对齐即可；

3、列表中项通过“-”表示，字典中的通过“:”表示；

4、# 表示注释，和python表示注释一样。

![1650179815_625bbee70630d43361fe4.png!small?1650179849641](https://image.3001.net/images/20220417/1650179815_625bbee70630d43361fe4.png!small?1650179849641)

![1650179837_625bbefd734472fe6b767.png!small?1650179871966](https://image.3001.net/images/20220417/1650179837_625bbefd734472fe6b767.png!small?1650179871966)

使用PyYAML>=5.1显示的结果

# 3、两个函数

yaml.dump()：将一个Python对象[序列化](https://so.csdn.net/so/search?q=%E5%BA%8F%E5%88%97%E5%8C%96&spm=1001.2101.3001.7020)生成为yaml文档。

yaml.load()：将一个yaml文档[反序列化](https://so.csdn.net/so/search?q=%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96&spm=1001.2101.3001.7020)为一个Python对象。

![1650179863_625bbf17e6270558c34b2.png!small?1650179900230](https://image.3001.net/images/20220417/1650179863_625bbf17e6270558c34b2.png!small?1650179900230)![1650179869_625bbf1d5804f7e6ecab1.png!small?1650179903814](https://image.3001.net/images/20220417/1650179869_625bbf1d5804f7e6ecab1.png!small?1650179903814)

可以看到，User对象经过yaml序列化之后内容为一行字符串，简单解释一下：“!!python/object”为yaml标签，yaml.load()会识别该标签并调用相应的方法执行反序列化操作；冒号后面的“__main__”为py文件名，这里为本文件的意思；“User”为序列化的对象类型，后面紧跟的大括号即为该对象的属性及其属性值。

# 4、PyYAML安全操作

## 1、PyYAML<5.1

### 1、测试环境(本地Python环境)

这里使用PyYAML==4.2b4进程测试，PyYAML历史版本可以参考：

<https://pypi.org/project/PyYAML/#history>

### 2、不安全的反序列化方法

在PyYAML 5.1版本之前我们有以下不安全的反序列化方法：

  * load(data)
  * load(data, Loader=Loader)
  * load_all(data)
  * load_all(data, Loader=Loader)

### 3、Demo

这里编写简单的Demo，一个py文件用于将恶意类序列化为字符串保存到yaml文件中，另一个py文件用于反序列化yaml文件内容为恶意类对象从而达到利用反序列化漏洞的目的。

#### 1、yaml_test.py

![1650179893_625bbf356378df5de12ee.png!small?1650179928081](https://image.3001.net/images/20220417/1650179893_625bbf356378df5de12ee.png!small?1650179928081)

先创建一个poc对象再调用yaml.dump()将其序列化为一个字符串，其中第9行代码为将默认的“__main__”替换为该文件名“yaml_test”，目的是为了后面yaml.load()反序列化该字符串的时候会根据yaml文件中的指引去读取yaml_
test.py中的poc这个类。

simple.yml文件内容如下所示：

![1650179903_625bbf3f9e158e7b340e0.png!small?1650179938117](https://image.3001.net/images/20220417/1650179903_625bbf3f9e158e7b340e0.png!small?1650179938117)

#### 2、yaml_verify.py

![1650179912_625bbf486dc4ec74e3c24.png!small?1650179946967](https://image.3001.net/images/20220417/1650179912_625bbf486dc4ec74e3c24.png!small?1650179946967)

通过yaml.load()读取目标yaml文件，之后"!!python/object"标签解析其中的名为yaml_test的module中的poc类，最后执行了该类对象的
**init** ()方法从而执行了命令。

### 4、漏洞成因

#### 1、PyYAML<5.1加载器

有如下几种类型：

(1)BaseLoader：仅加载最基本的YAML；

(2)SafeLoader：安全地加载YAML语言的子集，建议用于加载不受信任的输入(safe_load）；

(3)Loader：可以通过不受信任的数据输入轻松利用。

PyYAML<5.1默认的加载器使用的是Loader，调试一下。

![1650179942_625bbf664777febae9a4f.png!small?1650179976927](https://image.3001.net/images/20220417/1650179942_625bbf664777febae9a4f.png!small?1650179976927)![1650179952_625bbf70368554bdb24cc.png!small?1650179986860](https://image.3001.net/images/20220417/1650179952_625bbf70368554bdb24cc.png!small?1650179986860)

跟踪到Constructor，可以得到其针对Python语言特有的标签解析的处理函数对应列表：

(1)!!python/object: => Constructor.construct_python_object；

(2)!!python/object/apply: => Constructor.construct_python_object_apply；

(3)!!python/object/new: => Constructor.construct_python_object_new。

![1650179969_625bbf81d6d262a3767df.png!small?1650180004574](https://image.3001.net/images/20220417/1650179969_625bbf81d6d262a3767df.png!small?1650180004574)![1650179982_625bbf8ebd755c0ca1d42.png!small?1650180018298](https://image.3001.net/images/20220417/1650179982_625bbf8ebd755c0ca1d42.png!small?1650180018298)

#### 2、三个标签代码不同点与相同点

##### 1、不同点

1、从上面的代码中可以看到" !!python/object/new " 标签的代码实现其实就是" !!python/object/apply
"标签的代码实现，只是最后newobj参数值不同而已

2、查看官方文档，!!python/object标签的使用格式和另外两个根本就是两码事，其接收参数是使用大括号{}而非中括号[]，且并没有对参数args进行接收。也就是说，!!python/object标签只针对于对象类进行使用。

![1650179998_625bbf9edc5026d977048.png!small?1650180033452](https://image.3001.net/images/20220417/1650179998_625bbf9edc5026d977048.png!small?1650180033452)

那么对应的!!python/object/new和!!python/object/apply标签的payload可以写成:

!!python **/** object **/** apply **:** os **.** system **[** "calc.exe" **]**

!!python **/** object **/** new **:** os **.** system **[** "calc.exe" **]**

##### 2、相同点

这3个Python标签中都是调用了make_python_instance()函数

#### 3、分析make_python_instance()函数

##### !!python/object标签(construct_python_object()函数)

![1650180021_625bbfb57edbb3561efab.png!small?1650180056012](https://image.3001.net/images/20220417/1650180021_625bbfb57edbb3561efab.png!small?1650180056012)

还以刚才simple.yml文件内容为例

![1650180029_625bbfbd4edf9233f9bee.png!small?1650180063865](https://image.3001.net/images/20220417/1650180029_625bbfbd4edf9233f9bee.png!small?1650180063865)

那我们的payload就可以写成如下图所示的样子

![1650180038_625bbfc6e52a011d37d1b.png!small?1650180073491](https://image.3001.net/images/20220417/1650180038_625bbfc6e52a011d37d1b.png!small?1650180073491)

回来看make_python_instance()函数

![1650180045_625bbfcded86a98cf40f0.png!small?1650180080558](https://image.3001.net/images/20220417/1650180045_625bbfcded86a98cf40f0.png!small?1650180080558)

接下来查看find_python_name()函数

![1650180055_625bbfd7c9ca6c730852f.png!small?1650180092027](https://image.3001.net/images/20220417/1650180055_625bbfd7c9ca6c730852f.png!small?1650180092027)

可见最后返回值结果为<class ‘yaml.poc’>即代表yaml.py文件(模块)中的poc类

![1650180066_625bbfe250e0a2e47395d.png!small?1650180100942](https://image.3001.net/images/20220417/1650180066_625bbfe250e0a2e47395d.png!small?1650180100942)

回到make_python_instance()函数中，cls值就是<class ‘yaml.poc’>，如下图所示，最后返回结果就是恶意poc类生成的对象

![1650180079_625bbfef54c43e432c32b.png!small?1650180113940](https://image.3001.net/images/20220417/1650180079_625bbfef54c43e432c32b.png!small?1650180113940)

## 2、PyYAML >=5.1

### 1、测试环境(虚拟环境)

这里使用的是PyYAML5.2版本

### 2、PyYAML>=5.1加载器

有如下几种类型(多了两个)：

(1)BaseLoader：仅加载最基本的YAML

(2)FullLoader：加载完整的YAML语言,避免任意代码执行,默认加载器

(3)SafeLoader：安全地加载YAML语言的子集，建议用于加载不受信任的输入(safe_load）

(4)Loader：可以通过不受信任的数据输入轻松利用

(5)UnsafeLoader(也称为Loader向后兼容性）：原始的Loader代码，可以通过不受信任的数据输入轻松利用（unsafe_load）

在5.1之后，使用load()进行序列化操作时我们需要在方法里面加一个loader的请求参数，直接使用load请求时会显示以下warning，默认FullLoader

![1650180099_625bc003e14b9c8b88262.png!small?1650180134524](https://image.3001.net/images/20220417/1650180099_625bc003e14b9c8b88262.png!small?1650180134524)![1650180110_625bc00eb58c86aad8f64.png!small?1650180145275](https://image.3001.net/images/20220417/1650180110_625bc00eb58c86aad8f64.png!small?1650180145275)

不想显示warning加上Loader参数即可。

![1650180117_625bc015e59b1c5c73a16.png!small?1650180152546](https://image.3001.net/images/20220417/1650180117_625bc015e59b1c5c73a16.png!small?1650180152546)

### 3、不安全的反序列化方法

在PyYAML>=5.1版本中，提供了以下不安全的反序列化方法：

  * load(data, Loader=Loader)
  * load(data, Loader=UnsafeLoader)
  * load_all(data, Loader=Loader)
  * load_all(data, Loader=UnSafeLoader)
  * unsafe_load(data)
  * unsafe_load_all(data)

### 4、测试示例

还是以之前在小于5.1的Demo为例，在YAML 5.2版本中使用之前的Payload发现已无法实现RCE了，如下图

![1650180217_625bc079eae729e685875.png!small?1650180253927](https://image.3001.net/images/20220417/1650180217_625bc079eae729e685875.png!small?1650180253927)

因为YAML5.2版本默认使用加载器FullLoader，下面就来分析一下

#### 1、分析FullLoader

使用的是FullConstructor

![1650180229_625bc08544538eb6fd12f.png!small?1650180263856](https://image.3001.net/images/20220417/1650180229_625bc08544538eb6fd12f.png!small?1650180263856)

没有加载yaml_test文件(模块)，所以会报错，如下图

![1650180245_625bc095df58f6e1a7ec4.png!small?1650180281573](https://image.3001.net/images/20220417/1650180245_625bc095df58f6e1a7ec4.png!small?1650180281573)

#### 2、分析Loader

若使用Loader加载器的话，还是可以实现RCE了，如下图

![1650180256_625bc0a0e3b44313db405.png!small?1650180291506](https://image.3001.net/images/20220417/1650180256_625bc0a0e3b44313db405.png!small?1650180291506)

那么下面就分析一下，PyYAML5.2版本中Loader加载器为什么实现RCE，跟踪到Constructor

![1650180268_625bc0ac6cfcfee046ffa.png!small?1650180303078](https://image.3001.net/images/20220417/1650180268_625bc0ac6cfcfee046ffa.png!small?1650180303078)

继承了UnsafeConstructor类

![1650180277_625bc0b5662fbb62516d5.png!small?1650180311986](https://image.3001.net/images/20220417/1650180277_625bc0b5662fbb62516d5.png!small?1650180311986)

查看UnsafeConstructor类，发现其继承了FullConstructor类，使用super()函数调用父类FullConstructor的方法，可以观察到find_python_name()函数的参数unsafe值变为True，而我们在分析FullLoader时，若这个参数值为True，就会执行__import__(module_name)代码从而加载yaml_test文件(模块)

![1650180298_625bc0cac2d3d78506b2a.png!small?1650180333697](https://image.3001.net/images/20220417/1650180298_625bc0cac2d3d78506b2a.png!small?1650180333697)

如下图，这样就不会报错

![1650180308_625bc0d40dbf7d7afa8a7.png!small?1650180342812](https://image.3001.net/images/20220417/1650180308_625bc0d40dbf7d7afa8a7.png!small?1650180342812)

查看make_python_instance()函数，也避免了报错。

![1650180319_625bc0df4e1e8661b6d9a.png!small?1650180353972](https://image.3001.net/images/20220417/1650180319_625bc0df4e1e8661b6d9a.png!small?1650180353972)

#### 3、不同点

加载器FullLoader与Loader不同之处就在于参数unsafe的值是不同的！

# 5、总结

1、在这里，着重演示了yaml模块中load()函数中加载器的使用与实现恶意对象的分析过程

（1）其中包括如下函数(调用过程)：

construct_python_object()

\----make_python_instance()

\--------find_python_name()

（2）先执行find_python_name()函数再到make_python_instance()函数最后到construct_python_object()函数

（3）重点在于是否导入了自定义的模块，即在find_python_name()函数中，__import__()函数：__import__()函数用于动态加载类和函数，若一个模块经常变化就可以使用__import__()来动态载入。

（4）sys.modules是一个全局字典，该字典是python启动后就加载在内存中，每当导入新的模块，sys.modules都将记录这些模块。

2、最后说一下在处理YAML数据过程中的防御策略。

## 防御策略

1、要序列化数据，可以使用下面的安全函数:

  * safe_dump(data)
  * safe_dump_all(data)
  * dump(data,Dumper=SafeDumper)

2、要反序列化数据，可以使用下面的安全函数:

  * safe_load(data)
  * safe_load_all(data)
  * load(data,Loader=SafeLoader)


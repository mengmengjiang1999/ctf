**Riposte是一个基于Python的交互式Shell工具。它允许你轻松地将应用程序封装在定制的交互式shell中。关于构建交互式解释器（REPL）的常见繁琐工作已经被考虑到了，因此你可以专注于应用程序的特定域逻辑。**

## 安装

该软件包可在PyPI上使用，因此请使用[pip](https://pip.pypa.io/en/stable/quickstart/)进行安装：

    
    
    pip install riposte

Riposte支持Python 3.6及更高版本。

## 使用示例

    
    
    from riposte import Riposte
    
    calculator = Riposte(prompt="calc:~$ ")
    
    MEMORY = []
    
    
    @calculator.command("add")
    def add(x: int, y: int):
        result = f"{x} + {y} = {x + y}"
        MEMORY.append(result)
        calculator.success(result)
    
    
    @calculator.command("multiply")
    def multiply(x: int, y: int):
        result = f"{x} * {y} = {x * y}"
        MEMORY.append(result)
        calculator.success(result)
    
    
    @calculator.command("memory")
    def memory():
        for entry in MEMORY:
            calculator.print(entry)
    
    
    calculator.run()
    
    
    calc:~$ add 2 2
    [+] 2 + 2 = 4
    calc:~$ multiply 3 3
    [+] 3 * 3 = 9
    calc:~$ memory
    2 + 2 = 4
    3 * 3 = 9
    calc:~$

## 命令

首先，你需要注册一些命令以使REPL可操作。可以通过Riposte.command装饰器可以添加命令，并使用处理函数对其进行绑定。

    
    
    from riposte import Riposte
    
    repl = Riposte()
    
    @repl.command("hello")
    def hello():
        repl.success("Is it me you looking for?")
    
    repl.run()
    
    
    riposte:~ $ hello
    [+] Is it me you looking for?

另外Riposte.command接受一些可选参数：

> description 几个描述命令的词，你可以在以后用它来构建有意义的帮助
>
> [guides ](https://github.com/fwkz/riposte#guides)定义如何解释传递的参数

## 自动补全

Riposte支持命令的Tab键自动补全功能（tab-completion）。你可以以与注册命令类似的方式注册completer函数，只需使用Riposte.complete装饰器，并将其指向特定命令即可。

    
    
    from riposte import Riposte
    
    repl = Riposte()
    
    START_SUBCOMMANDS = ["foo", "bar"]
    
    
    @repl.command("start")
    def start(subcommand: str):
        if subcommand in START_SUBCOMMANDS:
            repl.status(f"{subcommand} started")
        else:
            repl.error("Unknown subcommand.")
    
    
    @repl.complete("start")
    def start_completer(text, line, start_index, end_index):
        
        return [
            subcommand
            for subcommand in START_SUBCOMMANDS
            if subcommand.startswith(text)
        ]
    
    
    repl.run()

补全功能由TAB键触发。每个补全函数都应返回有效选项列表，并接受以下参数：

> text 行中的最后一个单词
>
> line 整行的行内容
>
> start_index 该行中最后一个单词的起始索引
>
> end_index 该行中最后一个单词的结束索引

在我们的例子中：

    
    
    riposte:~ $ start ba<TAB>
    
    
    text -> "ba"
    line -> "start ba"
    start_index -> 6
    end_index -> 8

有了这些信息，你可以为每个命令构建自定义的completer函数。

## Guides

Guides是一种说明命令应如何解释用户通过提示传递的参数的方法。Riposte依靠[类型提示（Type
Hints）](https://docs.python.org/3/library/typing.html)来做到这一点。

    
    
    from riposte import Riposte
    
    repl = Riposte()
    
    @repl.command("guideme")
    def guideme(x: int, y: str):
        repl.print("x:", x, type(x))
        repl.print("y:", y, type(y))
    
    repl.run()
    
    
    riposte:~ $ guideme 1 1
    x: 1 <class 'int'>
    y: 1 <class 'str'>

在这两种情况下，我们都将value
1作为x和y传递。基于参数的类型提示，传递的参数在x的情况下被解释为int，在y的情况下被解释为str。你也可以将该技术用于不同的类型。

    
    
    from riposte import Riposte
    
    repl = Riposte()
    
    @repl.command("guideme")
    def guideme(x: dict, y: list):
        x["foo"] = "bar"
        repl.print("x:", x, type(x))
        
        y.append("foobar")
        repl.print("y:", y, type(y))
    
    repl.run()
    
    
    riposte:~ $ guideme "{'bar': 'baz'}" "['barbaz']"
    x: {'bar': 'baz', 'foo': 'bar'} <class 'dict'>
    y: ['barbaz', 'foobar'] <class 'list'>

另一种更为强大的定义guides用于处理函数参数的方法是，直接从Ricoste.command装饰器定义它。在本例中，以这种方式定义的guide优先于类型提示。

    
    
    from riposte import Riposte
    
    repl = Riposte()
    
    @repl.command("guideme", guides={"x": [int]})
    def guideme(x):
        repl.print("x:", x, type(x))
    
    repl.run()
    
    
    riposte:~ $ guideme 1
    x: 1 <class 'int'>

为什么这种方式更加强大？因为通过这种方式可以让你链接不同的guides，其中一个guide的输出是另一个guide的输入，创建验证或将输入转换为更复杂的类型。

    
    
    from collections import namedtuple
    
    from riposte import Riposte
    from riposte.exceptions import RiposteException
    from riposte.guides import literal
    
    repl = Riposte()
    
    
    def non_negative(value: int):
        if value < 0:
            raise RiposteException("Value can't be negative")
        
        return value
    
    
    Point = namedtuple("Point", ("x", "y"))
    
    
    def get_point(value: dict):
        return Point(**value)
    
    
    @repl.command("guideme",
                  guides={"x": [int, non_negative], "y": [literal, get_point]})
    def guideme(x, y):
        repl.print("x:", x, type(x))
        repl.print("y:", y, type(y))
    
    
    repl.run()
    
    
    riposte:~ $ guideme -1 '{"x": 1, "y": 2}'
    [-] Value can't be negative
    riposte:~ $ guideme 1 '{"x": 1, "y": 2}'
    x: 1 <class 'int'>
    y: Point(x=1, y=2) <class '__main__.Point'>
    riposte:~ $

这只是一个简单的函数调用，其中输入字符串被传递给链中的第一个引导函数。在这种情况下，调用如下所示：

    
    
    non_negative(int("-1"))  # guide chain for parameter `x`
    get_point(literal('{"x": 1, "y": 2}'))  # guide chain for parameter `y`

## 打印

Riposte内置线程安全打印方法：

> print
>
> info
>
> error
>
> status
>
> success

每个方法都遵循Python内置print()函数的签名。除了print之外，所有这些都提供与其名称相对应的信息着色（ informative
coloring）。

我们强烈建议你使用我们的线程安全打印API，但如果你知道自己在做什么，并且100％的确定，那么线程执行在你应用程序生命周期的某个阶段将永远不会出现，
你可以使用Python的内置print()函数。

## 扩展 PrinterMixin

如果要更改现有方法的样式或添加自定义方法，你可以对PrinterMixin类进行扩展。

    
    
    from riposte import Riposte
    from riposte.printer.mixins import PrinterMixin
    
    
    class ExtendedPrinterMixin(PrinterMixin):
        def success(self, *args, **kwargs):  # overwriting existing method
            self.print(*args, **kwargs)
        
        def shout(self, *args, **kwargs):  # adding new one
            self.print((*args, "!!!"), **kwargs)
    
    class CustomRiposte(Riposte, ExtendedPrinterMixin):
        pass
     
    repl = CustomRiposte()
    
    @repl.command("foobar")
    def foobar(message: str):
        repl.shout(message)

## 自定义 PrinterMixin

对现有的打印API不满意吗？没关系，你也可以使用PrinterBaseMixin及其线程安全_print方法从头开始构建自己的打印API。

    
    
    from riposte import Riposte
    from riposte.printer.mixins import PrinterBaseMixin
    
    
    class CustomPrinterMixin(PrinterBaseMixin):
        def ask(self, *args, **kwargs):  # adding new one
            self._print((*args, "???"), **kwargs)
            
        def shout(self, *args, **kwargs):  # adding new one
            self._print((*args, "!!!"), **kwargs)
    
    class CustomRiposte(Riposte, CustomPrinterMixin):
        pass
     
    repl = CustomRiposte()
    
    @repl.command("foobar")
    def foobar(message: str):
        repl.shout(message)
        repl.ask(message)
        repl.success(message)  # It'll raise exception as it's no longer available

## 使用 Pallete 对输出着色

如果你想在输出中添加一些颜色，可以使用Pallete。

    
    
    from riposte import Riposte
    from riposte.printer import Palette
    
    
    repl = Riposte()
    
    
    @repl.command("foo")
    def foo(msg: str):
        repl.print(Palette.GREEN.format(msg))  # It will be green

Pallete目前支持的颜色如下：

    
    
    GREY
    RED
    GREEN
    YELLOW
    BLUE
    MAGENTA
    CYAN
    WHITE
    BOLD

## History

命令历史记录存储在.riposte文件的HOME目录中。默认长度为100行。可以使用history_file和history_length参数更改这两个设置。

    
    
    from pathlib import Path
    from riposte import Riposte
    
    
    repl = Riposte(
        history_file=Path.home() / ".custom_history_file", 
        history_length=500,
    )

## Prompt

默认提示符为riposte:~ $你也可以自定义：

    
    
    from riposte import Riposte
    
    
    repl = Riposte(prompt="custom-prompt >>> ")
    repl.run()

你还可以通过覆盖Riposte.prompt属性，基于某个对象的状态动态解析提示布局。在以下示例中，我们将根据MODULE值确定prompt：

    
    
    from riposte import Riposte
    
    
    class Application:
        def __init__(self):
            self.module = None
    
    
    class CustomRiposte(Riposte):
        @property
        def prompt(self):
            if app.module:
                return f"foo:{app.module} > "
            else:
                return self._prompt  # reference to `prompt` parameter.
    
    
    app = Application()
    repl = CustomRiposte(prompt="foo > ")
    
    
    @repl.command("set")
    def set_module(module_name: str):
        app.module = module_name
        repl.success("Module has been set.")
    
    
    @repl.command("unset")
    def unset_module():
        app.module = None
        repl.success("Module has been unset.")
    
    
    repl.run()
    
    
    foo > set bar
    [+] Module has been set.
    foo:bar > unset
    [+] Module has been unset.
    foo >

## Banner

    
    
    # banner.py
    
    from riposte import Riposte
    
    BANNER = """ _   _      _ _         _    _            _     _ _ 
    | | | |    | | |       | |  | |          | |   | | |
    | |_| | ___| | | ___   | |  | | ___  _ __| | __| | |
    |  _  |/ _ \ | |/ _ \  | |/\| |/ _ \| '__| |/ _` | |
    | | | |  __/ | | (_) | \  /\  / (_) | |  | | (_| |_|
    \_| |_/\___|_|_|\___/   \/  \/ \___/|_|  |_|\__,_(_)
    Welcome User Hello World v1.2.3
    """
    
    repl = Riposte(banner=BANNER)
    
    
    @repl.command("hello")
    def hello():
        repl.print("Hello World!")
    
    
    repl.run()
    
    
    $ python banner.py
     _   _      _ _         _    _            _     _ _ 
    | | | |    | | |       | |  | |          | |   | | |
    | |_| | ___| | | ___   | |  | | ___  _ __| | __| | |
    |  _  |/ _ \ | |/ _ \  | |/\| |/ _ \| '__| |/ _` | |
    | | | |  __/ | | (_) | \  /\  / (_) | |  | | (_| |_|
    \_| |_/\___|_|_|\___/   \/  \/ \___/|_|  |_|\__,_(_)
    Welcome User Hello World v1.2.3
    
    riposte:~ $

## 项目状态

Riposte项目目前正处于开发阶段。未来可能会有一些重大变化，尽管这里出现的很多概念已在routerploit开发过程中经过了实战测试。

## 致谢

> [routersploit](https://github.com/threat9/routersploit)
>
> [click](https://click.palletsprojects.com/)

***参考来源：[GitHub](https://github.com/fwkz/riposte)，FB小编secist编译，转载请注明来自FreeBuf.COM**


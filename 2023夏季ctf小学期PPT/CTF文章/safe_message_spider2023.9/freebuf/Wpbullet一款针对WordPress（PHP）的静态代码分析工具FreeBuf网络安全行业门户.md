**今天给大家介绍的是一款名叫Wpbullet的工具，广大安全研究人员可以使用这款工具来对WordPress、插件、主题以及其他PHP项目进行静态代码分析。**

![bvbvbv.png](https://image.3001.net/images/20190614/1560491093_5d033455ee0c2.png!small)

## 工具安装

大家可以直接从Wpbullet的GitHub代码库中将项目克隆至本地，然后安装工具的依赖组件，并运行工具脚本：

    
    
    $ git clone <https://github.com/webarx-security/wpbullet> wpbullet
    
    $ cd wpbullet
    
    $ pip install -r requirements.txt
    
    $ python wpbullet.py

## 工具使用

下面给出的是所有可用的操作选项：

\--path(必需项) 系统路径或下载URL地址

### 使用样例：

    
    
    --path="/path/to/plugin"
    
    --path="<https://wordpress.org/plugins/example-plugin>"
    
    --path="<https://downloads.wordpress.org/plugin/example-plugin.1.5.zip>"

\--enabled(可选项) 检测给定的模块

### 使用样例：

    
    
    --enabled="SQLInjection,CrossSiteScripting"

\--disabled(可选项) 不检测给定的模块

### 使用样例：

    
    
    --disabled="SQLInjection,CrossSiteScripting"

\--cleanup(可选项) 在对远程下载的插件进行完扫描操作之后，自动删除本地.temp目录的内容

\--report(可选项) 将分析结果以JSON格式数据存储至reports/目录中

    
    
    $python wpbullet.py --path="/var/www/wp-content/plugins/plugin-name"

## 创建模块

Wpbullet的模块可扩展性以及灵活性都非常高，它允许我们重写每一个模块的BaseClass方法并实现我们自己的方法。

Modules目录中的每一个模块都继承了core.modules.BaseClass类的属性以及方法，因此每一个模块都需要的参数就是BaseClass了。

创建完成之后，模块需要在modules/__init__.py中导入。模块名和类名必须保持一致，否则Wpbullet将无法正常加载。

如果你想要在本项目的GitHub上pull request的话，请附带模块的单元测试数据。

### 模块样本

Modules/ExampleVulnerability.py

    
    
    from core.modules import BaseClass
    
    class ExampleVulnerability(object):
    
        # Vulnerability name
    
        name= "Cross-site Scripting"
    
        # Vulnerability severity
    
        severity = "Low-Medium"
    
        # Functions causing vulnerability
    
        functions = [
    
            "print"
    
            "echo"
    
        ]
    
        # Functions/regex that prevent exploitation
    
        blacklist = [
    
            "htmlspecialchars",
    
            "esc_attr"
    
    ]

## 重写正则式匹配模式  

正则式匹配模式由core.modules.BaseClass.build_pattern生成，因此我们可以根据自己的需要重写每一个模块类。

### Modules/ExampleVulnerability.py

    
    
    import copy
    
    ...
    
    #Build dynamic regex pattern to locate vulnerabilities in given content
    
    defbuild_pattern(self, content, file):
    
        user_input = copy.deepcopy(self.user_input)
    
        variables = self.get_input_variables(self,content)
    
        if variables:
    
            user_input.extend(variables)
    
        if self.blacklist:
    
            blacklist_pattern =r"(?!(\s?)+(.*(" + '|'.join(self.blacklist) + ")))"
    
        else:
    
            blacklist_pattern = ""
    
        self.functions = [self.functions_prefix + xfor x in self.functions]
    
        pattern = r"((" +'|'.join(self.functions) + ")\s{0,}\(?\s{0,1}" + blacklist_pattern +".*(" + '|'.join(user_input) + ").*)"
    
        return pattern

模块单元测试  

    
    
    $ python3 -m unittest

## 项目地址

Wpbullet：【[GitHub传送门](https://github.com/webarx-security/wpbullet)】

 *** 参考来源：[webarx-security](https://github.com/webarx-security/wpbullet)，FB小编Alpha_h4ck编译，转载请注明来自FreeBuf.COM**


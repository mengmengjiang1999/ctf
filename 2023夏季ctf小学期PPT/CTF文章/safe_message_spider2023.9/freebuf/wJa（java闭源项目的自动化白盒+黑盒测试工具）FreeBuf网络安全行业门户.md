# wJa（java闭源项目的自动化白盒+黑盒测试工具）

wJa，支持反编译java生成的jar包文件，整理成语法树，根据调用链进行污点分析，通过cheetah脚本语言编写测试脚本，确定可能存在的漏洞调用链，生成测试链接，进行fuzzer测试。

下面对网络上的一个Spring靶场进行SQL注入的分析测试。

## 环境准备

  1. 测试靶场

  2. java运行环境

  3. wJa

## wJa分析流程

![image](https://image.3001.net/images/20211221/1640084605_61c1b47d6bd5bcbc9534c.jpg!small)

## Step1 运行靶场

搭建好靶场环境，这里使用的靶场是在网上寻找到的，里面有创建数据库的脚本文件，环境一切准备就绪之后。

运行靶场，使用命令跑起jar包：

`java -jars shootingRange.jar `

![image](https://image.3001.net/images/20211221/1640084616_61c1b4886ace47bb93d96.png!small)

## Step2 使用wJa打开jar文件

使用命令：`java -jar wJa.jar`运行起程序，程序运行之后会要求选择待分析的jar程序，这里选择shootingRange.jar。

起来之后可以看到程序的主界面了。

![image](https://image.3001.net/images/20211221/1640084626_61c1b4922356268063a12.png!small)

 **左侧部分：**

Decompile：对jar包反编译的java资源管理器

cheetahLanguage：脚本管理器，包含支持库介绍，以及编写好的cheetah脚本

 **中间部分：**

Decompile：对jar包反编译的java代码显示部分

cheetahLanguage：编写cheetah脚本代码，运行测试

* * *

界面相对比较简单。

我们可以先看整个靶场的一个框架结构，从control层进行分析（Spring默认路径为`BOOT-INF/classes`）。

![image](https://image.3001.net/images/20211221/1640084637_61c1b49de92a956e2b15c.png!small)

可以看到control层都是提供对外开放的接口，所以我们可以确定这是入口类，所以我们可以将其确定为入口点。

从其中的一个入口点(one)根据一步步的调用追踪，我们可以得到如下调用链：

    
    
    indexLogic.getStudent(username);
    indexDb.getStudent(username);
    sql = "select * from students where username like '%" + username + "%'";
    jdbcTemplate.query(sql, ROW_MAPPER);
    

最终进入的危险函数：

![image](https://image.3001.net/images/20211221/1640084649_61c1b4a943a1e77b3aa0f.png!small)

当然，这是我们手动跟踪的，但是如何使用工具自动帮助我们进行追踪呢？

## Step3 编写白盒污点跟踪代码

### 污点分析

> 污点分析可以抽象成一个三元组〈 _sources_ , _sinks_ , _sanitizers_ 〉的形式, 其中, _source_ 即污点源,
> 代表直接引入不受信任的数据或者机密数据到系统中; _sink_ 即污点汇聚点, 代表直接产生安全敏感操作 (违反数据完整性) 或者泄露隐私数据到外界
> (违反数据保密性); _sanitizer_ 即无害处理,
> 代表通过数据加密或者移除危害操作等手段使数据传播不再对软件系统的信息安全产生危害.污点分析就是分析程序中由污点源引入的数据是否能够不经无害处理,
> 而直接传播到污点汇聚点.如果不能, 说明系统是信息流安全的; 否则, 说明系统产生了隐私数据泄露或危险数据操作等安全问题.

对于SQL注入这种漏洞，可以将污点分析的三元组实例化为下面三组内容：

source：Spring的接口入口点的参数

sink：jdbc的query方法

sanitizer：类似于Integer.value此类方法

* * *

### 代码编写

在检测类似于SQL注入类漏洞，我们需要的是跟踪调用链，所以需要使用的是`TrackVarIntoFun`函数

`TrackVarIntoFun`

    
    
    参数1:起始类
    参数2:起始方法
    参数3:起始方法参数下标
    参数4:目标方法的类
    参数5:目标方法
    参数6:目标方法的参数下标
    返回值:执行流node数组
    

  1. 起始类是我们需要分析的类，这里是`com/l4yn3/microserviceseclab/controller/IndexController`

  2. 起始方法是入口方法，也是这个类下面的所有接口方法

  3. 起始方法参数下标是要检测的入口参数下标

  4. 目标方法类是jdbc，这里是`org/springframework/jdbc/core/JdbcTemplate`

  5. 目标方法是query，jdbc查询数据的方法

  6. 目标方法的参数下标是第一个参数，sql语句

返回值是一个node执行流数组，node包含次node所在的class和node的AST。

我们设置开头的包名，那如何获取所有的方法名呢？

`GetAllMethodName`可以获取所有的方法名称，但是这里有一个注意的地方是，如果方法名是`<init>和<cinit>`的需要跳过，因为这两个方法是构造方法和静态代码块。

node中的AST可以通过`GetJavaSentence`方法得到对应生成的java代码。

还有一点需要注意的是，`TrackVarIntoFun`方法只是跟踪流，只是到目标方法就停止，如果没有到目标方法就停止了那么也是会返回所有的执行流，所以这里我们需要自己进行过滤。

所以现在的思路已经完成，通过`GetAllMethodName`获取所有的方法，然后对方法中的第一个参数进行追踪，查看其最终流向的是否是jdbc，并且判断流动过程中是否有类似于`Integer.value()`方法的存在，如果不存在，那噩梦非常可能就是一条可以被污染的链条。

最终我们可以编写出如下代码：

    
    
    #define filter1=String.valueOf(.*?)
    #define filter2=Integer.valueOf(.*?)
    function filter(sentence){
    	a = StrRe(sentence,filter1);
    	if(GetArrayNum(a) != 0){return 0;}
    	a = StrRe(sentence,filter2);
    	if(GetArrayNum(a) != 0){return 0;}
    	return 1;
    }
    function track(className,methodName){
    	array allNode;
    	allNode = TrackVarIntoFun(className,methodName,0,"org/springframework/jdbc/core/JdbcTemplate","query",0);
    	size = GetArrayNum(allNode);
    	if(StrFindStr(GetJavaSentence(allNode[ToInt(size-1)]),".query(",0) != "-1"){
    		i = 0;
    		print(methodName."参数流动:");
    		cc = 7;
    		cs = 1;
    		while(i < size){
    			sentence = GetJavaSentence(allNode[i]);
    			if(filter(sentence) == 0){cc = 5;cs = 5;printcolor("想办法绕过此类：",4);}
    			if(i == ToInt((size-1))){
    				if(cc != 5){cs = 2;cc = 3;}
    			}else{}
    			if(cc == 5){printcolor("[-]",6);}else{printcolor("[+]",1);}
    			printcolor(GetClassName(GetNodeClassName(allNode[i]))."   ",cc);
    			printcolor(sentence.StrRN(),cs);
    			i = ToInt(i+1);
    		}
    	}
    	return 0;
    }
    function main(args){
    	className = "com/l4yn3/microserviceseclab/controller/IndexController";
    	methods = GetAllMethodName(className);
    	size = GetArrayNum(methods);
    	i = 0;
    	while(i < size){
    		if(methods[i] != "<init>"){track(className,methods[i]);
    }
    		i = ToInt(i+1);
    	}
    }
    

如果对cheetah语法不熟悉，那么可以到https://github.com/Wker666/Demo中了解cheetah的详细语法，里面含有500+的渗透测试脚本可供学习。

最终我们白盒审计可以打印出如下内容：

![image](https://image.3001.net/images/20211221/1640084662_61c1b4b68c00957956c2e.png!small)

可以看到我们对没有过滤的调用链都进行了高亮显示，对有过滤的用红色进行显示。

## Step4 编写黑盒Fuzzer测试代码

### SQL注入检测函数

我们可以使用简单 or 1=1与or 1=2进行判断，为什么不能用and呢？因为我们没有默认值，所以需要通过or进行判断。

    
    
    function judgeSQLI(api){
    	res = HttpGet(api,"");
    	res1 = HttpGet(api."%27%20or%201=1--+","");
    	if(GetStrLength(res1[0]) != GetStrLength(res[0])){
    		res2 = HttpGet(api."%27%20or%202=1--+","");
    		if(GetStrLength(res2[0]) == GetStrLength(res[0])){
    			return 1;
    		}
    	}
    	return 0;
    }
    

如果你想要了解更多的cheetah编写sql注入的代码，可以看cheetah的GitHub，里面是有一个非常完整的SQL注入脚本代码的。

### 组成测试链接

因为Spring中使用大量注解进行设置，对于注解的解析，wJa提供了获取注解的方法。

  1. `GetClassAnnotation`获取类注解

  2. `GetClassMethodAnnotation`获取方法上的注解

  3. `GetClassMethodArgAnnotation`获取参数上的注解

  4. `GetAnnotationArgListValue`获取注解中list数据

  5. `GetAnnotationArgSingValue`获取注解中的数据

通过上述的注解方法我们可以构造完整的测试链接，当然我们可以编写一个参数进行解析注解参数数据。

    
    
    function getSpringAnnotationValue(an){
    	anSize = GetArrayNum(an);
    	i = 0;
    	while(i < anSize){
    		if(GetAnnotationName(an[i]) == "org/springframework/web/bind/annotation/RequestMapping"){
    			allValue = GetAnnotationArgListValue(an[i],"value");
    			return allValue[0];
    		}
    		if(GetAnnotationName(an[i]) == "org/springframework/web/bind/annotation/PostMapping"){
    			allValue = GetAnnotationArgListValue(an[i],"value");
    			return allValue[0];
    		}
    		if(GetAnnotationName(an[i]) == "org/springframework/web/bind/annotation/RequestParam"){
    			allValue = GetAnnotationArgSingValue(an[i],"value");
    			return allValue;
    		}
    
    		i = ToInt(i + 1);
    	}
    	return "";
    }
    

根据Spring的的注解，我们得到路径中的某一个值。

因为我们已经开启了8080端口的javaWeb服务，所以可以直接进行拼接组合成测试链接。

## Step5 白盒+黑盒 自动化测试

有了白盒测试和黑盒测试的代码部分，我们可以进行组装拼接，当白盒测试代码发现没有过滤函数，并且最终进入了危险函数，那么我们就启动黑盒测试进行真正意义上的Fuzzer。

这里附带完整的 白盒+黑盒 自动化测试脚本。

    
    
    #define filter1=String.valueOf(.*?)
    #define filter2=Integer.valueOf(.*?)
    function filter(sentence){
    	a = StrRe(sentence,filter1);
    	if(GetArrayNum(a) != 0){return 0;}
    	a = StrRe(sentence,filter2);
    	if(GetArrayNum(a) != 0){return 0;}
    	return 1;
    }
    function judgeSQLI(api){
    	res = HttpGet(api,"");
    	res1 = HttpGet(api."%27%20or%201=1--+","");
    	if(GetStrLength(res1[0]) != GetStrLength(res[0])){
    		res2 = HttpGet(api."%27%20or%202=1--+","");
    		if(GetStrLength(res2[0]) == GetStrLength(res[0])){
    			return 1;
    		}
    	}
    	return 0;
    }
    function track(className,methodName,url){
    	array allNode;
    	allNode = TrackVarIntoFun(className,methodName,0,"org/springframework/jdbc/core/JdbcTemplate","query",0);
    	size = GetArrayNum(allNode);
    	if(StrFindStr(GetJavaSentence(allNode[ToInt(size-1)]),".query(",0) != "-1"){
    		i = 0;
    		print(methodName."白盒测试调用链跟踪:");
    		cc = 7;
    		cs = 1;
    		while(i < size){
    			sentence = GetJavaSentence(allNode[i]);
    			noSan = filter(sentence);
    			if(noSan == 0){cc = 5;cs = 5;}
    			if(i == ToInt((size-1))){
    				if(cc != 5){cs = 2;cc = 3;}
    			}else{}
    			if(noSan == 0){
    				printcolor("[-]",6);printcolor("想办法绕过此类：",4);
    			}else{
    				printcolor("[+]",1);
    			}
    			printcolor(GetClassName(GetNodeClassName(allNode[i]))."   ",cc);
    			printcolor(sentence.StrRN(),cs);
    			i = ToInt(i+1);
    		}
    		if(cc != 5){
    			printcolor("白盒测试发现此调用链可能存在漏洞，生成测试链接进行黑盒测试".StrRN(),7);
    			an = GetClassMethodAnnotation(className,methodName);
    			arg_an = GetClassMethodArgAnnotation(className,methodName,0);
    			argName = getSpringAnnotationValue(arg_an);
    			if(argName != ""){
    				api = url.getSpringAnnotationValue(an)."?".argName."=Wker";
    				if(judgeSQLI(api) == 1){
    					printcolor("[+]生成测试链接:".api."   测试存在SQL注入漏洞!".StrRN(),3);
    				}else{
    					printcolor("[-]生成测试链接:".api."   测试不存在SQL注入漏洞!请自行测试。".StrRN(),5);
    				}
    			}else{
    				printcolor("测试链接生成失败,error:未找到参数入口!".StrRN(),5);
    			}
    		}
    	}
    	return 0;
    }
    function getSpringAnnotationValue(an){
    	anSize = GetArrayNum(an);
    	i = 0;
    	while(i < anSize){
    		if(GetAnnotationName(an[i]) == "org/springframework/web/bind/annotation/RequestMapping"){
    			allValue = GetAnnotationArgListValue(an[i],"value");
    			return allValue[0];
    		}
    		if(GetAnnotationName(an[i]) == "org/springframework/web/bind/annotation/PostMapping"){
    			allValue = GetAnnotationArgListValue(an[i],"value");
    			return allValue[0];
    		}
    		if(GetAnnotationName(an[i]) == "org/springframework/web/bind/annotation/RequestParam"){
    			allValue = GetAnnotationArgSingValue(an[i],"value");
    			return allValue;
    		}
    
    		i = ToInt(i + 1);
    	}
    	return "";
    }
    function main(args){
    	className = "com/l4yn3/microserviceseclab/controller/IndexController";
    	an = GetClassAnnotation(className);
    	classPath = "http://127.0.0.1:8080".getSpringAnnotationValue(an);
    	methods = GetAllMethodName(className);
    	size = GetArrayNum(methods);
    	i = 0;
    	while(i < size){
    		if(methods[i] != "<init>"){track(className,methods[i],classPath);
    }
    		i = ToInt(i+1);
    	}
    }
    

让我们运行一下，看一下最终执行的结果：

![image](https://image.3001.net/images/20211221/1640084672_61c1b4c0b50d18da925e4.png!small)

可以看到我们最终找到了两处白盒与黑盒完全符合要求的调用链，这样子的调用链是有极大可能存在漏洞的。


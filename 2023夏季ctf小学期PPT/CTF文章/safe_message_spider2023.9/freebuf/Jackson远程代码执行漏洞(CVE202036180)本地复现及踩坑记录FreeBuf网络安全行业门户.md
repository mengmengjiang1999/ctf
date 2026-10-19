### 一：漏洞简介

FasterXML Jackson是美国FasterXML公司的一款适用于Java的数据处理工具。jackson-databind是其中的一个具有数据绑定功能的核心组件之一。FasterXML jackson-databind 2.x <
2.9.10.8的版本存在该漏洞，该漏洞是由于org.apache.commons.dbcp2.cpdsadapter.DriverAdapterCPDS组件库存在不安全的反序列化，导致攻击者可以利用漏洞实现远程代码执行。

### 二：利用条件

开启enableDefaultTyping()

使用了com.h2database\com.newrelic.agent.java第三方依赖库

### 三：漏洞复现

  1.  **环境搭建**

    * 使用idea的maven项目进行环境搭建，操作如下所示：

    * 新建一个项目，选择maven

    * ![image](https://image.3001.net/images/20220314/1647248884_622f05f46f0ef0db16d76.png!small)

    * 填好项目名称和路径后点击Finish，idea会自动创建一个项目

    * ![image](https://image.3001.net/images/20220314/1647248902_622f0606226bb17f4c056.png!small)

    * 初始状态如图所示:

    * ![image](https://image.3001.net/images/20220314/1647248913_622f06116b08cb91af7b3.png!small)

    * 接下来替换漏洞需要的pom.xml，然后保存，idea会自动下载依赖

    * ![image](https://image.3001.net/images/20220314/1647248925_622f061d1312b06d962b4.png!small)

    * 如果没有自动下载，可以点击这里手动加载

    * ![image](https://image.3001.net/images/20220314/1647248935_622f06275b8ab102e805b.png!small)

    * 接下来可以在src -> main -> java -> poc.java创建一个poc.java文件

    * ![image](https://image.3001.net/images/20220314/1647248946_622f0632dc3cec034938e.png!small)

    * 然后需要启一个web服务并在目录下放入exec.sql这个sql文件用于反序列化成功后执行命令

    * ![image](https://image.3001.net/images/20220314/1647248957_622f063dde9cd2c9782d6.png!small)

    * 然后启动web服务并监听某端口

    * ![image](https://image.3001.net/images/20220314/1647248975_622f064fa77d462317c34.png!small)

    * 然后执行java文件会发现已弹出计算器

    * ![image](https://image.3001.net/images/20220314/1647248987_622f065b4cc4704955c1c.png!small)

  2.  **踩坑记录**

    * 执行java文件时报错程序包com.fasterxml.jackson.databind不存在

    * ![image](https://image.3001.net/images/20220314/1647248998_622f06668a900414310df.png!small)

    * 这个问题我们需要在项目根目录依次执行以下命令：

    * mvn clean install -Dmaven.test.skip=true

    * mvn -U idea:idea

    * ![image](https://image.3001.net/images/20220314/1647249010_622f0672adf81d7115808.jpg!small)

    * 然后我们会看见 BUILD SUCCESS字样代表安装成功

    * 如果发现执行完命令后出现error报错并且发现 **BUILD FAILURE** 字样，这时候可以尝试切换不同版本的mvn试试，可能与jdk版本以及mvn版本有关，如下：

    * ![image](https://image.3001.net/images/20220314/1647249025_622f0681abaddd74ff51b.png!small)

    * 然后我们继续执行java文件可能会报错：

    * ![image](https://image.3001.net/images/20220314/1647249037_622f068d8bbe5f197d8cf.png!small)

    * 这个错误是因为ObjectMapper的默认配置问题，我们需要更改ObjectMapper的默认配置，如上图所示新增一行代码或者已注释的部分代码都可以解决该问题

    * 还有可能遇到的问题是pom文件中配置了jackson的相关信息但是并没有起作用，还是报程序包com.fasterxml.jackson.databind不存在，这时我们可以尝试把这三个依赖的版本设置为同样的版本，并且重新加载maven。

    * 还有可能遇到程序报错：mapper.enableDefaultTyping(); 方法已过期，这时我们需要在pom.xml中查看jackson-databind版本是否>=2.10.0，Jackson ObjectMapper 中的 enableDefaultTyping 方法从 2.10.0 开始标记为过期，这时我们可以使用activateDefaultTyping方法来替代它或者切换版本到小于2.10.0版本。

  3. 个人github：https://artio-li.github.io/

### 五：参考链接

https://github.com/Al1ex/CVE-2020-36179

https://cn-sec.com/archives/245131.html

[https://stackoverflow.com/questions/23469784/com-fasterxml-jackson-databind-exc-unrecognizedpropertyexception-unrecognized-f#](https://stackoverflow.com/questions/23469784/com-fasterxml-jackson-databind-exc-unrecognizedpropertyexception-unrecognized-f)

https://blog.csdn.net/ls0111/article/details/77507340

https://segon.cn/jackson-objectmapper-enabledefaulttyping-deprecated.html


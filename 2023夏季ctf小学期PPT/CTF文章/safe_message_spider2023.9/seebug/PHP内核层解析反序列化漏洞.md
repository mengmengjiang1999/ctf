**作者：天融信阿尔法实验室  
公众号：<https://mp.weixin.qq.com/s/RL8_kDoHcZoED1G_BBxlWw>**

### 前言

在学习PHP的过程中发现有些PHP特性的东西不好理解，如PHP中的00截断，MD5缺陷，反序列化绕过`__wakeup`等等。本人不想拘泥于表面现象的理解，想探究PHP内核到底是怎样做到的。

下面是将用CTF中常用的一个反序列化漏洞CVE-2016-7124(绕过魔法函数`__wakeup`)为例，将此次调试PHP内核的过程分享出来。包括从内核源码调试环境的搭建，序列化与反序列化内核源码分析到最后的漏洞分析整个部分。

### 一、 一个例子引发的思考

我们可以首先看本人写的小例子。

![img](https://images.seebug.org/content/images/2019/03/26/1553567114000-ab7cb9c76e4cc6aeb218ee3a114334f5.png-w331s)

根据上图我们先介绍下PHP中的魔法函数：

我们先看下官方文档对几个常用魔法函数的介绍：

![img](https://images.seebug.org/content/images/2019/03/26/1553567115000-47f373936d6f18410d1ac0ee2c7fa8da.png-w331s)

![img](https://images.seebug.org/content/images/2019/03/26/1553567115000-a34a39fd81037f0db500b099773c927f.png-w331s)

![img](https://images.seebug.org/content/images/2019/03/26/1553567115000-096ad554dfa9970fb83cdad9bcdc002d.png-w331s)

这里稍作总结，当一个类被初始化为实例时会调用`__construct`，当被销毁时会调用`__destruct`。

当一个类调用serialize进行序列化时会自动调用`__sleep`函数，当字符串要利用unserialize反序列化成一个类时会调用`__wakeup`函数。上述魔法函数如果存在都将会自动进行调用。不用自己手动进行显示调用。

现在我们来看最开始的代码部分，在`__destruct`函数中有写入文件的敏感操作。我们这里利用反序列化构造危险的字符串有可能会造成代码执行漏洞。

当我们构造好相应的字符串准备进行利用时，我们却发现它的`__wakeup`函数中有过滤操作，这就给我们的构造造成了阻碍。因为我们知道反序列化无论如何都是要先调用`__wakeup`函数的。

这里我们不禁想到了利用这个PHP反序列化漏洞CVE-2016-7124(绕过魔法函数`__wakeup`)，轻松绕过反序列化会自动调用的魔法函数`___wakeup`，把敏感操作写入进了文件。

当然，上面的代码只是我个人举得一个简单例子，真实情况中不乏有上述情况的出现。但是这种绕过方法却使我非常感兴趣。PHP的内部到底是如何操作和处理才会影响到上层代码逻辑出现如此神奇的情况（BUG）。接下来本人将对PHP内核进行动态调试分析。探究此问题。

此漏洞(CVE-2016-7124)受影响版本PHP5系列为5.6.25之前，7.x系列为7.0.10之前。所以我们后面会编译两个版本：一为不受此漏洞影响的版本7.3.0，另一个版本为漏洞存在的版本5.6.10。通过两个版本的对比来更详细的了解其差异。

### 二、PHP源码调试环境搭建

我们都知道PHP是由C语言开发，因本人所使用环境为WIN 10,所以主要介绍Windows下的环境搭建。我们需要如下材料：

  * PHP源码。

  * PHP SDK工具包，用于构建PHP

  * 调试所需要IDE。

源码可在GITHUB上下载，链接：<https://github.com/php/php-src>，可以选择所需要的版本进行下载。

PHP SDK的工具包下载地址：[https://github.com/Microsoft/php-sdk-binary-tools
](https://github.com/Microsoft/php-sdk-binary-tools%20%E8%BF%99%E4%B8%AA%E5%9C%B0%E5%9D%80%E6%89%80%E4%B8%8B%E8%BD%BD%E7%9A%84%E5%B7%A5%E5%85%B7%E5%8C%85%E5%8F%AA%E6%94%AF%E6%8C%81VC14)
这个地址所下载的工具包只支持VC14，VC15。当然你也可以从<https://windows.php.net/downloads/>
找到支持PHP低版本的VC11,VC12等，在使用PHP SDK之前必须保证你有安装对应版本Windows SDK组件的VS。

后文中会使用PHP7.3.0和5.6.10，下面会介绍这两个版本的源码编译，其他版本手法类似。

#### 2.1 编译Windows PHP 7.3.0

本机环境WIN10 X64，PHP SDK是在上述github链接上下载。进入SDK目录，发现4个批处理文件，这里双击phpsdk-vc15-x64。

![img](https://images.seebug.org/content/images/2019/03/26/1553567116000-6f084d7c87ec299c16ffa30ffd7d25e7.png-w331s)

接着在此shell中输入 phpsdk_buildtree php7，会发现同目录下出现了php7文件夹，并且shell目录也发生了变化。

![img](https://images.seebug.org/content/images/2019/03/26/1553567116000-1889f3b75a0df5417a3008e683cb4b59.png-w331s)

接着我们把解压后的源码放在\php7\vc15\x64下，shell进入此文件夹内，利用phpsdk_deps –update –branch master
命令更新下载相关依赖组件。等待完成后，进入源码目录下双击buildconf.bat批处理文件，它会释放configure.bat和configure.js两个文件，在shell中运行configure
–disable-all –enable-cli –enable-debug –enable-phar 配置相应的编译选项，如还有别的需求，可执行
configure –help 查看

![img](https://images.seebug.org/content/images/2019/03/26/1553567116000-b5f4e5e34db953f7b45518b259a3e2a6.png-w331s)

根据提示，直接使用nmake进行编译。

![img](https://images.seebug.org/content/images/2019/03/26/1553567116000-f2d6c91af85ae82cfc24c4e6badae5f6.png-w331s)

编译完成，可执行文件目录在`php7\vc15\x64\php-src\x64\Debug_TS`文件夹下。我们可输入php -v查看相关信息。

![img](https://images.seebug.org/content/images/2019/03/26/1553567117000-6261cb59d3658aff76ebc30af424d2f8.png-w331s)

#### 2.2 编译Windows PHP 5.6.10

方法跟7.3.0 相同，只需注意的是PHP5.6使用Windows SDK组件版本为VC11，需要下载VS2012，并且不能使用github上下载的PHP
SDK进行编译，需要在<https://windows.php.net/downloads/> 上选择VC11 的PHP
SDK和相关依赖组件进行编译，其余和上述完全相同，这里不再重复。

![img](https://images.seebug.org/content/images/2019/03/26/1553567117000-21a867aaceed92eca8942da194e133a1.png-w331s)

#### 2.3 调试配置

因为我们上述已经编译好了PHP解释器，我们这里直接使用VSCODE来进行调试。

下载完成后安装C/C++调试扩展。

![img](https://images.seebug.org/content/images/2019/03/26/1553567117000-0226745f72a1e33e1e3c9b74c811e012.png-w331s)

接着打开源码目录，点击调试—>打开配置，会打开launch.json文件。

![img](https://images.seebug.org/content/images/2019/03/26/1553567117000-4b3adf8b8207c4e34995351e7e643ea8.png-w331s)

根据上图，配置好这三个参数后，可在当前目录下1.php中写PHP代码，在PHP源码中下断点直接进行调试。

调试环境搭建完成。

### 三、PHP反序列化源码解析

一般提及PHP反序列化，往往就是serialize和unserialize两个成对出现的函数，当然必不可少的还有`__sleep()`和`__wakeup()`这两个魔术方法。众所周知，序列化简单点来说就是对象存文件，反序列化刚好相反，从文件中把对象读取出来并实例化。

下面，我们根据上面搭好的调试环境，通过动态调试的手法来直观的反应PHP（7.3.0版本）中序列化与反序列化到底干了哪些事情。

#### 3.1 serialize源码分析

我们先写个不含有`__sleep`魔法函数的简单Demo：

![img](https://images.seebug.org/content/images/2019/03/26/1553567118000-7408db23dc5822342a96098fd55421cf.png-w331s)

接着我们在源码中全局搜索serialize函数，定位此函数是在var.c文件中。我们直接在函数头下断点，并启动调试。

![img](https://images.seebug.org/content/images/2019/03/26/1553567118000-0e1e84a007aca10bf0d1afe91c6ea66e.png-w331s)

我们可见在做了一些准备工作后，开始进入序列化处理函数，我们跟进`php_var_serialize`函数。

![img](https://images.seebug.org/content/images/2019/03/26/1553567118000-309ff47289939621a7cec3acac517e69.png-w331s)

我们这里继续跟进`php_var_serialize_intern`函数，下面就是主要处理函数了，因为函数代码比较多，我们这里只截出关键部分，此函数还在var.c文件中。

![img](https://images.seebug.org/content/images/2019/03/26/1553567119000-1b6be8add616e5b3fb5b02eb8d998715.png-w331s)

整个函数的结构是switch
case，通过宏`Z_TYPE_P`解析struc变体的类型(此宏展开为struc->u1.v.type)，来判断要序列化的类型，从而进入相应的CASE部分进行操作。下图为类型定义。

![img](https://images.seebug.org/content/images/2019/03/26/1553567119000-75b65b6069f2884e74798c1164f31866.png-w331s)

根据上图红框中的数字8，我们可知此时需要要序列化为一个对象`IS_OBJECT`，进入相应的CASE分支

![img](https://images.seebug.org/content/images/2019/03/26/1553567119000-7eb8d592405372c11cb43e893d3765e8.png-w331s)

我们在上图中看到了魔法函数`__sleep`的调用时机，因为我们写的Demo中并没有此函数，所以流程并不会进入此分支。不同的分支代表不同的处理流程，我们稍后再看带有魔法函数`__sleep`的流程。

![img](https://images.seebug.org/content/images/2019/03/26/1553567120000-621bdbf065997f125c7b38cf60d5a7a6.png-w331s)

因上面`case
IS_OBJECT`分支中没有流程命中，case中又没有break语句，继续执行进入`IS_ARRAY`分支，在这里从struc结构中提取出类名，计算其长度并赋值到buf结构中，并提取出类中要序列化的结构存入哈希数组中。

![img](https://images.seebug.org/content/images/2019/03/26/1553567120000-d702e2fdcd8a16e34bbb363e372701b5.png-w331s)

接下来就是利用`php_var_serialize_intern`函数递归解析整个哈希数组的过程，从中分别提取出变量名和值进行格式解析并将解析完成的字符串拼接到buf结构中。最后当整个过程结束后，整个字符串讲完全存进柔性数组结构buf中。

![img](https://images.seebug.org/content/images/2019/03/26/1553567120000-f8d25e6e32204e4c22eda44c0ad0068b.png-w331s)

从上图红框中可看出跟最终结果是相吻合的。我们接下来稍微修改下Demo，添加魔法函数`__sleep`，根据官方文档中描述，`__sleep`函数必须返回一个数组。我们并在该函数中调用了一个类的成员函数。观察其具体行为。

![img](https://images.seebug.org/content/images/2019/03/26/1553567120000-8b2c2360a2b02bc8a1bfbdd23fe52aaf.png-w331s)

前面流程完全相同，此处不再重复，我们从分支点开始看。

![img](https://images.seebug.org/content/images/2019/03/26/1553567121000-8aaf5a5abfdcfb84b0d08bcb6528ca8f.png-w331s)

我们直接跟进`php_var_serialize_call_sleep`函数。

![img](https://images.seebug.org/content/images/2019/03/26/1553567121000-966c0fb0c0f0d5237fb59f9c731a35cf.png-w331s)

我们这里继续跟进`call_user_function`，根据宏定义，它实际上是调用了`_call_user_function_ex`函数，在这里做了一些拷贝动作，故不做截图，流程接下来进入`zend_call_function`函数的调用。

![img](https://images.seebug.org/content/images/2019/03/26/1553567121000-0fc8b14374b1c9bef09dcbfed4fa45bc.png-w331s)

函数`zend_call_function`中，实际情况下，在`__sleep`中需要做一些我们自己的事情，这里PHP将要做的操作压入PHP自己的`zend_vm`引擎堆栈中，稍后会进行一条条解析(就是解析相应的OPCODE)。

![img](https://images.seebug.org/content/images/2019/03/26/1553567121000-d131abe9cbab0b1e47f00718bbac0774.png-w331s)

这里流程会命中此分支，我们跟进`zend_execute_ex`函数。

![img](https://images.seebug.org/content/images/2019/03/26/1553567122000-498e5c58e57ef9b94ad780319157406d.png-w331s)

我们这里可以看到在`ZEND_VM`中，整体体处理流程为while(1)循环，不断解析ZEND_VM栈中的操作。上图红框中ZEND_VM引擎会利用`ZEND_FASTCALL`方式派发到到相应的处理函数。

![img](https://images.seebug.org/content/images/2019/03/26/1553567122000-ba882da1d49a6cd533d2c4aa7925a656.png-w331s)

![img](https://images.seebug.org/content/images/2019/03/26/1553567122000-40fb58dfa7a00f36510e80e4b770da1d.png-w331s)

因为我们在`__sleep`中调用了成员函数show,这里首先定位出了show，接着会将接下来的操作继续压入`ZEND_VM`堆栈中进行下一轮新的解析(这里是处理show中的操作)，直到解析完整个操作为止。我们这里不再继续跟进。

![img](https://images.seebug.org/content/images/2019/03/26/1553567122000-ee01b2d9ff2d5a4fee34afb9defe2794.png-w331s)

还记得上面的传出参数retval么，也就是`__sleep`的返回值，上图为返回数组的第一个元素x，当然你也可以从变量中直接查看。

绕了这么大一圈，殊途同归，在处理完`_sleep`函数中的一系列操作之后，接下来用`php_var_serialize_class`函数来序列化类名，递归序列化其`_sleep`函数返回值中的结构。最终都把结果存在了buf结构中。至此序列化的整个流程完毕。

##### 3.1.1 SERIALIZE流程小结。

我们总结下序列化的流程 ：

当没有魔法函数时，序列化类名–>利用递归序列化剩下的结构

当存在魔法函数时，调用魔法函数`__sleep`–>利用ZEND_VM引擎解析PHP操作—>返回需要序列化结构的数组–>序列化类名–>利用递归序列化`__sleep`的返回值结构。

#### 3.2 unserialize源码分析

看完serialize的流程，接下来，我们还是从最简单的一个Demo来看unserialize流程。此例子不含魔法函数。

![img](https://images.seebug.org/content/images/2019/03/26/1553567123000-4eb7c0fee2edee3d179388a2da9a79f2.png-w331s)

方法跟上面相同，unserialize源码也在var.c文件中。

![img](https://images.seebug.org/content/images/2019/03/26/1553567123000-380b0f2e96d4f5041bc258a5bca7782c.png-w331s)

![img](https://images.seebug.org/content/images/2019/03/26/1553567123000-aab11183308aa18d11e006ebdb7455b8.png-w331s)

上图中涉及到了PHP7中的新特性，带过滤的反序列化，根据`allowed_classes`的设置情况来过滤相应的PHP对象，防止非法数据注入。被过滤的对象会被转化成`__PHP_Incomplete_Class`对象不能被直接使用，但是这里对反序列化流程没有影响，这里不做详细探讨。我们跟进`php_var_unserialize`函数。

![img](https://images.seebug.org/content/images/2019/03/26/1553567123000-3ef9b37ee8f08fb751ed362be4f7242d.png-w331s)

我们这里继续跟入`php_var_unserialize_internal`函数。

![img](https://images.seebug.org/content/images/2019/03/26/1553567124000-1399874d63245919472b5fc36fd6060e.png-w331s)

此函数内部主要操作流程为对字符串进行解析，然后跳转到相应的处理流程。上图中解析出第一个字母0，代表此次反序列化为一个对象。

![img](https://images.seebug.org/content/images/2019/03/26/1553567124000-8b31493ada7abd47795894e5f439e76c.png-w331s)

这里首先会解析出对象名字，并进行查表操作确定此对象确实存在，我们继续向下看。

![img](https://images.seebug.org/content/images/2019/03/26/1553567126000-7c6186b63ea56c5cbd44ee8148643c7e.png-w331s)

上述操作做完之后，我们这里根据对象名称new出了自己新的对象并进行了初始化，但是我们的反序列化操作还是没有完成，我们跟进`object_common2`函数。

在这里我们看到了对魔法函数的判断与检测，但是调用部分并不在此。我们继续跟进process_nested_data函数。

![img](https://images.seebug.org/content/images/2019/03/26/1553567127000-e2bd9760a0939c4624751c22378859cb.png-w331s)

![img](https://images.seebug.org/content/images/2019/03/26/1553567128000-b054da780ede508e246a239a9498166d.png-w331s)

看来这个函数利用WHILE循环来嵌套解析剩余的部分了，·其中包含两个`php_var_unserialize_internal`函数，第一个会解析名称，第二个是解析名称所对应的值。`process_nested_data`函数运行完毕后，字符串解析完毕，反序列化操作主要内容已经完成，流程即将进入尾声了。

![img](https://images.seebug.org/content/images/2019/03/26/1553567128000-308897e08e9148ad2c9e9530df5711bb.png-w331s)

逐层返回至最初的函数PHP_FUNCTION中，我们看到就是一些扫尾工作了，释放申请的空间，反序列化完毕。这里并没有调用到我们的魔法函数`__wakeup`。为了找出`__wakeup`的调用时机，我们这里修改下Demo。

![img](https://images.seebug.org/content/images/2019/03/26/1553567129000-6b888f869c1d93bd9dd688a6fe7406d2.png-w331s)

这里开始新的一轮调试。发现在序列化完成后，在`PHP_VAR_UNSERIALIZE_DESTROY`释放空间处出现了我们所希望看到的调用。

![img](https://images.seebug.org/content/images/2019/03/26/1553567130000-0d03c4eb76db44699cfa684d0e44140e.png-w331s)

还记得反序列化流程中当发现有`__wakeup`时对其进行的`VAR_WAKEUP_FLAG`标志么，在这里当遍历`bar_dtor_hash`数组遇到这个标志时，正式开启对`__wakeup`调用，后期的调用手法和前面所介绍的`__sleep`调用手法完全相同，这里不再做重复说明。至此，反序列化所有流程完毕。

##### 3.2.1 UNSERIALIZE流程小结。

我们可以从上面可以看到，反序列化流程相对于序列化流程来说并没有因为是否出现魔法函数来对流程造成分歧。Unserialize流程如下：

获取反序列化字符串–>根据类型进行反序列化—>查表找到对应的反序列化类–>根据字符串判断元素个数–>new出新实例–>迭代解析化剩下的字符串–>判断是否具有魔法函数__wakeup并标记—>释放空间并判断是否具有具有标记—>开启调用。

### 四、 PHP反序列化漏洞

有了上面源码基础的铺垫，我们现在再来探究漏洞CVE-2016-7124(绕过`__wakeup`)魔法函数。因此漏洞对版本有一定要求，我们使用上面编译好的另一个PHP版本(5.6.10)来复现和调试此漏洞。

首先我们进行一下漏洞复现：

![img](https://images.seebug.org/content/images/2019/03/26/1553567130000-312fbb2cdd307838cb3f2ad6be7b6938.png-w331s)

我们这里可以看到，TEST类中只包含一个元素$a，我们这里在反序列化时当修改元素字符串中代表元素个数的数值时，会触发此漏洞，该类避过了魔法函数`__wakeup`的调用。

当然在触发漏洞的过程中也发现了一个有趣的现象，触发手段并不只有这一种.

![img](https://images.seebug.org/content/images/2019/03/26/1553567130000-5b34f3a21017a0297748ec4ba4543c05.png-w331s)

上图中4个payload所对应的反序列化操作都会触发此漏洞。虽然说下方这四个都会触发漏洞，但是其中还有一些微小的差别。这里我们稍微修改下代码：

![img](https://images.seebug.org/content/images/2019/03/26/1553567131000-99607bbcafe7b8a07e3fd5e4f09aeb8e.png-w331s)

我们根据上图可以看到，在反序列化的字符串中，只要在解析类中的元素出现错误时，都会触发此漏洞。但是更改类元素内部操作(如上图的修改字符串长度，类变量类型等)会导致类成员变量赋值失败。只有修改类成员的个数(比原有成员个数大)时，才能保证类成员赋值时成功的。

我们下面来通过调试来看问题所在：

根据第三部分我们对反序列化源码的分析，猜测可能是在最后解析变量那里出了问题。我们这里直接上调试器动态调试下：

![img](https://images.seebug.org/content/images/2019/03/26/1553567131000-9d98fa35a20103e89af33fc4ba4bb4e0.png-w331s)

我们可以看到，与7.3.0版本的源码对比，此版本没有过滤参数，且经过这么多版本的迭代，低版本的处理过程现在看来也相对简略。但是整体谐逻辑并没有改变，我们这里直接跟进`php_var_unserialize`函数，此后相同逻辑不再进行重复说明，我们直接跟到差异处(object_common2函数)也就是处理类中成员变量的代码

![img](https://images.seebug.org/content/images/2019/03/26/1553567131000-a27e62f27131ef44b3b5bfe6998d3318.png-w331s)

在函数`object_common2`中，存在两个主要操作，`process_nested_data`迭代解析类中的数据和魔法函数`__wakeup`的调用，且当`process_nested_data`函数解析失败后，直接返回0值，后面的`__wakeup`函数将没有调用的机会。

这里就解释了为何触发漏洞不止一种payload。

![img](https://images.seebug.org/content/images/2019/03/26/1553567132000-54aca14c607c37ab647a8f02afbea301.png-w331s)

当只修改类成员的个数时，while循环可以完成的进行一次，这使得我们类中成员变量能被完整的赋值。当修改成员变量内部时，`pap_var_unserialize`函数调用失败，紧接着会调用`zval_dtor`
和`FREE_ZVAL`函数释放当前key(变量)空间，导致类中的变量赋值失败。

反观在PHP7.3.0版本中此处并没有出现调用过程，只是做了简单的标记，整个魔法函数的调用过程的时机移至释放数据处。这样就避免了这个绕过的问题。

此漏洞应该属于逻辑上的缺陷导致的。

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/866/>


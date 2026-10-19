**Nexus Repository Manager
3最近曝出两个el表达式解析漏洞，编号为[CVE-2020-10199](https://support.sonatype.com/hc/en-us/articles/360044882533)，[CVE-2020-10204](https://support.sonatype.com/hc/en-us/articles/360044356194-CVE-2020-10204-Nexus-Repository-Manager-3-Remote-Code-Execution-2020-03-31)，都是由Github Secutiry
Lab团队的@pwntester发现。由于之前Nexus3的漏洞没有去跟踪，所以当时diff得很头疼，并且Nexus3
bug与安全修复都是混在一起，更不容易猜到哪个可能是漏洞位置了。后面与@r00t4dm师傅一起复现出了[CVE-2020-10204](https://support.sonatype.com/hc/en-us/articles/360044356194-CVE-2020-10204-Nexus-Repository-Manager-3-Remote-Code-Execution-2020-03-31)，[CVE-2020-10204](https://support.sonatype.com/hc/en-us/articles/360044356194-CVE-2020-10204-Nexus-Repository-Manager-3-Remote-Code-Execution-2020-03-31)是[CVE-2018-16621](https://support.sonatype.com/hc/en-us/articles/360010789153-CVE-2018-16621-Nexus-Repository-Manager-Java-Injection-October-17-2018)的绕过，之后又有师傅弄出了[CVE-2020-10199](https://support.sonatype.com/hc/en-us/articles/360044882533)，这三个漏洞的根源是一样的，其实并不止这三处，官方可能已经修复了好几处这样的漏洞，由于历史不太好追溯回去，所以加了可能，通过后面的分析，就能看到了。还有之前的[CVE-2019-7238](https://support.sonatype.com/hc/en-us/articles/360017310793-CVE-2019-7238-Nexus-Repository-Manager-3-Missing-Access-Controls-and-Remote-Code-Execution-2019-02-05)，这是一个jexl表达式解析，一并在这里分析下，以及对它的修复问题，之前看到有的分析文章说这个漏洞是加了个权限来修复，可能那时是真的只加了个权限吧，不过我测试用的较新的版本，加了权限貌似也没用，在Nexus3高版本已经使用了jexl白名单的沙箱。**

##  测试环境

文中会用到三个Nexus3环境：

> nexus-3.14.0-04
>
> nexus-3.21.1-01
>
> nexus-3.21.2-03

nexus-3.14.0-04用于测试jexl表达式解析，nexus-3.21.1-01用于测试jexl表达式解析与el表达式解析以及diff，nexus-3.21.2-03用于测试el表达式解析以及diff

##  漏洞diff

CVE-2020-10199、CVE-2020-10204漏洞的修复界限是3.21.1与3.21.2，但是github开源的代码分支好像不对应，所以只得去下载压缩包来对比了。在官方下载了nexus-3.21.1-01与nexus-3.21.2-03，但是beyond对比需要目录名一样，文件名一样，而不同版本的代码有的文件与文件名都不一样。我是先分别反编译了对应目录下的所有jar包，然后用脚本将nexus-3.21.1-01中所有的文件与文件名中含有3.21.1-01的替换为了3.21.2-03，同时删除了META文件夹，这个文件夹对漏洞diff没什么用并且影响diff分析，所以都删除了，下面是处理后的效果：

![](https://image.3001.net/images/20200415/1586915886_5e966a2e68196.png!small)

如果没有调试和熟悉之前的Nexus3漏洞，直接去看diff可能会看得很头疼，没有目标的diff。

##  路由以及对应的处理类

###  一般路由

抓下nexus3发的包，随意的点点点，可以看到大多数请求都是POST类型的，URI都是/service/extdirect：

![](https://image.3001.net/images/20200415/1586915911_5e966a47b691e.png!small)

post内容如下：

    
    
    {"action":"coreui_Repository","method":"getBrowseableFormats","data":null,"type":"rpc","tid":7}

可以看下其他请求，json中都有action与method这两个key，在代码中搜索下coreui_Repository这个关键字：

![](https://image.3001.net/images/20200415/1586915926_5e966a56d40c6.png!small)

可以看到这样的地方，展开看下代码：

![](https://image.3001.net/images/20200415/1586915945_5e966a69d86a1.png!small)

通过注解方式注入了action，上面post的method->getBrowseableFormats也在中，通过注解注入了对应的method：

![](https://image.3001.net/images/20200415/1586915961_5e966a792df3f.png!small)

所以之后这样的请求，我们就很好定位路由与对应的处理类了

###  API路由

Nexus3的API也出现了漏洞，来看下怎么定位API的路由，在后台能看到Nexus3提供的所有API。

![](https://image.3001.net/images/20200415/1586916055_5e966ad72d515.png!small)

点几个看下包，有GET、POST、DELETE、PUT等类型的请求：

![](https://image.3001.net/images/20200415/1586916067_5e966ae3ca6ba.png!small)

没有了之前的action与method，这里用URI来定位，直接搜索/service/rest/beta/security/content-selectors定位不到，所以缩短关键字，用/beta/security/content-selectors来定位：

![](https://image.3001.net/images/20200415/1586916078_5e966aeed4f21.png!small)

![](https://image.3001.net/images/20200415/1586916091_5e966afb5313f.png!small)

通过@Path注解来注入URI，对应的处理方式也使用了对应的@GET、@POST来注解

可能还有其他类型的路由，不过也可以使用上面类似的方式进行搜索来定位。还有Nexus的权限问题，可以看到上面有的请求通过@RequiresPermissions来设置了权限，不过还是以实际的测试权限为准，有的在到达之前也进行了权限校验，有的操作虽然在web页面的admin页面，不过本不需要admin权限，可能无权限或者只需要普通权限。

##  buildConstraintViolationWithTemplate造成的几次Java EL漏洞

在跟踪调试了[CVE-2018-16621](https://support.sonatype.com/hc/en-us/articles/360010789153-CVE-2018-16621-Nexus-Repository-Manager-Java-Injection-October-17-2018)与[CVE-2020-10204](https://support.sonatype.com/hc/en-us/articles/360044356194-CVE-2020-10204-Nexus-Repository-Manager-3-Remote-Code-Execution-2020-03-31)之后，感觉buildConstraintViolationWithTemplate这个keyword可以作为这个漏洞的根源，因为从调用栈可以看出这个函数的调用处于Nexus包与hibernate-validator包的分界，并且计算器的弹出也是在它之后进入hibernate-validator的处理流程，即buildConstraintViolationWithTemplate(xxx).addConstraintViolation()，最终在hibernate-validator包中的ElTermResolver中通过valueExpression.getValue(context)完成了表达式的执行，与@r00t4dm师傅也说到了这个：

![](https://image.3001.net/images/20200415/1586916134_5e966b26aa079.png!small)

于是反编译了Nexus3所有jar包，然后搜索这个关键词（使用的修复版本搜索，主要是看有没有遗漏的地方没修复；Nexue3有开源部分代码，也可以直接在源码搜索）：

    
    
    F:\compare-file\nexus-3.21.2-03-win64\nexus-3.21.2-03\system\com\sonatype\nexus\plugins\nexus-healthcheck-base\3.21.2-03\nexus-healthcheck-base-3.21.2-03\com\sonatype\nexus\clm\validator\ClmAuthenticationValidator.java:
       26           return this.validate(ClmAuthenticationType.valueOf(iqConnectionXo.getAuthenticationType(), ClmAuthenticationType.USER), iqConnectionXo.getUsername(), iqConnectionXo.getPassword(), context);
       27        } else {
       28:          context.buildConstraintViolationWithTemplate("unsupported annotated object " + value).addConstraintViolation();
       29           return false;
       30        }
       ..
       35        case 1:
       36           if (StringUtils.isBlank(username)) {
       37:             context.buildConstraintViolationWithTemplate("User Authentication method requires the username to be set.").addPropertyNode("username").addConstraintViolation();
       38           }
       39  
       40           if (StringUtils.isBlank(password)) {
       41:             context.buildConstraintViolationWithTemplate("User Authentication method requires the password to be set.").addPropertyNode("password").addConstraintViolation();
       42           }
       43  
       ..
       52           }
       53  
       54:          context.buildConstraintViolationWithTemplate("To proceed with PKI Authentication, clear the username and password fields. Otherwise, please select User Authentication.").addPropertyNode("authenticationType").addConstraintViolation();
       55           return false;
       56        default:
       57:          context.buildConstraintViolationWithTemplate("unsupported authentication type " + authenticationType).addConstraintViolation();
       58           return false;
       59        }F:\compare-file\nexus-3.21.2-03-win64\nexus-3.21.2-03\system\org\hibernate\validator\hibernate-validator\6.1.0.Final\hibernate-validator-6.1.0.Final\org\hibernate\validator\internal\constraintvalidators\hv\ScriptAssertValidator.java:34        if (!validationResult && !this.reportOn.isEmpty()) {35           constraintValidatorContext.disableDefaultConstraintViolation();36:          constraintValidatorContext.buildConstraintViolationWithTemplate(this.message).addPropertyNode(this.reportOn).addConstraintViolation();37        }38  F:\compare-file\nexus-3.21.2-03-win64\nexus-3.21.2-03\system\org\hibernate\validator\hibernate-validator\6.1.0.Final\hibernate-validator-6.1.0.Final\org\hibernate\validator\internal\engine\constraintvalidation\ConstraintValidatorContextImpl.java:
       55     }
       56  
       57:    public ConstraintViolationBuilder buildConstraintViolationWithTemplate(String messageTemplate) {
       58        return new ConstraintValidatorContextImpl.ConstraintViolationBuilderImpl(messageTemplate, this.getCopyOfBasePath());
       59     }F:\compare-file\nexus-3.21.2-03-win64\nexus-3.21.2-03\system\org\sonatype\nexus\nexus-cleanup\3.21.0-02\nexus-cleanup-3.21.0-02\org\sonatype\nexus\cleanup\storage\config\CleanupPolicyAssetNamePatternValidator.java:18           } catch (RegexCriteriaValidator.InvalidExpressionException var4) {19              context.disableDefaultConstraintViolation();20:             context.buildConstraintViolationWithTemplate(var4.getMessage()).addConstraintViolation();21              return false;22           }F:\compare-file\nexus-3.21.2-03-win64\nexus-3.21.2-03\system\org\sonatype\nexus\nexus-cleanup\3.21.2-03\nexus-cleanup-3.21.2-03\org\sonatype\nexus\cleanup\storage\config\CleanupPolicyAssetNamePatternValidator.java:
       18           } catch (RegexCriteriaValidator.InvalidExpressionException var4) {
       19              context.disableDefaultConstraintViolation();
       20:             context.buildConstraintViolationWithTemplate(this.getEscapeHelper().stripJavaEl(var4.getMessage())).addConstraintViolation();
       21              return false;
       22           }F:\compare-file\nexus-3.21.2-03-win64\nexus-3.21.2-03\system\org\sonatype\nexus\nexus-scheduling\3.21.2-03\nexus-scheduling-3.21.2-03\org\sonatype\nexus\scheduling\constraints\CronExpressionValidator.java:
       29        } catch (IllegalArgumentException var4) {
       30           context.disableDefaultConstraintViolation();
       31:          context.buildConstraintViolationWithTemplate(this.getEscapeHelper().stripJavaEl(var4.getMessage())).addConstraintViolation();
       32           return false;
       33        }F:\compare-file\nexus-3.21.2-03-win64\nexus-3.21.2-03\system\org\sonatype\nexus\nexus-security\3.21.2-03\nexus-security-3.21.2-03\org\sonatype\nexus\security\privilege\PrivilegesExistValidator.java:
       42           if (!privilegeId.matches("^[a-zA-Z0-9\\-]{1}[a-zA-Z0-9_\\-\\.]*$")) {
       43              context.disableDefaultConstraintViolation();
       44:             context.buildConstraintViolationWithTemplate("Invalid privilege id: " + this.getEscapeHelper().stripJavaEl(privilegeId) + ". " + "Only letters, digits, underscores(_), hyphens(-), and dots(.) are allowed and may not start with underscore or dot.").addConstraintViolation();   45              return false;   46           }   ..   55        } else {   56           context.disableDefaultConstraintViolation();   57:          context.buildConstraintViolationWithTemplate("Missing privileges: " + missing).addConstraintViolation();   58           return false;   59        }F:\compare-file\nexus-3.21.2-03-win64\nexus-3.21.2-03\system\org\sonatype\nexus\nexus-security\3.21.2-03\nexus-security-3.21.2-03\org\sonatype\nexus\security\role\RoleNotContainSelfValidator.java:   49              if (this.containsRole(id, roleId, processedRoleIds)) {   50                 context.disableDefaultConstraintViolation();   51:                context.buildConstraintViolationWithTemplate(this.message).addConstraintViolation();   52                 return false;   53              }F:\compare-file\nexus-3.21.2-03-win64\nexus-3.21.2-03\system\org\sonatype\nexus\nexus-security\3.21.2-03\nexus-security-3.21.2-03\org\sonatype\nexus\security\role\RolesExistValidator.java:   42        } else {   43           context.disableDefaultConstraintViolation();   44:          context.buildConstraintViolationWithTemplate("Missing roles: " + missing).addConstraintViolation();
       45           return false;
       46        }F:\compare-file\nexus-3.21.2-03-win64\nexus-3.21.2-03\system\org\sonatype\nexus\nexus-validation\3.21.2-03\nexus-validation-3.21.2-03\org\sonatype\nexus\validation\ConstraintViolationFactory.java:
       75        public boolean isValid(ConstraintViolationFactory.HelperBean bean, ConstraintValidatorContext context) {
       76           context.disableDefaultConstraintViolation();
       77:          ConstraintViolationBuilder builder = context.buildConstraintViolationWithTemplate(this.getEscapeHelper().stripJavaEl(bean.getMessage()));
       78           NodeBuilderCustomizableContext nodeBuilder = null;
       79           String[] var8;

后面作者也发布了[漏洞分析](https://github.com/Cryin/Paper/blob/master/CVE-2018-16621%20Nexus%20Repository%20Manager3%20%E4%BB%BB%E6%84%8FEL%E8%A1%A8%E8%BE%BE%E5%BC%8F%E6%B3%A8%E5%85%A5.md)，确实用了buildConstraintViolationWithTemplate作为了漏洞的根源，利用这个关键点做的污点跟踪分析。

从上面的搜索结果中可以看到，el表达式导致的那三个CVE关键点也在其中，同时还有其他几个地方，有几个使用了this.getEscapeHelper().stripJavaEl做了清除，还有几个，看起来似乎也可以，心里一阵狂喜？然而，其他几个没有做清除的地方虽然能通过路由进入，但是利用不了，后面会挑选其中的一个做下分析。所以在开始说了官方可能修复了几个类似的地方，猜想有两种可能：

官方自己察觉到了那几个地方也会存在el解析漏洞，所以做了清除

有其他漏洞发现者提交了那几个做了清除的漏洞点，因为那几个地方可以利用；但是没清除的那几个地方由于没法利用，所以发现者并没有提交，官方也没有去做清除

不过感觉后一种可能性更大，毕竟官方不太可能有的地方做清除，有的地方不做清除，要做也是一起做清除工作。

###  CVE-2018-16621分析

这个漏洞对应上面的搜索结果是RolesExistValidator，既然搜索到了关键点，自己来手动逆向回溯下看能不能回溯到有路由处理的地方，这里用简单的搜索回溯下。

关键点在RolesExistValidator的isValid，调用了buildConstraintViolationWithTemplate。搜索下有没有调用RolesExistValidator的地方：

![](https://image.3001.net/images/20200415/1586916183_5e966b575c570.png!small)

在RolesExist中有调用，这种写法一般会把RolesExist当作注解来使用，并且进行校验时会调用RolesExistValidator.isValid()。继续搜索RolesExist：

![](https://image.3001.net/images/20200415/1586916194_5e966b620c193.png!small)

有好几处直接使用了RolesExist对roles属性进行注解，可以一个一个去回溯，不过按照Role这个关键字RoleXO可能性更大，所以先看这个（UserXO也可以的），继续搜索RoleXO：

![](https://image.3001.net/images/20200415/1586916209_5e966b7184b74.png!small)

会有很多其他干扰的，比如第一个红色标注RoleXOResponse，这种可以忽略，我们找直接使用RoleXO的地方。在RoleComponent中，看到第二个红色标注这种注解大概就知道，这里能进入路由了。第三个红色标注使用了roleXO，并且有roles关键字，上面RolesExist也是对roles进行注解的，所以这里猜测是对roleXO进行属性注入。有的地方反编译出来的代码不好理解，可以结合源码看：

![](https://image.3001.net/images/20200415/1586916223_5e966b7fe4c81.png!small)

可以看到这里就是将提交的参数注入给了roleXO，RoleComponent对应的路由如下：

![](https://image.3001.net/images/20200415/1586916234_5e966b8a81ce5.png!small)

通过上面的分析，我们大概知道了能进入到最终的RolesExistValidator，不过中间可能还有很多条件需要满足，需要构造payload然后一步一步测。这个路由对应的web页面位置如下：

![](https://image.3001.net/images/20200415/1586916625_5e966d11dcfbe.png!small)

测试（这里使用的3.21.1版本，CVE-2018-16621是之前的漏洞，在3.21.1早修复了，不过3.21.1又被绕过了，所以下面使用的是绕过的情况，将$换成$\\\x去绕过，绕过在后面两个CVE再说）：

![](https://image.3001.net/images/20200415/1586916637_5e966d1d7dccb.png!small)

修复方式：

![](https://image.3001.net/images/20200415/1586916651_5e966d2bab229.png!small)

加上了getEscapeHelper().stripJavaEL对el表达式做了清除，将${替换为了{，之后的两个CVE就是对这个修复方式的绕过：

![](https://image.3001.net/images/20200415/1586916663_5e966d37f365c.png!small)

###  CVE-2020-10204分析

这就是上面说到的对之前stripJavaEL修复的绕过，这里就不细分析了，利用$\\\x格式就不会被替换掉（使用3.21.1版本测试）：

![](https://image.3001.net/images/20200415/1586916682_5e966d4a2165b.png!small)

###  CVE-2020-10199分析

这个漏洞对应上面搜索结果是ConstraintViolationFactory：

![](https://image.3001.net/images/20200415/1586916732_5e966d7ce0ffd.png!small)

buildConstraintViolationWith（标号1）出现在了HelperValidator（标号2）的isValid中，HelperValidator又被注解在HelperAnnotation（标号3、4）之上，HelperAnnotation注解在了HelperBean（标号5）之上，在ConstraintViolationFactory.createViolation方法中使用到了HelperBean（标号6、7）。按照这个思路要找调用了ConstraintViolationFactory.createViolation的地方。

也来手动逆向回溯下看能不能回溯到有路由处理的地方。

搜索ConstraintViolationFactory：

![](https://image.3001.net/images/20200415/1586916798_5e966dbe5fd84.png!small)

有好几个，这里使用第一个BowerGroupRepositoriesApiResource分析，点进去看就能看出它是一个API路由：

![](https://image.3001.net/images/20200415/1586916816_5e966dd0839be.png!small)

ConstraintViolationFactory被传递给了super，在BowerGroupRepositoriesApiResource并没有调用ConstraintViolationFactory的其他函数，不过它的两个方法，也是调用了super对应的方法。它的super是AbstractGroupRepositoriesApiResource类：

![](https://image.3001.net/images/20200415/1586916843_5e966debccee5.png!small)

BowerGroupRepositoriesApiResource构造函数中调用的super，在AbstractGroupRepositoriesApiResource赋值了ConstraintViolationFactory（标号1），ConstraintViolationFactory的使用（标号2），调用了createViolation（在后面可以看到memberNames参数），这也是之前要到达漏洞点所需要的，这个调用处于validateGroupMembers中（标号3），validateGroupMembers的调用在createRepository（标号4）和updateRepository（标号5）中都进行了调用，而这两个方法通过上面的注解也可以看出，通过外部传递请求能到达。

BowerGroupRepositoriesApiResource的路由为/beta/repositories/bower/group，在后台API找到它来进行调用（使用3.21.1测试）：

![](https://image.3001.net/images/20200415/1586916973_5e966e6d50630.png!small)

还有AbstractGroupRepositoriesApiResource的其他几个子类也是可以的：

![](https://image.3001.net/images/20200415/1586917054_5e966ebe1131f.png!small)

###  CleanupPolicyAssetNamePatternValidator未做清除点分析

对应上面搜索结果的CleanupPolicyAssetNamePatternValidator，可以看到这里并没有做StripEL清除操作：

![](https://image.3001.net/images/20200415/1586917084_5e966edcdca32.png!small)

这个变量是通过报错抛出放到buildConstraintViolationWithTemplate中的，要是报错信息中包含了value值，那么这里就是可以利用的。

搜索CleanupPolicyAssetNamePatternValidator：

![](https://image.3001.net/images/20200415/1586917100_5e966eec9c8a8.png!small)

在CleanupPolicyAssetNamePattern类注解中使用了，继续搜索CleanupPolicyAssetNamePattern：

![](https://image.3001.net/images/20200415/1586917111_5e966ef797f6f.png!small)

在CleanupPolicyCriteria中的属性regex被CleanupPolicyAssetNamePattern注解了，继续搜索CleanupPolicyCriteria：

![](https://image.3001.net/images/20200415/1586917122_5e966f029665b.png!small)

![](https://image.3001.net/images/20200415/1586917134_5e966f0e22d0f.png!small)

在CleanupPolicyComponent中的to
CleanupPolicy方法中有调用，其中的cleanupPolicyXO.getCriteria也正好是CleanupPolicyCriteria对象。toCleanupPolicy在CleanupPolicyComponent的可通过路由进入的create、previewCleanup方法又调用了toCleanupPolicy。

构造payload测试：

![](https://image.3001.net/images/20200415/1586917219_5e966f6354924.png!small)

然而这里并不能利用，value值不会被包含在报错信息中，去看了下RegexCriteriaValidator.validate，无论如何构造，最终也只会抛出value中的一个字符，所以这里并不能利用。  

与这个类似的是CronExpressionValidator，那里也是通过抛出异常，但是那里是可以利用的，不过被修复了，可能之前已经有人提交过了。还有其他几个没做清除的地方，要么被if、else跳过了，要么不能利用。

人工去回溯查找的方式，如果关键字被调用的地方不多可能还好，不过要是被大量使用，可能就不是那么好处理了。不过上面几个漏洞，可以看到通过手动回溯查找还是可行的。

##  JXEL造成的漏洞（CVE-2019-7238）

可以参考下@iswin大佬之前的分析<https://www.anquanke.com/post/id/171116>，这里就不再去调试截图了。这里想写下之前对这个漏洞的修复，说是加了权限来修复，要是只加了权限，那不是还能提交一下？不过，测试了下3.21.1版本，就算用admin权限也无法利用了，想去看下是不是能绕过。在3.14.0中测试，确实是可以的：

![](https://image.3001.net/images/20200415/1586917247_5e966f7f0c798.png!small)

但是3.21.1中，就算加了权限，也是不行的。后面分别调试对比了下，以及通过下面这个测试：

    
    
    JexlEngine jexl = new JexlBuilder().create();String jexlExp = "''.class.forName('java.lang.Runtime').getRuntime().exec('calc.exe')";JexlExpression e = jexl.createExpression(jexlExp);JexlContext jc = new MapContext();jc.set("foo", "aaa");e.evaluate(jc);

才知道3.14.0与上面这个测试使用的是org.apache.commons.jexl3.internal.introspection.Uberspect处理，它的getMethod方法如下：

![](https://image.3001.net/images/20200415/1586917254_5e966f86ab4b4.png!small)

而在3.21.1中Nexus设置的是org.apache.commons.jexl3.internal.introspection.SandboxJexlUberspect，这个SandboxJexlUberspect，它的get
Method方法如下：

![](https://image.3001.net/images/20200415/1586917270_5e966f96412b1.png!small)

![](https://image.3001.net/images/20200415/1586917278_5e966f9e5e69e.png!small)

可以看出只允许调用String、Map、Collection类型的有限几个方法了。

##  总结

看完上面的内容，相信对Nexus3的漏洞大体有了解了，不会再无从下手的感觉。尝试看下下其他地方，例如后台有个LDAP，可进行jndi
connect操作，不过那里调用的是context.getAttribute，虽然会远程请求class文件，不过并不会加载class，所以并没有危害。

有的漏洞的根源点可能会在一个应用中出现相似的地方，就像上面那个buildConstraintViolationWithTemplate这个keyword一样，运气好说不定一个简单的搜索都能碰到一些相似漏洞（不过我运气貌似差了点，通过上面的搜索可以看到某些地方的修复，说明已经有人先行一步了，直接调用了buildConstraintViolationWithTemplate并且可用的地方似乎已经没有了）

仔细看下上面几个漏洞的payload，好像相似度很高，所以可以弄个类似fuzz参数的工具，搜集这个应用的历史漏洞payload，每个参数都可以测试下对应的payload，运气好可能会撞到一些相似漏洞

>  **原文：<https://paper.seebug.org/1166/>** **  
> **

***本文作者：Longofo@知道创宇404实验室，转载请注明来自FreeBuf.COM**  


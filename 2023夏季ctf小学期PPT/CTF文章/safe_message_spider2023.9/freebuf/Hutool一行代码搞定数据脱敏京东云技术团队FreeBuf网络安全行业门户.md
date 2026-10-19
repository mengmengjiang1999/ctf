## 1\. 什么是数据脱敏

### 1.1 数据脱敏的定义

数据脱敏百度百科中是这样定义的：

数据脱敏，指对某些敏感信息通过脱敏规则进行数据的变形，实现敏感隐私数据的可靠保护。这样就可以在开发、测试和其它非生产环境以及外包环境中安全地使用脱敏后的真实数据集。在涉及客户安全数据或者一些商业性敏感数据的情况下，在不违反系统规则条件下，对真实数据进行改造并提供测试使用，如身份证号、手机号、卡号、客户号等个人信息都需要进行数据脱敏。是数据库安全技术之一。

总的来说，数据脱敏是指对某些敏感信息通过脱敏规则进行数据的变形，实现敏感隐私数据的可靠保护。

在数据脱敏过程中，通常会采用不同的算法和技术，以根据不同的需求和场景对数据进行处理。例如，对于身份证号码，可以使用掩码算法（masking）将前几位数字保留，其他位用“X”或"*"代替；对于姓名，可以使用伪造（pseudonymization）算法，将真实姓名替换成随机生成的假名。

### 1.2 常用脱敏规则

替换、重排、加密、截断、掩码

## 2\. Hutool工具介绍

### 2.1 引入Maven配置

在项目的pom.xml的dependencies中加入以下内容，这里以5.8.16版本为例。

    
    
    <dependency><groupId>cn.hutool</groupId><artifactId>hutool-all</artifactId><version>5.8.16</version></dependency>

 **注意** ：Hutool 5.x支持JDK8+， 如果你的项目使用JDK7，请使用Hutool
4.x版本。本文使用的数据脱敏工具类只有在5.6+版本以上才提供。

### 2.2 Hutool包含的组件

一个Java基础工具类，对文件、流、加密解密、转码、正则、线程、XML等JDK方法进行封装，组成各种Util工具类，同时提供以下组件：

模块| 介绍  
---|---  
hutool-aop| JDK动态代理封装，提供非IOC下的切面支持  
hutool-bloomFilter| 布隆过滤，提供一些Hash算法的布隆过滤  
hutool-cache| 简单缓存实现  
hutool-core| 核心，包括Bean操作、日期、各种Util等  
hutool-cron| 定时任务模块，提供类Crontab表达式的定时任务  
hutool-crypto| 加密解密模块，提供对称、非对称和摘要算法封装  
hutool-db| JDBC封装后的数据操作，基于ActiveRecord思想  
hutool-dfa| 基于DFA模型的多关键字查找  
hutool-extra| 扩展模块，对第三方封装（模板引擎、邮件、Servlet、二维码、Emoji、FTP、分词等）  
hutool-http| 基于HttpUrlConnection的Http客户端封装  
hutool-log| 自动识别日志实现的日志门面  
hutool-script| 脚本执行封装，例如Javascript  
hutool-setting| 功能更强大的Setting配置文件和Properties封装  
hutool-system| 系统参数调用封装（JVM信息等）  
hutool-json| JSON实现  
hutool-captcha| 图片验证码实现  
hutool-poi| 针对POI中Excel和Word的封装  
hutool-socket| 基于Java的NIO和AIO的Socket封装  
hutool-jwt| JSON Web Token (JWT)封装实现  
  
可以根据需求对每个模块单独引入，也可以通过引入`hutool-all`方式引入所有模块，本文所使用的数据脱敏工具就是在hutool.core模块。

### 2.3 Hutool支持的脱敏数据类型

现阶段最新版本的Hutool支持的脱敏数据类型如下，基本覆盖了常见的敏感信息。

1.用户id

2.中文姓名

3.身份证号

4.座机号

5.手机号

6.地址

7.电子邮件

8.密码

9.中国大陆车牌，包含普通车辆、新能源车辆

10.银行卡

## 3\. Hutool数据脱敏实操

### 3.1 使用Hutool工具类一行代码实现脱敏

Hutool提供的脱敏方法如下图所示：

![](https://image.3001.net/images/20230810/1691662213_64d4b7859cbb94c76b467.png!small)

  

 **注意** ：Hutool
脱敏是通过*来代替敏感信息的，具体实现是在StrUtil.hide方法中，如果我们想要自定义隐藏符号，则可以把Hutool的源码拷出来，重新实现即可。

这里以手机号、银行卡号、身份证号、密码信息的脱敏为例，下面是对应的测试代码。

    
    
    importcn.hutool.core.util.DesensitizedUtil;importorg.junit.Test;importorg.springframework.boot.test.context.SpringBootTest;/**
     * 
     * @description: Hutool实现数据脱敏
     */@SpringBootTestpublicclassHuToolDesensitizationTest{@TestpublicvoidtestPhoneDesensitization(){Stringphone="13723231234";System.out.println(DesensitizedUtil.mobilePhone(phone));//输出：137****1234}@TestpublicvoidtestBankCardDesensitization(){StringbankCard="6217000130008255666";System.out.println(DesensitizedUtil.bankCard(bankCard));//输出：6217 **** **** *** 5666}@TestpublicvoidtestIdCardNumDesensitization(){StringidCardNum="411021199901102321";//只显示前4位和后2位System.out.println(DesensitizedUtil.idCardNum(idCardNum,4,2));//输出：4110************21}@TestpublicvoidtestPasswordDesensitization(){Stringpassword="www.jd.com_35711";System.out.println(DesensitizedUtil.password(password));//输出：****************}}

以上就是使用Hutool封装好的工具类实现数据脱敏。

### 3.2 配合JackSon通过注解方式实现脱敏

现在有了数据脱敏工具类，如果前端需要显示数据数据的地方比较多，我们不可能在每个地方都调用一个工具类，这样就显得代码太冗余了，那我们如何通过注解的方式优雅的完成数据脱敏呢？

如果项目是基于springboot的web项目，则可以利用springboot自带的jackson自定义序列化实现。它的实现原来其实就是在json进行序列化渲染给前端时，进行脱敏。

 **第一步：** **脱敏策略的枚举。**

    
    
     /**
     * @author
     * @description:脱敏策略枚举
     */publicenumDesensitizationTypeEnum{//自定义MY_RULE,//用户idUSER_ID,//中文名CHINESE_NAME,//身份证号ID_CARD,//座机号FIXED_PHONE,//手机号MOBILE_PHONE,//地址ADDRESS,//电子邮件EMAIL,//密码PASSWORD,//中国大陆车牌，包含普通车辆、新能源车辆CAR_LICENSE,//银行卡BANK_CARD
    }

上面表示支持的脱敏类型。

 **第二步：** **定义一个用于脱敏的 Desensitization 注解。**

•@Retention(RetentionPolicy.RUNTIME)：运行时生效。

•@Target(ElementType.FIELD)：可用在字段上。

•@JacksonAnnotationsInside：此注解可以点进去看一下是一个元注解，主要是用户打包其他注解一起使用。

•@JsonSerialize：上面说到过，该注解的作用就是可自定义序列化，可以用在注解上，方法上，字段上，类上，运行时生效等等，根据提供的序列化类里面的重写方法实现自定义序列化。

    
    
    /**
     * @author 
     */@Target(ElementType.FIELD)@Retention(RetentionPolicy.RUNTIME)@JacksonAnnotationsInside@JsonSerialize(using =DesensitizationSerialize.class)public@interfaceDesensitization{/**
         * 脱敏数据类型，在MY_RULE的时候，startInclude和endExclude生效
         */DesensitizationTypeEnumtype()defaultDesensitizationTypeEnum.MY_RULE;/**
         * 脱敏开始位置（包含）
         */intstartInclude()default0;/**
         * 脱敏结束位置（不包含）
         */intendExclude()default0;}

注：只有使用了自定义的脱敏枚举MY_RULE的时候，开始位置和结束位置才生效。

 **第三步：创建自定的序列化类**

这一步是我们实现数据脱敏的关键。自定义序列化类继承 JsonSerializer，实现ContextualSerializer接口，并重写两个方法。

    
    
    /**
     * @author 
     * @description: 自定义序列化类
     */@AllArgsConstructor@NoArgsConstructorpublicclassDesensitizationSerializeextendsJsonSerializer<String>implementsContextualSerializer{privateDesensitizationTypeEnumtype;privateIntegerstartInclude;privateIntegerendExclude;@Overridepublicvoidserialize(Stringstr,JsonGeneratorjsonGenerator,SerializerProviderserializerProvider)throwsIOException{switch(type){// 自定义类型脱敏caseMY_RULE:jsonGenerator.writeString(CharSequenceUtil.hide(str,startInclude,endExclude));break;// userId脱敏caseUSER_ID:jsonGenerator.writeString(String.valueOf(DesensitizedUtil.userId()));break;// 中文姓名脱敏caseCHINESE_NAME:jsonGenerator.writeString(DesensitizedUtil.chineseName(String.valueOf(str)));break;// 身份证脱敏caseID_CARD:jsonGenerator.writeString(DesensitizedUtil.idCardNum(String.valueOf(str),1,2));break;// 固定电话脱敏caseFIXED_PHONE:jsonGenerator.writeString(DesensitizedUtil.fixedPhone(String.valueOf(str)));break;// 手机号脱敏caseMOBILE_PHONE:jsonGenerator.writeString(DesensitizedUtil.mobilePhone(String.valueOf(str)));break;// 地址脱敏caseADDRESS:jsonGenerator.writeString(DesensitizedUtil.address(String.valueOf(str),8));break;// 邮箱脱敏caseEMAIL:jsonGenerator.writeString(DesensitizedUtil.email(String.valueOf(str)));break;// 密码脱敏casePASSWORD:jsonGenerator.writeString(DesensitizedUtil.password(String.valueOf(str)));break;// 中国车牌脱敏caseCAR_LICENSE:jsonGenerator.writeString(DesensitizedUtil.carLicense(String.valueOf(str)));break;// 银行卡脱敏caseBANK_CARD:jsonGenerator.writeString(DesensitizedUtil.bankCard(String.valueOf(str)));break;default:}}@OverridepublicJsonSerializer<?>createContextual(SerializerProviderserializerProvider,BeanPropertybeanProperty)throwsJsonMappingException{if(beanProperty !=null){// 判断数据类型是否为String类型if(Objects.equals(beanProperty.getType().getRawClass(),String.class)){// 获取定义的注解Desensitizationdesensitization =beanProperty.getAnnotation(Desensitization.class);// 为nullif(desensitization ==null){desensitization =beanProperty.getContextAnnotation(Desensitization.class);}// 不为nullif(desensitization !=null){// 创建定义的序列化类的实例并且返回，入参为注解定义的type,开始位置，结束位置。returnnewDesensitizationSerialize(desensitization.type(),desensitization.startInclude(),desensitization.endExclude());}}returnserializerProvider.findValueSerializer(beanProperty.getType(),beanProperty);}returnserializerProvider.findNullValueSerializer(null);}}

经过上述三步，已经完成了通过注解实现数据脱敏了，下面我们来测试一下。

首先定义一个要测试的pojo，对应的字段加入要脱敏的策略。

    
    
    /**
     *
     * @description:
     */@Data@NoArgsConstructor@AllArgsConstructorpublicclassTestPojo{privateStringuserName;@Desensitization(type =DesensitizationTypeEnum.MOBILE_PHONE)privateStringphone;@Desensitization(type =DesensitizationTypeEnum.PASSWORD)privateStringpassword;@Desensitization(type =DesensitizationTypeEnum.MY_RULE,startInclude =0,endExclude =2)privateStringaddress;}

接下来写一个测试的controller

    
    
    @RestControllerpublicclassTestController{@RequestMapping("/test")publicTestPojotestDesensitization(){TestPojotestPojo =newTestPojo();testPojo.setUserName("我是用户名");testPojo.setAddress("地球中国-北京市通州区京东总部2号楼");testPojo.setPhone("13782946666");testPojo.setPassword("sunyangwei123123123.");System.out.println(testPojo);returntestPojo;}}

![](https://image.3001.net/images/20230810/1691662214_64d4b78610207c46bfa61.png!small)

  

可以看到我们成功实现了数据脱敏。

## 4\. 其他常见的数据脱敏工具推荐

除了本文介绍的Hutool工具之外，还有一些其他的数据脱敏工具，常见脱敏方法或工具如下所示：

### 4.1 Apache ShardingSphere

Apache
ShardingSphere下面存在一个数据脱敏模块，此模块集成的常用的数据脱敏的功能。其基本原理是对用户输入的SQL进行解析拦截，并依靠用户的脱敏配置进行SQL的改写，从而实现对原文字段的加密及加密字段的解密。最终实现对用户无感的加解密存储、查询。

具体实现方式可参考下面文章： [https://jaskey.github.io/blog/2020/03/18/sharding-sphere-data-desensitization/](https://jaskey.github.io/blog/2020/03/18/sharding-sphere-data-desensitization/)

### 4.2 FastJSON

平时开发Web项目的时候，除了默认的Spring自带的序列化工具，FastJson也是一个很常用的Spring web Restful接口序列化的工具。

FastJSON实现数据脱敏的方式主要有两种：

•基于注解@JSONField实现：需要自定义一个用于脱敏的序列化的类，然后在需要脱敏的字段上通过@JSONField中的serializeUsing
指定为我们自定义的序列化类型即可。

•基于序列化过滤器：需要实现ValueFilter接口，重写process方法完成自定义脱敏，然后在JSON转换时使用自定义的转换策略。

具体实现可参考这篇文章：
[https://juejin.cn/post/7067916686141161479](https://juejin.cn/post/7067916686141161479)

### 4.3 Mybatis-mate

mybatisplus也提供了数据脱敏模块，mybatis-mate，不过在使用之前需要配置授权码。

配置内容如下所示：

    
    
    # Mybatis Mate 配置
    mybatis-mate:
      cert:
        grant: jxftsdfggggx
        license: GKXP9r4MCJhGID/DTGigcBcLmZjb1YZGjE4GXaAoxbtGsPC20sxpEtiUr2F7Nb1ANTUekvF6Syo6DzraA4M4oacwoLVTglzfvaEfadfsd232485eLJK1QsskrSJmreMnEaNh9lsV7Lpbxy9JeGCeM0HPEbRvq8Y+8dUt5bQYLklsa3ZIBexir+4XykZY15uqn1pYIp4pEK0+aINTa57xjJNoWuBIqm7BdFIb4l1TAcPYMTsMXhF5hfMmKD2h391HxWTshJ6jbt4YqdKD167AgeoM+B+DE1jxlLjcpskY+kFs9piOS7RCcmKBBUOgX2BD/JxhR2gQ==

具体实现可参考baomidou提供的如下代码： [https://gitee.com/baomidou/mybatis-mate-examples](https://gitee.com/baomidou/mybatis-mate-examples)

## 5\. 总结

本文主要介绍了数据脱敏的相关内容，首先介绍了数据脱敏的概念，在此基础上介绍了常用的数据脱敏规则；随后介绍了本文的重点Hutool工具及其使用方法，在此基础上进行了实操，分别演示了使用DesensitizedUtil工具类、配合Jackson通过注解的方式完成数据脱敏；最后，介绍了一些常见的数据脱敏方法，并附上了对应的教程链接供大家参考，本文内容如有不当之处，还请大家批评指正。

  

## 6\. 参考内容

Hutool工具官网：
[https://hutool.cn/docs/#/?id=%f0%9f%93%9a%e7%ae%80%e4%bb%8b](https://hutool.cn/docs/#/?id=%F0%9F%93%9A%E7%AE%80%E4%BB%8B)

聊聊如何自定义数据脱敏：
[https://juejin.cn/post/7046567603971719204](https://juejin.cn/post/7046567603971719204)

FastJSON实现数据脱敏：
<https://juejin.cn/post/7067916686141161479>[](https://juejin.cn/post/7067916686141161479)

> 作者：京东科技 孙扬威
>
> 来源：京东云开发者社区


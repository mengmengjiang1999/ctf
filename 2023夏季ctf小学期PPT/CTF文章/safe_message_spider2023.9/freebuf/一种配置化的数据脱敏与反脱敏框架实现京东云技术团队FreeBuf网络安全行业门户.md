## 1.tony框架背景

  * 在业务量日益剧增的背景下，大量数据在各种业务活动中产生，数据安全控制一直是治理的重要环节，数据脱敏属于安全控制的范畴。对互联网公司来说，数据安全一直是极为重视和敏感的话题。数据脱敏是指对某些敏感信息通过脱敏规则进行数据的变形，实现敏感隐私数据的可靠保护。涉及客户安全数据或者一些商业性敏感数据，如身份证号、手机号、卡号、客户号等个人信息按照相关部门规定，都需要进行数据脱敏。

  * 在现有的微服务技术架构背景下，敏感数据的使用存在如下痛点：

    *  **敏感数据与PC、APP客户端使用明文数据交互，数据安全无法保证。**

    *  **敏感数据浏览缺乏监控，无法针对性的做数据治理。**

    *  **微服务架构系统应用多而杂，期望引入一套通用的方案统一解决敏感数据安全问题。**

基于以上痛点，tony提供了一套完整、安全、透明化、低改造成本的数据脱敏整合解决方案。

## 2.tony框架简介

Tony是一款敏感数据脱敏与浏览记录监控工具，可对系统中的敏感信息进行脱敏处理，并在泄漏时提供追溯依据，为企业数据共享、迁移、分发提供安全保护措施。该项目基于spring进行开发，提供spring-boot-starter启动包，接入简单，主要实现功能如下：

​ **灵活的脱敏方案**

业务系统的数据千变万化，为确保所有业务数据都能够正常进行敏感信息处理，数据脱敏提供高灵活性的自定义脱敏配置。通过丰富多样的脱敏规则定义，敏感数据处理可实现高度契合业务的脱敏处理。

​ **统一的明文数据管理**

框架内置敏感数据对应的明文数据管理流程，将明文数据统一缓存管理，提供统一的明文数据访问api。

​ **浏览记录留痕**

针对不同用户对敏感信息明文数据的浏览动作，接入方可以自定义日志格式模版记录输出到日志文件中，做到每条数据的浏览有迹可循。

​ **异常浏览量预警**

接入方通过自定义脱敏配置可以设置不同场景的敏感浏览明文数据量阈值，开启告警后，当用户访问明文数据次数到达阈值后，会触发预警流程，接入方可自定义预警逻辑。

### tony整体架构：

tony-core模块定义了基本的脱敏功能实现，整体流程采用spi机制预留了充分的扩展空间。以tony-core为底座，集成汽车现有技术栈提供了tony-transformers模块对基础的脱敏功能进行了扩展：异步的缓存事件分发，分布式明文数据缓存，对接集团安全部门的敏感日志留痕，异常浏览量的邮件预警。

![tony架构图.png](https://image.3001.net/images/20230725/1690282366_64bfa97e803d644fd81ca.png!small)

name| desc  
---|---  
MaskAnnotationProcessor| 业务场景代理，通过注解代理对应的脱敏场景方法。  
IMaskProcess| 数据脱敏处理器  
IMaskLogProcessor| 数据浏览日志处理器  
IMaskCacheProcessor| 明文数据缓存处理器  
IMaskLimitProcessor| 明文数据访问限额管理  
IMaskWarningProcessor| 异常浏览预警处理  
IMaskContent| 上下文信息处理器  
IUnMaskProcessor| 明文数据获取处理器  
DefaultUnMaskProcessorAdapter| 明文数据获取适配器，提供从缓存中获取明文数据功能。  
DefaultMaskCacheProcess| 明文数据缓存处理器，提供分布式缓存功能。  
DefaultMaskContent| 上下文信息处理器，提供ThreadLocal实现。  
DefaultMaskWarningProcessor| 异常浏览预警处理，提供邮件告警实现。  
PlaintextProcess| 明文属于获取接口约束，可自定义明文数据获取的扩展。  
MaskMonitorCacheHandle| 缓存时间消费，异步消费缓存事件，存储明文数据。  
  
### tony处理流程详解：

tony和业务代码部署在一起，接入应用通过脱敏场景与脱敏配置项的指定来实现对应业务场景的脱敏代理。业务代码只需配置场景注解即可兼容使用。此时敏感数据的脱敏工作由tony负责，tony会拦截业务场景的响应数据，对敏感信息进行脱敏处理。

![tony处理流程详解.png](https://image.3001.net/images/20230725/1690282367_64bfa97fa0f4df02dd631.png!small)

### tony脱敏配置详解：

脱敏配置主要分为四部分：脱敏上下文配置，脱敏场景配置，脱敏预警配置以及日志留痕模版，其详情如下图所示：

![tony脱敏配置简介.png](https://image.3001.net/images/20230725/1690282368_64bfa9804c27bf31207a0.png!small)

key| name| desc  
---|---|---  
tony.appName| 接入系统名称|  
  
tony.maskSourceName| 脱敏白名单| 控制统一场景的接口对不同调用方进行数据是否脱敏控制  
tony.mask.XXX| 脱敏场景| XXX为具体场景的key  
tony.mask.XXX.enable| 动态开关| 控制是否开启脱敏  
tony.mask.XXX.limits| 明文浏览限额| 限制明文浏览次数  
tony.mask.XXX.cacheKey| 数据缓存解析规则| 示例：STATEMENT_BILL_PAGE:${argItem.id}  
tony.types.YYY| 脱敏字段| YYY为具体字段的key  
tony.types.YYY.regex| 脱敏规则配置| 脱敏的正则表达式 示例：(\d{3})\d{4}(\d{4})  
tony.types.YYY.replacement| 脱敏规则配置| 脱敏的正则表达式 示例：$1****$2  
tony.types.YYY.logName| 日志字段名称|  
  
  
## 3\. 系统详细设计

## 3.1 详细设计

### 3.1.1 活动图

![未命名绘图-第 14 页
\(1\).png](https://image.3001.net/images/20230725/1690282369_64bfa981031fc82ff9ee6.png!small)

### 3.1.2 时序图

![未命名绘图-第 13 页
\(2\).png](https://image.3001.net/images/20230725/1690282369_64bfa981b327beb8ea3a5.png!small)

### 3.1.3 类图

![Tony框架.png](https://image.3001.net/images/20230725/1690282370_64bfa9829851f866b98b2.png!small)

包| 职责  
---|---  
 **com.jd.car.tony.annoation**|  注解层 负责声明要被代理的业务操作。  
 **com.jd.car.tony.limit**|  负责记录敏感数据的访问次数，并提供预警。  
 **com.jd.car.tony.mask**|  管理基础配置，并根据配置进行敏感数据遮盖脱敏。  
 **com.jd.car.tony.log**|  记录敏感数据的访问操作，输出统一格式的日志信息。  
 **com.jd.car.tony.unmask**|  提供敏感数据的明文信息查看功能。  
 **com.jd.car.tony.support**|  util包，负责全局功能的支持。  
  
## 4\. 接入使用

#### 4.1 引入坐标

    
    
    <dependency>
                    <groupId>com.jd.car</groupId>
                    <artifactId>tony-spring-boot-starter</artifactId>
                    <version>1.8-RELEASE</version>
                </dependency>
    

#### 4.2 yaml配置

    
    
    tony:
      appName: "appName"
      #鉴权信息key
      sessionName: ""
      systemName: "systemName"
      warningName: "XXX"
      #脱敏白名单
      maskSourceName: ""
      types:
        name:
          regex: "([\\u4e00-\\u9fa5a-z0-9]{1})[\\u4e00-\\u9fa5a-z0-9]+"
          replacement: "$1**"
          logName: "accountName"
      mask:
        order:
          enable: true
          limits: 100
          limitError: false
          cacheKey: "order:${argItem.id}"
          menuName: "场景名称"
          name: "order"
          #日志记录操作类型
          maskLogOp: ""
          maskLogAccountType: 3
          
       #预警邮箱设置
       mail:
        mailHost: 
        mailPort: 
        mailUser: 
        mailPwd: 
        mailFrom: 
        mailTo: 
        copyto: 
        sendFlag: 
        
     #异步事件缓存明文数据配置，分布式缓存
     jd:
      cache:
        jimdb:
          enable: false
          url: ''
      event:
        enable: true
        queue:
          # 自定义queue名字，例如monitorQueue
          maskMonitorQueue:
            retryCount: 3
            maxBakSize: 1000
            # monitorHandle 处理事件的beanName
            handlerBean: maskMonitorCacheHandle 
    

#### 4.3 日志文件配置

    
    
    <?xml version="1.0" encoding="UTF-8"?>
    <configuration scan="true" scanPeriod="60 seconds" debug="false">
    
        <contextName>demo</contextName>
        <!-- 日志最大的历史 单位：天 -->
        <property name="maxHistory" value="90"/>
    
        <property name="LOG_PATTERN"
                  value="%d{yyyy-MM-dd HH:mm:ss.SSS,GMT+8:00} -%5p ${PID:- } --- [%X{PFTID}][%t] %-40.40logger{39}[%L] : %m%n"/>
    
        <property name="LOG_CHARSET" value="UTF-8"/>
    
        <property name="LOG_DES_PATTERN" value="%msg%n" />
    
        <!-- 彩色日志依赖的渲染类 -->
        <conversionRule conversionWord="clr" converterClass="org.springframework.boot.logging.logback.ColorConverter"/>
        <conversionRule conversionWord="wex"
                        converterClass="org.springframework.boot.logging.logback.WhitespaceThrowableProxyConverter"/>
        <conversionRule conversionWord="wEx"
                        converterClass="org.springframework.boot.logging.logback.ExtendedWhitespaceThrowableProxyConverter"/>
    
        <property name="LOG_PATTERN"
                  value="%d{yyyy-MM-dd HH:mm:ss.SSS,GMT+8:00} -%5p ${PID:- } --- [%X{PFTID}][%t] %-40.40logger{39}[%L] : %m%n"/>
    
        <!-- 彩色日志格式 -->
        <property name="CONSOLE_LOG_PATTERN"
                  value="${CONSOLE_LOG_PATTERN:-%clr(%d{yyyy-MM-dd HH:mm:ss.SSS}){faint} %clr(${LOG_LEVEL_PATTERN:-%5p}) %clr(${PID:- }){magenta} %clr(---){faint} %clr([%X{PFTID}][%15.15t]){faint} %clr(%-40.40logger{39}[%L]){cyan} %clr(:){faint} %m%n}"/>
    
    
        <appender name="mask" class="ch.qos.logback.core.rolling.RollingFileAppender">
            <file>${log.path}/today_log/mask.log</file>
            <filter class="ch.qos.logback.classic.filter.ThresholdFilter">
                <level>INFO</level>
            </filter>
            <rollingPolicy class="ch.qos.logback.core.rolling.TimeBasedRollingPolicy">
                <fileNamePattern>${log.path}/history_logs/mask-%d{yyyy-MM-dd}.log</fileNamePattern>
                <maxHistory>30</maxHistory>
            </rollingPolicy>
            <encoder>
                <charset>${LOG_CHARSET}</charset>
                <pattern>${LOG_DES_PATTERN}</pattern>
            </encoder>
        </appender>
        <logger name="com.jd.car.tony.log.DefaultMaskLogProcessor" additivity="false">
            <level value="INFO" />
            <appender-ref ref="mask" />
        </logger>
    
    </configuration>
    

#### 4.3 场景接入

    
    
    /**
         * 测试脱敏
         *
         * @return
         */
        @RequestMapping("test")
        @MaskMethod("order")
        public DemoResult test(AuthInfoBO authInfo) {
            return new DemoResult();
        }
    
        /**
         * 测试脱敏
         *
         * @return
         */
        @RequestMapping("test-list")
        @MaskMethod("order")
        public List<DemoResult> testList(AuthInfoBO authInfo) {
            List<DemoResult> objects = Lists.newArrayList();
            objects.add(new DemoResult());
            objects.add(new DemoResult());
            return objects;
        }
    
     		@Autowired
        private IUnMaskProcessor unMaskProcessorProxy;
    
        /**
         * 测试反脱敏
         *
         * @return
         */
        @RequestMapping("unmask")
        public Map testUnMask(@RequestBody UnMaskRequest unMaskRequest, AuthInfoBO authInfo) {
            return unMaskProcessorProxy.unMask(unMaskRequest, authInfo);
        }
    

#### 4.3 脱敏字段配置

    
    
    @Data
    public class DemoResult {
    
        @Mask(type = "name")
        private String userName = "jajajaasjcij";
    
        @Mask(type = "phone")
        private String userTel = "18911112222";
    
        private Long orderId = 1L;
    
    }
    

#### 4.4 业务监控

业务监控点| 触发逻辑  
---|---  
敏感数据明文查看| 单账号、单日、单接口访问次数到达访问限额时，则发送邮件给权限管理人员。  
敏感数据查询日志| 敏感数据脱敏后、明文数据查看时，按集团要求格式单独记录到日志文件中。  
  
  

> 作者：京东零售 邱新达
>
> 来源：京东云开发者社区


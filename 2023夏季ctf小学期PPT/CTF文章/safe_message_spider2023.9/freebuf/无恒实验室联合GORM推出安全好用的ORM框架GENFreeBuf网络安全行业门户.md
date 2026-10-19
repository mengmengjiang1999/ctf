## 背景

数据库操作是大多数程序员必不可少的工作， GORM 作为一个拥有 25k star 的项目已经是 Go 语言操作关系型数据库的首选。

  * 由于 GORM 中提供了很多 interface{} 形式的参数，这让程序员很容易误用，导致线上项目存在 SQL 注入的风险。
  * 在操作数据库时候，因为没有对应的结构体可以绑定，最后只能默默的拼接出一条 SQL 去执行。
  * 复杂的数据库表查询场景时，开发者需逐条手写数据表中的列与对应结构体的成员变量，逐条核对字段类型。遇到字段类型新增和变更，更改地方一大堆。

你和你的团队是否也为此事苦恼过？

## 什么是 GEN

GEN 是一个基于 GORM 的安全 ORM 框架，其主要通过代码生成方式实现 GORM 代码封装。旨在安全上避免业务代码出现 SQL
注入，同时给研发带来最佳用户体验。

### GEN 来告诉你，什么叫最佳用户体验：

  * 自动同步库表，省去繁琐复制
  * 代码一键生成，专注业务逻辑
  * 字段类型安全，执行 SQL 也安全
  * 查询优雅返回，完美兼容 GORM

GEN 提供了自动同步数据表结构体到 GORM 模型，使用非常简单，即使数据库字段信息改变，可以一键同步，数据库查询相关代码可以一键生成，CRUD
只需要调用对应的方法，开发体验飞起。GEN 采用了类型安全限制，所有参数都做了安全限制，完全不用担心存在注入；最重要的是自定义 SQL 只需要通过模板注释到
interface 的方法上，自动帮助你生成安全的代码，是的， **自定义 SQL 也不会出现 SQL 注入问题** ，而且工具完美兼容 GORM！

### 让我们看下直接使用 GORM 与 GEN 工具的对比

直接使用 GORM| 使用 GEN  
---|---  
需手动创建与数据表各列一一对应的结构体| 指定表名后自动读取并生成对应结构体  
需手动实现具体的 go 代码查询逻辑| 描述 SQL 查询逻辑即可，工具自动转换成安全稳定的代码  
查询接口十分灵活，但不能保持查询的 SQL 不发生语法错误，只能通过测试保证部分场景的正常运行| 查询接口使用类型安全，编译可通过，查询逻辑即是正常合理的  
需人工评经验保证业务不存在安全问题，一旦出错往往在上线前才能发现，影响上线流程| 提供的安全可靠的查询 API，开发时能用的就是安全的  
  
GORM 和 GEN 查询对比案例

    
    
    //GORM 需要先定义类型  
    var user model.User  
    err:=db.Where("id=?",5).Take(&user).Error  
      
    //GEN 可以直接查询，返回对应类型  
    user,err:= u.Where(u.ID.Eq(5)).Take()

## 如何使用 GEN

### 1\. 下载

    
    
    go get gorm.io/gen

### 2\. 生成

更详细的配置示例可以参照：最佳实践 DEMO(https://github.com/idersec/gendemo)

执行以下方法后即可在指定目录生成对应代码：

    
    
    import (  
    "gorm.io/gen"  
    )  
      
    func main() {  
    // 指定生成代码的具体(相对)目录，默认为：./query  
    // 默认情况下需要使用WithContext之后才可以查询，但可以通过设置gen.WithoutContext避免这个操作  
    g := gen.NewGenerator(gen.Config{  
    // 最终package不能设置为model，在有数据库表同步的情况下会产生冲突，若一定要使用可以单独指定model package的新名字  
    OutPath: "../dal/query",  
    ModelPkgPath: "../dal/model", // 默认情况下会跟随OutPath参数，在同目录下生成model目录  
    /* Mode: gen.WithoutContext,*/  
    })  
      
    // 复用工程原本使用的SQL连接配置db(*gorm.DB)  
    // 非必需，但如果需要复用连接时的gorm.Config或需要连接数据库同步表信息则必须设置  
    g.UseDB(db)  
      
    peopleTbl := g.GenerateModelAs("people", "People") // 指定对应表格的结构体名称  
    // 为指定的结构体或表格生成基础CRUD查询方法，ApplyInterface生成效果的子集  
    g.ApplyBasic(  
    model.User{},  
    peopleTbl,  
    )  
      
    // 为指定的数据库表实现除基础方法外的相关方法, 同时也会生成ApplyBasic对应的基础方法  
    // 可以认为ApplyInterface方法是ApplyBasic的扩展版  
    g.ApplyInterface(func(model.SearchByTenantMethod,model.UpdateByTenantMethod) {}, // 指定方法interface，可指定多个  
    model.Order{},  
    g.GenerateModel("Company"), // 在这里调用也会生成ApplyBasic对应的基础方法  
    )  
      
    // 执行并生成代码  
    g.Execute()  
    }

### 3\. 基础查询

执行生成代码后，GEN
会帮助生成基础的查询方法，并且绑定到结构体上，可以直接调用函数查询获取查询结果，不需要提前定义变量，参数和结构体字段类型绑定，防止研发过程中误用。

    
    
    u := query.Use(db).User  
    u.WithContext(ctx).Select(u.Name, u.Age).Create(&user)  
    // INSERT INTO `users` (`name`,`age`) VALUES ("modi", 18)  
      
    user, err := u.WithContext(ctx).Where(u.Name.Eq("iDer"),u.Age.Gte(18)).First()  
    // SELECT * FROM users WHERE name = "iDer" and age>=18;  
      
    _, err := u.WithContext(ctx).Where(u.ID.Eq(12)).Update(u.Name, "jinzhu")  
    // UPDATE users SET name="jinzhu", updated_at='2013-11-17 21:34:10' WHERE id=12;  
      
    e.WithContext(ctx).Where(u.ID.Eq(10)).Delete()  
    // DELETE from users where id = 10;  
      
    orders, err := o.WithContext(ctx).Where(u.Columns(o.Amount).Gt(o.Select(u.Amount.Avg())).Find()  
    // SELECT * FROM "orders" WHERE amount > (SELECT AVG(amount) FROM "orders");

GEN 满足了基本上所有的日常使用的查询方法，包括事务、关联关系等高级用法，更多案例请参考：https://github.com/go-gorm/gen#readme

### 4\. 自定义 SQL 查询

自定 SQL 的安全性是所有 ORM 最难解决的问题，GEN 使用模板注释的方法完美解决了这个问题，只需要将 SQL 注释到 interface
的方法上。SQL 支持简单的 where 查询和完整 SQL 查询，条件用`Where()`语法包住。Raw SQL 用`sql()`包住，也可省略直接写。

 **占位符**

  * `gen.T`用于返回数据的结构体，会根据生成结构体或者数据库表结构自动生成
  * `gen.M`表示`map[string]interface{}`,用于返回数据
  * `gen.RowsAffected`用于执行 SQL 进行更新或删除时候,用于返回影响行数
  * `@@table`查询的表名，如果没有传参，会根据结构体或者表名自动生成
  * `@@<name>`当表名或者字段名可控时候，用@@占位，name 为可变参数名，需要函数传入。
  * `@<name>`当数据可控时候，用@占位，name 为可变参数名，需要函数传入

 **子句**

目前支持 if 、where 、set 子句，子句需要用{{}}括起来，并且需要用`{{end}}`结束子句。where 和 set
子句会帮助做连接词补全和开头连接词删除。各个子句支持嵌套使用。

    
    
    type Method interface {  
    // Where("name=@name and age=@age")  
    SimpleFindByNameAndAge(name string, age int) (gen.T, error)  
      
    // select * from users where id=@id  
    FindUserToMap(id int) (gen.M, error)  
      
    // sql(insert into @@table (name,age) values (@name,@age) )  
    InsertValue(age int, name string) error  
      
    // select name from @@table where id=@id  
    FindNameById(id int) string  
      
    // select * from @@table  
    //  {{where}}  
    //      id>0  
    //      {{if cond}}id=@id {{end}}  
    //      {{if key!="" && value != ""}} or @@key=@value{{end}}  
    //  {{end}}  
    FindByIDOrCustom(cond bool, id int, key, value string) ([]gen.T, error)  
      
    // update @@table  
    //  {{set}}  
    //      update_time=now()  
    //      {{if name != ""}}  
    //          name=@name  
    //      {{end}}  
    //  {{end}}  
    //  {{where}}  
    //      id=@id  
    //  {{end}}  
    UpdateName(name string, id int) (gen.RowsAffected,error)  
    }

GEN 会自动生成安全的实现代码，并且和结构体绑定，使用时候直接调用对应的函数即可。

    
    
    user,err := u.SimpleFindByNameAndAge("zhangqiang",18)  
      
    resultMap,err:= u.FindUserToMap(2)  
      
    name := u.FindNameById(5)  
      
    users,err := u.FindByIDOrCustom(true, 10, "name", "modi")  
      
    rows,err := UpdateName("jinzhu", 12)

### 5\. 最佳实践目录推荐

    
    
    demo  
    ├── cmd  
    │   └── generate  
    │       └── generate.go # 包含main函数，执行其即可完成生成代码步骤  
    ├── dal  
    │   ├── dal.go # 实现具体的数据库连接等操作  
    │   └── model  
    │   │   ├── method.go # 指定所有自定义查询方法  
    │   │   └── model.go  # 描述与数据库表对应的数据结构(体)  
    │   └── query  # 生成的代码存放目录, 在执行代码生成操作后自动创建  
    │       └── gen.go # 生成的通用查询代码  
    │       └── tablename.gen.go # 生成的单个表字段和相关的查询代码  
    ├── biz  
    │   └── query.go # 实现业务逻辑，调用生成的代码查询数据库  
    ├── config  
    │   └── config.go # 存储相关的数据库DSN  
    ├── generate.sh # 调用generate中main函数生成代码的脚本（推荐使用）  
    ├── go.mod  
    ├── go.sum  
    └── main.go

 **GEN 项目地址**

  * https://github.com/go-gorm/gen

## 写在最后

  * GEN 是一个从开始研发就立足安全角度的项目，在项目过程中充分考虑业务使用的需求，特别是很多 GORM 的功能，GORM 项目已经维护发展了 8 年，集成了很多业务使用的需求。GEN 对 GORM 完全兼容，将 GORM 的所有功能实现到 GEN 工具中。在安全上，采用了类型安全限制和充分的安全检查，完全避免了出现 SQL 注入问题，在用户体验上，增加了自动同步表结构体功能和一键所有查询相关代码生成功能，开发体验拉满，快来在你的项目上试试吧 。

  * 无恒实验室(https://security.bytedance.com/security-lab)致力于为字节跳动旗下产品与业务保驾护航，亦极为重视开源软件与系统对业务安全的影响，在检测公司引入的开源框架和系统的同时，无恒实验室也着力于构建第三方框架和组件的漏洞缓解机制，并将持续与业界共享研究成果，协助企业业务避免遭受安全风险，亦望能与业内同行共同合作，为网络安全行业的发展做出贡献。


**直接审计tp的话应该会很有难度，不妨先了解一些tp内置规则和用法，便于在后续的审计中更好的理解代码含义。**

[ **源码下载链接**](https://www.sec-in.com/outLinkPage/?target=https://github.com/heyguojing/thinkphp5.1)

[ThinkPHP5.1 开发手册 ](https://www.sec-in.com/outLinkPage/?target=https://www.kancloud.cn/manual/thinkphp5_1/353951)

# **安装**

 **没有composer可以去下载，傻瓜式安装即可**[ **Composer (getcomposer.org)**](https://www.sec-in.com/outLinkPage/?target=https://getcomposer.org/download/)

 **使用composer安装**

    
    
    composer create-project topthink/think tp
    

**启动服务**

    
    
    cd tp
    php think run
    

**然后就可以在浏览器中访问**

    
    
    http://localhost:8000
    

**搭建成功**

![wKg0C2JeviAUGrMAABfbxtCDSc342.png](https://image.3001.net/images/20221008/1665220893_6341411d74fde8e6bee02.png!small)

#  **目录结构**

    
    
    www  WEB部署目录（或者子目录）
    application           应用目录
      common             公共模块目录（可以更改）
      module_name        模块目录
        common.php      模块函数文件
        controller      控制器目录
        model           模型目录
        view            视图目录
         ...            更多类库目录
      
      command.php        命令行定义文件
      common.php         公共函数文件
      tags.php           应用行为扩展定义文件
    
    config                应用配置目录
      module_name        模块配置目录
        database.php    数据库配置
        cache           缓存配置
         ...            
      
      app.php            应用配置
      cache.php          缓存配置
      cookie.php         Cookie配置
      database.php       数据库配置
      log.php            日志配置
      session.php        Session配置
      trace.php          Trace配置
    
    route                 路由定义目录
      route.php          路由定义
      ...                更多
    
    public                WEB目录（对外访问目录）
      index.php          入口文件
      router.php         快速测试文件
      .htaccess          用于apache的重写
    
    thinkphp              框架系统目录
      lang               语言文件目录
      library            框架类库目录
        think           Think类库包目录
        traits          系统Trait目录
      
      tpl                系统模板目录
      base.php           基础定义文件
      console.php        控制台入口文件
      convention.php     框架惯例配置文件
      helper.php         助手函数文件
      phpunit.xml        phpunit配置文件
      start.php          框架入口文件
    
    extend                扩展类库目录
    runtime               应用的运行时目录（可写，可定制）
    vendor                第三方类库目录（Composer依赖库）
    build.php             自动生成定义文件（参考）
    composer.json         composer 定义文件
    LICENSE.txt           授权说明文件
    README.md             README 文件
    think                 命令行入口文件
    

# **命名规范**

`ThinkPHP5` **遵循PSR-2命名规范和PSR-4自动加载规范，并且注意如下规范：**

##  **目录和文件**

目录不强制规范，驼峰和小写+下划线模式均支持；

类库、函数文件统一以.php为后缀；

类的文件名均以命名空间定义，并且命名空间的路径和类库文件所在路径一致；

类名和类文件名保持一致，统一采用驼峰法命名（首字母大写）；

##  **函数和类、属性命名**

  *  **类的命名采用驼峰法，并且首字母大写，例如`User`、**`UserType` **，默认不需要添加后缀，例如**`UserController` **应该直接命名为**`User` **；**
  *  **函数的命名使用小写字母和下划线（小写字母开头）的方式，例如`get_client_ip`；**
  *  **方法的命名使用驼峰法，并且首字母小写，例如`getUserName`；**
  *  **属性的命名使用驼峰法，并且首字母小写，例如`tableName`、**`instance` **；**
  *  **以双下划线“__”打头的函数或方法作为魔法方法，例如`__call`和`__autoload`；**

##  **常量和配置**

  * 常量以大写字母和下划线命名，例如`APP_PATH` **和`THINK_PATH`；**
  *  **配置参数以小写字母和下划线命名，例如`url_route_on`和**`url_convert` **；**

##  **数据表和字段**

  * 数据表和字段采用小写加下划线方式命名，并注意字段名不要以下划线开头，例如 **`think_user`** 表和`user_name` **字段，不建议使用驼峰和中文作为数据表字段命名。**

#  **URL解析模式**

    
    
    http://localhost/index.php/模块/控制器/操作/参数/值
    

**如果使用的是伪静态，就不必加上**`/thinkphp/tp5/public/index.php/` **了**

    
    
    http://127.0.0.1:8000/index/index/hello/name/Sentiment
    

![wKg0C2JewqALi9iAACDi9FfNU102.png](https://image.3001.net/images/20221008/1665220894_6341411e125a93cf26388.png!small)

![wKg0C2JexGAAnY3AAAvtBHmZ54837.png](https://image.3001.net/images/20221008/1665220895_6341411f136f11b997d15.png!small)

**在url地址栏里面如果不写模块、控制器和操作名，默认访问的就是index模块下面的index控制器下面的index操作，可以在config/app.php文件中进行修改。**

![wKg0C2JexiAVZQtAACP9fAkPrg521.png](https://image.3001.net/images/20221008/1665220911_6341412f1e7c55b518971.png!small)

##  **控制器定义**

 **控制器，即 controller，控制器文件存放在 controller 目录下**

 **类名和文件名大小写保持一致，采用驼峰法（）**

 **如果类名是 双字母组合，比如 class HelloWorld，url 访问时必须用：hello_world;**

 **想要原样方式访问 URL，则需要关闭配置文件中的自动转换**

`‘url_convert’ => false;`

 **在Test模块下，定义一个HelloWorld控制器，test操作**

    
    
    <?php
    namespace app\test\controller;
    
    class HelloWorld{
        public function test(){
            return 'hello_world!!!!!';
        }
    }
    

**访问HelloWorld控制器时，就必须以hello_world形式才行**

![wKg0C2JeyOAZagrAAAe3OgNmR4383.png](https://image.3001.net/images/20221008/1665220911_6341412f8d95c841f346c.png!small)

##  **渲染输出**

 **使用 view 输出模板**

###  **方法同名文件**

**tp中内置了一个view()方法，它可以找到同模块下的view/控制器同名文件夹(这里就是test)/与方法同名的文件.html(定义的是show方法，所以会自动追踪到show.html)**

![wKg0C2Jey2ADFtwAABzgrHNlTA929.png](https://image.3001.net/images/20221008/1665220912_6341413009271aba01813.png!small)

![wKg0C2JezSAAwsfAABrJGinL04751.png](https://image.3001.net/images/20221008/1665220912_6341413080455b10be5c8.png!small)

 **根据url解析模式，直接访问test模块，test控制器，show操作**

![wKg0C2Jez2AJ2rKAAAnU3sK1dw363.png](https://image.3001.net/images/20221008/1665220912_63414130ec2e8bc2659a3.png!small)

###  **不同名文件**

 **若不是方法同名.html,在view()中加上对应的html文件名即可(`view/同名控制器/参数同名.html)**

![wKg0C2Je0iAc3VuAAB6WBLnJhU282.png](https://image.3001.net/images/20221008/1665220913_6341413162d39b8cf05cd.png!small)

![wKg0C2Je06AQe3NAAAyQxzG6g619.png](https://image.3001.net/images/20221008/1665220913_63414131d36219e51a25b.png!small)

#  **数据库操作**

 **数据库配置在config/database.php下，数据库操作分为两种类型：DB类，模型类**

 **这里先设置下数据库名，用户名，密码，表前缀可选我这里填的think_**

![wKg0C2Je1iAZvZ4AACOPnhorE450.png](https://image.3001.net/images/20221008/1665220914_6341413245d58225c05a3.png!small)

 **下一步就是创建数据库了，在think数据库的think_data表下创建三个字段**

![wKg0C2Je2SAC2WSAACMB3i1xyg450.png](https://image.3001.net/images/20221008/1665220915_63414133504f198a9c9d1.png!small)

##  **DB类**

###  **原生查询**

 **支持**`query` **（查询操作）和**`execute` **（写入操作）方法**

####  **添加数据**

    
    
    <?php
    
    namespace app\test\controller;
    use think\Db;
    
    class Data{
        public function index(){
            $resault = Db::execute('insert into think_data (id,name,status) values(1,"Sentiment",1)');
            return dump($resault);
        }
    }
    

**访问方法**

![wKg0C2Je3WAVQRAABEyL5iTMY585.png](https://image.3001.net/images/20221008/1665220915_63414133c31c028a747b2.png!small)

 **执行成功**

![wKg0C2Je36AOe98AACTyevia9w926.png](https://image.3001.net/images/20221008/1665220916_634141343d925ae7f125d.png!small)

 **再插入一条**

    
    
    $resault = Db::execute('insert into think_data (id,name,status) values(1,"Tana",1)');
    
    

![wKg0C2Je5GABnUvAAAT6iTV2l8336.png](https://image.3001.net/images/20221008/1665220916_63414134b2a311aec8787.png!small)

#### **更新数据**

    
    
    <?php
    
    namespace app\test\controller;
    use think\Db;
    
    class Data{
        public function index(){
            $resault = Db::execute('update think_data set id=2 where name="Sentiment"');
            return dump($resault);
        }
    }
    

![wKg0C2Je7OARwvRAAAUA3fmvtQ771.png](https://image.3001.net/images/20221008/1665220917_63414135236b07a1ca762.png!small)

#### **删除数据**

    
    
    <?php
    
    namespace app\test\controller;
    use think\Db;
    
    class Data{
        public function index(){
            $resault = Db::execute('delete from think_data where name ="Tana"');
            return dump($resault);
        }
    }
    

![wKg0C2Je6uAcMfnAAAPkbyUnvI188.png](https://image.3001.net/images/20221008/1665220917_63414135899b9a34222da.png!small)

#### **查询数据**

 **query用于查询，默认情况下返回数组集，execute方法的返回值是影响的行数**

    
    
    <?php
    
    namespace app\test\controller;
    use think\Db;
    
    class Data{
        public function index(){
            $resault = Db::query('select * from think_data');
            return dump($resault);
        }
    }
    

![wKg0C2Je7ActcAABoZ91v3I794.png](https://image.3001.net/images/20221008/1665220918_6341413600648aca9c354.png!small)

### **查询构造器**

####  **添加数据**

**通过insert语句添加数据，如果设置了表前缀(prefix)则可以使用name(表后缀)，若没设置则需全名即：table(think_data)，也可应inserAll插入多条数据**

    
    
    <?php
    
    namespace app\test\controller;
    use think\Db;
    
    class Data{
        public function index(){
            $data=['id' => 1, 'name' => 'Sentiment','status'=>1];
            $resault = Db::name('data')->insert($data);
            return dump($resault);
        }
    }
    

#### **更新数据**

 **可以用update语句，也可以是tp封装的setField，同时若需要字段自增/自减也可以用setInc/setDec**

    
    
    <?php
    
    namespace app\test\controller;
    use think\Db;
    
    class Data{
        public function index(){
            $resault = Db::name('data')->where('name', "Sentiment")->update(['id' => '2']);
            //tp5封装函数
            $resault = Db::name('data')->where('name', "Sentiment")->setField('id',2);
            //不给第二个参数，默认为1
            $resault = Db::name('data')->where('name', "Sentiment")->setInc('id');
            //自减2
            $resault = Db::name('data')->where('name', "Sentiment")->setDec('id',2);
            return dump($resault);
        }
    }
    

#### **删除数据**

    
    
    <?php
    
    namespace app\test\controller;
    use think\Db;
    
    class Data{
        public function index(){
            $resault = Db::name('data')->where('name', "Tana")->delete();
            return dump($resault);
        }
    }
    

#### **查询数据**

    
    
    <?php
    
    namespace app\test\controller;
    use think\Db;
    
    class Data{
        public function index(){
            $resault = Db::name('data')->select();
            return dump($resault);
        }
    }
    

### **助手函数**

 **用`$db=\db('data');`代替`Db::name('data')`,db 助手函数默认会每次重新连接数据库，因此应当尽量避免多次调用。**

    
    
    <?php
    
    namespace app\test\controller;
    use think\Db;
    
    class Data{
        public function index(){
            $db=\db('data');
            $resault=$db->select();
            return dump($resault);
        }
    }
    

### **链式操作**

 **数据库提供的链式操作方法，可以有效的提高数据存取的代码清晰度和开发效率，并且支持所有的CURD操作（原生查询不支持链式操作）。**

 **链式操作不分先后，只要在查询方法(select()、find())前调用就行**

    
    
    Db::name('data') -> where('status',1) -> order('create_time') -> limit(10) -> select();
    

#### **链式操作查询方法**

 **连贯操作**|  **作用**|  **支持的参数类型**  
---|---|---  
 **where** *|  **用于AND查询**|  **字符串、数组和对象**  
 **whereOr** *|  **用于OR查询**|  **字符串、数组和对象**  
 **wheretime** *|  **用于时间日期的快捷查询**|  **字符串**  
 **table**|  **用于定义要操作的数据表名称**|  **字符串和数组**  
 **alias**|  **用于给当前数据表定义别名**|  **字符串**  
 **field** *|  **用于定义要查询的字段（支持字段排除）**|  **字符串和数组**  
 **order** *|  **用于对结果排序**|  **字符串和数组**  
 **limit**|  **用于限制查询结果数量**|  **字符串和数字**  
 **page**|  **用于查询分页（内部会转换成limit）**|  **字符串和数字**  
 **group**|  **用于对查询的group支持**|  **字符串**  
 **having**|  **用于对查询的having支持**|  **字符串**  
 **join** *|  **用于对查询的join支持**|  **字符串和数组**  
 **union** *|  **用于对查询的union支持**|  **字符串、数组和对象**  
 **view** *|  **用于视图查询**|  **字符串、数组**  
 **distinct**|  **用于查询的distinct支持**|  **布尔值**  
 **lock**|  **用于数据库的锁机制**|  **布尔值**  
 **cache**|  **用于查询缓存**|  **支持多个参数**  
 **relation** *|  **用于关联查询**|  **字符串**  
 **with** *|  **用于关联预载入**|  **字符串、数组**  
 **bind** *|  **用于数据绑定操作**|  **数组或多个参数**  
 **comment**|  **用于SQL注释**|  **字符串**  
 **force**|  **用于数据集的强制索引**|  **字符串**  
 **master**|  **用于设置主服务器读取数据**|  **布尔值**  
 **strict**|  **用于设置是否严格检测字段名是否存在**|  **布尔值**  
 **sequence**|  **用于设置Pgsql的自增序列名**|  **字符串**  
 **failException**|  **用于设置没有查询到数据是否抛出异常**|  **布尔值**  
 **partition**|  **用于设置分表信息**|  **数组 字符串**  
  
###  **查询表达式**

 **select()用于查询数据集，查询成功则返回一个二维数组，如果没有满足条件则返回空数组**

 **find()用于查找满足条件的第一个记录，如果查询成功，返回一个以为数组，如果失败则返回null**

 **表达式**|  **含义**|  **快捷查询方法**  
---|---|---  
 **=**|  **等于**|  
  
 **< >**|  **不等于**|  
  
 **>**|  **大于**|  
  
 **> =**|  **大于等于**|  
  
 **<**|  **小于**|  
  
 **< =**|  **小于等于**|  
  
 **[NOT] LIKE**|  **模糊查询**| `whereLike/whereNotLike`  
 **[NOT] BETWEEN**|  **（不在）区间查询**| `whereBetween/whereNotBetween`  
 **[NOT] IN**|  **（不在）IN 查询**| `whereIn/whereNotIn`  
 **[NOT] NULL**|  **查询字段是否（不）是NULL**| `whereNull/whereNotNull`  
 **[NOT] EXISTS**|  **EXISTS查询**| `whereExists/whereNotExists`  
 **[NOT] REGEXP**|  **正则（不）匹配查询（仅支持Mysql）**|  
  
 **[NOT] BETWEEM TIME**|  **时间区间比较**|  **whereBetweenTime**  
 **> TIME**|  **大于某个时间**| `whereTime`  
 **< TIME**|  **小于某个时间**| `whereTime`  
 **> = TIME**|  **大于等于某个时间**| `whereTime`  
 **< = TIME**|  **小于等于某个时间**| `whereTime`  
 **EXP**|  **表达式查询，支持SQL语法**| `whereExp`  
  
####  **比较查询**

 **查询id不等于1的数据**

    
    
    <?php
    
    namespace app\test\controller;
    use think\Db;
    
    class Data{
        public function index(){
            $result = Db::name('data')->where("id",'<>','1')->select();
            return dump($result);
        }
    }
    

#### **区间查询**

    
    
    <?php
    
    namespace app\test\controller;
    use think\Db;
    
    class Data{
        public function index(){
            //模糊查询name中带n的数据
            //$result = Db::name('data')->where("name",'like','%n%')->select();
            //区间查询id为1-3的数据
            $result = Db::name('data')->where("id",'BETWEEN','[1,3]')->select();
            return dump($result);
        }
    }
    

#### **时间查询**

 **查询2022-5-11以后的数据**

    
    
    $result = Db::name('data')->where("create_time",'> TIME','2022-5-11')->select();
    

#### **其它查询**

 **查询id=1或3的数据**

    
    
    $result = Db::name('data')->where("id",'EXP','IN (1,3)')->select();
    或
    $result = Db::name('data')->whereExp("id",'IN (1,3)')->select();
    

## **模型类**

**在模型中除了可以调用数据库类的方法之外（换句话说，数据库的所有查询方法模型中都可以支持），可以定义自己的方法，所以也可以把模型看成是数据库的增强版。**

###  **模型定义**

 **先建个think_user表**

![wKg0C2Je9CAECEAAC2gjHGPw176.png](https://image.3001.net/images/20221008/1665220918_6341413670558a6df2caa.png!small)

 **在test/model下建个think_user模型User,这里的模型名=表名，所以必须叫User**

![wKg0C2Je9qAL4UHAAB3lBYdWPo227.png](https://image.3001.net/images/20221008/1665220919_63414137072221a7b8091.png!small)

###  **新增数据**

 **建好模型就开始数据库操作了,use部分用到的就是刚刚定义的User，但为了不与控制器重名加了个as，这里用了两种方式添加数据**

    
    
    <?php
    namespace app\test\controller;
    use app\test\model\User as UserModel;
    
    class User
    {
        public function insert()
        {
    //        $user = new UserModel();
    //        $user->id=1;
    //        $user->name = 'Sentiment';
    //        $user->email = 'Sentiment@qq.com';
    //        $user->birthday=strtotime('2001-12-7');
    //        $user->save();
        //数组形式自定义
              $user['id']=2;
              $user['name']='Tana';
              $user['email']='Tana@qq.com';
              $user['birthday']=strtotime('2000-1-1');
              UserModel::create($user);
    
        }
    
    }
    

**访问test/user/insert，执行成功(注：这里定义了四个字段，所以在insert时候必须都加上，一开始以为会自动创建id就没加，结果一直没成功)**

![wKg0C2JeOATu81AAA9XSeDsiI178.png](https://image.3001.net/images/20221008/1665220919_6341413783a8ed1d6a5f1.png!small)

####  **批量添加**

 **也可以通过saveAll,批量新增**

    
    
    public function insertList(){
        $user = new UserModel();
        $list=[
            ['id'=>'3','name'=>'Mumu','email'=>'Mumu@qq.com','birthday'=>strtotime('2002-1-1')],
            ['id'=>'4','name'=>'Shelter','email'=>'Shelter@qq.com','birthday'=>strtotime('2003-1-1')]
        ];
        if($user->saveAll($list)){
            return 'Success';
        }else{
            return 'faild';
        }
    }
    

### **更新数据**

####  **查找并更新**

 **get获取id=1的数据**

    
    
    public function update(){
        $user = UserModel::get(1);
        $user->name='Mumu';
        $user->email='Mumu@qq.com';
        $user->birthday=strtotime('2002-1-1');
        $user->save();
        #dump($user);
    }
    

#### **直接更新数据**

    
    
    $user = new UserModel();
    $user->save(['name'=>'Shelter','email'=>'Shelter@qq.com'],['id'=>1]);
    

#### **批量更新**

    
    
    $user = new UserModel();
    $list=[
        ['id'=>'3','name'=>'Mumu','email'=>'Mumu@qq.com','birthday'=>strtotime('2002-1-1')],
        ['id'=>'4','name'=>'Shelter','email'=>'Shelter@qq.com','birthday'=>strtotime('2003-1-1')]
    ];
    

#### **通过数据库类更新**

    
    
    $user = new UserModel();
    $user->where('id',1)->update(['name'=>'Sentiment']);
    //包括主键的话也可以用下边这种方法
    //$user->update(['id'=>1,'name'=>'Tana']);
    

#### **静态方法**

    
    
    UserModel::where('id',1)->update(['name'=>'Sentiment']);
    //包括主键的话也可以用下边这种方法
    //UserModel::update(['id'=>1,'name'=>'Tana']);
    

### **查询数据**

####  **查询单个数据**

    
    
    //获取单个数据
    $user=UserModel::get(1);
    echo $user->name;
    
    //使用数组查询
    $user=UserModel::get(1);
    echo $user->email;
    
    //实例化模型后查询
    $user = new UserModel();
    $result = $user -> where('name','Sentiment')->find();
    echo $result->name;
    

#### **查询多个数据**

    
    
    //  获取多个数据
    //$list=UserModel::all('1,2');
    //  数组形式
    //$list=UserModel::all([1,2]);
    //foreach ($list as $key=>$value){
    //    echo $value->name;
    //  }
    
    //   实例化模型后查询
    $user = new UserModel();
    echo $user->where('id',1)->limit(2)->order('birthday','desc')->select();
    

### **删除数据**

    
    
    //删除当前模型
    $user = UserModel::get(1);
    $user->delete();
    
    //根据主键删除
    UserModel::destroy(1);
    //也可以删除多个
    UserModel::destroy('1,2');
    UserModel::destroy([1,2]);
    
    //条件删除
    UserModel::destroy(['id'=>1]);
    UserModel::where('id','>',0)->delete();
    

# **视图**

 **视图功能由**`\think\View`
**类配合视图驱动（也即模板引擎驱动）类一起完成，目前的内置模板引擎包含PHP原生模板和Think模板引擎。**

 **渲染模板最常用的是控制器类在继承系统控制器基类（**`\think\Controller` **）后调用**`fetch` **方法，调用格式：**

    
    
    fetch('[模板文件]'[,'模板变量（数组）'])
    

**常用方法：**

 **方法**|  **说明**  
---|---  
 **fetch**|  **渲染模板输出**  
 **assign**|  **模板变量赋值**  
 **engine**|  **初始化模板引擎**  
  
###  **视图渲染**

 **不给任何参数情况下默认返回，当前文件/view/控制器名/方法名.html**

    
    
    <?php
    namespace app\test\controller;
    use think\Controller;
    
    class See extends Controller{
        public function index(){
            // 自动定位
            //return $this->fetch();
            //test/view/see/index.html
    
            // 指定模板
            //return  $this->fetch('test');
            //test/view/see/test.html
    
            //指定目录
            //return $this->fetch('test/show');
            //test/view/test/show.html
    
            // 指定模块下的模板，适用于多模块
            //return $this->fetch('admin@public/test');
            //admin/view/public/test.html
    
            //view_path 下的模块
            //return $this->fetch('/Sentiment');
            //test/view/Sentiment.html
    
            // 如果没有继承 Controller 模块的话，可以使用助手函数 view() 方法，具体使用方法同上
            return view();
            //test/view/see/index.html
        }
    }
    

### **视图赋值**

 **视图赋值主要通过assign函数**

####  **assign赋值**

    
    
    //test/controller/Assign.php
    
    <?php
    namespace app\test\controller;
    use think\Controller;
    
    class Assign extends Controller{
        public function index(){
            //模板变量赋值
            $name='Sentiment';
            $age=18;
    //        $this->assign('name',$name);
    //        $this->assign('age',$age);
            //也可以通过数组赋值
            $this->assign([
                'name'=>$name,
                'age'=>$age,
            ]);
            return $this->fetch();
        }
    
    }
    

**想输出变量直接{$name}即可**

`/test/view/assign/index.html`

    
    
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Assign Test</title>
    </head>
    <body>
    this is assign/index.html</br>
    {$name}</br>
    {$age}
    </body>
    </html>
    

**访问/test/assign/index方法 成功返回body内容及变量值**

![wKg0C2JeeAWc34AAA2mCZNak667.png](https://image.3001.net/images/20221008/1665220920_63414138005f7f03ebde3.png!small)

####  **fetch赋值**

    
    
    return $this->fetch('index',['name'=>$name,'age'=>$age]);
    

#### **助手函数**

    
    
    return view('index',['name'=>$name,'age'=>$age]);

![wKg0C2JfAaAEA0GAAAka7wArDE410.png](https://image.3001.net/images/20221008/1665220920_634141386e66453d80ef6.png!small)

###  **视图过滤**

 **将6替换成了** < **br/ >**

![wKg0C2JfBOATIG1AAA20w3xP0A355.png](https://image.3001.net/images/20221008/1665220920_63414138cf6937849a558.png!small)

####  **初始化中全局过滤**

    
    
    <?php
    namespace app\test\controller;
    use think\Controller;
    
    class Assign extends Controller{
        public function index(){
                $this->assign(['name' => 'Sentiment6', 'age'=>186]);
            return $this->fetch();
        }
        public function initialize()
        {
            return $this->filter(function ($content) {
                return str_replace('6', '<br>', $content);
            });
        }
    
    }

#  **模板**

###  **变量输出**

 **普通输出方式**

    
    
    //test/controller/Assign.php
    <?php
    namespace app\test\controller;
    use think\Controller;
    
    class Assign extends Controller{
        public function index(){
            $this->assign('name', 'Sentiment');
            return $this->fetch();
        }
    }
    

**模板**

    
    
    //test/view/assign/index.html
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Assign Test</title>
    </head>
    <body>
    this is assign/index.html</br>
    Hello {$name}
    </body>
    </html>
    

![wKg0C2JfDaAX4GfAAAu2j4L9zo458.png](https://image.3001.net/images/20221008/1665220921_63414139435d55999bfe3.png!small)

**系统变量输出**

    
    
    {$Think.server.script_name} // 输出$_SERVER['SCRIPT_NAME']变量
    {$Think.session.user_id} // 输出$_SESSION['user_id']变量
    {$Think.get.page} // 输出$_GET['page']变量
    {$Think.cookie.name}  // 输出$_COOKIE['name']变量
    

**在index.html中加上{$Think.server.script_name}，即可输出对应的script_name值**

 **常量输出**

    
    
    {$Think.const.PHP_VERSION}
    或
    {$Think.PHP_VERSION}
    

**在**`Assign.php` **中定义个常量**

    
    
    define('AAA','this is define');
    

**在index.html加上**

    
    
    {$Think.AAA}
    

![wKg0C2JfGAS7jJAAAmIBygbc126.png](https://image.3001.net/images/20221008/1665220921_63414139b379189161672.png!small)

**配置输出**

    
    
    {$Think.config.default_module}
    {$Think.config.default_controller}
    

**语言配置**

    
    
    {$Think.lang.page_error}
    {$Think.lang.var_error}
    

**使用函数**

 **过滤方法**|  **描述**  
---|---  
 **date**|  **日期格式化（支持各种时间类型）**  
 **format**|  **字符串格式化**  
 **upper**|  **转换为大写**  
 **lower**|  **转换为小写**  
 **first**|  **输出数组的第一个元素**  
 **last**|  **输出数组的最后一个元素**  
 **default**|  **默认值**  
 **raw**|  **不使用（默认）转义**  
  
 **Assign.php**

    
    
    <?php
    namespace app\test\controller;
    use think\Controller;
    define('AAA','this is define');
    class Assign extends Controller{
        public function index(){
            $name='Sentiment';
            $time=time();
            $this->assign('name',$name);
            $this->assign('time',$time);
            return $this->fetch();
        }
    }
    

**index.html**

    
    
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Assign Test</title>
    </head>
    <body>
    this is assign/index.html<br> 
    {$name|md5}<br>                 //md5('Sentiment')
    {$name|upper|substr=0,3}<br>    //substr(upper('Sentiment'))
    {$time|date='Y-m-d H:i'}<br>    //时间
    </body>
    </html>
    

![wKg0C2JfICABzZWAABElNObf1I051.png](https://image.3001.net/images/20221008/1665220922_6341413a27d039ddbcefc.png!small)

### **原样输出**

 **加上{literal}后，{$name}就不会被解析，而是原样输出**

    
    
    {literal}
        Hello,{$name}！
    {/literal}
    

### **模板输出**

 **单行注释**

 **格式：**

    
    
    {/* 注释内容 */ } 或 {// 注释内容 } 
    

**例如**

    
    
    {// 这是模板注释内容 }
    

**注：**`{` **和注释标记之间不能有空格。**

 **多行注释**

 **支持多行注释，例如：**

    
    
    {/* 这是模板
    注释内容*/ }
    

**模板注释支持多行，模板注释在生成编译缓存文件后会自动删除，这一点和Html的注释不同。**

###  **模板布局**

 **全局配置方式**

 **开启**`layout_on`** 参数（默认不开启），并且设置布局入口文件名**`layout_name`
**（默认为layout）。(assign为我的view目录下的文件，根据自己情况修改或不加)**

    
    
    'layout_on'     =>  true,
    'layout_name'   =>  'assign/layout',
    

**在不开启**`layout_on`
**布局模板之前，会直接渲染`application/test/view/assign/index.html`模板文件,开启之后，首先会渲染**`application/test/view/layout.html`**
模板，布局模板的写法和其他模板的写法类似，本身也可以支持所有的模板标签以及包含文件，区别在于有一个特定的输出替换变量**`{__CONTENT__}`
**，例如，下面是一个典型的layout.html模板的写法：**

    
    
    {include file="public/header" /}
     {__CONTENT__}
    {include file="public/footer" /}
    

**在view/assign/下，新建layout.html,包含的是see/index.html**

    
    
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>a Test</title>
    </head>
    <body>
        {include file="see/index" /}<br>
        {__CONTENT__}
        {include file="see/index" /}<br>
    </body>
    </html>
    

**原本的assign/index.html把html标签去掉即可**

    
    
    {$name|md5}<br>
    {$name|upper|substr=0,3}<br>
    {$time|date='Y-m-d H:i'}<br>
    

**访问后{** **CONTENT** **}部分自动替换成了index.html内容**

![wKg0C2JfKWAYqKOAABkk6OMIm4991.png](https://image.3001.net/images/20221008/1665220922_6341413a97c9416a61f28.png!small)

 **这里的{** **CONTENT** **}是默认的也可以通过修改配置来定义**

 **这里通过配置文件定义的是全局配置，若某个文件不想使用该配置，则可以在html文件中加入**`{__NOLAYOUT__}`
**来取消本文件的全局配置**

    
    
    {__NOLAYOUT__}                  //加上后就不会被解析了
    {$name|md5}<br>
    {$name|upper|substr=0,3}<br>
    {$time|date='Y-m-d H:i'}<br>
    

**模板标签方式**

 **直接在模板文件中指定布局模板即可(前边的layout_on设置需要关闭)**

    
    
    {//__NOLAYOUT__}
    {layout name="assign/layout" /}
    {$name|md5}<br>
    {$name|upper|substr=0,3}<br>
    {$time|date='Y-m-d H:i'}<br>
    

**若需要使用其他模板布局(假设要用lay.html)，直接修改标签即可**

    
    
    {//__NOLAYOUT__}
    {layout name="assign/lay" /}
    {$name|md5}<br>
    {$name|upper|substr=0,3}<br>
    {$time|date='Y-m-d H:i'}<br>
    

**动态布局**

 **也不需要设置**`layout_on` **,加上**`$this->view->engine->layout(true);` **即可**

    
    
    <?php
    namespace app\test\controller;
    use think\Controller;
    define('AAA','this is define');
    class Assign extends Controller{
        public function index(){
            $name='Sentiment';
            $time=time();
            $this->assign('name',$name);
            $this->assign('time',$time);
            $this->view->engine->layout(true);          //在这里在这里
            return $this->fetch();
        }
    }
    

### **模板继承**

 **通过{block} {/block}标签，实现继承**

 **在view/assign/下，新建base.html**

    
    
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>base</title>
    </head>
    <body>
        {block name="header"}
            <div style= "width:10%; height:30px; background-color:yellow;">this is header</div>
        {/block}<br>
        {block name="footer"}
            <div style= "width:10%; height:30px; background-color:green;">this is footer</div>
        {/block}<br>
    </body>
    </html>
    

**view/assign/index.html**

通过extend继承`{extend name="assign/base" /}`

    
    
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>index</title>
    </head>
    <body>
        {extend name="assign/base" /}
    
    </body>
    </html>
    

![wKg0C2JfLaAMq8IAAAwMwM72wA040.png](https://image.3001.net/images/20221008/1665220923_6341413b0acee086b4eae.png!small)

**如果在子类中实现了与父类中同样的模板，则以子类中的内容显示，若此时想同时显示父类中的内容则可以通过{** **block** **}实现**

    
    
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>index</title>
    </head>
    <body>
        {extend name="assign/base" /}
        {block name="header"}{__block__}        //在这里 在这里
        <div style= "width:10%; height:30px; background-color:red;">this is header</div>
        {/block}<br>
        {block name="footer"}
        <div style= "width:10%; height:30px; background-color:blue;">this is footer</div>
        {/block}<br>
    </body>
    </html>
    

![wKg0C2JfMWAZxSUAABQKTV88nY289.png](https://image.3001.net/images/20221008/1665220923_6341413b769df48640ee2.png!small)

### **包含文件**

 **在模板布局中已经用到过了就不多解释了**

    
    
    {include file="see/index" /}
    

### **内置标签**

 **标签名**|  **作用**|  **包含属性**  
---|---|---  
 **include**|  **包含外部模板文件（闭合）**|  **file**  
 **load**|  **导入资源文件（闭合 包括js css import别名）**|
**file,href,type,value,basepath**  
 **volist**|  **循环数组数据输出**|  **name,id,offset,length,key,mod**  
 **foreach**|  **数组或对象遍历输出**|  **name,item,key**  
 **for**|  **For循环数据输出**|  **name,from,to,before,step**  
 **switch**|  **分支判断输出**|  **name**  
 **case**|  **分支判断输出（必须和switch配套使用）**|  **value,break**  
 **default**|  **默认情况输出（闭合 必须和switch配套使用）**|  **无**  
 **compare**|  **比较输出（包括eq neq lt gt egt elt heq nheq等别名）**|
**name,value,type**  
 **range**|  **范围判断输出（包括in notin between notbetween别名）**|  **name,value,type**  
 **present**|  **判断是否赋值**|  **name**  
 **notpresent**|  **判断是否尚未赋值**|  **name**  
 **empty**|  **判断数据是否为空**|  **name**  
 **notempty**|  **判断数据是否不为空**|  **name**  
 **defined**|  **判断常量是否定义**|  **name**  
 **notdefined**|  **判断常量是否未定义**|  **name**  
 **define**|  **常量定义（闭合）**|  **name,value**  
 **assign**|  **变量赋值（闭合）**|  **name,value**  
 **if**|  **条件判断输出**|  **condition**  
 **elseif**|  **条件判断输出（闭合 必须和if标签配套使用）**|  **condition**  
 **else**|  **条件不成立输出（闭合 可用于其他标签）**|  **无**  
 **php**|  **使用php代码**|  **无**  
  
 **volist**

 **这里以数据库内容举例，模板类获取数据库所有内容(数据库— >模板类有说过)**

    
    
    <?php
    namespace app\test\controller;
    use think\Controller;
    use app\test\model\User as UserModel;
    
    class Assign extends Controller{
        public function index(){
            $name=UserModel::all();
            $this->assign('name',$name);
            return $this->fetch();
        }
    }
    

**assign/index.html**

 **"name"为assign的值，根据变量进行修改**

    
    
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>index</title>
    </head>
    <body>
        {volist name="name" id="vo"}
            {$vo.id}====>{$vo.name}<br/>
        {/volist}
    </body>
    </html>
    

![wKg0C2JfNiAAdfHAAAjMfEEhuI397.png](https://image.3001.net/images/20221008/1665220923_6341413be63fae23dd163.png!small)

**可以加上**`offset="0" length="1"` **，定义获取数据的个数**

    
    
    {volist name="name" id="vo" offset="0" length="1"}
        {$vo.id}====>{$vo.name}<br/>
    {/volist}
    

**foreach**

 **实现结果同上**

    
    
    {foreach $name as $vo}
        {$vo.id}====>{$vo.name}<br/>
    {/foreach}
    

**for**

    
    
    {for start="开始值" end="结束值" comparison="用于比较，默认值是<" step="步长" name="循环变量名"}
    {/for}
    

**循环输出1-10**

    
    
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>index</title>
    </head>
    <body>
        {for start="1" end="10"}
        {$i}
        {/for}
    </body>
    </html>
    

![wKg0C2JfOGAPP63AAAh6YAvdqg993.png](https://image.3001.net/images/20221008/1665220924_6341413c6154ec6c0e752.png!small)

**php**

 **执行php语句**

    
    
    {php}
        echo 'hi Sentiment';
    {/php}
    

# **路由**

 **静态**

    
    
    Route::get('unserialize', 'unserialize/unserialize');
    

**访问unserialize后，便会自动跳转到unserialize/unserialize界面**

 **动态**

    
    
    Route::get('route/:id','test/Index/index');
    

**index.php**

    
    
    <?php
    namespace app\test\controller;
    use think\facade\Request;
    
    class Index
    {
        public function index(){
            dump(Request::route());
        }
    }
    

**id为我们动态输入的值，修改id后返回信息也会动态变化**

#  **请求**

###  **请求对象**

 **1.当控制器继承了控制器基类时，会自动被注入 Request 请求对象的功能**

    
    
    <?php
    namespace app\test\controller;
    use think\Controller;
    class Index extends Controller{
        public function index(){
            return $this->request->param('name');
        }
    }
    

![wKg0C2JfQOAYPtoAAAmzU09FU698.png](https://image.3001.net/images/20221008/1665220924_6341413cc50e1659329bb.png!small)

**2.不继承控制器基类(操作方法注入)**

 **无论是否继承系统的控制器基类，都可以使用操作方法注入。**

    
    
    <?php
    namespace app\test\controller;
    use think\Request;
    
    class Index {
        public function index(Request $request){
            return $request->param('name');
        }
    }
    

**跟**`1` **传参方式一样**

 **3、构造方法注入**

    
    
    <?php
    namespace app\test\controller;
    use think\Request;
    
    class Index {
        public function __construct(Request $request)
        {
            $this->request = $request;
        }
        public function index(){
            return $this->request->param('name');
        }
    }
    

**4、Facade调用(无依赖注入)**

 **在没有使用依赖注入的场合，可以通过**`Facade` **机制来静态调用请求对象的方法（注意**`use` **引入的类库区别）。**

    
    
    <?php
    namespace app\test\controller;
    use think\facade\Request;
    
    class Index {
    
        public function index(){
            return Request::param('name');
        }
    }
    

**5、助手函数(有无继承都可)**

 **为了简化调用，系统还提供了**`request` **助手函数，可以在任何需要的时候直接调用当前请求对象。**

    
    
    <?php
    namespace app\test\controller;
    
    class Index
    {
        public function index()
        {
            return request()->param('name');
        }
    }
    

### **请求信息**

`Request` **对象支持获取当前的请求信息，包括：**

 **方法**|  **含义**  
---|---  
`host`|  **当前访问域名或者IP**  
`scheme`|  **当前访问协议**  
`port`|  **当前访问的端口**  
`remotePort`|  **当前请求的REMOTE_PORT**  
`protocol`|  **当前请求的SERVER_PROTOCOL**  
`contentType`|  **当前请求的CONTENT_TYPE**  
`domain`|  **当前包含协议的域名**  
`subDomain`|  **当前访问的子域名**  
`panDomain`|  **当前访问的泛域名**  
`rootDomain`|  **当前访问的根域名（**`V5.1.6+` **）**  
`url`|  **当前完整URL**  
`baseUrl`|  **当前URL（不含QUERY_STRING）**  
`query`|  **当前请求的QUERY_STRING参数**  
`baseFile`|  **当前执行的文件**  
`root`|  **URL访问根地址**  
`rootUrl`|  **URL访问根目录**  
`pathinfo`|  **当前请求URL的pathinfo信息（含URL后缀）**  
`path`|  **请求URL的pathinfo信息(不含URL后缀)**  
`ext`|  **当前URL的访问后缀**  
`time`|  **获取当前请求的时间**  
`type`|  **当前请求的资源类型**  
`method`|  **当前请求类型**  
  
 **对于上面的这些请求方法，一般调用无需任何参数，但某些方法可以传入**`true` **参数，表示获取带域名的完整地址，例如：**

    
    
    use think\facade\Request;
    
    // 获取完整URL地址 不带域名
    Request::url();
    // 获取完整URL地址 包含域名
    Request::url(true);
    // 获取当前URL（不含QUERY_STRING） 不带域名
    Request::baseFile();
    // 获取当前URL（不含QUERY_STRING） 包含域名
    Request::baseFile(true);
    // 获取URL访问根地址 不带域名
    Request::root();
    // 获取URL访问根地址 包含域名
    Request::root(true);
    

**获取完整URL，不带域名**

    
    
    <?php
    namespace app\test\controller;
    use think\facade\Request;
    class Index
    {
        public function index()
        {
            return Request::url();
        }
    }
    

![wKg0C2JfVyADHdcAAAlTAzQylE262.png](https://image.3001.net/images/20221008/1665220925_6341413d3159afd777ded.png!small)

### **请求变量**

 **可以通过**`Request` **对象完成全局输入变量的检测、获取和安全过滤，支持包括**`$_GET` **、**`$_POST`
**、**`$_REQUEST` **、**`$_SERVER` **、**`$_SESSION` **、**`$_COOKIE` **、**`$_ENV`
**等系统变量，以及文件上传信息。(所有示例代码均使用**`Facade` **方式)**

    
    
    use think\facade\Request;
    

**1、使用 has() 方法，可以检测全局变量是否已经设置**

    
    
    <?php
    namespace app\test\controller;
    use think\facade\Request;
    class Index
    {
        public function index()
        {
            dump(Request::has('name','get'));
            dump(Request::has('id','post'));
        }
    }
    

![wKg0C2JfWOAYph0AABmtetlU676.png](https://image.3001.net/images/20221008/1665220925_6341413ddd2ca29915d8b.png!small)

**2、变量获取**

 **变量获取使用**`\think\Request` **类的如下方法及参数：**

 **变量类型方法('变量名/变量修饰符','默认值','过滤方法')**

 **变量类型方法包括：**

 **方法**|  **描述**  
---|---  
 **param**|  **获取当前请求的变量**  
 **get**|  **获取 $_GET 变量**  
 **post**|  **获取 $_POST 变量**  
 **put**|  **获取 PUT 变量**  
 **delete**|  **获取 DELETE 变量**  
 **session**|  **获取 $_SESSION 变量**  
 **cookie**|  **获取 $_COOKIE 变量**  
 **request**|  **获取 $_REQUEST 变量**  
 **server**|  **获取 $_SERVER 变量**  
 **env**|  **获取 $_ENV 变量**  
 **route**|  **获取 路由（包括PATHINFO） 变量**  
 **file**|  **获取 $_FILES 变量**  
  
 **获取当前强求变量**

    
    
    // 获取当前请求的name变量(过滤)
    Request::param('name');
    // 获取当前请求的所有变量（过滤）
    Request::param();
    // 获取当前请求的所有变量（原始数据、不过滤）
    Request::param(false);
    // 获取当前请求的所有变量（包含上传文件、过滤）
    Request::param(true);
    
    
    
    <?php
    namespace app\test\controller;
    use think\facade\Request;
    class Index
    {
        public function index()
        {
            dump(Request::param());
        }
    }
    

![wKg0C2JfW6AKF9sAABQnNJgB60054.png](https://image.3001.net/images/20221008/1665220926_6341413e5284e304858f6.png!small)

**3、变量过滤**

 **框架默认没有设置任何全局过滤规则，可以在应用配置文件中设置全局的过滤规则：**

    
    
    # config/app.php
    
    // 默认全局过滤方法 用逗号分隔多个
    'default_filter'         => 'htmlspecialchars',
    如果设置过滤方法，上传变量信息会获取不到
    
    # 单个设置
    dump(Request::param('name','','htmlspecialchars'));
    
    
    
    <?php
    namespace app\test\controller;
    use think\facade\Request;
    class Index
    {
        public function index()
        {
              dump(Request::param('name','','htmlspecialchars'));
        }
    }
    

**php7.3没成功，换成了7.4**

![wKg0C2JfXiAGYmeAAA1p4f1Pk4552.png](https://image.3001.net/images/20221008/1665220926_6341413ebdc8105d1563c.png!small)

 **4、获取部分变量(only)**

 **只获取当前请求的name变量**

    
    
    <?php
    namespace app\test\controller;
    use think\facade\Request;
    class Index
    {
        public function index()
        {   // 只获取当前请求的name变量
            dump(Request::only('name'));
            //数组形式
            //dump(Request::only(['name']));
        }
    }
    

![wKg0C2JfYeAcWvoAABPnvVuSU832.png](https://image.3001.net/images/20221008/1665220927_6341413f36d8c822c1408.png!small)

**except排除某些变量后获取**

    
    
    dump(Request::except('id'));
    //数组形式
    dump(Request::except(['id']));
    

**5、默认值**

    
    
    Request::get('name'); // 返回值为null
    Request::get('name',''); // 返回值为空字符串
    Request::get('name','default'); // 返回值为default
    
    
    
    <?php
    namespace app\test\controller;
    use think\facade\Request;
    class Index
    {
        public function index()
        {
            dump(Request::param('name','Sentiment'));
            dump(Request::param('name'));
            dump(Request::param('name','default'));
    
        }
    }
    

![wKg0C2JfZKADqAFAABjUFhJxwQ544.png](https://image.3001.net/images/20221008/1665220927_6341413fa5023fb74d609.png!small)

**6、变量修饰符**

 **Request::变量类型('变量名/修饰符');**

    
    
    /s(字符串) 
    /d(整型) 
    /b(布尔) 
    /a(数组) 
    /f(浮点)
    
    
    
    <?php
    namespace app\test\controller;
    use think\facade\Request;
    class Index
    {
        public function index()
        {
            dump(Request::param('name/s'));
            dump(Request::param('name/d'));
            dump(Request::param('name/a'));
    
        }
    }
    

![wKg0C2JfZuACSDsAABoeDnKUr4546.png](https://image.3001.net/images/20221008/1665220928_634141401c13716e3c2cf.png!small)

**7、路由获取**

    
    
    //test/controller/index
    <?php
    namespace app\test\controller;
    use think\facade\Request;
    class Index
    {
        public function index($id)
        {
            dump(Request::route());
        }
    }
    
    //route/route.php
    Route::get('route/:id','test/Index/index');
    

![wKg0C2JfbmAAoAABGdFKi94704.png](https://image.3001.net/images/20221008/1665220928_6341414085d3781c148a6.png!small)

**8、助手函数**

 **为了简化使用，还可以使用系统提供的**`input` **助手函数完成上述大部分功能。**

  *  **判断变量是否定义**

    
    
    <?php
    namespace app\test\controller;
    use think\facade\Request;
    class Index
    {
        public function index()
        {   //get
            dump(input('?get.name'));
            //post
            dump(input('?post.name'));
        }
    }
    

![wKg0C2JfciAenR4AABa7CiTI7o545.png](https://image.3001.net/images/20221008/1665220929_63414141014b4c23edd27.png!small)

  * **获取PARAM参数**

    
    
    dump(input('param.name')); // 获取单个参数
    dump(input('param.')); // 获取全部参数
    // 下面是等效的
    dump(input('name'));
    dump(input(''));
    

![wKg0C2Jfd2ABGqwAACNJJ7Bvk125.png](https://image.3001.net/images/20221008/1665220929_6341414172aa9cecee058.png!small)

  * **获取GET参数**

    
    
    // 获取单个变量
    dump(input('get.id'));
    // 使用过滤方法获取 默认为空字符串
    dump(input('get.name'));
    // 获取全部变量
    dump(input('get.'));
    

  * **使用过滤方法**

    
    
    dump(input('get.name','','htmlspecialchars')); // 获取get变量 并用htmlspecialchars函数过滤
    dump(input('username','','strip_tags')); // 获取param变量 并用strip_tags函数过滤
    dump(input('post.name','','org\Filter::safeHtml')); // 获取post变量 并用org\Filter类的safeHtml方法过滤
    

  * **使用变量修饰符**

    
    
    input('get.id/d');
    input('post.name/s');
    input('post.ids/a');
    

### **HTTP信息**

    
    
    <?php
    namespace app\test\controller;
    use think\facade\Request;
    class Index
    {
        public function index()
        {
            $info = Request::header();
            dump($info);
            dump($info['host']);
            dump($info['user-agent']);
        }
    }
    

![wKg0C2JfeqAOf4OAACbof2QHM242.png](https://image.3001.net/images/20221008/1665220930_634141420666f924255f7.png!small)

### **伪静态**

 **URL伪静态通常是为了满足更好的SEO效果，ThinkPHP支持伪静态URL设置，可以通过设置**`url_html_suffix`
**参数随意在URL的最后增加你想要的静态后缀，而不会影响当前操作的正常执行。**

 **可以通过ext()方法获取后缀**

    
    
    <?php
    namespace app\test\controller;
    use think\facade\Request;
    class Index
    {
        public function index()
        {
            return Request::ext();
        }
    
    }
    

**当访问index.pdf后会报错，但访问index.html则不会**

![wKg0C2JffOAFwMMAAAYZWWqhis573.png](https://image.3001.net/images/20221008/1665220930_634141427e3f200ab4dec.png!small)

 **这是因为在配置文件中设置的伪静态为html，若想用pdf，通过**`|` **分割加上即可**

    
    
    'url_html_suffix'        => 'html|pdf',
    

**在不该设置的情况下，使用 url::build() 获取当前完整 url，得到默认后缀为 .html**

    
    
    <?php
    namespace app\test\controller;
    use think\facade\Request;
    class Index
    {
        public function index()
        {
            return \think\facade\Url::build();
        }
    
    }
    

![wKg0C2Jff2AXBsZAAAeMEDgjM174.png](https://image.3001.net/images/20221008/1665220930_63414142e18d53eb003b8.png!small)

**若不想使用伪静态关闭即可**

    
    
    'url_html_suffix' => false,
    

### **参数绑定**

 **1、默认参数**

    
    
    <?php
    namespace app\test\controller;
    class Index
    {
        public function index($name='Sentiment',$id=1)
        {
            return 'name:'.$name.'<br>'.'id:'.$id;
        }
    }
    

![wKg0C2JfgWAKYnZAAAfo4CRI567.png](https://image.3001.net/images/20221008/1665220931_634141435374fba58e7b0.png!small)

![wKg0C2Jfg2AZPKAAAAiOeDrzw264.png](https://image.3001.net/images/20221008/1665220931_63414143bac8e588d9622.png!small)

**2、成对解析，可以换顺序**

![wKg0C2JfhSAXma0AAAkA5ngE2A537.png](https://image.3001.net/images/20221008/1665220932_634141443e5f38d5a0a93.png!small)

    
    
    // URL参数方式 0 按名称成对解析 1 按顺序解析
    'url_param_type'         => 0,
    

### **请求缓存**

 **全局缓存**

    
    
    // 是否开启请求缓存 true自动缓存 支持设置请求缓存规则
    'request_cache'          => false,
    // 请求缓存有效期，建议3600，时间太短没有意义
    'request_cache_expire'   => null,  
    
    // 全局请求缓存排除规则
    'request_cache_except'   => [],
    

**开启缓存后，第二次访问时，会自动获取请求缓存的数据响应输出，并发送304状态码**

 **单独缓存**

    
    
    //route/route.php
    Route::get('route/:id','test/Index/index')->cache(3600);
    //test/controller/index.php
    <?php
    namespace app\test\controller;
    use think\facade\Request;
    class Index
    {
        public function index()
        {
            dump(Request::param());
            dump(Request::route());
        }
    }
    

**刷新一次后状态码变成304，这时就已经缓存了，当我改变index.php的内容后，访问/route/777仍然是这个界面**

![wKg0C2JfhyAUi53AACZmeOizXs757.png](https://image.3001.net/images/20221008/1665220932_63414144a036e8f6f3e6b.png!small)

#  **响应**

 **响应（**`Response`
**）对象用于动态响应客户端请求，控制发送给用户的信息。通常用于输出数据给客户端或者浏览器。由**`think\Response` **类或者子类完成。**

###  **响应参数**

 **响应输出，包括 return(),json(),view()**

    
    
    <?php
    namespace app\test\controller;
    class Index
    {
        public function response(){
            return response('index','201');
            //return response('index')->code('201');
            //设置头信息
            //return response('index')->code('201')->header(['Cache-control' => 'no-cache,must-revalidate']); sh
        }
    
    }
    

![wKg0C2JfiaAd7pxAABX2lpsMc585.png](https://image.3001.net/images/20221008/1665220933_634141451e729e6aa2d01.png!small)

### **重定向**

 **redirect() 方法页面重定向**

    
    
    <?php
    namespace app\test\controller;
    class Index
    {
        public function response(){
            return redirect('http://sentiment1.top');
        }
    }
    

**站内重定向，直接输入路由地址或相对地址即可**

    
    
    return redirect('/index/index/hello/name/Sentiment');
    
    return redirect('hello')->params(['name'=>'Sentiment']);
    
    return redirect('hello',['name'=>'Sentiment']);
    

### **文件下载**

 **文本文件和图片文件都可以使用 download() 方法下载**

    
    
    <?php
    namespace app\test\controller;
    class Index
    {
        public function down(){
            $data='this is test';
            return download($data,'test.txt',true);
        }
    }
    

**访问/test/index/down后便可下载test.txt,内容为this is test**


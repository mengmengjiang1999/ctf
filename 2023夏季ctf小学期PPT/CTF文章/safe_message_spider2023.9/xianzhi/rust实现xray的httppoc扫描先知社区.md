### 作者: Mob2003

### 读取poc文件

直接使用第三方库serde,serde_json,serder_yaml,serde-tuple-vec-map 进行反序列化
对xray的yml文件进行解析，在构造结构体的时候，我们发现，有一些看上去应该是HashMap类型的变量，执行起来却必须是有序的,如

    
    
    set:
    reverse: newReverse()
    reverseURL: reverse.url

必须先执行reverse，再把reverse.url赋值给reverseURL
这时候我们想要用BtreeMap去反序列化，却发现排出来的循序，未必是符合poc编写者所写的，这时候serde-tuple-vec-map就派上用场了，这个库的主要作用是将 yml或者json中的map，反序列化成为Vec，以便于我们获得与原始json、yml顺序一致的map
使用方法也很简单

    
    
    pub struct Template {
    pub name: String,
    pub transport: String,
    #[serde(with = "tuple_vec_map",default)]
    pub set: Vec<(String, String)>,
    pub payloads: Option<bool>,
    #[serde(with = "tuple_vec_map",default)]
    pub rules: Vec<(String, TemplateRule)>,
    pub expression: String,
    pub detail: TemplateDetail,
    }

其他类型并没有什么特殊的，按照yml和json的原始格式，设置为对应的Vec或者String就可以了，主要是使用
#[serde(rename="xxx",default)]重命名和设置默认值

### 执行poc

刚开始执行到一个简单的xray poc的时候，发现只需要执行一个r0()并根据r0里面expression简单判断一下status ==
200，随便找一个http包，请求一下url，并
判断status是不是200就完事了，等尝试执行更多的poc，却发现expression里面的内容变得非常复杂，查看了xray文档发现，是使用了谷歌cel
Common Expression Language
，使得静态编译语言获得执行动态文本代码的能力，谷歌给golang开发了完整一套cel第三方库，很不幸谷歌并没有给rust弄一份板条
箱，github上与docs.rs上并没有完整的cel三方库，最终选择了cel-interpreter，cel-parser进行二次开发，相关代码已上传到github上，如果你想要自己实现一个 cel解析引擎，可以参考一下下面的流程

新建一个全局ctx，初始化一些公共方法,如下

    
    
    let mut ctx: Context = Default::default();
    ctx.add_async_function("randomInt", randint());
    ctx.add_async_function("bcontains", bcontains());
    ctx.add_async_function("randomLowercase", random_lowercase());
    ctx.add_async_function("string", string());

读取一个poc文件，创建一个子ctx，子ctx把set存到子ctx上

    
    
    for (k, _) in t.set.iter() {
    set.insert(
    "{{".to_string() + &k + "}}",
    context.get_variable(k).await?.to_string(),
    );
    }
    context.add_variable("set", set.into());

从子ctx，生成孙ctx，孙ctx添加上rules闭包，闭包里写好了http请求与将结果存到孙ctx，并执行rule的expression判断

    
    
    let mut context = Context::from_parent(&context);
    for (k, mut rule) in t.rules {
    context.add_async_function(&k, get_http_async_closure(req.clone(), rule));
    }

使用孙ctx，执行最外面的expression，如r0() &&
r1()，cel解析器会先把r0的闭包调出来执行，为false返回false，为true则继续执行
r1()，最终根据r1返回true(poc验证成功)或者false(poc扫描失败)

    
    
    match Program::compile(&t.expression)
    .unwrap()
    .execute(context)
    .await
    {
    Ok(res) => match res {
    CelType::Bool(res) => {
    return Ok(res);
    }
    other => {
    return Err(CelError::Custom(format!("未预料结果 {:?}", other)));
    }
    },
    Err(e) => return Err(e),
    };

### 总结

开发xray
poc的http扫描的时候，遇到最大的问题是谷歌cel的解析，最终只能自己去二开来实现，所以这个rust二开的cel解析执行引擎，只能用来执行本poc扫描，如
果用作其他不保证达到你想要的的效果，其次问题是遇到rust里最难写的 异步闭包保存到map与执行，这个在另一篇文章再进行介绍。

github地址：<https://github.com/Mob2003>


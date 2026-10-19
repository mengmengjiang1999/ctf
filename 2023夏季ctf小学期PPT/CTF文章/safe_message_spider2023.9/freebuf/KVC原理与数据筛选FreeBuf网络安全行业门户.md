作者：宋宏帅

## 1 前言

在技术论坛中看到一则很有意思的KVC案例：

    
    
    @interface Person : NSObject
    @property (nonatomic, copy) NSString *name;
    @property (nonatomic, assign) NSInteger age;
    @end
    Person *person = [Person new];
    person.name = @"Tom";
    person.age = 10;
    [person setValue:@"100" forKey:@"age"];//此处赋值为字符串，类中属性为Integer

第一反应是崩溃，因为OC是类型敏感的。可是自己实现并打印后的结果出于意料,没有崩溃且赋值成功。所以有了深入了解KVC的内部实现的想法！

## 2 什么是KVC

key-value-coding:键值编码，一种可以通过键名间接访问和赋值对象属性的机制  
KVC是通过NSObject、NSArray、NSDictionary等的类别来实现的  
主要方法包括一下几个：

    
    
    - (nullable id)valueForKey:(NSString *)key;
    - (void)setValue:(nullable id)value forKey:(NSString *)key;
    - (void)setNilValueForKey:(NSString *)key;
    - (void)setValue:(nullable id)value forUndefinedKey:(NSString *)key;
    - (nullable id)valueForUndefinedKey:(NSString *)key;

``

## 3 KVC执行分析

那么上面的案例中的- (void)setValue:(nullable id)value forKey:(NSString
*)key;是怎样的执行过程呢？借助反汇编工具获得Foundation.framework部分源码(为了解决和系统API冲突问题增加前缀_d,NS替换为DS)，以此分析KVC执行过程。（流程中的边界判断等已经忽略，如想了解可以参考源码，本文只探究主流程。）

### 3.1 设置属性

##### 3.1.1 查找访问器方法或成员变量

    
    
    + (DSKeyValueSetter *)_d_createValueSetterWithContainerClassID:(id)containerClassID key:(NSString *)key {
    DSKeyValueSetter *setter = nil;
    char key_cstr_upfirst[key_cstr_len + 1];
    key_cstr[key_cstr_len + 1];
    ...
    Method method = NULL;
    //按顺序寻找set<Key>,_set<Key>,setIs<Key>。找到后则生成对应的seter
    if ((method = DSKeyValueMethodForPattern(self, "set%s:", key_cstr_upfirst)) ||
    (method = DSKeyValueMethodForPattern(self, "_set%s:", key_cstr_upfirst)) ||
    (method = DSKeyValueMethodForPattern(self, "setIs%s:", key_cstr_upfirst))
    ) { //生成Method：包含selector，IMP。返回和参数类型字符串
    setter = [[DSKeyValueMethodSetter alloc] initWithContainerClassID:containerClassID key:key method:method];
    } else if ([self accessInstanceVariablesDirectly]) {//如果没有找到对应的访问器方且工厂方法accessInstanceVariablesDirectly == ture ，则按照顺序查找查找成员变量_<key>,_is<Key>,<key>,is<Key>(注意key的首字母大小写，查找到则生成对应的setter)
    Ivar ivar = NULL;
    if ((ivar = DSKeyValueIvarForPattern(self, "_%s", key_cstr)) ||
    (ivar = DSKeyValueIvarForPattern(self, "_is%s", key_cstr_upfirst)) ||
    (ivar = DSKeyValueIvarForPattern(self, "%s", key_cstr)) ||
    (ivar = DSKeyValueIvarForPattern(self, "is%s", key_cstr_upfirst))
    ) {
    setter = [[DSKeyValueIvarSetter alloc] initWithContainerClassID:containerClassID key:key containerIsa:self ivar:ivar];
    }
    }
    ...
    return setter;
    }

``

查找顺序如下：

  1. 查找访问器方法：set,_set,setIs
  2. 如果步骤1中没找到对应的方法且 accessInstanceVariablesDirectly == YES

则查找顺序如下：_,_is,,is  
查找不到则调用valueForUndefinedKey并抛出异常

##### 3.1.2 生成setter

    
    
    + (DSKeyValueSetter *)_d_createOtherValueSetterWithContainerClassID:(id)containerClassID key:(NSString *)key {
    return [[DSKeyValueUndefinedSetter alloc] initWithContainerClassID:containerClassID key:key containerIsa:self];
    }
    //构造方法确定方法编号 d_setValue:forUndefinedKey: 和方法指针IMP _DSSetValueAndNotifyForUndefinedKey
    - (id)initWithContainerClassID:(id)containerClassID key:(NSString *)key containerIsa:(Class)containerIsa {
    ...
    return [super initWithContainerClassID:containerClassID key:key implementation:method_getImplementation(class_getInstanceMethod(containerIsa, @selector(d_setValue:forUndefinedKey:))) selector:@selector(d_setValue:forUndefinedKey:) extraArguments:arguments count:1];
    }

``

  1. ````

![](https://image.3001.net/images/20221129/1669689334_63856ff671a3a60e8b5db.png!small)

##### 3.1.3 赋值

基本的访问器方法、变量的查找和异常处理已经清楚的知道了。那么上面的例子是如何出现的呢？明明传入的是字符串，最后赋值的时候转变为访问器方法所对应的类型？继续刨根问底！

DSKeyValueSetter对象已经生成，即确定了发送消息的对象object、访问器方法名SEL、访问器函数指针IMP、以及使用KVC时传入的Key和Value。下面进入方法调用阶段：_DSSetUsingKeyValueSetter(self,setter,
value);

![](https://image.3001.net/images/20221129/1669689335_63856ff71ce2893bb4c49.jpg!small)

IMP指针为_DSSetIntValueForKeyWithMethod其定义如下：之所以有文章开头提到的效果就是这里起了作用，在IMP调用的时候做了[value
valueGetSelectorName]，将对应的NSNumber转换为简单数据类型。这里是intValue。

    
    
    void _DSSetIntValueForKeyWithMethod(id object, SEL selector,id value, NSString *key, Method method) {// object:person selector:setAge: value:@(100) key:age method:selector + IMP + 返回类型和参数类型 即_extraArgument2,其在第一步查找到访问器方法后生成
    __DSSetPrimitiveValueForKeyWithMethod(object, selector, value, key, method, int, intValue);
    }
    #define __DSSetPrimitiveValueForKeyWithMethod(object, selector, value, key, method, valueType, valueGetSelectorName) do {\
    if (value) {\
    void (*imp)(id,SEL,valueType) = (void (*)(id,SEL,valueType))method_getImplementation(method);\
    imp(object, method_getName(method), [value valueGetSelectorName]);\调用person的setAge:方法。参数为100
    }\
    else {\
    [object setNilValueForKey:key];\
    }\
    }while(0)
    //如果第一步中没有找到访问器方法只找到了成员变量则直接执行赋值操作
    void _DSSetIntValueForKeyInIvar(id object, SEL selector, id value, NSString *key, Ivar ivar) {
    if (value) {
    *(int *)object_getIvarAddress(object, ivar) = [value intValue];
    }
    else {
    [object setNilValueForKey:key];
    }
    }

起始问题完美解决！执行流程如下：

``

  1. ````

![](https://image.3001.net/images/20221129/1669689336_63856ff8780ab1a0dcf84.png!small)

### 3.2 取值

##### 3.2.1 查找访问器方法或成员变量

    
    
    + (DSKeyValueGetter *)_d_createValueGetterWithContainerClassID:(id)containerClassID key:(NSString *)key {
    DSKeyValueGetter * getter = nil;
    ...
    Method getMethod = NULL;
    if((getMethod = DSKeyValueMethodForPattern(self,"get%s",keyCStrUpFirst)) ||
    (getMethod = DSKeyValueMethodForPattern(self,"%s",keyCStr)) ||
    (getMethod = DSKeyValueMethodForPattern(self,"is%s",keyCStrUpFirst)) ||
    (getMethod = DSKeyValueMethodForPattern(self,"_get%s",keyCStrUpFirst)) ||
    (getMethod = DSKeyValueMethodForPattern(self,"_%s",keyCStr))) {
    getter = [[DSKeyValueMethodGetter alloc] initWithContainerClassID:containerClassID key:key method:getMethod];
    }// 查找对应的访问器方法
    ...
    else if([self accessInstanceVariablesDirectly]) {//查找属性
    Ivar ivar = NULL;
    if((ivar = DSKeyValueIvarForPattern(self, "_%s", keyCStr)) ||
    (ivar = DSKeyValueIvarForPattern(self, "_is%s", keyCStrUpFirst)) ||
    (ivar = DSKeyValueIvarForPattern(self, "%s", keyCStr)) ||
    (ivar = DSKeyValueIvarForPattern(self, "is%s", keyCStrUpFirst))
    ) {
    getter = [[DSKeyValueIvarGetter alloc] initWithContainerClassID:containerClassID key:key containerIsa:self ivar:ivar];
    }
    }
    }
    if(!getter) {
    getter = [self _d_createValuePrimitiveGetterWithContainerClassID:containerClassID key:key];
    }
    return getter;
    }

  

````

  1. 按照get,,is,_的顺序查找成员方法
  2. 如果1.没有找到对应的方法且accessInstanceVariablesDirectly==YES，则继续查找成员变量，查找顺序为_,_is,,is
  3. 如果1，2没有找到对应的方法和属性则调用 valueForUndefinedKey:并抛出异常

##### 3.2.2 如上步骤没定位到访问器方法或成员变量则走下面的流程生成对应的getter

    
    
    访问器方法生成IMP
    - (id)initWithContainerClassID:(id)containerClassID key:(NSString *)key method:(Method)method {
    NSUInteger methodArgumentsCount = method_getNumberOfArguments(method);
    NSUInteger extraAtgumentCount = 1;
    if(methodArgumentsCount == 2) {
    char *returnType = method_copyReturnType(method);
    IMP imp = NULL;
    switch (returnType[0]) {
    ...
    case 'i': {
    imp = (IMP)_DSGetIntValueWithMethod;
    } break;
    ...
    free(returnType);
    if(imp) {
    void *arguments[3] = {0};
    if(extraAtgumentCount > 0) {
    arguments[0] = method;
    }
    return [super initWithContainerClassID:containerClassID key:key implementation:imp selector:method_getName(method) extraArguments:arguments count:extraAtgumentCount];
    }
    }

````

单步调试后可以看到具体的IMP类型

![](https://image.3001.net/images/20221129/1669689337_63856ff91d714896693c0.jpg!small)

定义如下：

    
    
    NSNumber * _DSGetIntValueWithMethod(id object, SEL selctor, Method method) {//
    return [[[NSNumber alloc] initWithInt: ((int (*)(id,SEL))method_getImplementation(method))(object, method_getName(method))] autorelease];
    }

````

  1. ````

##### 3.2.3 取值

取值调用如下：

![](https://image.3001.net/images/20221129/1669689338_63856ffa0dbfda5693a37.jpg!small)

### 4 简单数据类型KVC包装和拆装关系

NSNunber:

![](https://image.3001.net/images/20221129/1669689338_63856ffacde26e0ed3eec.png!small)

NSValue

![](https://image.3001.net/images/20221129/1669689339_63856ffb7196c3f4896c1.png!small)

## 5 KVC高级

 **修改数组中对象的属性**  
[array valueForKeyPath:@”uppercaseString”]  
利用KVC可以批量修改属性的成员变量值

 **求和，平均数，最大值，最小值**  
NSNumbersum= [array valueForKeyPath:@”[@sum](https://github.com/sum
"@sum").self”];  
NSNumberavg= [array valueForKeyPath:@”[@avg](https://github.com/avg
"@avg").self”];  
NSNumbermax= [array valueForKeyPath:@”[@max](https://github.com/max
"@max").self”];  
NSNumbermin= [array valueForKeyPath:@”[@min](https://github.com/min
"@min").self”];

## 6 数据筛选

经过上面的分析可以明白KVC的真正执行流程。下面结合日常工程中的实际应用来优雅的处理数据筛选问题。使用KVC处理可以减少大量for的使用并增加代码可读性和健壮性。  
如图所示：

![](https://image.3001.net/images/20221129/1669689340_63856ffc3af8fe47715bb.jpg!small)

项目中的细节如下：修改拒收数量时更新总妥投数和总拒收数、勾选明细更新总妥投数和总拒收数、全选、清空、反选。如果用通常的做法是每次操作都要循环去计算总数和记录选择状态。下面是采用KVC的实现过程。  
模型涉及：

    
    
      
    

  1. `@property (nonatomic,copy)NSString* skuCode;`
  2. `@property (nonatomic,copy)NSString* goodsName;`
  3. `@property (nonatomic,assign)NSInteger totalAmount;`
  4. `@property (nonatomic,assign)NSInteger rejectAmount;`
  5. `@property (nonatomic,assign)NSInteger deliveryAmount;`
  6. `///单选用`
  7. `@property (nonatomic, assign) BOOL selected;`

  1. ````

1）更新总数

    
    
    - (void)updateDeliveryInfo {
    //总数
    NSNumber *allDeliveryAmount = [self.orderDetailModel.deliveryGoodsDetailList valueForKeyPath:@"@sum.totalAmount"];
    //妥投数
    NSNumber *allRealDeliveryAmount = [self.orderDetailModel.deliveryGoodsDetailList valueForKeyPath:@"@sum.deliveryAmount"];
    //拒收数
    NSNumber *allRejectAmount = [self.orderDetailModel.deliveryGoodsDetailList valueForKeyPath:@"@sum.rejectAmount"];
    }

````

  1. ````

2）全选  
[self.orderDetailModel.deliveryGoodsDetailList setValue:@(YES)
forKeyPath:@”selected”];

3）清空  
[self.orderDetailModel.deliveryGoodsDetailList setValue:@(NO)
forKeyPath:@”selected”];

4)反选

    
    
    NSPredicate *selectedPredicate = [NSPredicate predicateWithFormat:@"selected == %@",@(YES)];
    NSArray *selectedArray = [self.orderDetailModel.deliveryGoodsDetailList filteredArrayUsingPredicate:selectedPredicate];
    NSPredicate *unSelectedPredicate = [NSPredicate predicateWithFormat:@"selected == %@",@(NO)];
    NSArray *unSelectedArray = [self.orderDetailModel.deliveryGoodsDetailList filteredArrayUsingPredicate:unSelectedPredicate];
    [selectedArray setValue:@(NO) forKeyPath:@"selected"];
    [unSelectedArray setValue:@(YES) forKeyPath:@"selected"];

````

  1. ````

## 7 总结

KVC在处理简单数据类型时会经过数据封装和拆装并转换为对应的数据类型。通过KVC的特性我们可以在日常使用中更加优雅的对数据进行筛选和处理。优点如下：可阅读性更高，健壮性更好。


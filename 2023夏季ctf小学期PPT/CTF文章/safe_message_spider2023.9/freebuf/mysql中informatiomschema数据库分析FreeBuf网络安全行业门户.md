## 分析

在mysql5.0.x的版本中，新增了information_schema数据库，此数据库中存储着整个mysql数据库中所有数据库的信息。在该数据库中，有schemata，tables，columns表。

### schemata表

该表中存储着所有数据库的名字信息等

![](https://image.3001.net/images/20220321/1647868039_623878872b43d95104b9a.png!small)

其中的schema_name列中存储着数据库的名字，所以如果想查看所有数据库的名字，可以使用payload：select group-concat(schema_name) from information_schema.schemata
表示从information_schema数据中的schemata表中查看schema_name列中的数据

### tables表

该表中存储着数据库中所有表的信息，以及该表的从属数据库名字信息

![](https://image.3001.net/images/20220321/1647868042_6238788ae244f8d43207e.png!small)

由此可知，table_name中存储着表的信息，而table_schema表中存储着该表所属数据库的名称，所以我么要查询表的名字的话，可以使用payload：select
group_concat(table_name) from information_schema.tables where
table_schema=’dvwa’

### columns表

该表中存储着数据库中所有列的信息以及数据还有起所属的表，数据库的名字信息等

![](https://image.3001.net/images/20220321/1647868047_6238788f1b2ff6b59e109.png!small)

由此可知，column_name中存储着所有列的名字信息，table_name中存储着该列所属的表的名字信息，table_schema中存储着该表表的所属的数据库名字信息

    
    
    select group_concat(column_name) from information_schema.columns where table_name=’users’ and table_schema=‘dvwa’

爆破user和password列中的数据：select group_concat(user,’:’,password) from dvwa.users


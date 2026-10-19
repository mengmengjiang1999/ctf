# 实验背景

近一年来发生几起的数据库连接被打满的情况，初步分析是应用使用连接数量“超过了”连接池（DBCP1.4）的上限，导致数据库连接被打满，其中一个结论是连接池的bug导致

# 问题分析

1、DBCP连接池的Bug导致连接数超过大小设置，其根本原因是在连接池初始化的时候，有可能创建多个连接池导致

  1. `protected synchronized DataSource createDataSource()`
  2. `throws SQLException {`
  3. `if (closed) {`
  4. `throw new SQLException("Data source is closed");`
  5. `}`
  6. ``
  7. `// Return the pool if we have already created it`
  8. `if (dataSource != null) {`
  9. `return (dataSource);`
  10. `}`
  11. ``
  12. `// create factory which returns raw physical connections`
  13. `ConnectionFactory driverConnectionFactory = createConnectionFactory();`
  14. ``
  15. `// create a pool for our connections`
  16. `createConnectionPool();`
  17. ``
  18. `// Set up statement pool, if desired`
  19. `GenericKeyedObjectPoolFactory statementPoolFactory = null;`
  20. `if (isPoolPreparedStatements()) {`
  21. `statementPoolFactory = new GenericKeyedObjectPoolFactory(null,`
  22. `-1, // unlimited maxActive (per key)`
  23. `GenericKeyedObjectPool.WHEN_EXHAUSTED_FAIL,`
  24. `0, // maxWait`
  25. `1, // maxIdle (per key)`
  26. `maxOpenPreparedStatements);`
  27. `}`
  28. ``
  29. `// Set up the poolable connection factory`
  30. `createPoolableConnectionFactory(driverConnectionFactory, statementPoolFactory, abandonedConfig);`
  31. ``
  32. `// Create and return the pooling data source to manage the connections`
  33. `createDataSourceInstance();`
  34. ``
  35. `try {`
  36. `for (int i = 0 ; i < initialSize ; i++) {`
  37. `connectionPool.addObject();`
  38. `}`
  39. `} catch (Exception e) {`
  40. `throw new SQLNestedException("Error preloading the connection pool", e);`
  41. `}`
  42. ``
  43. `return dataSource;`
  44. `}`

createDataSource方法里边调用createConnectionPool方法，如果后面方式执行失败，比如createPoolableConnectionFactory，当再次调用createDataSource，又会再次调用createConnectionPool，从而初始化多次连接池，下面是createConnectionPool

  1. `protected void createConnectionPool() {`
  2. `// Create an object pool to contain our active connections`
  3. `GenericObjectPool gop;`
  4. `if ((abandonedConfig != null) && (abandonedConfig.getRemoveAbandoned())) {`
  5. `gop = new AbandonedObjectPool(null,abandonedConfig);`
  6. `}`
  7. `else {`
  8. `gop = new GenericObjectPool();`
  9. `}`
  10. `gop.setMaxActive(maxActive);`
  11. `gop.setMaxIdle(maxIdle);`
  12. `gop.setMinIdle(minIdle);`
  13. `gop.setMaxWait(maxWait);`
  14. `gop.setTestOnBorrow(testOnBorrow);`
  15. `gop.setTestOnReturn(testOnReturn);`
  16. `gop.setTimeBetweenEvictionRunsMillis(timeBetweenEvictionRunsMillis);`
  17. `gop.setNumTestsPerEvictionRun(numTestsPerEvictionRun);`
  18. `gop.setMinEvictableIdleTimeMillis(minEvictableIdleTimeMillis);`
  19. `gop.setTestWhileIdle(testWhileIdle);`
  20. `connectionPool = gop;`
  21. `}`

显然这个情况只能是模块启动初始化的时候产生，且连接都不会被使用，而线上出现的问题是连接都在执行sql，不是这种情况！在1.4x的这个bug已经修复  
2、启动参数分析，从启动参数入手，看一下是不是连接池主动释放连接，导致正在使用的连接被释放，从而创建新的连接，给我们的现象是“连接数”超过了连接池的限制，下面是一个入库的连接池参数

  1. `partition1.driverClassName=com.mysql.jdbc.Driver`
  2. `partition1.initialSize=2`
  3. `partition1.maxActive=25`
  4. `partition1.minIdle=2`
  5. `partition1.maxIdle=5`
  6. `partition1.maxWait=3000`
  7. `partition1.threadPoolSize=10`
  8. `partition1.logAbandoned=true`
  9. `partition1.testWhileIdle=true`
  10. `partition1.testOnReturn=false`
  11. `partition1.testOnBorrow=true`
  12. `partition1.validationQuery=select now()`
  13. `//在每次空闲连接回收器线程(如果有)运行时检查的连接数量`
  14. `partition1.numTestsPerEvictionRun=5`
  15. `//在空闲连接回收器线程运行期间休眠的时间值,以毫秒为单位`
  16. `partition1.timeBetweenEvictionRunsMillis=30000`
  17. `//连接在池中保持空闲而不被空闲连接回收器线程`
  18. `partition1.minEvictableIdleTimeMillis=180000`
  19. `//设置了rmoveAbandoned=true 那么在getNumActive()快要到getMaxActive()的时候，系统会进行无效的Connection的回收，回收的 Connection为removeAbandonedTimeout(默认300秒)中设置的秒数后没有使用的Connection`
  20. `partition1.removeAbandoned=true`
  21. `//强制回收连接的时间，单位秒`
  22. `partition1.removeAbandonedTimeout=18`

注意connectionProperties参数

  1. `<bean id="partition[j]" class="org.apache.commons.dbcp.BasicDataSource"`
  2. `destroy-method="close">`
  3. `<property name="driverClassName" value="${partition[j].driverClassName}" ></property>`
  4. `<property name="url" value="${partition[j].url}" ></property>`
  5. `<property name="username" value="${partition[j].username}" ></property>`
  6. `<property name="password" value="${partition[j].password}" ></property>`
  7. `<property name="defaultAutoCommit" value="false" ></property>`
  8. `<property name="maxActive" value="${partition[j].maxActive}" ></property>`
  9. `<property name="maxIdle" value="${partition[j].maxIdle}" ></property>`
  10. `<property name="maxWait" value="${partition[j].maxWait}" ></property>`
  11. `<property name="initialSize" value="${partition[j].initialSize}" ></property>`
  12. `<property name="minIdle" value="${partition[j].minIdle}" ></property>`
  13. `<property name="logAbandoned" value="${partition[j].logAbandoned}" ></property>`
  14. `<property name="testWhileIdle" value="${partition[j].testWhileIdle}" ></property>`
  15. `<property name="testOnReturn" value="${partition[j].testOnReturn}" ></property>`
  16. `<property name="testOnBorrow" value="${partition[j].testOnBorrow}" ></property>`
  17. `<property name="validationQuery" value="${partition[j].validationQuery}" ></property>`
  18. `<property name="numTestsPerEvictionRun" value="${partition[j].numTestsPerEvictionRun}" ></property>`
  19. `<property name="timeBetweenEvictionRunsMillis" value="${partition[j].timeBetweenEvictionRunsMillis}" ></property>`
  20. `<property name="minEvictableIdleTimeMillis" value="${partition[j].minEvictableIdleTimeMillis}" ></property>`
  21. `<property name="removeAbandoned" value="${partition[j].removeAbandoned}" ></property>`
  22. `<property name="removeAbandonedTimeout" value="${partition[j].removeAbandonedTimeout}" ></property>`
  23. `<property name="connectionProperties" value="useUnicode=true;`
  24. `characterEncoding=utf8;initialTimeout=1;connectTimeout=1000;socketTimeout=6000;`
  25. `rewriteBatchedStatements=true;autoReconnectForPools=true;autoReconnect=true;maxReconnects=1;`
  26. `failOverReadOnly=false;roundRobinLoadBalance=true;allowMultiQueries=true"></property>`
  27. `</bean>`

从上面参数我们重点关注removeAbandonedTimeout 这个参数的意义

  1. `//创建连接`
  2. `public Object borrowObject() throws Exception {`
  3. `if (config != null`
  4. `&& config.getRemoveAbandoned()`
  5. `&& (getNumIdle() < 2)`
  6. `&& (getNumActive() > getMaxActive() - 3) ) {`
  7. `removeAbandoned();`
  8. `}`
  9. `Object obj = super.borrowObject();`
  10. `if (obj instanceof AbandonedTrace) {`
  11. `((AbandonedTrace) obj).setStackTrace();`
  12. `}`
  13. `if (obj != null && config != null && config.getRemoveAbandoned()) {`
  14. `synchronized (trace) {`
  15. `trace.add(obj);`
  16. `}`
  17. `}`
  18. `...`
  19. ``
  20. `private void removeAbandoned() {`
  21. `// Generate a list of abandoned connections to remove`
  22. `long now = System.currentTimeMillis();`
  23. `long timeout = now - (config.getRemoveAbandonedTimeout() * 1000);`
  24. `ArrayList remove = new ArrayList();`
  25. `synchronized (trace) {`
  26. `Iterator it = trace.iterator();`
  27. `while (it.hasNext()) {`
  28. `AbandonedTrace pc = (AbandonedTrace) it.next();`
  29. `if (pc.getLastUsed() > timeout) {`
  30. `continue;`
  31. `}`
  32. `if (pc.getLastUsed() > 0) {`
  33. `remove.add(pc);`
  34. `}`
  35. `}`
  36. `}`
  37. ``
  38. `// Now remove the abandoned connections`
  39. `Iterator it = remove.iterator();`
  40. `while (it.hasNext()) {`
  41. `AbandonedTrace pc = (AbandonedTrace) it.next();`
  42. `if (config.getLogAbandoned()) {`
  43. `pc.printStackTrace();`
  44. `} `
  45. `try {`
  46. `invalidateObject(pc);`
  47. `} catch (Exception e) {`
  48. `e.printStackTrace();`
  49. `}`
  50. ``
  51. `}`
  52. `}`

代从代码可以看出，配置了removeAbandonedOnBorrow和removeAbandonedTimeout就是触发正在使用的连接remove，假如这个时候，数据库正在执行sql，就会出现连接池已经断开连接，而数据库的连接还在执行，造成数据库的连接超过连接池的显现，如果少量慢sql执行时间大于removeAbandonedTimeout，不会出现问题，出现大量的慢sql，就会导致数据库中的这种连接越来越多，最后把数据库打满

# 实验过程

创建测试库

  1. `mkdir /usr/local/data/mysql`
  2. `docker run -d -e MYSQL_ROOT_PASSWORD=root --name centos/mysql-57-centos7 -v /usr/local/data/mysql:/var/lib/mysql -p 3306:3306 mysql --character-set-server=utf8mb4 --collation-server=utf8mb4_unicode_ci --lower_case_table_names=1`

创建测试库

  1. `create database test ;`

构建测试类，核心代码

  1. `public void setUp() throws Exception {`
  2. `ds = createDataSource();`
  3. `ds.setDriverClassName("com.mysql.jdbc.Driver");`
  4. `ds.setUrl("jdbc:mysql://127.0.0.1:3306/test?allowMultiQueries=true&characterEncoding=UTF-8&autoReconnect=true&failOverReadOnly=false&useSSL=false&allowPublicKeyRetrieval=true");`
  5. `ds.setUsername("root");`
  6. `ds.setPassword("Htbuy@2016");`
  7. `ds.setMaxActive(1);`
  8. `ds.setMaxWait(1000);`
  9. `ds.setTestWhileIdle(true);`
  10. `ds.setTestOnBorrow(true);`
  11. `ds.setTestOnReturn(false);`
  12. `ds.setValidationQuery("select now()");`
  13. `ds.setNumTestsPerEvictionRun(5);`
  14. `ds.setMinEvictableIdleTimeMillis(2000);`
  15. `ds.setLogAbandoned(true);`
  16. `ds.setRemoveAbandoned(true);`
  17. `ds.setRemoveAbandonedTimeout(1);`
  18. `}`
  19. `public void testAbandoned() throws Exception {`
  20. ``
  21. `for (int i = 0; i < 20; i++) {`
  22. `Thread t = new Thread(new Runnable() {`
  23. `@Override`
  24. `public void run() {`
  25. `try {`
  26. `Connection conn = ds.getConnection();`
  27. `Statement statement = conn.createStatement();`
  28. `ResultSet resultSet = null; `
  29. `#模拟慢sql`
  30. `resultSet = statement.executeQuery("select sleep(100),now()");`
  31. `while (resultSet.next()) {`
  32. `System.out.println("result+" + resultSet.getString(1));`
  33. `}`
  34. `resultSet.close();`
  35. `statement.close();`
  36. `conn.close();`
  37. `} catch (Exception ex) {`
  38. `System.out.println(ex.getMessage());`
  39. ``
  40. `}`
  41. `System.out.println(Thread.currentThread().getName() + "---------------------- end----------------------");`
  42. `}`
  43. `});`
  44. `t.setName(i + "");`
  45. `t.start();`
  46. `Thread.sleep((i + 1) * 1000);`
  47. `}`
  48. `System.out.println(Thread.currentThread().getName() + "---------------------- end----------------------");`
  49. `Thread.sleep(1000000);`
  50. `}`

通过运行上面代码，并没有像我们所期望那样，超过连接的最大限制1，通过RemoveAbandoned=true和RemoveAbandonedTimeout=1
应该已经触发了连接池的Abandoned机制，但是都阻塞到下面的一行代码，DelegatingStatement的close方法

  1. `/**`
  2. `* Close this DelegatingStatement, and close`
  3. `* any ResultSets that were not explicitly closed.`
  4. `*/`
  5. `public void close() throws SQLException {`
  6. `try {`
  7. `try {`
  8. `if (_conn != null) {`
  9. `_conn.removeTrace(this);`
  10. `_conn = null;`
  11. `}`
  12. ``
  13. `// The JDBC spec requires that a statment close any open`
  14. `// ResultSet's when it is closed.`
  15. `// FIXME The PreparedStatement we're wrapping should handle this for us.`
  16. `// See bug 17301 for what could happen when ResultSets are closed twice.`
  17. `List resultSets = getTrace();`
  18. `if( resultSets != null) {`
  19. `ResultSet[] set = (ResultSet[]) resultSets.toArray(new ResultSet[resultSets.size()]);`
  20. `for (int i = 0; i < set.length; i++) {`
  21. `set[i].close();`
  22. `}`
  23. `clearTrace();`
  24. `}`
  25. `//阻塞地方`
  26. `_stmt.close();`
  27. `}`
  28. `catch (SQLException e) {`
  29. `handleException(e);`
  30. `}`
  31. `}`
  32. `finally {`
  33. `_closed = true;`
  34. `}`
  35. `}`

当我们在url设置socketTimeout=1000，这时候阻塞的地方成功执行完成，超过数据库出现大量的连接数1，问题重现！同时出现典型的日志The
last packet successfully received from the server was 1,001 milliseconds ago.
The last packet sent successfully to the server was 1,001 milliseconds ago.  
![](https://image.3001.net/images/20230515/1684133684_6461d734c64be6277b8bf.png!small)  
当设置socketTimeout=1000，RemoveAbandoned=false ，并没有重现问题，且都是大量的等待连接超时  
![](https://image.3001.net/images/20230515/1684133685_6461d7358ecfff76802d0.png!small)  
原因是下面的代码差异，开启RemoveAbandoned，使用的是AbandonedObjectPool，而不开启是默认的GenericObjectPool，AbandonedObjectPool增加了Abandoned逻辑

  1. `*/`
  2. `protected void createConnectionPool() {`
  3. `// Create an object pool to contain our active connections`
  4. `GenericObjectPool gop;`
  5. `if ((abandonedConfig != null) && (abandonedConfig.getRemoveAbandoned())) {`
  6. `gop = new AbandonedObjectPool(null,abandonedConfig);`
  7. `}`
  8. `else {`
  9. `gop = new GenericObjectPool();`
  10. `}`
  11. `gop.setMaxActive(maxActive);`
  12. `gop.setMaxIdle(maxIdle);`
  13. `gop.setMinIdle(minIdle);`
  14. `gop.setMaxWait(maxWait);`
  15. `gop.setTestOnBorrow(testOnBorrow);`
  16. `gop.setTestOnReturn(testOnReturn);`
  17. `gop.setTimeBetweenEvictionRunsMillis(timeBetweenEvictionRunsMillis);`
  18. `gop.setNumTestsPerEvictionRun(numTestsPerEvictionRun);`
  19. `gop.setMinEvictableIdleTimeMillis(minEvictableIdleTimeMillis);`
  20. `gop.setTestWhileIdle(testWhileIdle);`
  21. `connectionPool = gop;`
  22. `}`

# 总结

当RemoveAbandoned=true， 且执行时间超过socketTimeout
，达到RemoveAbandonedTimeout的触发点时，就会导致数据库连接数超过连接池的限制，注意这种情况关闭模块是没用的，sql还在数据库中执行，应该直接kill或者切库操作！！

# 优化方案

1、关闭RemoveAbandoned设置，目前wms系统的还是AP和TP混合型，有很大的几率触发这种情况  
2、经过邱玉堃复核模块测试，需要关闭socketTimeout参数，引用的1.4.jar版本与源码的1.4版本存在差异  
3、 注意当mysql-connector-java 版本小于5.1.45就会出现这个bug


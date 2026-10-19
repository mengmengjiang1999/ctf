## ​1 前言

ElasticSearch是一个实时的分布式搜索与分析引擎，常用于大量非结构化数据的存储和快速检索场景，具有很强的扩展性。纵使其有诸多优点，在搜索领域远超关系型数据库，但依然存在与关系型数据库同样的深度分页问题，本文就此问题做一个实践性分析探讨

## 2 from + size分页方式

from +
size分页方式是ES最基本的分页方式，类似于关系型数据库中的limit方式。from参数表示：分页起始位置；size参数表示：每页获取数据条数。例如：

  

    
    
    GET /wms_order_sku/_search
    {
      "query": {
        "match_all": {}
      },
      "from": 10,
      "size": 20
    }
    
    

该条DSL语句表示从搜索结果中第10条数据位置开始，取之后的20条数据作为结果返回。这种分页方式在ES集群内部是如何执行的呢？

在ES中，搜索一般包括2个阶段，Query阶段和Fetch阶段，Query阶段主要确定要获取哪些doc，也就是返回所要获取doc的id集合，Fetch阶段主要通过id获取具体的doc。

### 2.1 Query阶段

![81dbfa3c-3bee-40f9-a44b-50d3e436807720220118150800.png](https://image.3001.net/images/20221114/1668415567_6372004f151e8b75682d4.png!small)

如上图所示，Query阶段大致分为3步：

  * 第一步：Client发送查询请求到Server端，Node1接收到请求然后创建一个大小为from + size的优先级队列用来存放结果，此时Node1被称为coordinating node（协调节点）；
  * 第二步：Node1将请求广播到涉及的shard上，每个shard内部执行搜索请求，然后将执行结果存到自己内部的大小同样为from+size的优先级队列里；
  * 第三步：每个shard将暂存的自身优先级队列里的结果返给Node1，Node1拿到所有shard返回的结果后，对结果进行一次合并，产生一个全局的优先级队列，存在Node1的优先级队列中。（如上图中，Node1会拿到(from + size) * 6 条数据，这些数据只包含doc的唯一标识_id和用于排序的_score，然后Node1会对这些数据合并排序，选择前from + size条数据存到优先级队列）；

### 2.2 Fetch阶段

![7085c081-0a9d-47f8-a8d5-6c5e753b4ce120220118150832.png](https://image.3001.net/images/20221114/1668415568_637200502cc065e412492.png!small)

如上图所示，当Query阶段结束后立马进入Fetch阶段，Fetch阶段也分为3步：

  * 第一步：Node1根据刚才合并后保存在优先级队列中的from+size条数据的id集合，发送请求到对应的shard上查询doc数据详情；
  * 第二步：各shard接收到查询请求后，查询到对应的数据详情并返回为Node1；（Node1中的优先级队列中保存了from + size条数据的_id，但是在Fetch阶段并不需要取回所有数据，只需要取回从from到from + size之间的size条数据详情即可，这size条数据可能在同一个shard也可能在不同的shard，因此Node1使用multi-get来提高性能）
  * 第三步：Node1获取到对应的分页数据后，返回给Client；

### 2.3 ES示例

依据上述我们对from + size分页方式两阶段的分析会发现，假如起始位置from或者页条数size特别大时，对于数据查询和coordinating
node结果合并都是巨大的性能损耗。

例如：索引 wms_order_sku 有1亿数据，分10个shard存储，当一个请求的from = 1000000， size =
10。在Query阶段，每个shard就需要返回1000010条数据的_id和_score信息，而coordinating node就需要接收10 *
1000010条数据，拿到这些数据后需要进行全局排序取到前1000010条数据的_id集合保存到coordinating
node的优先级队列中，后续在Fetch阶段再去获取那10条数据的详情返回给客户端。

分析：这个例子的执行过程中，在Query阶段会在每个shard上均有巨大的查询量，返回给coordinating
node时需要执行大量数据的排序操作，并且保存到优先级队列的数据量也很大，占用大量节点机器内存资源。

### 2.4 实现示例

![76093f8f-d35f-4588-9d88-f0668fe0d05c20220118150926.png](https://image.3001.net/images/20221114/1668415568_63720050ef60f61df0d1d.png!small)

  

    
    
    private SearchHits getSearchHits(BoolQueryBuilder queryParam, int from, int size, String orderField) {
            SearchRequestBuilder searchRequestBuilder = this.prepareSearch();
            searchRequestBuilder.setQuery(queryParam).setFrom(from).setSize(size).setExplain(false);
            if (StringUtils.isNotBlank(orderField)) {
                searchRequestBuilder.addSort(orderField, SortOrder.DESC);
            }
            log.info("getSearchHits searchBuilder:{}", searchRequestBuilder.toString());
            SearchResponse searchResponse = searchRequestBuilder.execute().actionGet();
            log.info("getSearchHits searchResponse:{}", searchResponse.toString());
            return searchResponse.getHits();
        }
    
    

### 2.5 小结

其实ES对结果窗口的返回数据有默认10000条的限制（参数：index.max_result_window = 10000），当from +
size的条数大于10000条时ES提示可以通过scroll方式进行分页，非常不建议调大结果窗口参数值。

![9e52797c-d636-45a0-8cb1-62bd18dc430620220118151216.png](https://image.3001.net/images/20221114/1668415569_63720051af18c73942c3f.png!small)

## 3 Scroll分页方式

scroll分页方式类似关系型数据库中的cursor（游标），首次查询时会生成并缓存快照，返回给客户端快照读取的位置参数（scroll_id），后续每次请求都会通过scroll_id访问快照实现快速查询需要的数据，有效降低查询和存储的性能损耗。

### 3.1 执行过程

scroll分页方式在Query阶段同样也是coordinating
node广播查询请求，获取、合并、排序其他shard返回的数据_id集合，不同的是scroll分页方式会将返回数据_id的集合生成快照保存到coordinating
node上。Fetch阶段以游标的方式从生成的快照中获取size条数据的_id，并去其他shard获取数据详情返回给客户端，同时将下一次游标开始的位置标识_scroll_id也返回。这样下次客户端发送获取下一页请求时带上scroll_id标识，coordinating
node会从scroll_id标记的位置获取接下来size条数据，同时再次返回新的游标位置标识scroll_id，这样依次类推直到取完所有数据。

### 3.2 ES示例

第一次查询时不需要传入_scroll_id，只要带上scroll的过期时间参数（scroll=1m）、每页大小（size）以及需要查询数据的自定义条件即可，查询后不仅会返回结果数据，还会返回_scroll_id。

  

    
    
    GET /wms_order_sku2021_10/_search?scroll=1m
    {
      "query": {
        "bool": {
          "must": [
            {
              "range": {
                "shipmentOrderCreateTime": {
                  "gte": "2021-10-04 00:00:00",
                  "lt": "2021-10-15 00:00:00"
                }
              }
            }
          ]
        }
      },
      "size": 20
    }
    
    

![1668415455_6371ffdf435660a2ca637.jpg!small](https://image.3001.net/images/20221114/1668415455_6371ffdf435660a2ca637.jpg!small)

第二次查询时不需要指定索引，在JSON请求体中带上前一个查询返回的scroll_id，同时传入scroll参数，指定刷新搜索结果的缓存时间（上一次查询缓存1分钟，本次查询会再次重置缓存时间为1分钟）

  

    
    
    GET /_search/scroll
    {
      "scroll":"1m",
      "scroll_id" : "DnF1ZXJ5VGhlbkZldGNoIAAAAAJFQdUKFllGc2E4Y2tEUjR5VkpKbkNtdDFMNFEAAAACJj74YxZmSWhNM2tVbFRiaU9VcVpDUWpKSGlnAAAAAiY--F4WZkloTTNrVWxUYmlPVXFaQ1FqSkhpZwAAAAJMQKhIFmw2c1hwVFk1UXppbDhZcW1za2ZzdlEAAAACRUHVCxZZRnNhOGNrRFI0eVZKSm5DbXQxTDRRAAAAAkxAqEcWbDZzWHBUWTVRemlsOFlxbXNrZnN2UQAAAAImPvhdFmZJaE0za1VsVGJpT1VxWkNRakpIaWcAAAACJ-MhBhZOMmYzWVVMbFIzNkdnN1FwVXVHaEd3AAAAAifjIQgWTjJmM1lVTGxSMzZHZzdRcFV1R2hHdwAAAAIn4yEHFk4yZjNZVUxsUjM2R2c3UXBVdUdoR3cAAAACJ5db8xZxeW5NRXpHOFR0eVNBOHlOcXBGbWdRAAAAAifjIQkWTjJmM1lVTGxSMzZHZzdRcFV1R2hHdwAAAAJFQdUMFllGc2E4Y2tEUjR5VkpKbkNtdDFMNFEAAAACJj74YhZmSWhNM2tVbFRiaU9VcVpDUWpKSGlnAAAAAieXW_YWcXluTUV6RzhUdHlTQTh5TnFwRm1nUQAAAAInl1v0FnF5bk1Fekc4VHR5U0E4eU5xcEZtZ1EAAAACJ5db9RZxeW5NRXpHOFR0eVNBOHlOcXBGbWdRAAAAAkVB1Q0WWUZzYThja0RSNHlWSkpuQ210MUw0UQAAAAImPvhfFmZJaE0za1VsVGJpT1VxWkNRakpIaWcAAAACJ-MhChZOMmYzWVVMbFIzNkdnN1FwVXVHaEd3AAAAAkVB1REWWUZzYThja0RSNHlWSkpuQ210MUw0UQAAAAImPvhgFmZJaE0za1VsVGJpT1VxWkNRakpIaWcAAAACTECoShZsNnNYcFRZNVF6aWw4WXFtc2tmc3ZRAAAAAiY--GEWZkloTTNrVWxUYmlPVXFaQ1FqSkhpZwAAAAJFQdUOFllGc2E4Y2tEUjR5VkpKbkNtdDFMNFEAAAACRUHVEBZZRnNhOGNrRFI0eVZKSm5DbXQxTDRRAAAAAiY--GQWZkloTTNrVWxUYmlPVXFaQ1FqSkhpZwAAAAJFQdUPFllGc2E4Y2tEUjR5VkpKbkNtdDFMNFEAAAACJj74ZRZmSWhNM2tVbFRiaU9VcVpDUWpKSGlnAAAAAkxAqEkWbDZzWHBUWTVRemlsOFlxbXNrZnN2UQAAAAInl1v3FnF5bk1Fekc4VHR5U0E4eU5xcEZtZ1EAAAACTECoRhZsNnNYcFRZNVF6aWw4WXFtc2tmc3ZR"
    }
    
    

![1668415467_6371ffeb2a33c8f594c62.jpg!small](https://image.3001.net/images/20221114/1668415467_6371ffeb2a33c8f594c62.jpg!small)

### 3.3 实现示例

![1668415477_6371fff5cf12d9ec8f0bc.jpg!small](https://image.3001.net/images/20221114/1668415477_6371fff5cf12d9ec8f0bc.jpg!small)

  

    
    
    protected <T> Page<T> searchPageByConditionWithScrollId(BoolQueryBuilder queryParam, Class<T> targetClass, Page<T> page) throws IllegalAccessException, InstantiationException, InvocationTargetException {
            SearchResponse scrollResp = null;
            String scrollId = ContextParameterHolder.get("scrollId");
            if (scrollId != null) {
                scrollResp = getTransportClient().prepareSearchScroll(scrollId).setScroll(new TimeValue(60000)).execute()
                        .actionGet();
            } else {
                logger.info("基于scroll的分页查询，scrollId为空");
                scrollResp = this.prepareSearch()
                        .setSearchType(SearchType.QUERY_AND_FETCH)
                        .setScroll(new TimeValue(60000))
                        .setQuery(queryParam)
                        .setSize(page.getPageSize()).execute().actionGet();
                ContextParameterHolder.set("scrollId", scrollResp.getScrollId());
            }
            SearchHit[] hits = scrollResp.getHits().getHits();
            List<T> list = new ArrayList<T>(hits.length);
            for (SearchHit hit : hits) {
                T instance = targetClass.newInstance();
                this.convertToBean(instance, hit);
                list.add(instance);
            }
            page.setTotalRow((int) scrollResp.getHits().getTotalHits());
            page.setResult(list);
            return page;
        }
    
    

![up-4294893c55903f3bbfaaeb54b4835b90ae6.png](https://image.3001.net/images/20221115/1668481262_637300eedec759659e956.png!small)

### 3.4 小结

scroll分页方式的优点就是减少了查询和排序的次数，避免性能损耗。缺点就是只能实现上一页、下一页的翻页功能，不兼容通过页码查询数据的跳页，同时由于其在搜索初始化阶段会生成快照，后续数据的变化无法及时体现在查询结果，因此更加适合一次性批量查询或非实时数据的分页查询。

启用游标查询时，需要注意设定期望的过期时间（scroll =
1m），以降低维持游标查询窗口所需消耗的资源。注意这个过期时间每次查询都会重置刷新为1分钟，表示游标的闲置失效时间（第二次以后的查询必须带scroll =
1m参数才能实现）

## 4 Search After分页方式

Search After分页方式是ES
5新增的一种分页查询方式，其实现的思路同Scroll分页方式基本一致，通过记录上一次分页的位置标识，来进行下一次分页数据的查询。相比于Scroll分页方式，它的优点是可以实时体现数据的变化，解决了查询快照导致的查询结果延迟问题。

### 4.1 执行过程

Search After方式也不支持跳页功能，每次查询一页数据。第一次每个shard返回一页数据（size条），coordinating node一共获取到
shard数 * size条数据 ， 接下来coordinating
node在内存中进行排序，取出前size条数据作为第一页搜索结果返回。当拉取第二页时，不同于Scroll分页方式，Search
After方式会找到第一页数据被拉取的最大值，作为第二页数据拉取的查询条件。

这样每个shard还是返回一页数据（size条），coordinating node获取到 shard数 *
size条数据进行内存排序，取得前size条数据作为全局的第二页搜索结果。  
后续分页查询以此类推…

### 4.2 ES示例

第一次查询只传入排序字段和每页大小size

    
    
    GET /wms_order_sku2021_10/_search
    {
      "query": {
        "bool": {
          "must": [
            {
              "range": {
                "shipmentOrderCreateTime": {
                  "gte": "2021-10-12 00:00:00",
                  "lt": "2021-10-15 00:00:00"
                }
              }
            }
          ]
        }
      },
      "size": 20,
      "sort": [
        {
          "_id": {
            "order": "desc"
          }
        },{
          "shipmentOrderCreateTime":{
            "order": "desc"
          }
        }
      ]
    }
    
    

![1668415546_6372003a4b1cb6eaf70a3.jpg!small](https://image.3001.net/images/20221114/1668415546_6372003a4b1cb6eaf70a3.jpg!small)

接下来每次查询时都带上本次查询的最后一条数据的 _id 和 shipmentOrderCreateTime字段，循环往复就能够实现不断下一页的功能

    
    
    GET /wms_order_sku2021_10/_search
    {
      "query": {
        "bool": {
          "must": [
            {
              "range": {
                "shipmentOrderCreateTime": {
                  "gte": "2021-10-12 00:00:00",
                  "lt": "2021-10-15 00:00:00"
                }
              }
            }
          ]
        }
      },
      "size": 20,
      "sort": [
        {
          "_id": {
            "order": "desc"
          }
        },{
          "shipmentOrderCreateTime":{
            "order": "desc"
          }
        }
      ],
      "search_after": ["SO-460_152-1447931043809128448-100017918838",1634077436000]
    }
    
    

### 4.3 实现示例

![1668415533_6372002d62c2ddd206caf.jpg!small](https://image.3001.net/images/20221114/1668415533_6372002d62c2ddd206caf.jpg!small)

    
    
    public <T> ScrollDto<T> queryScrollDtoByParamWithSearchAfter(
                BoolQueryBuilder queryParam, Class<T> targetClass, int pageSize, String afterId,
                List<FieldSortBuilder> fieldSortBuilders) {
            SearchResponse scrollResp;
            long now = System.currentTimeMillis();
            SearchRequestBuilder builder = this.prepareSearch();
            if (CollectionUtils.isNotEmpty(fieldSortBuilders)) {
                fieldSortBuilders.forEach(builder::addSort);
            }
            builder.addSort("_id", SortOrder.DESC);
            if (StringUtils.isBlank(afterId)) {
                log.info("queryScrollDtoByParamWithSearchAfter基于afterId的分页查询，afterId为空");
                SearchRequestBuilder searchRequestBuilder = builder.setSearchType(SearchType.DFS_QUERY_THEN_FETCH)
                        .setQuery(queryParam).setSize(pageSize);
                scrollResp = searchRequestBuilder.execute()
                        .actionGet();
                log.info("queryScrollDtoByParamWithSearchAfter基于afterId的分页查询,afterId 为空，searchRequestBuilder:{}", searchRequestBuilder);
            } else {
                log.info("queryScrollDtoByParamWithSearchAfter基于afterId的分页查询，afterId=" + afterId);
                Object[] afterIds = JSON.parseObject(afterId, Object[].class);
                SearchRequestBuilder searchRequestBuilder = builder.setSearchType(SearchType.DFS_QUERY_THEN_FETCH)
                        .setQuery(queryParam).searchAfter(afterIds).setSize(pageSize);
                log.info("queryScrollDtoByParamWithSearchAfter基于afterId的分页查询，searchRequestBuilder:{}", searchRequestBuilder);
                scrollResp = searchRequestBuilder.execute()
                        .actionGet();
            }
            SearchHit[] hits = scrollResp.getHits().getHits();
            log.info("queryScrollDtoByParamWithSearchAfter基于afterId的分页查询，totalRow={}, size={}, use time:{}", scrollResp.getHits().getTotalHits(), hits.length, System.currentTimeMillis() - now);
            now = System.currentTimeMillis();
    
            List<T> list = new ArrayList<>();
            if (ArrayUtils.getLength(hits) > 0) {
                list = Arrays.stream(hits)
                        .filter(Objects::nonNull)
                        .map(SearchHit::getSourceAsMap)
                        .filter(Objects::nonNull)
                        .map(JSON::toJSONString)
                        .map(e -> JSON.parseObject(e, targetClass))
                        .collect(Collectors.toList());
                afterId = JSON.toJSONString(hits[hits.length - 1].getSortValues());
            }
            log.info("es数据转换bean，totalRow={}, size={}, use time:{}", scrollResp.getHits().getTotalHits(), hits.length, System.currentTimeMillis() - now);
            return ScrollDto.<T>builder().scrollId(afterId).result(list).totalRow((int) scrollResp.getHits().getTotalHits()).build();
        }
    
    

### 4.4 小结

Search After分页方式采用记录作为游标，因此Search
After要求doc中至少有一条全局唯一变量（示例中使用_id和时间戳，实际上_id已经是全局唯一）。Search
After方式是无状态的分页查询，因此数据的变更能够及时的反映在查询结果中，避免了Scroll分页方式无法获取最新数据变更的缺点。同时Search
After不用维护scroll_id和快照，因此也节约大量资源。

## 5 总结思考

### 5.1 ES三种分页方式对比总结

![1668415564_6372004c4163885e6207a.jpg!small](https://image.3001.net/images/20221114/1668415564_6372004c4163885e6207a.jpg!small)

  * 如果数据量小（from+size在10000条内），或者只关注结果集的TopN数据，可以使用from/size 分页，简单粗暴
  * 数据量大，深度翻页，后台批处理任务（数据迁移）之类的任务，使用 scroll 方式
  * 数据量大，深度翻页，用户实时、高并发查询需求，使用 search after 方式

### 5.2 个人思考

  * 在一般业务查询页面中，大多情况都是10-20条数据为一页，10000条数据也就是500-1000页。正常情况下，对于用户来说，有极少需求翻到比较靠后的页码来查看数据，更多的是通过查询条件框定一部分数据查看其详情。因此在业务需求敲定初期，可以同业务人员商定1w条数据的限定，超过1w条的情况可以借助导出数据到Excel表，在Excel表中做具体的操作。
  * 如果给导出中心返回大量数据的场景可以使用Scroll或Search After分页方式，相比之下最好使用Search After方式，既可以保证数据的实时性，也具有很高的搜索性能。
  * 总之，在使用ES时一定要避免深度分页问题，要在跳页功能实现和ES性能、资源之间做一个取舍。必要时也可以调大max_result_window参数，原则上不建议这么做，因为1w条以内ES基本能保持很不错的性能，超过这个范围深度分页相当耗时、耗资源，因此谨慎选择此方式。

* * *

作者：何守优


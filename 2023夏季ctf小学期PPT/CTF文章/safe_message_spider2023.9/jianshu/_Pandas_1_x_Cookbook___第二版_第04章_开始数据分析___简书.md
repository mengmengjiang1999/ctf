《Pandas 1.x Cookbook · 第二版》第04章 开始数据分析

[ SeanCheney](https://www.jianshu.com/u/130f76596b02)关注赞赏支持

# 《Pandas 1.x Cookbook · 第二版》第04章 开始数据分析

[第01章 Pandas基础](https://www.jianshu.com/p/9115de83bb88)  
[第02章 DataFrame基础运算](https://www.jianshu.com/p/5edda52d122f)  
[第03章 创建和持久化DataFrame](https://www.jianshu.com/p/5edda52d122f)  
第04章 开始数据分析  
[第05章 探索性数据分析](https://www.jianshu.com/p/e1006dda4b8d)  
[第06章 选取数据子集](https://www.jianshu.com/p/1ee9787c3712)  
[第07章 过滤行](https://www.jianshu.com/p/b0b159f3cf1c)  
[第08章 索引对齐](https://www.jianshu.com/p/509414c2e0be)

* * *

# 4.1 数据分析流程

探索性数据分析，Exploratory Data Analysis (EDA) ，通常不包括创建模型，但包括总结数据集的特征和可视化。

读取数据，使用`.sample`方法查看数据：

    
    
    >>> import pandas as pd
    >>> import numpy as np
    >>> college = pd.read_csv("data/college.csv")
    >>> college.sample(random_state=42)
               INSTNM         CITY  ... MD_EARN_WNE_P10  GRAD_DEBT_MDN_SUPP
    3649  Career P...  San Antonio  ...        20700           14977
    

查看数据集的维度：

    
    
    >>> college.shape
    (7535, 27)
    

用`.info`方法，查看每列的数据类型，非空值的数量，内存占用：

    
    
    >>> college.info()
    <class 'pandas.core.frame.DataFrame'>
    RangeIndex: 7535 entries, 0 to 7534
    Data columns (total 27 columns):
     #   Column              Non-Null Count  Dtype
    ---  ------              --------------  -----
     0   INSTNM              7535 non-null   object
     1   CITY                7535 non-null   object
     2   STABBR              7535 non-null   object
     3   HBCU                7164 non-null   float64
     4   MENONLY             7164 non-null   float64
     5   WOMENONLY           7164 non-null   float64
     6   RELAFFIL            7535 non-null   int64
     7   SATVRMID            1185 non-null   float64
     8   SATMTMID            1196 non-null   float64
     9   DISTANCEONLY        7164 non-null   float64
     10  UGDS                6874 non-null   float64
     11  UGDS_WHITE          6874 non-null   float64
     12  UGDS_BLACK          6874 non-null   float64
     13  UGDS_HISP           6874 non-null   float64
     14  UGDS_ASIAN          6874 non-null   float64
     15  UGDS_AIAN           6874 non-null   float64
     16  UGDS_NHPI           6874 non-null   float64
     17  UGDS_2MOR           6874 non-null   float64
     18  UGDS_NRA            6874 non-null   float64
     19  UGDS_UNKN           6874 non-null   float64
     20  PPTUG_EF            6853 non-null   float64
     21  CURROPER            7535 non-null   int64
     22  PCTPELL             6849 non-null   float64
     23  PCTFLOAN            6849 non-null   float64
     24  UG25ABV             6718 non-null   float64
     25  MD_EARN_WNE_P10     6413 non-null   object
     26  GRAD_DEBT_MDN_SUPP  7503 non-null   object
    dtypes: float64(20), int64(2), object(5)
    memory usage: 1.6+ MB
    

查看数值列的情况，转置以读取更多输出：

    
    
    >>> college.describe(include=[np.number]).T
                count        mean  ...         75%    max
    HBCU       7164.0    0.014238  ...    0.000000    1.0
    MENONLY    7164.0    0.009213  ...    0.000000    1.0
    WOMENONLY  7164.0    0.005304  ...    0.000000    1.0
    RELAFFIL   7535.0    0.190975  ...    0.000000    1.0
    SATVRMID   1185.0  522.819409  ...  555.000000  765.0
    ...           ...         ...  ...         ...    ...
    PPTUG_EF   6853.0    0.226639  ...    0.376900    1.0
    CURROPER   7535.0    0.923291  ...    1.000000    1.0
    PCTPELL    6849.0    0.530643  ...    0.712900    1.0
    PCTFLOAN   6849.0    0.522211  ...    0.745000    1.0
    UG25ABV    6718.0    0.410021  ...    0.572275    1.0
    

查看对象（字符串）列的情况：

    
    
    >>> college.describe(include=[np.object]).T
                 count unique          top  freq
    INSTNM        7535   7535  Academy ...     1
    CITY          7535   2514     New York    87
    STABBR        7535     59           CA   773
    MD_EARN_W...  6413    598  PrivacyS...   822
    GRAD_DEBT...  7503   2038  PrivacyS...  1510
    

#### 更多

在`.describe`方法中指定分位数：

    
    
    >>> college.describe(
    >>>     include=[np.number],
    ...     percentiles=[
    ...         0.01,
    ...         0.05,
    ...         0.10,
    ...         0.25,
    ...         0.5,
    ...         0.75,
    ...         0.9,
    ...         0.95,
    ...         0.99,
    ...     ],
    ... ).T
                count        mean  ...         99%    max
    HBCU       7164.0    0.014238  ...    1.000000    1.0
    MENONLY    7164.0    0.009213  ...    0.000000    1.0
    WOMENONLY  7164.0    0.005304  ...    0.000000    1.0
    RELAFFIL   7535.0    0.190975  ...    1.000000    1.0
    SATVRMID   1185.0  522.819409  ...  730.000000  765.0
    ...           ...         ...  ...         ...    ...
    PPTUG_EF   6853.0    0.226639  ...    0.946724    1.0
    CURROPER   7535.0    0.923291  ...    1.000000    1.0
    PCTPELL    6849.0    0.530643  ...    0.993908    1.0
    PCTFLOAN   6849.0    0.522211  ...    0.986368    1.0
    UG25ABV    6718.0    0.410021  ...    0.917383    1.0
    

* * *

# 4.2 数据字典

数据字典是个包含元数据和注释的表格，它的主要目的是解释列名。

`college_data_dictionary.csv`中包含了大学数据集的数据字典：

    
    
    >>> pd.read_csv("data/college_data_dictionary.csv")
        column_name  description
    0        INSTNM  Institut...
    1          CITY  City Loc...
    2        STABBR  State Ab...
    3          HBCU  Historic...
    4       MENONLY  0/1 Men ...
    ..          ...          ...
    22      PCTPELL  Percent ...
    23     PCTFLOAN  Percent ...
    24      UG25ABV  Percent ...
    25  MD_EARN_...  Median E...
    26  GRAD_DEB...  Median d...
    

* * *

# 4.3 通过改变数据类型降低内存

选取一些数据类型不同的列，以便观察内存占用：

    
    
    >>> college = pd.read_csv("data/college.csv")
    >>> different_cols = [
    ...     "RELAFFIL",
    ...     "SATMTMID",
    ...     "CURROPER",
    ...     "INSTNM",
    ...     "STABBR",
    ... ]
    >>> col2 = college.loc[:, different_cols]
    >>> col2.head()
       RELAFFIL  SATMTMID  ...       INSTNM STABBR
    0         0     420.0  ...  Alabama ...     AL
    1         0     565.0  ...  Universi...     AL
    2         1       NaN  ...  Amridge ...     AL
    3         0     590.0  ...  Universi...     AL
    4         0     430.0  ...  Alabama ...     AL
    

检查每列的数据类型：

    
    
    >>> col2.dtypes
    RELAFFIL      int64
    SATMTMID    float64
    CURROPER      int64
    INSTNM       object
    STABBR       object
    dtype: object
    

检查每列占用了多少内存：

    
    
    >>> original_mem = col2.memory_usage(deep=True)
    >>> original_mem
    Index          128
    RELAFFIL     60280
    SATMTMID     60280
    CURROPER     60280
    INSTNM      660240
    STABBR      444565
    dtype: int64
    

列`RELAFFIL`没有必要使用64位，使用`.astype`方法将其转换为8位：

    
    
    >>> col2["RELAFFIL"] = col2["RELAFFIL"].astype(np.int8)
    

再次检查数据类型：

    
    
    >>> col2.dtypes
    RELAFFIL       int8
    SATMTMID    float64
    CURROPER      int64
    INSTNM       object
    STABBR       object
    dtype: object 
    

再次检查内存占用，可以看到`RELAFFIL`一列的内存大大降低：

    
    
    >>> col2.memory_usage(deep=True)
    Index          128
    RELAFFIL      7535
    SATMTMID     60280
    CURROPER     60280
    INSTNM      660240
    STABBR      444565
    dtype: int64
    

要节省更多内存，如果基数（基数是唯一值的数量）低的话，可以将object数据改为category：

    
    
    >>> col2.select_dtypes(include=["object"]).nunique()
    INSTNM    7535
    STABBR      59
    dtype: int64
    

`STABBR`列的基数低，不到原始数据的百分之一，可以将其做转换：

    
    
    >>> col2["STABBR"] = col2["STABBR"].astype("category")
    >>> col2.dtypes
    RELAFFIL        int8
    SATMTMID     float64
    CURROPER       int64
    INSTNM        object
    STABBR      category
    dtype: object
    

再次查看内存占用：

    
    
    >>> new_mem = col2.memory_usage(deep=True)
    >>> new_mem
    Index          128
    RELAFFIL      7535
    SATMTMID     60280
    CURROPER     60280
    INSTNM      660699
    STABBR       13576
    dtype: int64   
    

最后，比较内存优化前后的比例：

    
    
    >>> new_mem / original_mem
    Index       1.000000
    RELAFFIL    0.125000
    SATMTMID    1.000000
    CURROPER    1.000000
    INSTNM      1.000695
    STABBR      0.030538
    dtype: float64
    

#### 更多

改变列中的一个值，可以观察内存的变化：

    
    
    >>> college.loc[0, "CURROPER"] = 10000000
    >>> college.loc[0, "INSTNM"] = (
    ...     college.loc[0, "INSTNM"] + "a"
    ... )
    >>> college[["CURROPER", "INSTNM"]].memory_usage(deep=True)
    Index           80
    CURROPER     60280
    INSTNM      660804
    dtype: int64
    

如果整数列中的一个值变为缺失值，则该列会强制变为浮点类型：

    
    
    >>> college["MENONLY"].dtype
    dtype('float64')
    >>> college["MENONLY"].astype(np.int8)
    Traceback (most recent call last):
      ...
    ValueError: Cannot convert non-finite values (NA or inf) to integer
    

下面的四种方法的效果相同：

    
    
    college.describe(include=['int64', 'float64']).T
    college.describe(include=[np.int64, np.float64]).T
    college.describe(include=['int', 'float']).T
    college.describe(include=['number']).T
    

数据类型字符串还可以用在`.astype`方法中：

    
    
    >>> college.assign(
    ...     MENONLY=college["MENONLY"].astype("float16"),
    ...     RELAFFIL=college["RELAFFIL"].astype("int8"),
    ... )
               INSTNM         CITY  ... MD_EARN_WNE_P10  GRAD_DEBT_MDN_SUPP
    0     Alabama ...       Normal  ...        30300           33888       
    1     Universi...   Birmingham  ...        39700         21941.5       
    2     Amridge ...   Montgomery  ...        40100           23370       
    3     Universi...   Huntsville  ...        45500           24097       
    4     Alabama ...   Montgomery  ...        26600         33118.5       
    ...           ...          ...  ...          ...             ...       
    7530  SAE Inst...   Emeryville  ...          NaN            9500       
    7531  Rasmusse...  Overland...  ...          NaN           21163       
    7532  National...  Highland...  ...          NaN            6333       
    7533  Bay Area...     San Jose  ...          NaN     PrivacyS...       
    7534  Excel Le...  San Antonio  ...          NaN           12125
    

查看`RangeIndex`和`Int64Index`两种索引类型的内存占用：

    
    
    >>> college.index = pd.Int64Index(college.index)
    >>> college.index.memory_usage()  # 原先是80
    60280
    

* * *

# 4.4 选择最大值中最小值

使用`.nlargest`和`.nsmallest`从排名前100的电影中，选择成本最低的5个电影：

    
    
    >>> movie = pd.read_csv("data/movie.csv")
    >>> movie2 = movie[["movie_title", "imdb_score", "budget"]]
    >>> movie2.head()
       movie_title  imdb_score       budget
    0       Avatar         7.9  237000000.0
    1  Pirates ...         7.1  300000000.0
    2      Spectre         6.8  245000000.0
    3  The Dark...         8.5  250000000.0
    4  Star War...         7.1          NaN
    

选择`imdb_score`得分前100的电影：

    
    
    >>> movie2.nlargest(100, "imdb_score").head()
          movie_title  imdb_score      budget
                       movie_title  imdb_score      budget
    2725          Towering Inferno         9.5         NaN
    1920  The Shawshank Redemption         9.3  25000000.0
    3402             The Godfather         9.2   6000000.0
    2779                   Dekalog         9.1         NaN
    4312      Kickboxer: Vengeance         9.1  17000000.0
    

选择前百名电影中，成本最低的5个电影：

    
    
    >>> (
    ...     movie2.nlargest(100, "imdb_score").nsmallest(
    ...         5, "budget"
    ...     )
    ... )
                   movie_title  imdb_score    budget
    4804        Butterfly Girl         8.7  180000.0
    4801    Children of Heaven         8.5  180000.0
    4706          12 Angry Men         8.9  350000.0
    4550          A Separation         8.4  500000.0
    4636  The Other Dream Team         8.4  500000.0
    

* * *

# 4.5 使用排序选择每组中最大值

在本节中，我们尝试找到每年评分最高的电影。

读取电影数据集，只保留其中的三个列：`movie_title`、`title_year`、`imdb_score`：

    
    
    >>> movie = pd.read_csv("data/movie.csv")
    >>> movie[["movie_title", "title_year", "imdb_score"]]
                                         movie_title  ...
    0                                         Avatar  ...
    1       Pirates of the Caribbean: At World's End  ...
    2                                        Spectre  ...
    3                          The Dark Knight Rises  ...
    4     Star Wars: Episode VII - The Force Awakens  ...
    ...                                          ...  ...
    4911                     Signed Sealed Delivered  ...
    4912                               The Following  ...
    4913                        A Plague So Pleasant  ...
    4914                            Shanghai Calling  ...
    4915                           My Date with Drew  ...
    

按照`title_year`进行从小到大排列：

    
    
    >>> (
    ...     movie[
    ...         ["movie_title", "title_year", "imdb_score"]
    ...     ].sort_values("title_year", ascending=True)
    ... )
                                               movie_title  ...
    4695  Intolerance: Love's Struggle Throughout the Ages  ...
    4833                    Over the Hill to the Poorhouse  ...
    4767                                    The Big Parade  ...
    2694                                        Metropolis  ...
    4697                               The Broadway Melody  ...
    ...                                                ...  ...
    4683                                            Heroes  ...
    4688                                       Home Movies  ...
    4704                                        Revolution  ...
    4752                                      Happy Valley  ...
    4912                                     The Following  ...
    

同时对两列进行排列：

    
    
    >>> (
    ...     movie[
    ...          ["movie_title", "title_year", "imdb_score"]
    ...     ].sort_values(
    ...         ["title_year", "imdb_score"], ascending=False
    ...     )
    ... )
                          movie_title  title_year  imdb_score
    4312         Kickboxer: Vengeance      2016.0         9.1
    4277  A Beginner's Guide to Snuff      2016.0         8.7
    3798                      Airlift      2016.0         8.5
    27     Captain America: Civil War      2016.0         8.2
    98            Godzilla Resurgence      2016.0         8.2
    ...                           ...         ...         ...
    1391                    Rush Hour         NaN         5.8
    4031                     Creature         NaN         5.0
    2165              Meet the Browns         NaN         3.5
    3246   The Bold and the Beautiful         NaN         3.5
    2119                 The Bachelor         NaN         2.9
    

使用`.drop_duplicates`方法，只保留每年的第一行数据：

    
    
    >>> (
    ...     movie[["movie_title", "title_year", "imdb_score"]]
    ...     .sort_values(
    ...         ["title_year", "imdb_score"], ascending=False
    ...     )
    ...     .drop_duplicates(subset="title_year")
    ... )
          movie_title  title_year  imdb_score
    4312  Kickboxe...      2016.0         9.1
    3745  Running ...      2015.0         8.6
    4369  Queen of...      2014.0         8.7
    3935  Batman: ...      2013.0         8.4
    3     The Dark...      2012.0         8.5
    ...           ...         ...         ...
    2694   Metropolis      1927.0         8.3
    4767  The Big ...      1925.0         8.3
    4833  Over the...      1920.0         4.8
    4695  Intolera...      1916.0         8.0
    2725  Towering...         NaN         9.5
    

#### 更多

还可以使用`.groupby`方法，实现同样的目标：

    
    
    >>> (
    ...     movie[["movie_title", "title_year", "imdb_score"]]
    ...     .groupby("title_year", as_index=False)
    ...     .apply(
    ...         lambda df:df.sort_values(
    ...             "imdb_score", ascending=False
    ...         ).head(1)
    ...     )
    ...     .droplevel(0)
    ...     .sort_values("title_year", ascending=False)
    ... )
             movie_title  title_year  imdb_score
    90 4312  Kickboxe...      2016.0         9.1
    89 3745  Running ...      2015.0         8.6
    88 4369  Queen of...      2014.0         8.7
    87 3935  Batman: ...      2013.0         8.4
    86 3     The Dark...      2012.0         8.5
    ...              ...         ...         ...
    4  4555  Pandora'...      1929.0         8.0
    3  2694   Metropolis      1927.0         8.3
    2  4767  The Big ...      1925.0         8.3
    1  4833  Over the...      1920.0         4.8
    0  4695  Intolera...      1916.0         8.0
    

参数`ascending`可以传入一组布尔值，对列分别进行排列：

    
    
    >>> (
    ...     movie[
    ...         [
    ...             "movie_title",
    ...             "title_year",
    ...             "content_rating",
    ...             "budget",
    ...         ]
    ...     ]
    ...     .sort_values(
    ...         ["title_year", "content_rating", "budget"],
    ...         ascending=[False, False, True],
    ...     )
    ...     .drop_duplicates(
    ...         subset=["title_year", "content_rating"]
    ...     )
    ... )
          movie_title  title_year content_rating      budget
    4026    Compadres      2016.0            R     3000000.0
    4658  Fight to...      2016.0        PG-13      150000.0
    4661   Rodeo Girl      2016.0           PG      500000.0
    3252  The Wailing      2016.0    Not Rated           NaN
    4659  Alleluia...      2016.0          NaN      500000.0
    ...           ...         ...          ...           ...
    2558   Lilyhammer         NaN        TV-MA    34000000.0
    807   Sabrina,...         NaN         TV-G     3000000.0
    848   Stargate...         NaN        TV-14     1400000.0
    2436       Carlos         NaN    Not Rated           NaN
    2119  The Bach...         NaN          NaN     3000000.0
    

* * *

# 4.6 使用`sort_values`复制n个最大值

使用`nlargest`和`. nsmallest`实现4.5中同样的目标：

    
    
    >>> movie = pd.read_csv("data/movie.csv")
    >>> (
    ...     movie[["movie_title", "imdb_score", "budget"]]
    ...     .nlargest(100, "imdb_score")
    ...     .nsmallest(5, "budget")
    ... )
                   movie_title  imdb_score    budget
    4804        Butterfly Girl         8.7  180000.0
    4801    Children of Heaven         8.5  180000.0
    4706          12 Angry Men         8.9  350000.0
    4550          A Separation         8.4  500000.0
    4636  The Other Dream Team         8.4  500000.0
    

使用`.sort_values`实现提取`imdb_score`最高的100部电影：

    
    
    >>> (
    ...     movie[["movie_title", "imdb_score", "budget"]]
    ...     .sort_values("imdb_score", ascending=False)
    ...     .head(100)
    ... )
          movie_title  imdb_score      budget
    2725  Towering...         9.5         NaN
    1920  The Shaw...         9.3  25000000.0
    3402  The Godf...         9.2   6000000.0
    2779      Dekalog         9.1         NaN
    4312  Kickboxe...         9.1  17000000.0
    ...           ...         ...         ...
    3799  Anne of ...         8.4         NaN
    3777  Requiem ...         8.4   4500000.0
    3935  Batman: ...         8.4   3500000.0
    4636  The Othe...         8.4    500000.0
    2455       Aliens         8.4  18500000.0
    

紧接着上一步操作，提取其中成本最低的5部电影：

    
    
    >>> (
    ...     movie[["movie_title", "imdb_score", "budget"]]
    ...     .sort_values("imdb_score", ascending=False)
    ...     .head(100)
    ...     .sort_values("budget")
    ...     .head(5)
    ... )
                        movie_title  imdb_score    budget
    4815  A Charlie Brown Christmas         8.4  150000.0
    4801         Children of Heaven         8.5  180000.0
    4804             Butterfly Girl         8.7  180000.0
    4706               12 Angry Men         8.9  350000.0
    4636       The Other Dream Team         8.4  500000.0
    

#### 更多

因为8.4分的电影比较多，`.nlargest`和`.sort_values`略有不同，导致得分前百的电影的DataFrame并不相同。如果在`.sort_values`中传入`kind='mergsort'`，两者的结果就相同了。

    
    
    >>> (
    ...     movie[["movie_title", "imdb_score", "budget"]]
    ...     .nlargest(100, "imdb_score")
    ...     .tail()
    ... )
                    movie_title  imdb_score     budget
    4023                 Oldboy         8.4  3000000.0
    4163  To Kill a Mockingbird         8.4  2000000.0
    4395         Reservoir Dogs         8.4  1200000.0
    4550           A Separation         8.4   500000.0
    4636   The Other Dream Team         8.4   500000.0
    >>> (
    ...     movie[["movie_title", "imdb_score", "budget"]]
    ...     .sort_values("imdb_score", ascending=False)
    ...     .head(100)
    ...     .tail()
    ... )
          movie_title  imdb_score      budget
    3799  Anne of ...         8.4         NaN
    3777  Requiem ...         8.4   4500000.0
    3935  Batman: ...         8.4   3500000.0
    4636  The Othe...         8.4    500000.0
    2455       Aliens         8.4  18500000.0
    

* * *

# 4.7 计算跟踪止损单

止损单是股票交易中常用的术语。如果用100美元每股购买了股票，如果是90%止损，则止损单的价格是90美元。

如果股票涨到了120美元，则止损单价格变为了108美元。如果股票降到了110美元，止损单价格仍然是108美元。只有股票上涨时，止损单价格才上涨。

本节需要安装第三方库`pandas-datareader`，使用`conda install pandas-datareader`或`pip install
pandas-datareader`进行安装。可能还需要安装`requests_cache`。

这里使用的的是特斯拉的股票（TSLA），假设在2017开盘日购买了股票：

    
    
    >>> import datetime
    >>> import pandas_datareader.data as web
    >>> import requests_cache
    >>> session = requests_cache.CachedSession(
    ...     cache_name="cache",
    ...     backend="sqlite",
    ...     expire_after=datetime.timedelta(days=90),
    ... )
    >>> tsla = web.DataReader(
    ...     "tsla",
    ...     data_source="yahoo",
    ...     start="2017-1-1",
    ...     session=session,
    ... )
    >>> tsla.head(8)
                      High         Low  ...    Volume   Adj Close
    Date                                ...
    2017-01-03  220.330002  210.960007  ...   5923300  216.990005
    2017-01-04  228.000000  214.309998  ...  11213500  226.990005
    2017-01-05  227.479996  221.949997  ...   5911700  226.750000
    2017-01-06  230.309998  225.449997  ...   5527900  229.009995
    2017-01-09  231.919998  228.000000  ...   3979500  231.279999
    2017-01-10  232.000000  226.889999  ...   3660000  229.869995
    2017-01-11  229.979996  226.679993  ...   3650800  229.729996
    2017-01-12  230.699997  225.580002  ...   3790200  229.589996
    

简单起见，使用的是每个交易日的收盘价：

    
    
    >>> tsla_close = tsla["Close"]
    

使用`.cummax`方法跟踪最高收盘价：

    
    
    >>> tsla_cummax = tsla_close.cummax()
    >>> tsla_cummax.head()
    Date
    2017-01-03    216.990005
    2017-01-04    226.990005
    2017-01-05    226.990005
    2017-01-06    229.009995
    2017-01-09    231.279999
    Name: Close, dtype: float64
    

乘以0.9就能得到止损单价格了：

    
    
    >>> (tsla["Close"].cummax().mul(0.9).head())
    Date
    2017-01-03    195.291005
    2017-01-04    204.291005
    2017-01-05    204.291005
    2017-01-06    206.108995
    2017-01-09    208.151999
    Name: Close, dtype: float64
    

#### 更多

和`cummax`相对，`.cummin`可以追踪最低值：

    
    
    weight.cummin() * 1.05
    

* * *

[第01章 Pandas基础](https://www.jianshu.com/p/9115de83bb88)  
[第02章 DataFrame基础运算](https://www.jianshu.com/p/5edda52d122f)  
[第03章 创建和持久化DataFrame](https://www.jianshu.com/p/5edda52d122f)  
第04章 开始数据分析  
[第05章 探索性数据分析](https://www.jianshu.com/p/e1006dda4b8d)  
[第06章 选取数据子集](https://www.jianshu.com/p/1ee9787c3712)  
[第07章 过滤行](https://www.jianshu.com/p/b0b159f3cf1c)  
[第08章 索引对齐](https://www.jianshu.com/p/509414c2e0be)

### 推荐阅读[更多精彩内容 __](https://www.jianshu.com/)

  * [《Pandas 1.x Cookbook · 第二版》Pandas 数据分析宝典第二版](https://www.jianshu.com/p/62524f4c240e)

《Pandas 1.x Cookbook》这本书一年前就出版了，关注的人不算多，但评价很高，而我也很喜欢Cookb...

[SeanCheney](https://www.jianshu.com/u/130f76596b02)阅读 3,217评论 0赞 10

  * [《Pandas 1.x Cookbook · 第二版》第03章 创建和持久化DataFrame](https://www.jianshu.com/p/5edda52d122f)

第01章 Pandas基础[https://www.jianshu.com/p/9115de83bb88]第02章...

[SeanCheney](https://www.jianshu.com/u/130f76596b02)阅读 1,409评论 0赞 7

  * [《Pandas Cookbook》第03章 数据分析入门](https://www.jianshu.com/p/05cb76788c80)

第01章 Pandas基础第02章 DataFrame运算第03章 数据分析入门第04章 选取数据子集第05章 布...

[SeanCheney](https://www.jianshu.com/u/130f76596b02)阅读 5,011评论 3赞 23

  * [《Pandas 1.x Cookbook · 第二版》第02章 DataFrame基础运算](https://www.jianshu.com/p/914e4a05799a)

第01章 Pandas基础[https://www.jianshu.com/p/9115de83bb88]第02章...

[SeanCheney](https://www.jianshu.com/u/130f76596b02)阅读 1,211评论 0赞 3

  * [《Pandas 1.x Cookbook · 第二版》第01章 Pandas基础](https://www.jianshu.com/p/9115de83bb88)

第01章 Pandas基础第02章 DataFrame基础运算[https://www.jianshu.com/p...

[SeanCheney](https://www.jianshu.com/u/130f76596b02)阅读 4,297评论 0赞 17

 
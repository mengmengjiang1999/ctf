《Pandas 1.x Cookbook · 第二版》第06章 选取数据子集

[ SeanCheney](https://www.jianshu.com/u/130f76596b02)关注赞赏支持

# 《Pandas 1.x Cookbook · 第二版》第06章 选取数据子集

[第01章 Pandas基础](https://www.jianshu.com/p/9115de83bb88)  
[第02章 DataFrame基础运算](https://www.jianshu.com/p/5edda52d122f)  
[第03章 创建和持久化DataFrame](https://www.jianshu.com/p/5edda52d122f)  
[第04章 开始数据分析](https://www.jianshu.com/p/07e171e92112)  
[第05章 探索性数据分析](https://www.jianshu.com/p/e1006dda4b8d)  
第06章 选取数据子集  
[第07章 过滤行](https://www.jianshu.com/p/b0b159f3cf1c)  
[第08章 索引对齐](https://www.jianshu.com/p/509414c2e0be)

* * *

# 6.1 选取Series数据

读取大学数据集，使用校名作为索行引：

    
    
    >>> import pandas as pd
    >>> import numpy as np
    >>> college = pd.read_csv(
    ...     "data/college.csv", index_col="INSTNM"
    ... )
    >>> city = college["CITY"]
    >>> city
    INSTNM
    Alabama A & M University                                       Normal
    University of Alabama at Birmingham                        Birmingham
    Amridge University                                         Montgomery
    University of Alabama in Huntsville                        Huntsville
    Alabama State University                                   Montgomery
    ...
    SAE Institute of Technology  San Francisco                 Emeryville
    Rasmussen College - Overland Park                         Overland...
    National Personal Training Institute of Cleveland         Highland...
    Bay Area Medical Academy - San Jose Satellite Location       San Jose
    Excel Learning Center-San Antonio South                   San Antonio
    Name: CITY, Length: 7535, dtype: object
    

从Series选取标量值：

    
    
    >>> city["Alabama A & M University"]
    'Normal'
    

使用`.loc`提取标量值：

    
    
    >>> city.loc["Alabama A & M University"]
    'Normal'
    

使用`.iloc`提取标量值：

    
    
    >>> city.iloc[0]
    'Normal'
    

提取出多个值，如果传入的是列表，返回的是Series：

    
    
    >>> city[
    ...     [
    ...         "Alabama A & M University",
    ...         "Alabama State University",
    ...     ]
    ... ]
    INSTNM
    Alabama A & M University        Normal
    Alabama State University    Montgomery
    Name: CITY, dtype: object
    

使用`.loc`重复上面的步骤：

    
    
    >>> city.loc[
    ...     [
    ...         "Alabama A & M University",
    ...         "Alabama State University",
    ...     ]
    ... ]
    INSTNM
    Alabama A & M University        Normal
    Alabama State University    Montgomery
    Name: CITY, dtype: object
    

使用`.iloc`重复上面的步骤：

    
    
    >>> city.iloc[[0, 4]]
    INSTNM
    Alabama A & M University        Normal
    Alabama State University    Montgomery
    Name: CITY, dtype: object
    

使用切片提取多值：

    
    
    >>> city[
    ...     "Alabama A & M University":"Alabama State University"
    ... ]
    INSTNM
    Alabama A & M University                   Normal
    University of Alabama at Birmingham    Birmingham
    Amridge University                     Montgomery
    University of Alabama in Huntsville    Huntsville
    Alabama State University               Montgomery
    Name: CITY, dtype: object
    

使用位置切片提取多值：

    
    
    >>> city[0:5]
    INSTNM
    Alabama A & M University                   Normal
    University of Alabama at Birmingham    Birmingham
    Amridge University                     Montgomery
    University of Alabama in Huntsville    Huntsville
    Alabama State University               Montgomery
    Name: CITY, dtype: object
    

使用布尔数组提取多值：

    
    
    >>> alabama_mask = city.isin(["Birmingham", "Montgomery"])
    >>> city[alabama_mask]
    INSTNM
    University of Alabama at Birmingham    Birmingham
    Amridge University                     Montgomery
    Alabama State University               Montgomery
    Auburn University at Montgomery        Montgomery
    Birmingham Southern College            Birmingham
                                              ...     
    Fortis Institute-Birmingham            Birmingham
    Hair Academy                           Montgomery
    Brown Mackie College-Birmingham        Birmingham
    Nunation School of Cosmetology         Birmingham
    Troy University-Montgomery Campus      Montgomery
    Name: CITY, Length: 26, dtype: object
    

#### 更多

使用`.loc`和`.iloc`在原始DataFrame操作也可以实现同样的目的：

    
    
    >>> college.loc["Alabama A & M University", "CITY"]
    'Normal'
    >>> college.iloc[0, 0]
    'Normal'
    >>> college.loc[
    ...     [
    ...         "Alabama A & M University",
    ...         "Alabama State University",
    ...     ],
    ...     "CITY",
    ... ]
    INSTNM
    Alabama A & M University        Normal
    Alabama State University    Montgomery
    Name: CITY, dtype: object
    >>> college.iloc[[0, 4], 0]
    INSTNM
    Alabama A & M University        Normal
    Alabama State University    Montgomery
    Name: CITY, dtype: object
    >>> college.loc[
    ...     "Alabama A & M University":"Alabama State University",
    ...     "CITY",
    ... ]
    INSTNM
    Alabama A & M University                   Normal
    University of Alabama at Birmingham    Birmingham
    Amridge University                     Montgomery
    University of Alabama in Huntsville    Huntsville
    Alabama State University               Montgomery
    Name: CITY, dtype: object
    >>> college.iloc[0:5, 0]
    INSTNM
    Alabama A & M University                   Normal
    University of Alabama at Birmingham    Birmingham
    Amridge University                     Montgomery
    University of Alabama in Huntsville    Huntsville
    Alabama State University               Montgomery
    Name: CITY, dtype: object
    

使用`.loc`切片时要注意，索引如果越界，会返回空值：

    
    
    >>> city.loc[
    ...     "Reid State Technical College":"Alabama State University"
    ... ]
    Series([], Name: CITY, dtype: object)
    

* * *

# 6.2 选取DataFrame行

这一节和上节有点像，还是先读取数据：

    
    
    >>> college = pd.read_csv(
    ...     "data/college.csv", index_col="INSTNM"
    ... )
    >>> college.sample(5, random_state=42)
                         CITY STABBR  ...  MD_EARN_WNE_P10  GRAD_DEBT_MDN_SUPP
    INSTNM                            ...
    Career Po...  San Antonio     TX  ...        20700            14977
    Ner Israe...    Baltimore     MD  ...  PrivacyS...      PrivacyS...
    Reflectio...      Decatur     IL  ...          NaN      PrivacyS...
    Capital A...  Baton Rouge     LA  ...        26400      PrivacyS...
    West Virg...   Montgomery     WV  ...        43400            23969
    <BLANKLINE>
    [5 rows x 26 columns]
    

使用`.iloc`提取一整行：

    
    
    >>> college.iloc[60]
    CITY                  Anchorage
    STABBR                       AK
    HBCU                          0
    MENONLY                       0
    WOMENONLY                     0
                            ...
    PCTPELL                  0.2385
    PCTFLOAN                 0.2647
    UG25ABV                  0.4386
    MD_EARN_WNE_P10           42500
    GRAD_DEBT_MDN_SUPP      19449.5
    Name: University of Alaska Anchorage, Length: 26, dtype: object
    

使用`.loc`实现上一步：

    
    
    >>> college.loc["University of Alaska Anchorage"]
    CITY                  Anchorage
    STABBR                       AK
    HBCU                          0
    MENONLY                       0
    WOMENONLY                     0
                            ...
    PCTPELL                  0.2385
    PCTFLOAN                 0.2647
    UG25ABV                  0.4386
    MD_EARN_WNE_P10           42500
    GRAD_DEBT_MDN_SUPP      19449.5
    Name: University of Alaska Anchorage, Length: 26, dtype: object
    

使用`.iloc`提取一组不连续的行：

    
    
    >>> college.iloc[[60, 99, 3]]
                        CITY STABBR  ...  MD_EARN_WNE_P10  GRAD_DEBT_MDN_SUPP
    INSTNM                           ...
    Universit...   Anchorage     AK  ...        42500          19449.5
    Internati...       Tempe     AZ  ...        22200            10556
    Universit...  Huntsville     AL  ...        45500            24097
    <BLANKLINE>
    [3 rows x 26 columns]
    

使用`.loc`提取一组不连续的行：

    
    
    >>> labels = [
    ...     "University of Alaska Anchorage",
    ...     "International Academy of Hair Design",
    ...     "University of Alabama in Huntsville",
    ... ]
    >>> college.loc[labels]
                        CITY STABBR  ...  MD_EARN_WNE_P10  GRAD_DEBT_MDN_SUPP
    INSTNM                           ...
    Universit...   Anchorage     AK  ...        42500          19449.5
    Internati...       Tempe     AZ  ...        22200            10556
    Universit...  Huntsville     AL  ...        45500            24097
    <BLANKLINE>
    [3 rows x 26 columns]
    

使用`.iloc`提取一组连续的行：

    
    
    >>> college.iloc[99:102]
                     CITY STABBR  ...  MD_EARN_WNE_P10  GRAD_DEBT_MDN_SUPP
    INSTNM                        ...
    Internati...    Tempe     AZ  ...        22200            10556
    GateWay C...  Phoenix     AZ  ...        29800             7283
    Mesa Comm...     Mesa     AZ  ...        35200             8000
    <BLANKLINE>
    [3 rows x 26 columns]
    

`.loc`的切片是包含起始和结束的索引的：

    
    
    >>> start = "International Academy of Hair Design"
    >>> stop = "Mesa Community College"
    >>> college.loc[start:stop]
                     CITY STABBR  ...  MD_EARN_WNE_P10  GRAD_DEBT_MDN_SUPP
    INSTNM                        ...
    Internati...    Tempe     AZ  ...        22200            10556
    GateWay C...  Phoenix     AZ  ...        29800             7283
    Mesa Comm...     Mesa     AZ  ...        35200             8000
    <BLANKLINE>
    [3 rows x 26 columns]
    

#### 更多

将行索引的序号转变为字符串：

    
    
    >>> college.iloc[[60, 99, 3]].index.tolist()
    ['University of Alaska Anchorage', 'International Academy of Hair Design', 'University of Alabama in Huntsville']
    

* * *

# 6.3 同时选取DataFrame的行和列

`.iloc`和`.loc`可以使用双切片，同时提取行和列：

    
    
    >>> college = pd.read_csv(
    ...     "data/college.csv", index_col="INSTNM"
    ... )
    >>> college.iloc[:3, :4]
                        CITY STABBR  HBCU  MENONLY
    INSTNM                                        
    Alabama A...      Normal     AL   1.0      0.0
    Universit...  Birmingham     AL   0.0      0.0
    Amridge U...  Montgomery     AL   0.0      0.0
    >>> college.loc[:"Amridge University", :"MENONLY"]
                        CITY STABBR  HBCU  MENONLY
    INSTNM                                        
    Alabama A...      Normal     AL   1.0      0.0
    Universit...  Birmingham     AL   0.0      0.0
    Amridge U...  Montgomery     AL   0.0      0.0
    

选取不同两列的所有行：

    
    
    >>> college.iloc[:, [4, 6]].head()
                                         WOMENONLY  SATVRMID
    INSTNM
    Alabama A & M University                   0.0     424.0
    University of Alabama at Birmingham        0.0     570.0
    Amridge University                         0.0       NaN
    University of Alabama in Huntsville        0.0     595.0
    Alabama State University                   0.0     425.0
    >>> college.loc[:, ["WOMENONLY", "SATVRMID"]].head()
                                         WOMENONLY  SATVRMID
    INSTNM
    Alabama A & M University                   0.0     424.0
    University of Alabama at Birmingham        0.0     570.0
    Amridge University                         0.0       NaN
    University of Alabama in Huntsville        0.0     595.0
    Alabama State University                   0.0     425.0
    

选取不连续的行和列：

    
    
    >>> college.iloc[[100, 200], [7, 15]]
                                           SATMTMID  UGDS_NHPI
    INSTNM
    GateWay Community College                   NaN     0.0029
    American Baptist Seminary of the West       NaN        NaN
    >>> rows = [
    ...     "GateWay Community College",
    ...     "American Baptist Seminary of the West",
    ... ]
    >>> columns = ["SATMTMID", "UGDS_NHPI"]
    >>> college.loc[rows, columns]
                                           SATMTMID  UGDS_NHPI
    INSTNM
    GateWay Community College                   NaN     0.0029
    American Baptist Seminary of the West       NaN        NaN
    

选取一个标量值：

    
    
    >>> college.iloc[5, -4]
    0.401
    >>> college.loc["The University of Alabama", "PCTFLOAN"]
    0.401
    

选取单列，对行做切分：

    
    
    >>> college.iloc[90:80:-2, 5]
    INSTNM                              
    Empire Beauty School-Flagstaff     0
    Charles of Italy Beauty College    0
    Central Arizona College            0
    University of Arizona              0
    Arizona State University-Tempe     0
    Name: RELAFFIL, dtype: int64
    >>> start = "Empire Beauty School-Flagstaff"
    >>> stop = "Arizona State University-Tempe"
    >>> college.loc[start:stop:-2, "RELAFFIL"]
    INSTNM                              
    Empire Beauty School-Flagstaff     0
    Charles of Italy Beauty College    0
    Central Arizona College            0
    University of Arizona              0
    Arizona State University-Tempe     0
    Name: RELAFFIL, dtype: int64
    

#### 更多

下面两种操作等价：

    
    
    college.iloc[:10]
    college.iloc[:10, :]
    

* * *

# 6.4 用整数和标签选取数据

先读取数据：

    
    
    >>> college = pd.read_csv(
    ...     "data/college.csv", index_col="INSTNM"
    ... )
    

使用`.get_loc`找到某一列的序号：

    
    
    >>> col_start = college.columns.get_loc("UGDS_WHITE")
    >>> col_end = college.columns.get_loc("UGDS_UNKN") + 1
    >>> col_start, col_end
    (10, 19)
    

用`col_start`和`col_end`选取列：

    
    
    >>> college.iloc[:5, col_start:col_end]
                  UGDS_WHITE  UGDS_BLACK  ...  UGDS_NRA  UGDS_UNKN
    INSTNM                                ...                     
    Alabama A...      0.0333      0.9353  ...    0.0059     0.0138
    Universit...      0.5922      0.2600  ...    0.0179     0.0100
    Amridge U...      0.2990      0.4192  ...    0.0000     0.2715
    Universit...      0.6988      0.1255  ...    0.0332     0.0350
    Alabama S...      0.0158      0.9208  ...    0.0243     0.0137
    <BLANKLINE>
    [5 rows x 9 columns]
    

#### 更多

行索引切片提取多行多列：

    
    
    >>> row_start = college.index[10]
    >>> row_end = college.index[15]
    >>> college.loc[row_start:row_end, "UGDS_WHITE":"UGDS_UNKN"]
                  UGDS_WHITE  UGDS_BLACK  ...  UGDS_NRA  UGDS_UNKN
    INSTNM                                ...                     
    Birmingha...      0.7983      0.1102  ...    0.0000     0.0051
    Chattahoo...      0.4661      0.4372  ...    0.0000     0.0139
    Concordia...      0.0280      0.8758  ...    0.0466     0.0000
    South Uni...      0.3046      0.6054  ...    0.0019     0.0326
    Enterpris...      0.6408      0.2435  ...    0.0012     0.0069
    James H F...      0.6979      0.2259  ...    0.0007     0.0009
    <BLANKLINE>
    [6 rows x 9 columns]
    

* * *

# 6.5 按字母顺序切分

先读取数据：

    
    
    >>> college = pd.read_csv(
    ...     "data/college.csv", index_col="INSTNM"
    ... )
    

尝试选取`Sp`和`Su`之间的学校：

    
    
    >>> college.loc["Sp":"Su"]
    Traceback (most recent call last):
      ...
    ValueError: index must be monotonic increasing or decreasing
    During handling of the above exception, another exception occurred:
    Traceback (most recent call last):
      ...
    KeyError: 'Sp'
    

报错是因为索引没有排序，对索引做排序：

    
    
    >>> college = college.sort_index()
    

重复一开始的操作：

    
    
    >>> college.loc["Sp":"Su"]
                        CITY STABBR  ...  MD_EARN_WNE_P10  GRAD_DEBT_MDN_SUPP
    INSTNM                           ...
    Spa Tech ...     Ipswich     MA  ...        21500             6333
    Spa Tech ...    Plymouth     MA  ...        21500             6333
    Spa Tech ...    Westboro     MA  ...        21500             6333
    Spa Tech ...   Westbrook     ME  ...        21500             6333
    Spalding ...  Louisville     KY  ...        41700            25000
    ...                  ...    ...  ...          ...              ...
    Studio Ac...    Chandler     AZ  ...          NaN             6333
    Studio Je...    New York     NY  ...  PrivacyS...      PrivacyS...
    Stylemast...    Longview     WA  ...        17000            13320
    Styles an...      Selmer     TN  ...  PrivacyS...      PrivacyS...
    Styletren...   Rock Hill     SC  ...  PrivacyS...           9495.5
    <BLANKLINE>
    [201 rows x 26 columns]
    

#### 更多

用`.is_monotonic_increasing`或`is_monotonic_decreasing`判断索引是否是单调排序的：

    
    
    >>> college = college.sort_index(ascending=False)
    >>> college.index.is_monotonic_decreasing
    True
    >>> college.loc["E":"B"]
                                                      CITY  ...
    INSTNM                                                  ...
    Dyersburg State Community College            Dyersburg  ...
    Dutchess Community College                Poughkeepsie  ...
    Dutchess BOCES-Practical Nursing Program  Poughkeepsie  ...
    Durham Technical Community College              Durham  ...
    Durham Beauty Academy                           Durham  ...
    ...                                                ...  ...
    Bacone College                                Muskogee  ...
    Babson College                               Wellesley  ...
    BJ's Beauty & Barber College                    Auburn  ...
    BIR Training Center                            Chicago  ...
    B M Spurr School of Practical Nursing        Glen Dale  ...
    

* * *

[第01章 Pandas基础](https://www.jianshu.com/p/9115de83bb88)  
[第02章 DataFrame基础运算](https://www.jianshu.com/p/5edda52d122f)  
[第03章 创建和持久化DataFrame](https://www.jianshu.com/p/5edda52d122f)  
[第04章 开始数据分析](https://www.jianshu.com/p/07e171e92112)  
[第05章 探索性数据分析](https://www.jianshu.com/p/e1006dda4b8d)  
第06章 选取数据子集  
[第07章 过滤行](https://www.jianshu.com/p/b0b159f3cf1c)  
[第08章 索引对齐](https://www.jianshu.com/p/509414c2e0be)

### 推荐阅读[更多精彩内容 __](https://www.jianshu.com/)

  * [《Pandas Cookbook》第04章 选取数据子集](https://www.jianshu.com/p/bd0bc1b5b4b6)

第01章 Pandas基础第02章 DataFrame运算第03章 数据分析入门第04章 选取数据子集第05章 布...

[SeanCheney](https://www.jianshu.com/u/130f76596b02)阅读 5,408评论 2赞 8

  * [《Pandas 1.x Cookbook · 第二版》第05章 探索性数据分析](https://www.jianshu.com/p/e1006dda4b8d)

第01章 Pandas基础[https://www.jianshu.com/p/9115de83bb88]第02章...

[SeanCheney](https://www.jianshu.com/u/130f76596b02)阅读 789评论 0赞 2

  * [《Pandas 1.x Cookbook · 第二版》第01章 Pandas基础](https://www.jianshu.com/p/9115de83bb88)

第01章 Pandas基础第02章 DataFrame基础运算[https://www.jianshu.com/p...

[SeanCheney](https://www.jianshu.com/u/130f76596b02)阅读 4,297评论 0赞 17

  * [《Pandas 1.x Cookbook · 第二版》第02章 DataFrame基础运算](https://www.jianshu.com/p/914e4a05799a)

第01章 Pandas基础[https://www.jianshu.com/p/9115de83bb88]第02章...

[SeanCheney](https://www.jianshu.com/u/130f76596b02)阅读 1,211评论 0赞 3

  * [《Pandas 1.x Cookbook · 第二版》第04章 开始数据分析](https://www.jianshu.com/p/07e171e92112)

第01章 Pandas基础[https://www.jianshu.com/p/9115de83bb88]第02章...

[SeanCheney](https://www.jianshu.com/u/130f76596b02)阅读 637评论 0赞 2

 
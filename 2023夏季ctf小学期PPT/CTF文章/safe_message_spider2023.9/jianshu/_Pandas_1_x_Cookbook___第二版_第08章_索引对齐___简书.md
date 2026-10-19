《Pandas 1.x Cookbook · 第二版》第08章 索引对齐

[ SeanCheney](https://www.jianshu.com/u/130f76596b02)关注赞赏支持

# 《Pandas 1.x Cookbook · 第二版》第08章 索引对齐

[第01章 Pandas基础](https://www.jianshu.com/p/9115de83bb88)  
[第02章 DataFrame基础运算](https://www.jianshu.com/p/5edda52d122f)  
[第03章 创建和持久化DataFrame](https://www.jianshu.com/p/5edda52d122f)  
[第04章 开始数据分析](https://www.jianshu.com/p/07e171e92112)  
[第05章 探索性数据分析](https://www.jianshu.com/p/e1006dda4b8d)  
[第06章 选取数据子集](https://www.jianshu.com/p/1ee9787c3712)  
[第07章 过滤行](https://www.jianshu.com/p/b0b159f3cf1c)  
第08章 索引对齐

* * *

# 8.1 检查索引对象

读取大学数据集，用变量`columns`存储列索引：

    
    
    >>> import pandas as pd
    >>> import numpy as np
    >>> college = pd.read_csv("data/college.csv")
    >>> columns = college.columns
    >>> columns
    Index(['INSTNM', 'CITY', 'STABBR', 'HBCU', 'MENONLY', 'WOMENONLY', 'RELAFFIL',
           'SATVRMID', 'SATMTMID', 'DISTANCEONLY', 'UGDS', 'UGDS_WHITE',
           'UGDS_BLACK', 'UGDS_HISP', 'UGDS_ASIAN', 'UGDS_AIAN', 'UGDS_NHPI',
           'UGDS_2MOR', 'UGDS_NRA', 'UGDS_UNKN', 'PPTUG_EF', 'CURROPER', 'PCTPELL',
           'PCTFLOAN', 'UG25ABV', 'MD_EARN_WNE_P10', 'GRAD_DEBT_MDN_SUPP'],
          dtype='object')
    

用`.values`属性获取底层的NumPy数组：

    
    
    >>> columns.values
    array(['INSTNM', 'CITY', 'STABBR', 'HBCU', 'MENONLY', 'WOMENONLY',
           'RELAFFIL', 'SATVRMID', 'SATMTMID', 'DISTANCEONLY', 'UGDS',
           'UGDS_WHITE', 'UGDS_BLACK', 'UGDS_HISP', 'UGDS_ASIAN', 'UGDS_AIAN',
           'UGDS_NHPI', 'UGDS_2MOR', 'UGDS_NRA', 'UGDS_UNKN', 'PPTUG_EF',
           'CURROPER', 'PCTPELL', 'PCTFLOAN', 'UG25ABV', 'MD_EARN_WNE_P10',
           'GRAD_DEBT_MDN_SUPP'], dtype=object)
    

用标量、列表和切片从`columns`提取数据：

    
    
    >>> columns[5]
    'WOMENONLY'
    >>> columns[[1, 8, 10]]
    Index(['CITY', 'SATMTMID', 'UGDS'], dtype='object')
    >>> columns[-7:-4]
    Index(['PPTUG_EF', 'CURROPER', 'PCTPELL'], dtype='object')
    

索引对象和Series和DataFrames有公用的方法：

    
    
    >>> columns.min(), columns.max(), columns.isnull().sum()
    ('CITY', 'WOMENONLY', 0)
    

索引对象支持运算和比较：

    
    
    >>> columns + "_A"
    Index(['INSTNM_A', 'CITY_A', 'STABBR_A', 'HBCU_A', 'MENONLY_A',
    'WOMENONLY_A',
           'RELAFFIL_A', 'SATVRMID_A', 'SATMTMID_A', 'DISTANCEONLY_A', 'UGDS_A',
           'UGDS_WHITE_A', 'UGDS_BLACK_A', 'UGDS_HISP_A', 'UGDS_ASIAN_A',
           'UGDS_AIAN_A', 'UGDS_NHPI_A', 'UGDS_2MOR_A', 'UGDS_NRA_A',
           'UGDS_UNKN_A', 'PPTUG_EF_A', 'CURROPER_A', 'PCTPELL_A', 'PCTFLOAN_A',
           'UG25ABV_A', 'MD_EARN_WNE_P10_A', 'GRAD_DEBT_MDN_SUPP_A'],
          dtype='object')
    >>> columns > "G"
    array([ True, False,  True,  True,  True,  True,  True,  True,  True,
           False,  True,  True,  True,  True,  True,  True,  True,  True,
            True,  True,  True, False,  True,  True,  True,  True,  True])
    

索引是不可变对象：

    
    
    >>> columns[1] = "city"
    Traceback (most recent call last):
      ...
    TypeError: Index does not support mutable operations
    

#### 更多

索引支持集合运算：

    
    
    >>> c1 = columns[:4]
    >>> c1
    Index(['INSTNM', 'CITY', 'STABBR', 'HBCU'], dtype='object')
    >>> c2 = columns[2:6]
    >>> c2
    Index(['STABBR', 'HBCU', 'MENONLY', 'WOMENONLY'], dtype='object')
    >>> c1.union(c2)  # or 'c1 | c2'
    Index(['CITY', 'HBCU', 'INSTNM', 'MENONLY', 'STABBR', 'WOMENONLY'],
    dtype='object')
    >>> c1.symmetric_difference(c2)  # or 'c1 ^ c2'
    Index(['CITY', 'INSTNM', 'MENONLY', 'WOMENONLY'], dtype='object')
    

* * *

# 8.2 生成笛卡尔积

创建两个部分相同的Series：

    
    
    >>> s1 = pd.Series(index=list("aaab"), data=np.arange(4))
    >>> s1
    a    0
    a    1
    a    2
    b    3
    dtype: int64
    >>> s2 = pd.Series(index=list("cababb"), data=np.arange(6))
    >>> s2
    c    0
    a    1
    b    2
    a    3
    b    4
    b    5
    dtype: int64
    

将这两个Series相加，就生成了笛卡尔积：

    
    
    >>> s1 + s2
    a    1.0
    a    3.0
    a    2.0
    a    4.0
    a    3.0
    a    5.0
    b    5.0
    b    7.0
    b    8.0
    c    NaN
    dtype: float64
    

#### 更多

如果索引相同，顺序也一致，就不会生成笛卡尔积：

    
    
    >>> s1 = pd.Series(index=list("aaabb"), data=np.arange(5))
    >>> s2 = pd.Series(index=list("aaabb"), data=np.arange(5))
    >>> s1 + s2
    a    0
    a    2
    a    4
    b    6
    b    8
    dtype: int64
    

如果索引中的元素相同，但顺序不一致，也会产生笛卡尔积：

    
    
    >>> s1 = pd.Series(index=list("aaabb"), data=np.arange(5))
    >>> s2 = pd.Series(index=list("bbaaa"), data=np.arange(5))
    >>> s1 + s2
    a    2
    a    3
    a    4
    a    3
    a    4
        ..
    a    6
    b    3
    b    4
    b    4
    b    5
    Length: 13, dtype: int64
    

如果索引的顺序不同，但没有重复对象，则不会生成笛卡尔积：

    
    
    >>> s3 = pd.Series(index=list("ab"), data=np.arange(2))
    >>> s4 = pd.Series(index=list("ba"), data=np.arange(2))
    >>> s3 + s4
    a    1
    b    1
    dtype: int64
    

* * *

# 8.3 索引爆炸

读取员工数据集：

    
    
    >>> employee = pd.read_csv(
    ...     "data/employee.csv", index_col="RACE"
    ... )
    >>> employee.head()
                  UNIQUE_ID POSITION_TITLE  ...   HIRE_DATE    JOB_DATE
    RACE                                    ...                        
    Hispanic/...          0  ASSISTAN...    ...  2006-06-12  2012-10-13
    Hispanic/...          1  LIBRARY ...    ...  2000-07-19  2010-09-18
    White                 2  POLICE O...    ...  2015-02-03  2015-02-03
    White                 3  ENGINEER...    ...  1982-02-08  1991-05-25
    White                 4  ELECTRICIAN    ...  1989-06-19  1994-10-22
    

判断下面两个对象是否等价：

    
    
    >>> salary1 = employee["BASE_SALARY"]
    >>> salary2 = employee["BASE_SALARY"]
    >>> salary1 is salary2
    True
    

这两个对象指向相同，如果要做一个全新的对象，需要使用`.copy`方法：

    
    
    >>> salary2 = employee["BASE_SALARY"].copy()
    >>> salary1 is salary2
    False
    

改变一个索引的顺序：

    
    
    >>> salary1 = salary1.sort_index()
    >>> salary1.head()
    RACE
    American Indian or Alaskan Native    78355.0
    American Indian or Alaskan Native    26125.0
    American Indian or Alaskan Native    98536.0
    American Indian or Alaskan Native        NaN
    American Indian or Alaskan Native    55461.0
    Name: BASE_SALARY, dtype: float64
    >>> salary2.head()
    RACE
    Hispanic/Latino    121862.0
    Hispanic/Latino     26125.0
    White               45279.0
    White               63166.0
    White               56347.0
    Name: BASE_SALARY, dtype: float64
    

将两个Series相加：

    
    
    >>> salary_add = salary1 + salary2
    >>> salary_add.head()
    RACE
    American Indian or Alaskan Native    138702.0
    American Indian or Alaskan Native    156710.0
    American Indian or Alaskan Native    176891.0
    American Indian or Alaskan Native    159594.0
    American Indian or Alaskan Native    127734.0
    Name: BASE_SALARY, dtype: float64
    

为了对比，再创建一个`salary_add1`，比较这几个Series的长度：

    
    
    # 索引顺序不同时，产生了笛卡尔积
    >>> salary_add1 = salary1 + salary1
    >>> len(salary1), len(salary2), len(salary_add), len(
    ...     salary_add1
    ... )
    (2000, 2000, 1175424, 2000)
    

#### 更多

笛卡尔积的数量是可以计算的：

    
    
    >>> index_vc = salary1.index.value_counts(dropna=False)
    >>> index_vc
    Black or African American            700
    White                                665
    Hispanic/Latino                      480
    Asian/Pacific Islander               107
    NaN                                   35
    American Indian or Alaskan Native     11
    Others                                 2
    Name: RACE, dtype: int64
    >>> index_vc.pow(2).sum()
    1175424
    

* * *

# 8.4 用不等索引填充值

读取三个棒球数据集：

    
    
    >>> baseball_14 = pd.read_csv(
    ...     "data/baseball14.csv", index_col="playerID"
    ... )
    >>> baseball_15 = pd.read_csv(
    ...     "data/baseball15.csv", index_col="playerID"
    ... )
    >>> baseball_16 = pd.read_csv(
    ...     "data/baseball16.csv", index_col="playerID"
    ... )
    >>> baseball_14.head()
               yearID  stint teamID lgID  ...  HBP   SH   SF  GIDP
    playerID                              ...
    altuvjo01    2014      1    HOU   AL  ...  5.0  1.0  5.0  20.0
    cartech02    2014      1    HOU   AL  ...  5.0  0.0  4.0  12.0
    castrja01    2014      1    HOU   AL  ...  9.0  1.0  3.0  11.0
    corpoca01    2014      1    HOU   AL  ...  3.0  1.0  2.0   3.0
    dominma01    2014      1    HOU   AL  ...  5.0  2.0  7.0  23.0
    

检查哪些索引位于`baseball_14`而不在`baseball_15`中：

    
    
    >>> baseball_14.index.difference(baseball_15.index)
    Index(['corpoca01', 'dominma01', 'fowlede01', 'grossro01', 'guzmaje01',
           'hoeslj01', 'krausma01', 'preslal01', 'singljo02'],
          dtype='object', name='playerID')
    >>> baseball_15.index.difference(baseball_14.index)
    Index(['congeha01', 'correca01', 'gattiev01', 'gomezca01', 'lowrije01',
           'rasmuco01', 'tuckepr01', 'valbulu01'],
          dtype='object', name='playerID')
    

查询每名选手的击球数：

    
    
    >>> hits_14 = baseball_14["H"]
    >>> hits_15 = baseball_15["H"]
    >>> hits_16 = baseball_16["H"]
    >>> hits_14.head()
    playerID
    altuvjo01    225
    cartech02    115
    castrja01    103
    corpoca01     40
    dominma01    121
    Name: H, dtype: int64
    

将两列相加：

    
    
    >>> (hits_14 + hits_15).head()
    playerID
    altuvjo01    425.0
    cartech02    193.0
    castrja01    174.0
    congeha01      NaN
    corpoca01      NaN
    Name: H, dtype: float64
    

发现有缺失值，使用`fill_value`来填充：

    
    
    >>> hits_14.add(hits_15, fill_value=0).head()
    playerID
    altuvjo01    425.0
    cartech02    193.0
    castrja01    174.0
    congeha01     46.0
    corpoca01     40.0
    Name: H, dtype: float64
    

在加上`hits_16`：

    
    
    >>> hits_total = hits_14.add(hits_15, fill_value=0).add(
    ...     hits_16, fill_value=0
    ... )
    >>> hits_total.head()
    playerID
    altuvjo01    641.0
    bregmal01     53.0
    cartech02    193.0
    castrja01    243.0
    congeha01     46.0
    Name: H, dtype: float64
    

检查是否有缺失值：

    
    
    >>> hits_total.hasnans
    False
    

#### 更多

DataFrame在相加时，也支持填充：

    
    
    >>> df_14 = baseball_14[["G", "AB", "R", "H"]]
    >>> df_14.head()
                 G   AB   R    H
    playerID                    
    altuvjo01  158  660  85  225
    cartech02  145  507  68  115
    castrja01  126  465  43  103
    corpoca01   55  170  22   40
    dominma01  157  564  51  121
    
    >>> df_15 = baseball_15[["AB", "R", "H", "HR"]]
    >>> df_15.head()
                AB   R    H  HR
    playerID                   
    altuvjo01  638  86  200  15
    cartech02  391  50   78  24
    castrja01  337  38   71  11
    congeha01  201  25   46  11
    correca01  387  52  108  22
    

* * *

# 8.5 从不同的DataFrame添加列

读取数据集：

    
    
    >>> employee = pd.read_csv("data/employee.csv")
    >>> dept_sal = employee[["DEPARTMENT", "BASE_SALARY"]]
    

对值进行排序：

    
    
    >>> dept_sal = dept_sal.sort_values(
    ...     ["DEPARTMENT", "BASE_SALARY"],
    ...     ascending=[True, False],
    ... )
    

对`DEPARTMENT`列进行去重：

    
    
    >>> max_dept_sal = dept_sal.drop_duplicates(
    ...     subset="DEPARTMENT"
    ... )
    >>> max_dept_sal.head()
           DEPARTMENT  BASE_SALARY
                            DEPARTMENT  BASE_SALARY
    1494    Admn. & Regulatory Affairs     140416.0
    149       City Controller's Office      64251.0
    236                   City Council     100000.0
    647   Convention and Entertainment      38397.0
    1500   Dept of Neighborhoods (DON)      89221.0
    

将列`DEPARTMENT`作为行索引：

    
    
    >>> max_dept_sal = max_dept_sal.set_index("DEPARTMENT")
    >>> employee = employee.set_index("DEPARTMENT")
    

给`employee`添加一个新列：

    
    
    >>> employee = employee.assign(
    ...     MAX_DEPT_SALARY=max_dept_sal["BASE_SALARY"]
    ... )
    >>> employee
                                   UNIQUE_ID  ... MAX_D/ALARY
    DEPARTMENT                                ...
    Municipal Courts Department            0  ...    121862.0
    Library                                1  ...    107763.0
    Houston Police Department-HPD          2  ...    199596.0
    Houston Fire Department (HFD)          3  ...    210588.0
    General Services Department            4  ...     89194.0
    ...                                  ...  ...         ...
    Houston Police Department-HPD       1995  ...    199596.0
    Houston Fire Department (HFD)       1996  ...    210588.0
    Houston Police Department-HPD       1997  ...    199596.0
    Houston Police Department-HPD       1998  ...    199596.0
    Houston Fire Department (HFD)       1999  ...    210588.0
    

用query方法检查是否存在`BASE_SALARY`高于`MAX_DEPT_SALARY`的行：

    
    
    >>> employee.query("BASE_SALARY > MAX_DEPT_SALARY")
    Empty DataFrame
    Columns: [UNIQUE_ID, POSITION_TITLE, BASE_SALARY, RACE, EMPLOYMENT_TYPE, GENDER, EMPLOYMENT_STATUS, HIRE_DATE, JOB_DATE, MAX_DEPT_SALARY]
    Index: []
    

将前面的方法组合成链式方法：

    
    
    >>> employee = pd.read_csv("data/employee.csv")
    >>> max_dept_sal = (
    ...     employee
    ...     [["DEPARTMENT", "BASE_SALARY"]]
    ...     .sort_values(
    ...         ["DEPARTMENT", "BASE_SALARY"],
    ...         ascending=[True, False],
    ...     )
    ...     .drop_duplicates(subset="DEPARTMENT")
    ...     .set_index("DEPARTMENT")
    ... )
    >>> (
    ...     employee
    ...     .set_index("DEPARTMENT")
    ...     .assign(
    ...         MAX_DEPT_SALARY=max_dept_sal["BASE_SALARY"]
    ...     )
    ... )
                  UNIQUE_ID POSITION_TITLE  ...    JOB_DATE MAX_DEPT_SALARY
    DEPARTMENT                              ...
    Municipal...          0  ASSISTAN...    ...  2012-10-13     121862.0
    Library               1  LIBRARY ...    ...  2010-09-18     107763.0
    Houston P...          2  POLICE O...    ...  2015-02-03     199596.0
    Houston F...          3  ENGINEER...    ...  1991-05-25     210588.0
    General S...          4  ELECTRICIAN    ...  1994-10-22      89194.0
    ...                 ...          ...    ...         ...          ...
    Houston P...       1995  POLICE O...    ...  2015-06-09     199596.0
    Houston F...       1996  COMMUNIC...    ...  2013-10-06     210588.0
    Houston P...       1997  POLICE O...    ...  2015-10-13     199596.0
    Houston P...       1998  POLICE O...    ...  2011-07-02     199596.0
    Houston F...       1999  FIRE FIG...    ...  2010-07-12     210588.0
    

#### 更多

在索引对齐的过程中，如果索引不能对齐，就会产生缺失值。只用`max_dept_sal`的前三行做新列：

    
    
    >>> (
    ...     employee
    ...     .set_index("DEPARTMENT")
    ...     .assign(
    ...         MAX_SALARY2=max_dept_sal["BASE_SALARY"].head(3)
    ...     )
    ...     .MAX_SALARY2
    ...     .value_counts(dropna=False)
    ... )
    NaN         1955
    140416.0      29
    100000.0      11
    64251.0        5
    Name: MAX_SALARY2, dtype: int64
    

我的方法是使用`groupby`和`transform`，后面章节会详细讨论：

    
    
    >>> max_sal = (
    ...     employee
    ...     .groupby("DEPARTMENT")
    ...     .BASE_SALARY
    ...     .transform("max")
    ... )
    >>> (employee.assign(MAX_DEPT_SALARY=max_sal))
    UNIQUE_ID POSITION_TITLE  ...    JOB_DATE  MAX_DEPT_SALARY
    0             0  ASSISTAN...    ...  2012-10-13     121862.0
    1             1  LIBRARY ...    ...  2010-09-18     107763.0
    2             2  POLICE O...    ...  2015-02-03     199596.0
    3             3  ENGINEER...    ...  1991-05-25     210588.0
    4             4  ELECTRICIAN    ...  1994-10-22      89194.0
    ...         ...          ...    ...         ...          ...
    1995       1995  POLICE O...    ...  2015-06-09     199596.0
    1996       1996  COMMUNIC...    ...  2013-10-06     210588.0
    1997       1997  POLICE O...    ...  2015-10-13     199596.0
    1998       1998  POLICE O...    ...  2011-07-02     199596.0
    1999       1999  FIRE FIG...    ...  2010-07-12     210588.0
    

下面的方法是将`groupby`和`merge`联用：

    
    
    >>> max_sal = (
    ...     employee
    ...     .groupby("DEPARTMENT")
    ...     .BASE_SALARY
    ...     .max()
    ... )
    >>> (
    ...     employee.merge(
    ...         max_sal.rename("MAX_DEPT_SALARY"),
    ...         how="left",
    ...         left_on="DEPARTMENT",
    ...         right_index=True,
    ...     )
    ... )
    UNIQUE_ID POSITION_TITLE  ...    JOB_DATE  MAX_DEPT_SALARY
    0             0  ASSISTAN...    ...  2012-10-13     121862.0
    1             1  LIBRARY ...    ...  2010-09-18     107763.0
    2             2  POLICE O...    ...  2015-02-03     199596.0
    3             3  ENGINEER...    ...  1991-05-25     210588.0
    4             4  ELECTRICIAN    ...  1994-10-22      89194.0
    ...         ...          ...    ...         ...          ...
    1995       1995  POLICE O...    ...  2015-06-09     199596.0
    1996       1996  COMMUNIC...    ...  2013-10-06     210588.0
    1997       1997  POLICE O...    ...  2015-10-13     199596.0
    1998       1998  POLICE O...    ...  2011-07-02     199596.0
    1999       1999  FIRE FIG...    ...  2010-07-12     210588.0
    

* * *

# 8.6 高亮每列的最大值

读取数据集：

    
    
    >>> college = pd.read_csv(
    ...     "data/college.csv", index_col="INSTNM"
    ... )
    >>> college.dtypes
    CITY                   object
    STABBR                 object
    HBCU                  float64
    MENONLY               float64
    WOMENONLY             float64
                           ...
    PCTPELL               float64
    PCTFLOAN              float64
    UG25ABV               float64
    MD_EARN_WNE_P10        object
    GRAD_DEBT_MDN_SUPP     object
    Length: 26, dtype: object
    

随机检查数据：

    
    
    >>> college.MD_EARN_WNE_P10.sample(10, random_state=42)
    INSTNM
    Career Point College                                      20700
    Ner Israel Rabbinical College                       PrivacyS...
    Reflections Academy of Beauty                               NaN
    Capital Area Technical College                            26400
    West Virginia University Institute of Technology          43400
    Mid-State Technical College                               32000
    Strayer University-Huntsville Campus                      49200
    National Aviation Academy of Tampa Bay                    45000
    University of California-Santa Cruz                       43000
    Lexington Theological Seminary                              NaN
    Name: MD_EARN_WNE_P10, dtype: object
    >>> college.GRAD_DEBT_MDN_SUPP.sample(10, random_state=42)
    INSTNM
    Career Point College                                      14977
    Ner Israel Rabbinical College                       PrivacyS...
    Reflections Academy of Beauty                       PrivacyS...
    Capital Area Technical College                      PrivacyS...
    West Virginia University Institute of Technology          23969
    Mid-State Technical College   
    

用`.value_counts`查看为什么是字符串：

    
    
    >>> college.MD_EARN_WNE_P10.value_counts()
    PrivacySuppressed    822
    38800                151
    21500                 97
    49200                 78
    27400                 46
                        ...
    66700                  1
    163900                 1
    64400                  1
    58700                  1
    64100                  1
    Name: MD_EARN_WNE_P10, Length: 598, dtype: int64
    >>> set(college.MD_EARN_WNE_P10.apply(type))
    {<class 'float'>, <class 'str'>}
    >>> college.GRAD_DEBT_MDN_SUPP.value_counts()
    PrivacySuppressed    1510
    9500                  514
    27000                 306
    25827.5               136
    25000                 124
                         ...
    16078.5                 1
    27763.5                 1
    6382                    1
    27625                   1
    11300                   1
    Name: GRAD_DEBT_MDN_SUPP, Length: 2038, dtype: int64
    

使用`to_numeric`将其转化为数值类型，参数`errors='coerce'`可以将字符串转换为`NaN`：

    
    
    >>> cols = ["MD_EARN_WNE_P10", "GRAD_DEBT_MDN_SUPP"]
    >>> for col in cols:
    ...     college[col] = pd.to_numeric(
    ...         college[col], errors="coerce"
    ...     )
    >>> college.dtypes.loc[cols]
    MD_EARN_WNE_P10       float64
    GRAD_DEBT_MDN_SUPP    float64
    dtype: object
    

选取数值类型数据：

    
    
    >>> college_n = college.select_dtypes("number")
    >>> college_n.head()
                  HBCU  MENONLY  ...  MD_EARN_WNE_P10  GRAD_DEBT_MDN_SUPP
    INSTNM                       ...
    Alabama A...   1.0      0.0  ...      30300.0          33888.0
    Universit...   0.0      0.0  ...      39700.0          21941.5
    Amridge U...   0.0      0.0  ...      40100.0          23370.0
    Universit...   0.0      0.0  ...      45500.0          24097.0
    Alabama S...   1.0      0.0  ...      26600.0          33118.5
    

有的二分列只有1和0两种数值，用`.nunique`进行判断：

    
    
    >>> binary_only = college_n.nunique() == 2
    >>> binary_only.head()
    HBCU          True
    MENONLY       True
    WOMENONLY     True
    RELAFFIL      True
    SATVRMID     False
    dtype: bool
    

用布尔数组创建二分列表：

    
    
    >>> binary_cols = binary_only[binary_only].index
    >>> binary_cols
    Index(['HBCU', 'MENONLY', 'WOMENONLY', 'RELAFFIL', 'DISTANCEONLY', 'CURROPER'], dtype='object')
    

使用`drop`方法删除这些二分列表：

    
    
    >>> college_n2 = college_n.drop(columns=binary_cols)
    >>> college_n2.head()
                  SATVRMID  SATMTMID  ...  MD_EARN_WNE_P10  GRAD_DEBT_MDN_SUPP
    INSTNM                            ...
    Alabama A...     424.0     420.0  ...      30300.0          33888.0
    Universit...     570.0     565.0  ...      39700.0          21941.5
    Amridge U...       NaN       NaN  ...      40100.0          23370.0
    Universit...     595.0     590.0  ...      45500.0          24097.0
    Alabama S...     425.0     430.0  ...      26600.0          33118.5
    

用`idxmax`方法找到每列最大值对应的行索引标签：

    
    
    >>> max_cols = college_n2.idxmax()
    >>> max_cols
    SATVRMID                      California Institute of Technology
    SATMTMID                      California Institute of Technology
    UGDS                               University of Phoenix-Arizona
    UGDS_WHITE                Mr Leon's School of Hair Design-Moscow
    UGDS_BLACK                    Velvatex College of Beauty Culture
                                             ...
    PCTPELL                                 MTI Business College Inc
    PCTFLOAN                                  ABC Beauty College Inc
    UG25ABV                           Dongguk University-Los Angeles
    MD_EARN_WNE_P10                     Medical College of Wisconsin
    GRAD_DEBT_MDN_SUPP    Southwest University of Visual Arts-Tucson
    Length: 18, dtype: object
    

在`max_cols`上调用`unique`方法，能得到所有行索引的值：

    
    
    >>> unique_max_cols = max_cols.unique()
    >>> unique_max_cols[:5]
    array(['California Institute of Technology',
           'University of Phoenix-Arizona',
           "Mr Leon's School of Hair Design-Moscow",
           'Velvatex College of Beauty Culture',
           'Thunderbird School of Global Management'], dtype=object)
    

使用`.style`高亮所有最大值：

    
    
    college_n2.loc[unique_max_cols].style.highlight_max()
    

重写上面的代码，提高可读性：

    
    
    >>> def remove_binary_cols(df):
    ...     binary_only = df.nunique() == 2
    ...     cols = binary_only[binary_only].index.tolist()
    ...     return df.drop(columns=cols)
    >>> def select_rows_with_max_cols(df):
    ...     max_cols = df.idxmax()
    ...     unique = max_cols.unique()
    ...     return df.loc[unique]
    >>> (
    ...     college
    ...     .assign(
    ...         MD_EARN_WNE_P10=pd.to_numeric(
    ...             college.MD_EARN_WNE_P10, errors="coerce"
    ...         ),
    ...         GRAD_DEBT_MDN_SUPP=pd.to_numeric(
    ...             college.GRAD_DEBT_MDN_SUPP, errors="coerce"
    ...         ),
    ...     )
    ...     .select_dtypes("number")
    ...     .pipe(remove_binary_cols)
    ...     .pipe(select_rows_with_max_cols)
    ... )
                  SATVRMID  SATMTMID  ...  MD_EARN_WNE_P10  GRAD_DEBT_MDN_SUPP
    INSTNM                            ...
    Californi...     765.0     785.0  ...      77800.0          11812.5
    Universit...       NaN       NaN  ...          NaN          33000.0
    Mr Leon's...       NaN       NaN  ...          NaN          15710.0
    Velvatex ...       NaN       NaN  ...          NaN              NaN
    Thunderbi...       NaN       NaN  ...     118900.0              NaN
    ...                ...       ...  ...          ...              ...
    MTI Busin...       NaN       NaN  ...      23000.0           9500.0
    ABC Beaut...       NaN       NaN  ...          NaN          16500.0
    Dongguk U...       NaN       NaN  ...          NaN              NaN
    Medical C...       NaN       NaN  ...     233100.0              NaN
    Southwest...       NaN       NaN  ...      27200.0          49750.0
    

#### 更多

可以用`axis`参数，高亮每行的最大值：

    
    
    >>> college = pd.read_csv(
    ...     "data/college.csv", index_col="INSTNM"
    ... )
    >>> college_ugds = college.filter(like="UGDS_").head()
    

* * *

# 8.7 用链式方法替换idxmax

和上一节一样，读取数据集，只选取目标数值列：

    
    
    >>> def remove_binary_cols(df):
    ...     binary_only = df.nunique() == 2
    ...     cols = binary_only[binary_only].index.tolist()
    ...     return df.drop(columns=cols)
    >>> college_n = (
    ...     college
    ...     .assign(
    ...         MD_EARN_WNE_P10=pd.to_numeric(
    ...             college.MD_EARN_WNE_P10, errors="coerce"
    ...         ),
    ...         GRAD_DEBT_MDN_SUPP=pd.to_numeric(
    ...             college.GRAD_DEBT_MDN_SUPP, errors="coerce"
    ...         ),
    ...     )
    ...     .select_dtypes("number")
    ...     .pipe(remove_binary_cols)
    ... )
    

使用`max`方法，找到每列的最大值：

    
    
    >>> college_n.max().head()
    SATVRMID         765.0
    SATMTMID         785.0
    UGDS          151558.0
    UGDS_WHITE         1.0
    UGDS_BLACK         1.0
    dtype: float64
    

使用`eq`方法，将DataFrame中的每个值和列的最大值比较：

    
    
    >>> college_n.eq(college_n.max()).head()
                  SATVRMID  SATMTMID  ...  MD_EARN_WNE_P10  GRAD_DEBT_MDN_SUPP
    INSTNM                            ...
    Alabama A...     False     False  ...        False            False
    Universit...     False     False  ...        False            False
    Amridge U...     False     False  ...        False            False
    Universit...     False     False  ...        False            False
    Alabama S...     False     False  ...        False            False
    

使用`.any`找到包含True值的行：

    
    
    >>> has_row_max = (
    ...     college_n
    ...     .eq(college_n.max())
    ...     .any(axis="columns")
    ... )
    >>> has_row_max.head()
    INSTNM
    Alabama A & M University               False
    University of Alabama at Birmingham    False
    Amridge University                     False
    University of Alabama in Huntsville    False
    Alabama State University               False
    dtype: bool
    

检查有多少个最大值：

    
    
    >>> college_n.shape
    (7535, 18)
    >>> has_row_max.sum()
    401
    

这说明，有的列存在多个最大值。回到上面的步骤，用`cumsum`方法检查：

    
    
    >>> college_n.eq(college_n.max()).cumsum()
                  SATVRMID  SATMTMID  ...  MD_EARN_WNE_P10  GRAD_DEBT_MDN_SUPP
    INSTNM                            ...
    Alabama A...         0         0  ...            0                0
    Universit...         0         0  ...            0                0
    Amridge U...         0         0  ...            0                0
    Universit...         0         0  ...            0                0
    Alabama S...         0         0  ...            0                0
    ...                ...       ...  ...          ...              ...
    SAE Insti...         1         1  ...            1                2
    Rasmussen...         1         1  ...            1                2
    National ...         1         1  ...            1                2
    Bay Area ...         1         1  ...            1                2
    Excel Lea...         1         1  ...            1                2
    

`cumsum`方法再重复一下，找到1出现的地方：

    
    
    >>> (college_n.eq(college_n.max()).cumsum().cumsum())
                  SATVRMID  SATMTMID  ...  MD_EARN_WNE_P10  GRAD_DEBT_MDN_SUPP
    INSTNM                            ...
    Alabama A...         0         0  ...            0                0
    Universit...         0         0  ...            0                0
    Amridge U...         0         0  ...            0                0
    Universit...         0         0  ...            0                0
    Alabama S...         0         0  ...            0                0
    ...                ...       ...  ...          ...              ...
    SAE Insti...      7305      7305  ...         3445            10266
    Rasmussen...      7306      7306  ...         3446            10268
    National ...      7307      7307  ...         3447            10270
    Bay Area ...      7308      7308  ...         3448            10272
    Excel Lea...      7309      7309  ...         3449            10274
    

现在再用`any`方法找到至少有一个`True`值的列：

    
    
    >>> has_row_max2 = (
    ...     college_n.eq(college_n.max())
    ...     .cumsum()
    ...     .cumsum()
    ...     .eq(1)
    ...     .any(axis="columns")
    ... )
    >>> has_row_max2.head()
    INSTNM
    Alabama A & M University               False
    University of Alabama at Birmingham    False
    Amridge University                     False
    University of Alabama in Huntsville    False
    Alabama State University               False
    dtype: bool
    

现在，has_row_max2的True值就不必列数多了：

    
    
    >>> has_row_max2.sum()
    16
    

计算最大值对应的行索引标签：

    
    
    >>> idxmax_cols = has_row_max2[has_row_max2].index
    >>> idxmax_cols
    Index(['Thunderbird School of Global Management',
           'Southwest University of Visual Arts-Tucson', 'ABC Beauty College Inc',
           'Velvatex College of Beauty Culture',
           'California Institute of Technology',
           'Le Cordon Bleu College of Culinary Arts-San Francisco',
           'MTI Business College Inc', 'Dongguk University-Los Angeles',
           'Mr Leon's School of Hair Design-Moscow',
           'Haskell Indian Nations University', 'LIU Brentwood',
           'Medical College of Wisconsin', 'Palau Community College',
           'California University of Management and Sciences',
           'Cosmopolitan Beauty and Tech School', 'University of Phoenix-Arizona'],
          dtype='object', name='INSTNM')
    
    
    
    >>> set(college_n.idxmax().unique()) == set(idxmax_cols)
    True
    

将其写成`idx_max`函数：

    
    
    >>> def idx_max(df):
    ...     has_row_max = (
    ...         df
    ...         .eq(df.max())
    ...         .cumsum()
    ...         .cumsum()
    ...         .eq(1)
    ...         .any(axis="columns")
    ...     )
    ...     return has_row_max[has_row_max].index
    >>> idx_max(college_n)
    Index(['Thunderbird School of Global Management',
           'Southwest University of Visual Arts-Tucson', 'ABC Beauty College Inc',
           'Velvatex College of Beauty Culture',
           'California Institute of Technology',
           'Le Cordon Bleu College of Culinary Arts-San Francisco',
           'MTI Business College Inc', 'Dongguk University-Los Angeles',
           'Mr Leon's School of Hair Design-Moscow',
           'Haskell Indian Nations University', 'LIU Brentwood',
           'Medical College of Wisconsin', 'Palau Community College',
           'California University of Management and Sciences',
           'Cosmopolitan Beauty and Tech School', 'University of Phoenix-Arizona'],
          dtype='object', name='INSTNM')
    

#### 更多

比较两种方法的速度：

    
    
    >>> def idx_max(df):
    ...     has_row_max = (
    ...         df
    ...         .eq(df.max())
    ...         .cumsum()
    ...         .cumsum()
    ...         .eq(1)
    ...         .any(axis="columns")
    ...         [lambda df_: df_]
    ...         .index
    ...     )
    ...     return has_row_max
    >>> %timeit college_n.idxmax().values
    1.12 ms ± 28.4 μs per loop (mean ± std. dev. of 7 runs, 1000 loops each)
    >>> %timeit idx_max(college_n)
    5.35 ms ± 55.2 μs per loop (mean ± std. dev. of 7 runs, 100 loops each)
    

* * *

# 8.8 发现列的最常见最大值

读取数据集：

    
    
    >>> college = pd.read_csv(
    ...     "data/college.csv", index_col="INSTNM"
    ... )
    >>> college_ugds = college.filter(like="UGDS_")
    >>> college_ugds.head()
                  UGDS_WHITE  UGDS_BLACK  ...  UGDS_NRA  UGDS_UNKN
    INSTNM                                ...
    Alabama A...      0.0333      0.9353  ...    0.0059     0.0138
    Universit...      0.5922      0.2600  ...    0.0179     0.0100
    Amridge U...      0.2990      0.4192  ...    0.0000     0.2715
    Universit...      0.6988      0.1255  ...    0.0332     0.0350
    Alabama S...      0.0158      0.9208  ...    0.0243     0.0137
    

用`.idxmax`在列上，找到最高比例种族对应的学校：

    
    
    >>> highest_percentage_race = college_ugds.idxmax(
    ...     axis="columns"
    ... )
    >>> highest_percentage_race.head()
    INSTNM
    Alabama A & M University
    University of Alabama at Birmingham
    Amridge University
    University of Alabama in Huntsville
    Alabama State University
    dtype: object
    

查看最大值的分布情况：

    
    
    >>> highest_percentage_race.value_counts(normalize=True)
    UGDS_WHITE    0.670352
    UGDS_BLACK    0.151586
    UGDS_HISP     0.129473
    UGDS_UNKN     0.023422
    UGDS_ASIAN    0.012074
    UGDS_AIAN     0.006110
    UGDS_NRA      0.004073
    UGDS_NHPI     0.001746
    UGDS_2MOR     0.001164
    dtype: float64
    

#### 更多

对于黑人占多数的学校，其它族裔是如何分布的：

    
    
    >>> (
    ...     college_ugds
    ...     [highest_percentage_race == "UGDS_BLACK"]
    ...     .drop(columns="UGDS_BLACK")
    ...     .idxmax(axis="columns")
    ...     .value_counts(normalize=True)
    ... )
    UGDS_WHITE    0.661228
    UGDS_HISP     0.230326
    UGDS_UNKN     0.071977
    UGDS_NRA      0.018234
    UGDS_ASIAN    0.009597
    UGDS_2MOR     0.006718
    UGDS_AIAN     0.000960
    UGDS_NHPI     0.000960
    dtype: float64
    

* * *

[第01章 Pandas基础](https://www.jianshu.com/p/9115de83bb88)  
[第02章 DataFrame基础运算](https://www.jianshu.com/p/5edda52d122f)  
[第03章 创建和持久化DataFrame](https://www.jianshu.com/p/5edda52d122f)  
[第04章 开始数据分析](https://www.jianshu.com/p/07e171e92112)  
[第05章 探索性数据分析](https://www.jianshu.com/p/e1006dda4b8d)  
[第06章 选取数据子集](https://www.jianshu.com/p/1ee9787c3712)  
[第07章 过滤行](https://www.jianshu.com/p/b0b159f3cf1c)  
第08章 索引对齐

### 推荐阅读[更多精彩内容 __](https://www.jianshu.com/)

  * [《Pandas 1.x Cookbook · 第二版》第04章 开始数据分析](https://www.jianshu.com/p/07e171e92112)

第01章 Pandas基础[https://www.jianshu.com/p/9115de83bb88]第02章...

[SeanCheney](https://www.jianshu.com/u/130f76596b02)阅读 637评论 0赞 2

  * [《Pandas 1.x Cookbook · 第二版》第03章 创建和持久化DataFrame](https://www.jianshu.com/p/5edda52d122f)

第01章 Pandas基础[https://www.jianshu.com/p/9115de83bb88]第02章...

[SeanCheney](https://www.jianshu.com/u/130f76596b02)阅读 1,409评论 0赞 7

  * [《Pandas 1.x Cookbook · 第二版》第07章 过滤行](https://www.jianshu.com/p/b0b159f3cf1c)

第01章 Pandas基础[https://www.jianshu.com/p/9115de83bb88]第02章...

[SeanCheney](https://www.jianshu.com/u/130f76596b02)阅读 597评论 0赞 3

  * [《Pandas 1.x Cookbook · 第二版》第01章 Pandas基础](https://www.jianshu.com/p/9115de83bb88)

第01章 Pandas基础第02章 DataFrame基础运算[https://www.jianshu.com/p...

[SeanCheney](https://www.jianshu.com/u/130f76596b02)阅读 4,297评论 0赞 17

  * [《Pandas 1.x Cookbook · 第二版》第06章 选取数据子集](https://www.jianshu.com/p/1ee9787c3712)

第01章 Pandas基础[https://www.jianshu.com/p/9115de83bb88]第02章...

[SeanCheney](https://www.jianshu.com/u/130f76596b02)阅读 554评论 0赞 2

 
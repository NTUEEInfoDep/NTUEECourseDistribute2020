# NTUEECourse2020Distribution

配合 2020 年新版電機系預選網站的分發程式。

[預選網站 repo](https://github.com/NTUEEInfoDep/NTUEECourseWebsite2020)

## Usage

把預選網站匯出的`selections.json`放進`secret-data/`資料夾裡，格式如下：

```
[
  {
    "userID": "B07901069",
    "grade": 3,
    "selections": {
      "Ten-Select-Two": [],
      "Electronics-one": [],
      "Electormagnetics-one": [],
      "Linear-Algebra": [],
      "Differential-Equation": [],
      "Algorithm": []
    }
  },
  ...
]
```

---

今年的特殊規則：三保一

請將已選上的人們寫成`preselect.json`，放進`secret-data/`資料夾裡，格式如下：

```
{
  "B0X901XXX": ["電力電子"],
  "B0Y901YYY": ["網路與多媒體", "光電"],
  "B0Z901ZZZ": ["網路與多媒體", "數電實驗"],
  ...
}
```

註：數電實驗比較特別，不在`courses.json`十選二的`options`裡。

---

準備好`courses.json`，格式請參考[這裡](/data/courses.json)。

說明：

1. id 須和預選網站匯出的課程 id 一致
2. name 就是課程名稱
3. type 有三種："必修", "電電實驗", "十選二"
4. options 裡的 key 須和預選網站各課程的 options 一致
5. limit 代表該選項的限制人數
6. 十選二要額外填一個"priority"，值可以是 true, false, 或數字。
   1. true 代表高年級優先
   2. false 代表無年級保障
   3. 數字代表大幾優先，例如 3 代表大三優先，4 代表大四優先。

---

跑以下指令

```
python distribute.py
```

把`secret-data/`資料夾裡的`results.csv`給學術部。

## 演算法

# NTUEECourse2020Distribution

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

> 今年的特殊規則：三保一
> 請將已選上的人們寫成`preselect.json`，放進`secret-data/`資料夾裡，格式如下：

```
{
  "B0X901XXX": ["電力電子"],
  "B0Y901YYY": ["網路與多媒體", "光電"],
  "B0Z901ZZZ": ["網路與多媒體", "數電實驗"],
  ...
}
```

> 註：數電實驗比較特別，不在`courses.json`十選二的`options`裡。

準備好`courses.json`，格式請參考[這裡](/data/courses.json)。

跑以下指令

```
python distribute.py
```

把`secret-data/`資料夾裡的`results.csv`給學術部。

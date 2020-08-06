# NTUEECourse2020Distribution

配合 2020 年新版電機系預選網站的分發程式。

[預選網站 repo](https://github.com/NTUEEInfoDep/NTUEECourseWebsite2020)

## Maintainer

[劉奇聖](https://github.com/MortalHappiness), email: `b07901069@ntu.edu.tw`

有找到 bug 的話歡迎大家發 issue 或寄信給我。

## Usage

把預選網站匯出的 `selections.json` 放進 `secret-data/` 資料夾裡，格式如下：

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

其中 Array 裡的內容是該學生選擇的選項(String)照志願序排序，選項必須在 [courses.json](/data/courses.json) 的 options 裡。

---

今年的特殊規則：三保一

請將已選上的人們寫成 `preselect.json` ，放進 `secret-data/` 資料夾裡，格式如下：

```
{
  "B0X901XXX": ["電力電子"],
  "B0Y901YYY": ["網路與多媒體", "光電"],
  "B0Z901ZZZ": ["網路與多媒體", "數電實驗"],
  ...
}
```

註：數電實驗比較特別，不在 `courses.json` 十選二的 `options` 裡。

---

準備好 `courses.json` ，格式請參考[這裡](/data/courses.json)或[過往資料](/courses_history)。

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
python main.py
```

把 `secret-data/` 資料夾裡的 `results.csv` 給學術部。

註：另外還會生成一份 `analysis.csv`，顯示有幾個人中第幾志願(不含數電和三保一)，一併交給學術部。

## 演算法

系必修：全部都有高年級優先。

電子電路實驗：全部都無高年級優先。

十選二實驗：視個別實驗而定，每個人最多可以中兩個。

演算法核心：把每個人的第 1 志願拿起來排，如果有某個選項爆了的話則要抽籤，抽籤時會考慮每個人的優先度。接著拿大家的第 2 志願起來排，依此類推直到結束。

優先度計算：

1. 每個人的起始優先度是 0
2. 如果遇到有高年級優先的課，根據你是 X 年級優先度加 X (4 年級以上算 4 年級)
3. 如果是大 X 優先而且你是大 X，則你的優先度加 1。
4. 如果該課程可以中複數以上選項(如十選二)，則你的優先度會減掉 (10 \* (你已經中幾個))。
5. 如果遇到需要抽籤的時候，會從高優先度的人開始抽。

數電實驗：選中數電實驗的人算選中一個選項，因此抽籤時優先度會扣十。

三保一：有三保一的人算選中一個選項，優先度扣十，除此之外原先志願序的該格會被設成 None ，無法在該輪進行抽籤。

Example：

假設你的第 1 志願電力電子，第 2 志願半導體，第 3 志願電磁波，如果三保一中半導體且沒有退選，則算你選中一個。在"拿大家的第 1 志願起來排"的階段如果電力電子需要抽籤，則你的優先度會以(-10) 去和別人競爭。在"拿大家的第 2 志願起來排"的階段因為你的第 2 志願被設成 None 故會被直接跳過。

### 優先度抽籤(詳細實作請看 PrioritySampler class)

假設有這些學生要抽籤(key: 學號, value: 優先度)，名額有 3 個

```
{
  "BAAAAAAAA": 0,
  "BBBBBBBBB": 0,
  "BCCCCCCCC": 4,
  "BDDDDDDDD" -10,
  "BEEEEEEEE": 4,
}
```

首先把相同優先度的學生 group 在一起，變成：

```
{
  0: ["BAAAAAAAA", "BBBBBBBBB"],
  4: ["BCCCCCCCC", "BEEEEEEEE"],
  -10: ["BDDDDDDDD"],
}
```

接著從中拿出優先度最高的 group，即是 4 那個 group，因此 "BCCCCCCCC" 和 "BEEEEEEEE" 都會被選上，剩下一個名額。

接著取出優先度第 2 高的 group，即 0 那個 group，裡面有兩個人但只剩一個名額，故隨機抽籤二選一，假設選到 "BBBBBBBBB" 。

此時已沒有名額，故選上的學生為 "BBBBBBBBB"，"BCCCCCCCC", "BEEEEEEEE" 這 3 個。

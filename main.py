from prettytable import PrettyTable
import random
import heapq
import json
import csv

# ========================================


class PrioritySampler:
    """
    A container that can sample based on priority.
    """

    def __init__(self):
        self._students = dict()

    def add(self, student_id, priority):
        # heapq is min heap, so we need to invert the priority
        self._students[student_id] = -priority

    def sample(self, num):
        assert num > 0, "sample num must be positive int"
        if num >= len(self._students):
            return self.popall()

        # group students by priority
        priority_group = dict()
        for student_id, priority in self._students.items():
            priority_group.setdefault(priority, list()).append(student_id)
        # create a priority queue
        priorities = list(priority_group.keys())
        heapq.heapify(priorities)

        sampled = list()
        while num > 0:
            students = priority_group[heapq.heappop(priorities)]
            if len(students) > num:
                students = random.sample(students, num)
            sampled.extend(students)
            num -= len(students)

        for student_id in sampled:
            del self._students[student_id]
        return sampled

    def popall(self):
        ret = list(self._students.keys())
        self._students = dict()
        return ret


class Option:
    def __init__(self, name, limit, priority):
        """
        self._full: 是否已經飽和不能再加更多學生
        self._students: 已經分發中此選項的學生們
        self._priority_sampler: 準備分發到此選項的學生們
        """
        assert type(limit) == int and limit > 0, "limit must be positive int"
        assert type(priority) == bool or \
            (type(priority) == int and priority in [1, 2, 3, 4]), \
            "priority must be bool or 1, 2, 3, 4"
        self._name = name
        self._limit = limit
        self._priority = priority
        self._full = False
        self._students = list()
        self._priority_sampler = PrioritySampler()

    def add_student(self, student_id, student_data):
        if self._full:
            return False
        # priority越大越優先
        priority = 0
        # 超過4年級算4年級
        grade = min(student_data["grade"], 4)

        # 調整priority
        if self._priority is True:
            priority += grade
        if type(self._priority) == int and grade == self._priority:
            priority += 1
        # 如果已經中某些選項的話則降priority
        priority -= 10 * student_data["num"]

        self._priority_sampler.add(student_id, priority)
        return True

    def recover_from_full(self):
        if self._full:
            return []
        space_left = self._limit - len(self._students)
        students_to_be_add = self._priority_sampler.sample(space_left)
        self._students.extend(students_to_be_add)
        if len(self._students) == self._limit:
            self._full = True
        reject = self._priority_sampler.popall()
        return reject


class Course:
    def __init__(self, course):
        """
        self._max_select(int): 每個人最多可以選到幾個option
        """
        self._id = course["id"]
        self._name = course["name"]
        self._options = dict()
        self._max_select = 1  # 一般課程每個人最多只會中一個選項

        for name, config in course["options"].items():
            # 必修全部都有高年級保障
            if course["type"] == "必修":
                option = Option(name, config["limit"], True)
            # 電電實驗全部都無高年級保障
            elif course["type"] == "電電實驗":
                option = Option(name, config["limit"], False)
            # 十選二的priority自己決定(寫在config裡)
            elif course["type"] == "十選二":
                option = Option(name, config["limit"], config["priority"])
                self._max_select = 2  # 十選二每個人最多可以中兩個選項
            else:
                raise ValueError("Invalid course type!")
            self._options[name] = option

    def distribute(self, students, preselect):
        competitors = dict()
        for student in students:
            selection = student["selections"][self._id]
            if selection:
                competitors[student["userID"]] = {
                    "grade": student["grade"],
                    "selection": selection.copy(),
                    "num": 0,  # 這個學生已經選中幾個選項
                }

        # 處理三保一、數電等先抽的課
        if self._id == "Ten-Select-Two":
            self.deal_with_preselect(preselect, competitors)

        # 分發開始
        wish_index = 0  # 現在正在排的是第幾志願
        while competitors:
            # 把大家的志願填進選項裡
            for student_id, student_data in competitors.items():
                wish = student_data["selection"][wish_index]
                # 以下這兩行是三保一的特殊處理
                if wish is None:
                    continue
                if self._options[wish].add_student(student_id, student_data):
                    student_data["num"] += 1
            # 如果選項爆了的話要抽籤
            for option in self._options.values():
                reject = option.recover_from_full()
                for student_id in reject:
                    competitors[student_id]["num"] -= 1
            # 把已經得到最大可中選項的人或已經用完志願的人移除
            to_be_delete = list()
            for student_id, student_data in competitors.items():
                if student_data["num"] > self._max_select:
                    raise ValueError("num exceeds max_select")
                if (student_data["num"] == self._max_select or
                        len(student_data["selection"]) <= wish_index + 1):
                    to_be_delete.append(student_id)
            for student_id in to_be_delete:
                del competitors[student_id]
            wish_index += 1

    def deal_with_preselect(self, preselect, competitors):
        """
        處理三保一、數電等先抽的課

        Note: competitors will be modified
        """
        # 把中數電的人填進數電實驗
        self._options["數電實驗"] = Option("數電實驗", 99999, False)
        to_be_delete = list()
        for student_id, option_names in preselect.items():
            if "數電實驗" in option_names:
                self._options["數電實驗"]._students.append(student_id)
                if student_id in competitors:
                    competitors[student_id]["num"] += 1
                option_names.remove("數電實驗")
        for student_id, option_names in preselect.items():
            if not option_names:
                to_be_delete.append(student_id)
        for student_id in to_be_delete:
            del preselect[student_id]

        # 處理三保一
        for student_id, option_names in preselect.items():
            student_data = competitors[student_id]
            for option_name in option_names:
                self._options[option_name].add_student(student_id, student_data)
                student_data["num"] += 1
                # 把原志願序的該格變成None
                idx = student_data["selection"].index(option_name)
                student_data["selection"][idx] = None

        for option in self._options.values():
            reject = option.recover_from_full()
            assert reject == [], "preselect should not be rejected"

        # 清理(把已經得到最大可中選項的人或已經用完志願的人移除)
        to_be_delete = list()
        for student_id, student_data in competitors.items():
            if student_data["num"] > self._max_select:
                raise ValueError("num exceeds max_select")
            if student_data["num"] == self._max_select:
                to_be_delete.append(student_id)
        for student_id in to_be_delete:
            del competitors[student_id]


# ========================================


def read_courses():
    with open('./data/courses.json') as fin:
        courses = json.load(fin)
    return [Course(course) for course in courses]


def read_selections():
    with open('./secret-data/selections.json') as fin:
        students = json.load(fin)
    for student in students:
        student["userID"] = student["userID"].upper()
    return students


def read_preselect():
    with open('./secret-data/preselect.json') as fin:
        preselect = json.load(fin)
    return preselect

# ========================================


def analyze(courses):
    students = read_selections()
    preselect = read_preselect()

    students_dict = dict()
    for student in students:
        students_dict[student["userID"]] = student

    course_analyses = dict()
    for course in courses:
        competitors = dict()
        for student_id, student in students_dict.items():
            selection = student["selections"][course._id]
            if selection:
                competitors[student_id] = set()
        course_analyses[course._name] = competitors

    for course in courses:
        for option in course._options.values():
            for student_id in option._students:
                if (student_id in preselect and
                        option._name in preselect[student_id]):
                    continue
                student = students_dict[student_id]
                selection = student["selections"][course._id]
                wish_idx = selection.index(option._name)
                course_analyses[course._name][student_id].add(wish_idx + 1)

    rows = list()
    # 有人中到的最大志願
    max_wish = 1
    for students in course_analyses.values():
        for wishes in students.values():
            if not wishes:
                continue
            max_wish = max(max_wish, max(wishes))
    header = ["課程名稱", "中0個", "中1個", "中2個"]
    header.extend([f"第{i}志願" for i in range(1, max_wish + 1)])
    rows.append(header)

    if "十選二實驗" in course_analyses:
        print("不包含數電、三保一:")
    for course_name, students in course_analyses.items():
        row = [0] * len(header)
        row[0] = course_name
        for wishes in students.values():
            assert len(wishes) <= 2, "max wish is 2"
            row[len(wishes) + 1] += 1
            for wish in wishes:
                row[wish + 3] += 1
        rows.append(row)
    print_table(rows)

    if "十選二實驗" in course_analyses:
        print("包含數電、三保一之後的十選二(不含只報名數電沒選十選二的):")
        ten_select_two = course_analyses["十選二實驗"]
        for student_id in preselect:
            for option in preselect[student_id]:
                if option == "數電實驗":
                    continue
                wishes = students_dict[student_id]["selections"]["Ten-Select-Two"]
                wish_idx = wishes.index(option)
                assert (wish_idx + 1) not in ten_select_two[student_id]
                ten_select_two[student_id].add(wish_idx + 1)
        rows = list()
        rows.append(header)
        row = [0] * len(header)
        row[0] = "十選二實驗"
        for wishes in ten_select_two.values():
            assert len(wishes) <= 2, "max wish is 2"
            row[len(wishes) + 1] += 1
            for wish in wishes:
                row[wish + 3] += 1
        rows.append(row)
        print_table(rows)


def print_table(table):
    x = PrettyTable()
    x.field_names = table[0]
    for row in table[1:]:
        x.add_row(row)
    print(x)


def main():
    courses = read_courses()
    students = read_selections()
    preselect = read_preselect()
    for course in courses:
        course.distribute(students, preselect)

    # export
    rows = list()
    rows.append(["student_id", "course_name", "teacher"])
    for course in courses:
        for option in course._options.values():
            for student_id in sorted(option._students):
                if course._id == "Ten-Select-Two":
                    rows.append([student_id, option._name, ""])
                else:
                    rows.append([student_id, course._name, option._name])
    with open("secret-data/result.csv", "w", newline="") as fout:
        writer = csv.writer(fout)
        writer.writerows(rows)

    analyze(courses)

# ========================================


if __name__ == '__main__':
    main()

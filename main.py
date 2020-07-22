import random
import heapq
import json

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
        grade = max(student_data["grade"], 4)

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

    def distribure(self, students):

        if self._id != "Electronics-one":
            return

        print(f"分發： {self._name}...")
        competitors = dict()
        for student in students:
            selection = student["selections"][self._id]
            if selection:
                competitors[student["userID"]] = {
                    "grade": student["grade"],
                    "selection": selection.copy(),
                    "num": 0,  # 這個學生已經選中幾個選項
                }

        wish_index = 0  # 現在正在排的是第幾志願
        while competitors:
            # 把大家的志願填進選項裡
            for student_id, student_data in competitors.items():
                wish = student_data["selection"][wish_index]
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

        for option in self._options.values():
            print(option._name, option._students)


# ========================================


def read_courses():
    with open('./data/courses.json') as fin:
        courses = json.load(fin)
    return [Course(course) for course in courses]


def read_selections():
    with open('./secret-data/selections.json') as fin:
        selections = json.load(fin)
    return selections

# ========================================


def main():
    courses = read_courses()
    students = read_selections()
    for course in courses:
        course.distribure(students)
    # print(selections)

# ========================================


if __name__ == '__main__':
    main()

from enum import Enum


# 給与種別
class SalaryKind(Enum):
    NORMAL = "給与"
    BONUS = "賞与"
    SPECIAL = "特別金"

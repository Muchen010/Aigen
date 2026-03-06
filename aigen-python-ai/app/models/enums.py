"""
枚举类型定义

对应 Java 端: model/enums/CodeGenTypeEnum.java, ImageCategoryEnum.java
"""

from enum import StrEnum


class CodeGenType(StrEnum):
    """代码生成类型枚举。对应 Java: CodeGenTypeEnum.java"""

    HTML = "html"
    MULTI_FILE = "multi_file"
    VUE_PROJECT = "vue_project"


class ImageCategory(StrEnum):
    """图片分类枚举。对应 Java: ImageCategoryEnum.java"""

    HERO = "hero"
    BACKGROUND = "background"
    ICON = "icon"
    ILLUSTRATION = "illustration"
    LOGO = "logo"

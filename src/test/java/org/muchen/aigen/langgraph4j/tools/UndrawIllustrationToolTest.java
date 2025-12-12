package org.muchen.aigen.langgraph4j.tools;

import jakarta.annotation.Resource;
import org.junit.jupiter.api.Test;
import org.muchen.aigen.langgraph4j.model.ImageCategoryEnum;
import org.muchen.aigen.langgraph4j.model.ImageResource;
import org.springframework.boot.test.context.SpringBootTest;

import java.util.List;

import static org.junit.jupiter.api.Assertions.*;

@SpringBootTest
class UndrawIllustrationToolTest {

    @Resource
    private UndrawIllustrationTool undrawIllustrationTool;

    @Test
    void testSearchIllustrations() {
        // 测试正常搜索插画
        List<ImageResource> illustrations = undrawIllustrationTool.searchIllustrations("work");

        // 1. 基础非空检查
        assertNotNull(illustrations, "返回的列表不应为 null");

        // 2. 关键修复：先检查是否有内容，再取值
        // 如果这里失败，JUnit 会提示 "搜索结果为空..."，而不是直接抛出 IndexOutOfBoundsException
        assertFalse(illustrations.isEmpty(), "搜索结果为空，未找到关键词 'happy' 相关的插画");

        // 验证返回的插画资源
        ImageResource firstIllustration = illustrations.get(0); // 现在安全了
        assertEquals(ImageCategoryEnum.ILLUSTRATION, firstIllustration.getCategory());
        assertNotNull(firstIllustration.getDescription());
        assertNotNull(firstIllustration.getUrl());
        assertTrue(firstIllustration.getUrl().startsWith("http"));

        System.out.println("搜索到 " + illustrations.size() + " 张插画");
        illustrations.forEach(illustration ->
                System.out.println("插画: " + illustration.getDescription() + " - " + illustration.getUrl())
        );
    }
}

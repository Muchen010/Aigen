package org.muchen.aigen.langgraph4j;

import jakarta.annotation.Resource;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;
import org.muchen.aigen.langgraph4j.state.WorkflowContext;
import org.muchen.aigen.model.entity.User;
import org.muchen.aigen.model.enums.CodeGenTypeEnum;
import org.springframework.boot.test.context.SpringBootTest;

import static org.junit.jupiter.api.Assertions.*;

@SpringBootTest
class CodeGenWorkflowTest {

    @Resource
    private CodeGenWorkflow codeGenWorkflow;

    @Test
    void testTechBlogWorkflow() {
        // 1. 准备模拟数据
        Long mockAppId = 1002L;
        User mockUser = new User();
        mockUser.setId(2L); // 必须设置 ID，因为 Context 会用到
        mockUser.setUserName("test_admin");

        String prompt = "创建一个技术博客网站，需要展示编程教程和系统架构,代码量不超过200行";

        // 2. 执行工作流
        // 场景 A: 传入 null 让 RouterNode 自动判断类型 (模拟 Service 层未知类型的情况)
        // 场景 B: 传入 CodeGenTypeEnum.HTML 强制指定 (模拟 Service 层已确定的情况)
        System.out.println("=== 开始测试: 技术博客生成 ===");
        WorkflowContext result = codeGenWorkflow.executeWorkflow(
                mockAppId,
                prompt,
                mockUser,
                null // 传入 null，测试 RouterNode 的智能路由能力
        );

        // 3. 验证结果
        Assertions.assertNotNull(result);
        Assertions.assertNotNull(result.getGeneratedCodeDir(), "生成代码目录不应为空");

        System.out.println("--------------------------------------------------");
        System.out.println("最终生成类型: " + result.getGenerationType());
        System.out.println("生成的代码目录: " + result.getGeneratedCodeDir());
        System.out.println("构建结果目录: " + result.getBuildResultDir());
        System.out.println("--------------------------------------------------");
    }

    @Test
    void testVueProjectWorkflow() {
        // 1. 准备模拟数据
        Long mockAppId = 1002L;
        User mockUser = new User();
        mockUser.setId(1L);

        String prompt = "创建一个Vue前端项目，包含用户管理和数据展示功能";

        // 2. 执行工作流 (强制指定为 VUE_PROJECT)
        System.out.println("=== 开始测试: Vue 项目生成 ===");
        WorkflowContext result = codeGenWorkflow.executeWorkflow(
                mockAppId,
                prompt,
                mockUser,
                CodeGenTypeEnum.VUE_PROJECT // 强制指定类型，跳过 Router 分析
        );

        // 3. 验证结果
        Assertions.assertNotNull(result);
        // Vue 项目应该会有 buildResultDir (如果构建成功)
        // 注意：本地测试如果没有安装 Node.js 环境，构建可能会失败，这里视环境而定
        if (result.getBuildResultDir() != null) {
            System.out.println("Vue 项目构建成功，产物目录: " + result.getBuildResultDir());
        } else {
            System.err.println("Vue 项目构建未产生结果 (可能是环境缺少 Node.js 或构建失败)");
        }

        Assertions.assertEquals(CodeGenTypeEnum.VUE_PROJECT, result.getGenerationType());
    }
}

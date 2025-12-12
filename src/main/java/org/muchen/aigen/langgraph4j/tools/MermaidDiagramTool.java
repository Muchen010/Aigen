package org.muchen.aigen.langgraph4j.tools;

import cn.hutool.core.io.FileUtil;
import cn.hutool.core.util.RandomUtil;
import cn.hutool.core.util.RuntimeUtil;
import cn.hutool.core.util.StrUtil;
import cn.hutool.system.SystemUtil;
import dev.langchain4j.agent.tool.P;
import dev.langchain4j.agent.tool.Tool;
import jakarta.annotation.Resource;
import lombok.extern.slf4j.Slf4j;
import org.muchen.aigen.exception.BusinessException;
import org.muchen.aigen.exception.ErrorCode;
import org.muchen.aigen.langgraph4j.model.ImageCategoryEnum;
import org.muchen.aigen.langgraph4j.model.ImageResource;
import org.muchen.aigen.manager.CosManager;
import org.springframework.stereotype.Component;

import java.io.File;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

@Slf4j
@Component
public class MermaidDiagramTool {

    @Resource
    private CosManager cosManager;

    // 如果不指定这个，mmdc 因为没有下载内置浏览器会直接报错
    private static final String PUPPETEER_CONFIG_PATH = "D:\\language\\JAVA\\Aigen\\puppeteer-config.json";

    @Tool("将 Mermaid 代码转换为架构图图片，用于展示系统结构和技术关系")
    public List<ImageResource> generateMermaidDiagram(@P("Mermaid 图表代码") String mermaidCode,
                                                      @P("架构图描述") String description) {
        if (StrUtil.isBlank(mermaidCode)) {
            return new ArrayList<>();
        }
        try {
            // 转换为SVG图片
            File diagramFile = convertMermaidToSvg(mermaidCode);
            // 上传到COS
            String keyName = String.format("/mermaid/%s/%s",
                    RandomUtil.randomString(5), diagramFile.getName());
            String cosUrl = cosManager.uploadFile(keyName, diagramFile);
            // 清理临时文件
            FileUtil.del(diagramFile);
            if (StrUtil.isNotBlank(cosUrl)) {
                return Collections.singletonList(ImageResource.builder()
                        .category(ImageCategoryEnum.ARCHITECTURE)
                        .description(description)
                        .url(cosUrl)
                        .build());
            }
        } catch (Exception e) {
            log.error("生成架构图失败: {}", e.getMessage(), e);
            // 这里为了让测试能通过或者显式看到错误，建议不吞掉异常，或者确保返回空列表
        }
        return new ArrayList<>();
    }

    /**
     * 将Mermaid代码转换为SVG图片
     */
    private File convertMermaidToSvg(String mermaidCode) {
        // 创建临时输入文件
        File tempInputFile = FileUtil.createTempFile("mermaid_input_", ".mmd", true);
        FileUtil.writeUtf8String(mermaidCode, tempInputFile);

        // 创建临时输出文件
        File tempOutputFile = FileUtil.createTempFile("mermaid_output_", ".svg", true);

        // 1. 确定命令名
        String command = SystemUtil.getOsInfo().isWindows() ? "mmdc.cmd" : "mmdc";

        // 2. 构建命令列表 (使用 ProcessBuilder 方式更安全，避免空格路径问题)
        // 命令格式: mmdc -i input.mmd -o output.svg -b transparent -p config.json
        List<String> cmdList = new ArrayList<>();
        cmdList.add(command);
        cmdList.add("-i");
        cmdList.add(tempInputFile.getAbsolutePath());
        cmdList.add("-o");
        cmdList.add(tempOutputFile.getAbsolutePath());
        cmdList.add("-b");
        cmdList.add("transparent");

        // 重要：添加浏览器配置文件路径
        if (FileUtil.exist(PUPPETEER_CONFIG_PATH)) {
            cmdList.add("-p");
            cmdList.add(PUPPETEER_CONFIG_PATH);
        } else {
            log.warn("未找到 Puppeteer 配置文件: {}, mmdc 可能会因为找不到浏览器而失败", PUPPETEER_CONFIG_PATH);
        }

        try {
            log.info("执行 Mermaid 命令: {}", String.join(" ", cmdList));

            // 3. 执行命令并获取 Process 对象
            Process process = new ProcessBuilder(cmdList)
                    .redirectErrorStream(true) // 合并标准输出和错误输出
                    .start();

            // 读取输出流（防止缓冲区满导致挂起，同时获取错误日志）
            String output = RuntimeUtil.getResult(process, StandardCharsets.UTF_8);
            int exitCode = process.waitFor();

            if (exitCode != 0) {
                log.error("Mermaid CLI 执行异常，退出码: {}, 输出日志:\n{}", exitCode, output);
                throw new BusinessException(ErrorCode.SYSTEM_ERROR, "Mermaid CLI 执行失败: " + output);
            }

            // 4. 检查输出文件
            if (!tempOutputFile.exists() || tempOutputFile.length() == 0) {
                log.error("Mermaid CLI 执行看似成功但文件为空。CLI日志:\n{}", output);
                throw new BusinessException(ErrorCode.SYSTEM_ERROR, "Mermaid CLI 生成了空文件");
            }
        } catch (Exception e) {
            // 如果是 BusinessException 直接抛出，其他的包装一下
            if (e instanceof BusinessException) {
                throw (BusinessException) e;
            }
            throw new BusinessException(ErrorCode.SYSTEM_ERROR, "Mermaid 转换过程出错: " + e.getMessage());
        } finally {
            // 清理输入文件
            FileUtil.del(tempInputFile);
        }

        return tempOutputFile;
    }
}
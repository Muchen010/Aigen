package org.muchen.aigen;

import org.mybatis.spring.annotation.MapperScan;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
@MapperScan("org.muchen.aigen.mapper")
public class AigenApplication {

	public static void main(String[] args) {
		SpringApplication.run(AigenApplication.class, args);
	}

}

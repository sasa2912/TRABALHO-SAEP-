CREATE DATABASE IF NOT EXISTS `saep_db` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE `saep_db`;

SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS `agendamento`;
DROP TABLE IF EXISTS `pet`;
DROP TABLE IF EXISTS `tutor`;
DROP TABLE IF EXISTS `usuario`;
SET FOREIGN_KEY_CHECKS = 1;


CREATE TABLE `usuario` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `nome` VARCHAR(100) NOT NULL,
    `email` VARCHAR(100) NOT NULL UNIQUE,
    `senha` VARCHAR(255) NOT NULL,
    `cargo` VARCHAR(50) NOT NULL,
    `criado_em` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


CREATE TABLE `tutor` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `nome` VARCHAR(120) NOT NULL,
    `cpf` VARCHAR(255) NOT NULL,
    `telefone` VARCHAR(20) NOT NULL,
    `email` VARCHAR(100) NOT NULL,
    `endereco` VARCHAR(200) NOT NULL,
    `criado_em` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


CREATE TABLE `pet` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `tutor_id` INT NOT NULL,
    `nome` VARCHAR(80) NOT NULL,
    `especie` VARCHAR(50) NOT NULL,
    `raca` VARCHAR(50) NOT NULL,
    `data_nascimento` DATE NOT NULL,
    `peso` DECIMAL(5,2) NOT NULL,
    `observacoes` TEXT,
    `criado_em` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT `fk_pet_tutor` FOREIGN KEY (`tutor_id`) REFERENCES `tutor` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


CREATE TABLE `agendamento` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `pet_id` INT NOT NULL,
    `data_agendamento` DATE NOT NULL,
    `hora_agendamento` TIME NOT NULL,
    `tipo_servico` VARCHAR(100) NOT NULL,
    `status` VARCHAR(30) NOT NULL DEFAULT 'Agendado',
    `observacoes` TEXT,
    `criado_em` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT `fk_agendamento_pet` FOREIGN KEY (`pet_id`) REFERENCES `pet` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


INSERT INTO `usuario` (`id`, `nome`, `email`, `senha`, `cargo`) VALUES
(1, 'Dra. Camila Silveira', 'camila.vet@clinica.com', 'scrypt:32768:8:1$1QnmUJ4hPeKDAVIx$fe65ee32cdd01148c6480cbb9c2c22d24fa35c28ef34e717d48160fceaa2bb6725df97661550e8ad2b716c763a7680f1eaddfc713ca21ef0467084a5b78f7bcc', 'Médica Veterinária'),
(2, 'Dr. Roberto Albuquerque', 'roberto.vet@clinica.com', 'scrypt:32768:8:1$wUWEWZiu70Q1F4dK$843755d52de3b692b6e34009f75cab7c2c9ffc03274f8f9a8bff9dc951eea9fb1c876126d7dd302095b385aa8399c2c3e3293a1442ae87f0ee4ef06ff1a3bace', 'Médico Veterinário'),
(3, 'Ana Paula Souza', 'recepcao@clinica.com', 'scrypt:32768:8:1$6XdtBjnDZfRUUkpT$3e00c34ba622f367469bf1ed01cccd77942c46f82f1e164bacdbef9cc756a9da68507c29c7c3d3771794de7dacfd5565c1a7bdf61014fc15b3f2edb77676e3e1', 'Recepcionista');

INSERT INTO `tutor` (`id`, `nome`, `cpf`, `telefone`, `email`, `endereco`) VALUES
(1, 'Mariana Fernandes Costa', 'gAAAAABq-ujEJ3dk2c_SP-lrCSX84yjlrRmyjWVun4QLM3tzana7jBQaAQymp6SDcvp4uV0RCaZsKtK_F0UWN9e6x9sisCpI3Q==', '(11) 98765-4321', 'mariana.costa@email.com', 'Rua das Flores, 120 - Jardins, São Paulo/SP'),
(2, 'Carlos Eduardo Santos', 'gAAAAABq-ujETraUp_1wKpazw_SUEoM7fS9S1lh7o8BAQIcz3ybBKNqphapzQ9ELZwqhfTwgxD9ZlVPc9WpeAjCD9-3cKz5H7Q==', '(11) 97654-3210', 'carlos.santos@email.com', 'Av. Paulista, 1500, Apto 82 - Bela Vista, São Paulo/SP'),
(3, 'Beatriz Lima Oliveira', 'gAAAAABq-ujERckKRJegOqLLdmt_M98iTlxyTiZAW70r9K2gx4okbGrlw5ayXQr9dhS8ChUuD5mSY04zb_ry3HM1uOLfMHU9yQ==', '(11) 96543-2109', 'beatriz.oliveira@email.com', 'Rua dos Pinheiros, 450 - Pinheiros, São Paulo/SP'),
(4, 'Rodrigo Mendes Rocha', 'gAAAAABq-ujEN-n4ee1ncq9nG24p19H4qXqk0y5ytrQlAC8g6GhBtcKovQImqW4aNz3QZ-c-Db7P9-xuQHkQKCPNCvx8Y2_5HQ==', '(11) 95432-1098', 'rodrigo.rocha@email.com', 'Rua Augusta, 980 - Consolação, São Paulo/SP');

INSERT INTO `pet` (`id`, `tutor_id`, `nome`, `especie`, `raca`, `data_nascimento`, `peso`, `observacoes`) VALUES
(1, 1, 'Thor', 'Canina', 'Golden Retriever', '2021-04-10', 32.50, 'Dócil e brincalhão. Alergia leve a pulgas, acompanhamento dermatológico.'),
(2, 1, 'Luna', 'Felina', 'Siamês', '2022-08-15', 4.20, 'Muito calma. Carteira de vacinação rigorosamente em dia.'),
(3, 2, 'Bob', 'Canina', 'Poodle Toy', '2020-01-20', 5.80, 'Cardiopata leve, necessita acompanhamento periódico e exames regulares.'),
(4, 3, 'Mel', 'Felina', 'Persa', '2023-02-11', 3.90, 'Pelagem longa, cuidados oftalmológicos preventivos diários.'),
(5, 4, 'Pipoca', 'Ave', 'Calopsita', '2022-11-05', 0.09, 'Necessita de corte periódico preventivo das penas das asas.');

INSERT INTO `agendamento` (`id`, `pet_id`, `data_agendamento`, `hora_agendamento`, `tipo_servico`, `status`, `observacoes`) VALUES
(1, 1, '2026-11-20', '09:00:00', 'Consulta Clínica Geral', 'Confirmado', 'Check-up semestral completo e pesagem de rotina.'),
(2, 2, '2026-11-20', '10:30:00', 'Vacinação Antirrábica e V5', 'Agendado', 'Reforço anual de vacinas quádrupla e antirrábica.'),
(3, 3, '2026-11-21', '14:00:00', 'Exame Cardiológico / Ecodoppler', 'Confirmado', 'Avaliação periódica com cardiologista veterinário.'),
(4, 4, '2026-11-22', '11:00:00', 'Limpeza de Tártaro / Profilaxia', 'Agendado', 'Procedimento odontológico com anestesia inalatória.'),
(5, 5, '2026-11-23', '16:00:00', 'Consulta Especializada de Aves', 'Agendado', 'Aparar penas e verificar saúde geral das penas e bico.');



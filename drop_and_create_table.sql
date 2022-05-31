USE `fantrax`;

DROP TABLE IF EXISTS `player_match`;

CREATE TABLE `player_match` (
	`id` INT(10) NOT NULL AUTO_INCREMENT,
	`season` CHAR(9) NULL DEFAULT NULL COLLATE 'utf8mb4_0900_ai_ci',
	`player` VARCHAR(250) NULL DEFAULT NULL COLLATE 'utf8mb4_0900_ai_ci',
	`position` CHAR(1) NULL DEFAULT NULL COLLATE 'utf8mb4_0900_ai_ci',
	`date` DATE NULL DEFAULT NULL,
	`team` CHAR(3) NULL DEFAULT NULL COLLATE 'utf8mb4_0900_ai_ci',
	`opp` CHAR(3) NULL DEFAULT NULL COLLATE 'utf8mb4_0900_ai_ci',
	`where` CHAR(1) NULL DEFAULT NULL COLLATE 'utf8mb4_0900_ai_ci',
	`score` VARCHAR(5) NULL DEFAULT NULL COLLATE 'utf8mb4_0900_ai_ci',
	`min` INT(10) NULL DEFAULT NULL,
	`fpts` FLOAT NULL DEFAULT NULL,
	`ghost_fpts` FLOAT NULL DEFAULT NULL,
	`adjusted_fpts` FLOAT NULL DEFAULT NULL,
	`adjusted_ghost_fpts` FLOAT NULL DEFAULT NULL,
	`g` INT(10) NULL DEFAULT NULL,
	`at` INT(10) NULL DEFAULT NULL,
	`cs` INT(10) NULL DEFAULT NULL,
	`s` INT(10) NULL DEFAULT NULL,
	`sot` INT(10) NULL DEFAULT NULL,
	`kp` INT(10) NULL DEFAULT NULL,
	`cos` INT(10) NULL DEFAULT NULL,
	`acnc` INT(10) NULL DEFAULT NULL,
	`tkw` INT(10) NULL DEFAULT NULL,
	`int` INT(10) NULL DEFAULT NULL,
	`bs` INT(10) NULL DEFAULT NULL,
	`clr` INT(10) NULL DEFAULT NULL,
	`aer` INT(10) NULL DEFAULT NULL,
	`dis` INT(10) NULL DEFAULT NULL,
	`erg` INT(10) NULL DEFAULT NULL,
	`yc` INT(10) NULL DEFAULT NULL,
	`rc` INT(10) NULL DEFAULT NULL,
	`pkm` INT(10) NULL DEFAULT NULL,
	`pkd` INT(10) NULL DEFAULT NULL,
	`og` INT(10) NULL DEFAULT NULL,
	`gao` INT(10) NULL DEFAULT NULL,
	PRIMARY KEY (`id`) USING BTREE,
	INDEX `season` (`season`) USING BTREE,
	INDEX `player` (`player`) USING BTREE,
	INDEX `position` (`position`) USING BTREE,
	INDEX `date` (`date`) USING BTREE,
	INDEX `team` (`team`) USING BTREE,
	INDEX `opp` (`opp`) USING BTREE,
	INDEX `where` (`where`) USING BTREE
)
COLLATE='utf8mb4_0900_ai_ci'
ENGINE=InnoDB
ROW_FORMAT=DYNAMIC;
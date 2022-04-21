USE `fantrax`;

SELECT MAX(`season`) INTO @latest_season FROM player_match;

DELETE FROM `player_match`
WHERE `season` = @latest_season;
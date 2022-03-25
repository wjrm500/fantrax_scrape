SELECT AVG(`fpts`) INTO @avg_fpts
     , AVG(`ghost_fpts`) INTO @avg_ghost_fpts
FROM fantrax.player_match_2;

DROP TEMPORARY TABLE IF EXISTS temp;

CREATE TEMPORARY TABLE temp AS
	SELECT `opp`
		  , `where`
		  , `position`
		  , AVG(`fpts`) AS `group_avg_fpts`
		  , AVG(`ghost_fpts`) AS `group_avg_ghost_fpts`
	FROM fantrax.player_match_2
	GROUP BY `opp`, `where`, `position`;

ALTER TABLE fantrax.player_match_2
	ADD adjusted_fpts FLOAT AFTER ghost_fpts,
	ADD adjusted_ghost_fpts FLOAT AFTER adjusted_fpts;

UPDATE fantrax.player_match_2 AS pm
	JOIN temp AS t
		ON pm.`opp` = t.`opp`
			AND pm.`where` = t.`where`
			AND pm.`position` = t.`position`;
SET adjusted_fpts = ROUND(pm.`fpts` - t.`group_avg_fpts` + @avg_fpts, 2),
	adjusted_ghost_fpts = ROUND(pm.`ghost_fpts` - t.`group_avg_ghost_fpts` + @avg_ghost_fpts, 2);
/* Get average points and ghost points across all matches */

SELECT AVG(`fpts`), AVG(`ghost_fpts`) INTO @avg_fpts, @avg_ghost_fpts
FROM fantrax.player_match_2;

/*
Get average points and ghost points by "situation"

Why?
	Values used to adjust points, according to situational difficulty. For example, a forward playing at home against Norwich
	in the 2021-22 season is likely to score more points than a forward playing away against Liverpool in the same season.
	Therefore, we work out for example the average score of forwards playing at home against Norwich in the 2021-22 season,
	and use this to modulate the fpts value of all records where this situation is observed.

Why multiple subqueries?
	The subquery SQ1 in the query below was originally the entire temp table here, but I realised that grouping by four
	dimensions led to some small group sizes with outlandish data, particularly when you go back multiple seasons - this is
	because the data only includes 2021-22 Premier League players, not players who were active at the time, which means that
	any match data for the 2013-14 season, for example, only includes players who played in both 2013-14 and 2021-22, of
	which there are few. By knocking out a grouping field in each subsequent subquery, each situation can be assigned the
	average points and ghost points values from the most specific "large" group it belongs to (with large being defined as
	having at least 50 data points), to avoid having to use outlandish data to adjust with.
*/

DROP TEMPORARY TABLE IF EXISTS temp;

CREATE TEMPORARY TABLE temp AS
	SELECT sq1.`season`
		, sq1.`opp`
		, sq1.`where`
		, sq1.`position`
		, CASE WHEN sq1.`count` > 50 THEN 'sq1'
					WHEN sq2.`count` > 50 THEN 'sq2'
					WHEN sq3.`count` > 50 THEN 'sq3'
					ELSE 'sq4'
					END AS `subquery`
		, CASE WHEN sq1.`count` > 50 THEN sq1.`group_avg_fpts`
					WHEN sq2.`count` > 50 THEN sq2.`group_avg_fpts`
					WHEN sq3.`count` > 50 THEN sq3.`group_avg_fpts`
					ELSE sq4.`group_avg_fpts`
					END AS `group_avg_fpts`
		, CASE WHEN sq1.`count` > 50 THEN sq1.`group_avg_ghost_fpts`
					WHEN sq2.`count` > 50 THEN sq2.`group_avg_ghost_fpts`
					WHEN sq3.`count` > 50 THEN sq3.`group_avg_ghost_fpts`
					ELSE sq4.`group_avg_ghost_fpts`
					END AS `group_avg_ghost_fpts`
	FROM (
			SELECT `season`
				, `opp`
				, `where`
				, `position`
				, AVG(`fpts`) AS `group_avg_fpts`
				, AVG(`ghost_fpts`) AS `group_avg_ghost_fpts`
				, COUNT(*) AS `count`
			FROM fantrax.player_match_2
			GROUP BY `season`, `opp`, `where`, `position`
			) AS sq1
		JOIN (
			SELECT `season`
				, `opp`
				, `position`
				, AVG(`fpts`) AS `group_avg_fpts`
				, AVG(`ghost_fpts`) AS `group_avg_ghost_fpts`
				, COUNT(*) AS `count`
			FROM fantrax.player_match_2
			GROUP BY `season`, `opp`, `position`
			) AS sq2
			ON sq1.`season` = sq2.`season`
				AND sq1.`opp` = sq2.`opp`
				AND sq1.`position` = sq2.`position`
		JOIN (
			SELECT `season`
				, `opp`
				, AVG(`fpts`) AS `group_avg_fpts`
				, AVG(`ghost_fpts`) AS `group_avg_ghost_fpts`
				, COUNT(*) AS `count`
			FROM fantrax.player_match_2
			GROUP BY `season`, `opp`
			) AS sq3
			ON sq1.`season` = sq3.`season`
				AND sq1.`opp` = sq3.`opp`
		JOIN (
			SELECT `opp`
				, AVG(`fpts`) AS `group_avg_fpts`
				, AVG(`ghost_fpts`) AS `group_avg_ghost_fpts`
				, COUNT(*) AS `count`
			FROM fantrax.player_match_2
			GROUP BY `opp`
			) AS sq4
			ON sq1.`opp` = sq4.`opp`;

/* Add columns with adjusted data */

ALTER TABLE fantrax.player_match_2
	ADD adjusted_fpts FLOAT AFTER ghost_fpts,
	ADD adjusted_ghost_fpts FLOAT AFTER adjusted_fpts;

UPDATE fantrax.player_match_2 AS pm
	JOIN temp AS t
		ON pm.`season` = t.`season`
			AND pm.`opp` = t.`opp`
			AND pm.`where` = t.`where`
			AND pm.`position` = t.`position`
SET adjusted_fpts = ROUND(pm.`fpts` - t.`group_avg_fpts` + @avg_fpts, 2),
	adjusted_ghost_fpts = ROUND(pm.`ghost_fpts` - t.`group_avg_ghost_fpts` + @avg_ghost_fpts, 2);

/*
Adjust adjusted points to counteract temporal effects of adjusting points

Why?
	I noticed that adjusting the points led to a downwards adjustment in historic seasons and an upwards adjustment in more
	recent seasons. I wanted to counteract this effect.
*/

DROP TEMPORARY TABLE IF EXISTS temp;

CREATE TEMPORARY TABLE temp AS
	SELECT @num := @num + 1 AS `rank`
		  , sq.*
	FROM (
			SELECT YEAR(`date`) AS `year`
				  , MONTH(`date`) AS `month`
				  , AVG(adjusted_fpts - fpts) AS avg_adjustment
			FROM fantrax.player_match_2
			GROUP BY YEAR(`date`), MONTH(`date`)
			ORDER BY YEAR(`date`), MONTH(`date`)
			) AS sq
	JOIN (SELECT @num := 0) AS dummy;

DROP TEMPORARY TABLE IF EXISTS temp2;

CREATE TEMPORARY TABLE temp2 AS SELECT * FROM temp;

DROP TEMPORARY TABLE IF EXISTS temp3;

CREATE TEMPORARY TABLE temp3 AS
	SELECT t.*
		  , AVG(t2.avg_adjustment) AS avg_avg_adjustment
	FROM temp AS t
		JOIN temp2 AS t2
			ON t2.`rank` BETWEEN t.`rank` - 4 AND t.`rank`
	GROUP BY t.`rank`
	ORDER BY t.`rank`;

UPDATE fantrax.player_match_2 AS pm
	JOIN temp3 AS t
		ON YEAR(pm.`date`) = t.`year`
			AND MONTH(pm.`date`) = t.`month`
SET adjusted_fpts = ROUND(pm.`adjusted_fpts` - t.avg_avg_adjustment, 2),
	adjusted_ghost_fpts = ROUND(pm.`adjusted_ghost_fpts` - t.avg_avg_adjustment, 2);
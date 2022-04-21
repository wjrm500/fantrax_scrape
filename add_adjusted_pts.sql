/* Get average points and ghost points across all matches */

DROP TEMPORARY TABLE IF EXISTS temp;

CREATE TEMPORARY TABLE temp AS
	SELECT `season`
		  , AVG(`fpts`) AS `avg_fpts`
		  , AVG(`ghost_fpts`) AS `avg_ghost_fpts`
	FROM fantrax.player_match
	GROUP BY `season`;

ALTER TABLE temp
	ADD INDEX season_idx(`season`);

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

DROP TEMPORARY TABLE IF EXISTS temp2;

CREATE TEMPORARY TABLE temp2 AS
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
			FROM fantrax.player_match
			GROUP BY `season`, `opp`, `where`, `position`
			) AS sq1
		JOIN (
			SELECT `season`
				, `opp`
				, `position`
				, AVG(`fpts`) AS `group_avg_fpts`
				, AVG(`ghost_fpts`) AS `group_avg_ghost_fpts`
				, COUNT(*) AS `count`
			FROM fantrax.player_match
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
			FROM fantrax.player_match
			GROUP BY `season`, `opp`
			) AS sq3
			ON sq1.`season` = sq3.`season`
				AND sq1.`opp` = sq3.`opp`
		JOIN (
			SELECT `opp`
				, AVG(`fpts`) AS `group_avg_fpts`
				, AVG(`ghost_fpts`) AS `group_avg_ghost_fpts`
				, COUNT(*) AS `count`
			FROM fantrax.player_match
			GROUP BY `opp`
			) AS sq4
			ON sq1.`opp` = sq4.`opp`;
		
ALTER TABLE temp2
	ADD INDEX season_idx(`season`),
	ADD INDEX opp_idx(`opp`),
	ADD INDEX where_idx(`where`),
	ADD INDEX position_idx(`position`);

/* Add columns with adjusted data */

/*ALTER TABLE fantrax.player_match
	ADD adjusted_fpts FLOAT AFTER ghost_fpts,
	ADD adjusted_ghost_fpts FLOAT AFTER adjusted_fpts;*/

UPDATE fantrax.player_match AS pm
	JOIN temp AS t
		ON pm.`season` = t.`season`
	JOIN temp2 AS t2
		ON pm.`season` = t2.`season`
			AND pm.`opp` = t2.`opp`
			AND pm.`where` = t2.`where`
			AND pm.`position` = t2.`position`
SET adjusted_fpts = ROUND(pm.`fpts` - t2.`group_avg_fpts` + t.`avg_fpts`, 2),
	adjusted_ghost_fpts = ROUND(pm.`ghost_fpts` - t2.`group_avg_ghost_fpts` + t.`avg_ghost_fpts`, 2);
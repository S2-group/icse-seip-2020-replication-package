-- Generic Terminal command
-- mysql -u root -p ghtorrent_restore -e "QUERY" > FILE 

-- 0a - Search all projects containing the ROS keyword (as a whole word) in either their name or description:

select count(*) from projects where description REGEXP '([[:blank:][:punct:]]|^)ROS([[:blank:][:punct:]]|$)' or name REGEXP '([[:blank:][:punct:]]|^)ROS([[:blank:][:punct:]]|$)'; 

-- 0b - Search all projects whose topic is also ROS

SELECT * FROM (
(select * from projects ) as t1
INNER JOIN 
(select * from project_topics WHERE topic_name = "ROS") as t2
ON t1.id = t2.project_id)

-- 0c - union of 0a and 0b

SELECT * from 
(select * from projects where description REGEXP '([[:blank:][:punct:]]|^)ROS([[:blank:][:punct:]]|$)' or name REGEXP '([[:blank:][:punct:]]|^)ROS([[:blank:][:punct:]]|$)') as t3
UNION 
(SELECT id, url, owner_id, name, description, language, created_at, forked_from, deleted, updated_at FROM (
(select * from projects) as t1
INNER JOIN 
(select project_id from project_topics WHERE topic_name = 'ROS') as t2
ON t1.id = t2.project_id)) 
;

-- 1 - Filter  fork repositories

SELECT * from 
(select * from projects where description REGEXP '([[:blank:][:punct:]]|^)ROS([[:blank:][:punct:]]|$)' or name REGEXP '([[:blank:][:punct:]]|^)ROS([[:blank:][:punct:]]|$)' or forked_from IS NULL) as t3
UNION 
(SELECT id, url, owner_id, name, description, language, created_at, forked_from, deleted, updated_at FROM (
(select * from projects) as t1
INNER JOIN 
(select project_id from project_topics WHERE topic_name = 'ROS') as t2
ON t1.id = t2.project_id))

-- 1a - Save the currently-selected repositories into the projects_ros_no_forks table

INSERT INTO projects_ros_no_forks SELECT * from 
(select * from projects where (description REGEXP '([[:blank:][:punct:]]|^)ROS([[:blank:][:punct:]]|$)' or name REGEXP '([[:blank:][:punct:]]|^)ROS([[:blank:][:punct:]]|$)') and forked_from IS NULL) as t3
UNION 
(SELECT id, url, owner_id, name, description, language, created_at, forked_from, deleted, updated_at FROM (
(select * from projects) as t1
INNER JOIN 
(select project_id from project_topics WHERE topic_name = 'ROS') as t2
ON t1.id = t2.project_id));

-- 2 - Filter  repositories with #commits < 100

select * FROM projects_ros_no_forks WHERE deleted = 0;SELECT * FROM (select projects_ros_no_forks.*, count(commits.project_id) as number_of_commits
from projects_ros_no_forks
left join commits
on (projects_ros_no_forks.id = commits.project_id)
group by
projects_ros_no_forks.id) as t WHERE t.number_of_commits >= 100;

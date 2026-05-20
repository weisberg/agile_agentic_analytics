select owner, count(*) as open_tasks
from sample_tasks
where status = 'open'
group by owner
order by open_tasks desc;


.load ./hurtledemo
create virtual table temp.csv using csv(filename=demo/codes.csv);
select * from csv where not term like '%allergy%' limit 5;
select '---';
select * from csv where not term like '%allergy%' limit 5;
select '---';
create virtual table temp.github_issues
using github_issues(organisation=opensafely-core, repo=databuilder);
select * from github_issues where state = 'closed' and updated_at >= "2022-06-06";
select '---';
select * from github_issues where number = 123;
select '---';
select * from github_issues where number = 12345;
select '---';
select * from github_issues;

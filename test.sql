.load seriespy
select('---');
select value from generate_series(0, 6, 2);
select('---');
select * from generate_series(0, 6, 2) order by value desc;
select('---');
select * from generate_series(6, 0, -2) order by value desc;
select('---');
select * from generate_series(6, 0, -2) order by value;
select('---');
select * from generate_series where start = 0 and stop = 10;
select('---');
select * from generate_series where stop = 10 and start = 0;
select('---');
select rowid, value, start, stop, step from generate_series where stop = 10 and start = 0 and step = 2;
select * from generate_series where start = 0 order by stop;

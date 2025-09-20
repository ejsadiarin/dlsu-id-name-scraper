select * from students;
select count(*) from students;
select * from students where name is not '';
select count(*) from students where name is not '';

-- 12303003

select * from students where name like lower('%edwin%');

-- see record anomalies
select * from students where name like lower('%submitted%') or name like 'NOT%' or name like '%LAST NAME%' or name like lower('%dtcf%') or name like lower('id number');

select count(*) from students where name like lower('%submitted%') or name like 'NOT%' or name like '%LAST NAME%' or name like lower('%dtcf%') or name like lower('id number');

UPDATE students SET name = '' WHERE id = ;

-- clean LAST NAME, FIRST NAME
UPDATE students SET name = '' WHERE name = 'LAST NAME, FIRST NAME';

DELETE from students where id in (12328685,12328693,12328707)

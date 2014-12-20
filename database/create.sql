create table img (
img_no int,
img_date datetime,
img_name varchar(255),
mail varchar(255),
subject varchar(255),
comment text,
url varchar(255),
host varchar(255),
password varchar(255),
ext varchar(255),
width int,
height int,
img_time varchar(255),
checksum varchar(255),
primary key (img_no),
key idx_date_no_subject (img_date, img_no, subject)
);

create table tree (
head_img_no int,
img_nos text,
img_count int,
primary key (head_img_no)
);

create table tweet (
target_name varchar(255),
img_no int,
img_count int,
status int,
retry_count int default 0,
primary key (target_name, img_no, img_count)
);

show tables;

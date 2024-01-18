-- create database TaskA;
create database TaskA;
use TaskA;
create table if not exists `user` (
    `id` int(11) not null auto_increment,
    `username` varchar(36) not null,
    `password` varchar(255) not null,
    `product_url` varchar(255) not null,
    `systhesis_url` varchar(255) null,
    `session_id` varchar(255) null,
    `created_at` timestamp not null default current_timestamp,
    `updated_at` timestamp not null default current_timestamp on update current_timestamp,
    primary key (`id`)
) engine=InnoDB default charset=utf8mb4;

create table if not exists logo (
    `id` int(11) not null auto_increment,
    `user_id` int(11) not null,
    `url` varchar(255) not null,
    `created_at` timestamp not null default current_timestamp,
    `updated_at` timestamp not null default current_timestamp on update current_timestamp,
    primary key (`id`),
    foreign key (`user_id`) references `user` (`id`)
) engine=InnoDB default charset=utf8mb4;

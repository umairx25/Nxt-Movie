
USE NxtMovie;

ALTER TABLE movies MODIFY COLUMN id INT PRIMARY KEY AUTO_INCREMENT;

create table movies
(
    id          int PRIMARY KEY (AUTO_INCREMENT),
    title       varchar(50),
    image       varchar(100),
    release     int,
    rating      varchar(20),
    metacritic  decimal,
    description varchar(500),
    audience    decimal,
    directors   varchar(50),
    runtime     varchar(15),
    genres      varchar(400)
    CONSTRAINT AUTO_INCREMENT id
);
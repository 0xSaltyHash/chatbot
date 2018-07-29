CREATE TABLE user_preference (
    fb_id INTEGER NOT NULL,
    subject INTEGER DEFAULT NULL,
    UNIQUE(fb_id, subject)
);

CREATE TABLE subject(
    sub_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    date_of_birth TEXT NOT NULL,
    bio TEXT NOT NULL
);


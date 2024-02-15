BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "book" (
	"book_id"	INTEGER NOT NULL,
	"book_name"	VARCHAR(50),
	"author"	VARCHAR(6),
	"content"	VARCHAR(100),
	"cover"	VARCHAR(100),
	"price"	FLOAT,
	"section_id"	INTEGER,
	PRIMARY KEY("book_id"),
	FOREIGN KEY("section_id") REFERENCES "section"("section_id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "borrowing" (
	"user_id"	INTEGER NOT NULL,
	"book_id"	INTEGER NOT NULL,
	"date_issued"	DATETIME,
	"return_date"	DATETIME,
	PRIMARY KEY("user_id","book_id"),
	FOREIGN KEY("user_id") REFERENCES "user"("user_id") ON DELETE CASCADE,
	FOREIGN KEY("book_id") REFERENCES "book"("book_id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "ratings" (
	"book_id"	INTEGER NOT NULL,
	"user_id"	INTEGER NOT NULL,
	"rating"	INTEGER,
	PRIMARY KEY("book_id","user_id"),
	FOREIGN KEY("book_id") REFERENCES "book"("book_id") ON DELETE CASCADE,
	FOREIGN KEY("user_id") REFERENCES "user"("user_id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "section" (
	"section_id"	INTEGER NOT NULL,
	"section_name"	VARCHAR(50),
	"description"	VARCHAR(50),
	"date_created"	DATETIME,
	PRIMARY KEY("section_id")
);
CREATE TABLE IF NOT EXISTS "user" (
	"user_id"	INTEGER NOT NULL,
	"user_name"	VARCHAR(50),
	"role"	VARCHAR(50),
	"email"	VARCHAR(50),
	"password"	VARCHAR(50),
	"authenticated"	BOOLEAN,
	"premium"	BOOLEAN,
	PRIMARY KEY("user_id")
);
INSERT INTO "book" VALUES (1,'Wings of Fire','APJ Abdul Kalam','202402-1403-0305-487ed152-0ee5-4f73-bb89-b2c2cb3ce259.pdf','202402-1403-0305-bb4467b2-f741-4141-8d7e-0262247d15d0.jpg',350.0,1);
INSERT INTO "book" VALUES (2,'Atomic Habits','James Clear','202402-1403-0345-64cd28ed-9e4d-4ced-b58c-4b6b0c8d518f.pdf','202402-1403-0345-6ba8d1ac-261d-4bfb-9e4d-0a6458edb08a.jpg',180.0,2);
INSERT INTO "book" VALUES (3,'Ikigai','Hector Garcia','202402-1403-0415-03161a35-bb6d-4db4-bf0a-e82dac76956e.pdf','202402-1403-0415-239a360f-cf2e-40ff-8cde-89d852b22be0.jpg',250.0,2);
INSERT INTO "book" VALUES (4,'Indian Mythology','Devdutt Pattanaik','202402-1403-0514-40c71cee-dab5-4b51-b715-c61d6f09aed0.pdf','202402-1403-0514-8b56d852-c2f2-469d-944d-9590dfdec955.jpg',400.0,3);
INSERT INTO "book" VALUES (5,'The Man Who Was A Woman','Devdutt Pattanaik','202402-1403-0559-7e6e369d-c56f-4965-b292-3e3411558fd3.pdf','202402-1403-0559-d38d2f5f-7a33-4e99-b757-0812c7964112.jpg',340.0,3);
INSERT INTO "book" VALUES (6,'The Subtle Art Of Not Giving A F*ck','Mark Manson','202402-1403-0644-bbd202c6-56a5-4224-9be0-348d6f3ccbe1.pdf','202402-1403-0644-16f39385-5903-45bb-a737-73e5b886b48a.jpg',250.0,2);
INSERT INTO "book" VALUES (7,'Freedom At Midnight','Dominique Lapierre and Larry Collins','202402-1403-0726-cfec7771-f363-4bee-8de8-64f6679451dc.epub','202402-1403-0726-f632c570-30a3-4d88-be58-61ec6aaac99d.jpg',700.0,4);
INSERT INTO "book" VALUES (8,'The Da Vinci Code','Dan Brown','202402-1403-0758-74ac4209-bbdf-403a-849b-975745684014.pdf','202402-1403-0758-3728754a-c4b7-4059-bf93-f7ab5d48bf8e.jpg',550.0,5);
INSERT INTO "book" VALUES (9,'Love Story','Erich Segal','202402-1403-0833-aefdf967-0fe6-4479-aa5c-8aa6cb2c7869.pdf','202402-1403-0833-72c4f6a2-9be7-43fe-9a92-7f872b10130d.jpg',180.0,6);
INSERT INTO "book" VALUES (10,'Narendra Modi - A Political Biography','Andy Marino','202402-1403-0943-2128140c-2e57-49fc-9be6-7f1683cbc209.pdf','202402-1403-0943-99b57b91-d6d2-4441-a400-508a4cda17bd.jpg',5.0,7);
INSERT INTO "book" VALUES (11,'Exam Warriors','Narendra Modi','202402-1403-1017-976bd4b0-4654-440e-aaf0-e9d177f61c44.azw3','202402-1403-1017-e5dd6aad-4fe2-4325-b850-0bb0ca4cca67.jpg',2.0,7);
INSERT INTO "book" VALUES (12,'Sapiens','Yuval Noah Harari','202402-1403-1215-4c62ca0f-7f64-473c-9b91-856e9fdb0fea.pdf','202402-1403-1215-49b46385-15df-452a-8222-491093230c34.jpg',320.0,8);
INSERT INTO "book" VALUES (13,'Silmarillion','JRR Tolkien','202402-1403-1407-da054965-13c3-40db-864f-da7f3d133838.pdf','202402-1403-1407-b7a20a6e-c3ff-49bd-a2bd-9c8750efdef3.jpg',1500.0,9);
INSERT INTO "section" VALUES (1,'Biographies','Life Stories Condensed','2024-02-13 21:28:57.953969');
INSERT INTO "section" VALUES (2,'Self Help','Insightful tools to enhance mental well-being','2024-02-13 21:29:30.156898');
INSERT INTO "section" VALUES (3,'Mythology','Ancient Indian mythlogies and folk lores','2024-02-13 21:29:57.838307');
INSERT INTO "section" VALUES (4,'History','Narrating humanity''s journey through conflicts and calm','2024-02-13 21:30:56.286506');
INSERT INTO "section" VALUES (5,'Mystery/Thriller','Captivation fictional stories','2024-02-13 21:31:56.453128');
INSERT INTO "section" VALUES (6,'Romance','To kindle the flame of passion inside','2024-02-13 21:32:14.310082');
INSERT INTO "section" VALUES (7,'Trash','Kachra','2024-02-13 21:32:20.955857');
INSERT INTO "section" VALUES (8,'Anthropology','Study of humans, culture and evolution','2024-02-13 21:41:05.659551');
INSERT INTO "section" VALUES (9,'Fiction','Captivation fictional stories','2024-02-13 21:43:28.452077');
INSERT INTO "user" VALUES (1,'admin','admin','admin@kitaab.com','sha256$rkhTPeCKYvPSU83W$02ac3146fb695d55236d4c0236e89fd98b69dafedb84da54802e1d1aa08be06a',0,0);
INSERT INTO "user" VALUES (2,'user1','user','user1@kitaab.com','sha256$iW5PKPE1cNu6D3T3$1d33912991b592d070ed95a07b64caf0bd4b52cbc3e3a621c6116cfea137afc0',0,0);
COMMIT;

# disc-entries-file file format

Disc entries file is a csv file defining all the information of the discs to add.
The csv use a semicolon `;` as delimiter.
The csv has no headers, the meaning of each column defined as below.

- texture_file
- track_file
- title
- internal_name

all the names can be relative to pwd.

```csv
cover/music1_cover.png;music1.mp3;Never Gonna Give You Up;never_gonna_give_you_up
cover/music2_cover.png;music2.mp3;Hotel California;hotel_california
```
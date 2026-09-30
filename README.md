# Date It
A simple python utility to insert a file or directory's creation date into its name.

By default, the program acts upon the current working directory.
```shell
dateit.pyz
```
Files and folders can be specified manually.
```shell
dateit.pyz "Important Work Document.docx"
```
## Additional arguments
```
-h, --help - Print help information.
-v, --verbose - Explain why files were skipped.
-d, --date - A custom date to insert matching YY-MM-DD.
--hidden - Act upon hidden files.
```
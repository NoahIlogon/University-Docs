# Unix Technology and Engineering - Problem Set Overview

## 1. BASH Command Line Editing
- **Tab Completion**: 
  - Press TAB to auto-complete file paths or command names.
  - For example, type `/u` and press TAB to expand it to `/usr/`.
- **Command History**: 
  - Use the arrow keys to cycle through previous commands.
- **Exit Shell**: 
  - Use `Ctrl+D` to exit the shell or type `bash` to start a new shell.

## 2. Unix Command Line Tools
- **`man` Command**: 
  - Use `man <command>` to view the manual for any command (e.g., `man ls`).
  
- **Basic Commands**:
  - `ls`: List files and directories.
  - `cd`: Change the current directory.

## 3. Regular Expressions and GREP
- **`grep`**: Search for patterns in files.
  - Example: `grep hello file.txt` finds lines containing "hello".
  - Use regular expressions for advanced pattern matching (e.g., `hel*o` to match "helo", "hello", etc.).

## 4. The Stream Processor SED
- **`sed`**: Modify text in files based on regular expressions.
  - Example: `sed -e "s/hello/byebye/" filename` replaces "hello" with "byebye".
  - Use `g` for global replacement (`sed -e "s/hello/byebye/g"`).

## 5. The vi Editor, `cat`, and `more`
- **`vi`**: A powerful text editor with two modes (insert and command).
  - Learn how to start, save, and search using `vi`.
- **`cat`**: Display the contents of a file (`cat filename.txt`).
- **`more`**: View long files page by page (`more filename.txt`).

## 6. The Swiss-Army Knife of Stream Processing: AWK
- **`awk`**: A powerful text processing tool for line-by-line file processing.
  - Example: `awk '{print $3}'` prints the third column of each line.
  - Can be used for calculations, text transformations, and more.

## 7. Chaining Commands together through Pipes
- **Piping**: Use `|` to connect the output of one command to the input of another.
  - Example: `cmd1 test.data | cmd2` sends the output of `cmd1` to `cmd2`.

## Tasks and Problems
- **Problem 3.1**: Review the usage of the `ls` and `cd` commands.
- **Problem 3.2**: Learn about regular expressions and the `grep` command.
- **Problem 3.3**: Use `sed` to modify files with regex.
- **Problem 4.1 & 4.2**: Learn the basics of the `vi` editor and use `more` for viewing files.
- **Problem 4.3**: Write `awk` scripts to process files.
- **Problem 5.1**: Use pipes to chain commands like `wc` and `awk`.

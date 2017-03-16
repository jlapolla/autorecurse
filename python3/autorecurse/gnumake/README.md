## Operation Outline

`autorecurse` performs the following steps when you invoke `autorecurse
gnumake`:

- Locate all makefiles in the working directory and its subfolders
  (recursively). These are called **nested makefiles**.
- Read all targets in nested makefiles. These are called **nested
  targets**.
- Add nested targets to the current `make` invocation. This allows the
  targets in the main makefile to seamlessly depend on nested targets.

### Logical Targets and Literal Targets

Consider the following folder hierarchy:

```
.
..
Makefile
Backup.zip
MusicPlayer/
  Makefile
  Program.exe
  Installer.exe
  Filters/
    Makefile
    Filters.dll
```

Here, `Backup.zip`, `Program.exe`, `Installer.exe`, and `Filters.dll`
are `make` targets.

Consider the following commands:

- `make MusicPlayer/Filters/Filters.dll` run from `.`.
- `make Filters/Filters.dll` run from `./MusicPlayer`.
- `make Filters.dll` run from `./MusicPlayer/Filters`.
- `make -C MusicPlayer/Filters Filters.dll` run from `.`.

To the user, these commands all update the same target: `Filters.dll`.
In this sense `Filters.dll` is a  **logical target**.

In `make`, these commands update three different targets:
`MusicPlayer/Filters/Filters.dll`, `Filters/Filters.dll`, and
`Filters.dll`. We'll call this sense of the word "target" a **literal
target**.

Notice that for a given logical target, the literal target
representation changes when the working directory changes.

To add nested targets to the current `make` invocation, `autorecurse`
translates logical targets into literal targets suitable for the working
directory that `make` will execute commands in. Only the literal targets
are passed to `make`.

The working directory that `make` will execute commands in is called the
**execution directory**. `autorecurse` uses the execution directory to
translate logical targets into literal targets.

When `make` is invoked without `-C`, the execution directory is the
current working directory. When `make` is invoked with `-C`, the
execution directory is the directory specified by `-C`.

### Operation Outline, Revision II

Let's elaborate on the steps given in the Operation Outline section.

`autorecurse` performs the following steps when you invoke `autorecurse
gnumake`:

- Determine the **exeuction directory**. If there are no `-C` options,
  this is the current working directory.
- Locate all makefiles in the execution directory and its subfolders
  (recursively). These are called **nested makefiles**.
- Read all targets in nested makefiles. These are called **nested
  targets**.
- Translate all nested targets into literal targets relative to the
  execution directory.
- Add literal targets to the current `make` invocation. This allows the
  targets in the main makefile to seamlessly depend on nested targets.

### Intermediate Files

To add literal nested targets to `make`, `autorecurse` first creates a
makefile that defines **rules** for all nested targets. This file is
called a **nested rule file**. Then `autorecurse` passes the nested rule
file to `make` with the `-f` option.

The **recipe** for each nested target in a nested rule file is `make -C
<nested-makefile-dir> -f <nested-makefile>`, where
`<nested-makefile-dir>` and `<nested-makefile>` correspond to the
particular nested makefile that the nested target is defined in.

*Aside: While it is possible to use an arbitrary, user-configurable `-C`
directory for each nested makefile, this version of `autorecurse` uses
the directory that the nested makefile resides in (i.e. the output of
`dirname <nested-makefile>`).*

Since a nested rule file defines rules for literal targets (as opposed
to logical targets), a particular nested rule file is only valid for a
single execution directory.

### Updating Nested Rule Files

Nested rule files are derived from the nested makefiles of a particular
execution directory. A nested rule file must be updated whenever its
corresponding nested makefiles are updated.

`autorecurse` uses `make` to update nested rule files. To accomplish
this, `autorecurse` searches the execution directory for nested
makefiles, and then creates a temporary makefile that defines a rule for
updating the nested rule file. This temporary makefile is called a
**nested rule update file**, or just **nested update file**.

A nested update file has one rule which defines how to update the
corresponding nested rule file:

- The rule's **target** is the nested rule file.
- The rule's prerequisites are the corresponding nested makefiles.
- The rule's recipe is always `autorecurse nestedrules -C
  <execution-directory> -o <nested-rule-file>`.

Once the nested update file is created, `autorecurse` invokes `make`
with:

`make -f <nested-update-file> -f <nested-rule-file> <OTHER_ARGUMENTS>`

`make` uses the rule in the nested update file to decide if the nested
rule file needs to be updated. `make` will automatically update the
nested rule file, or create it if it does not exist, before continuing.

The following excerpt from the GNU Make manual explains how this works:

> [A]fter reading in all makefiles, `make` will consider each as a goal
> target and attempt to update it. If a makefile has a rule which says
> how to update it (found either in that very makefile or in another
> one) or if an implicit rule applies to it (see [Using Implicit
> Rules][8]), it will be updated if necessary. After all makefiles have
> been checked, if any have actually been changed, `make` starts with a
> clean slate and reads all the makefiles over again.

*[GNU Make manual, 3.5 How Makefiles Are Remade][7]*

The nested rule file is deleted after `make` executes, since it is
re-created on each invocation when `autorecurse` locates nested
makefiles.

### Operation Outline, Revision III

Let's elaborate on the steps given in the Operation Outline section.

`autorecurse` performs the following steps when you invoke `autorecurse
gnumake`:

- Determine the **exeuction directory**. If there are no `-C` options,
  this is the current working directory.
- Locate all makefiles in the execution directory and its subfolders
  (recursively). These are called **nested makefiles**.
- Create a **nested update file** for the execution directory.
- Invoke `make -f <nested-update-file> -f <nested-rule-file>
  <OTHER_ARGUMENTS>`
  - If the **nested rule file** needs to be updated, `make` will call
    `autorecurse nestedrules -C <execution-directory> -o
    <nested-rule-file>`, and the following additional steps occur as a
    result:
  - Locate all nested makefiles in the execution directory.
  - Read all targets in nested makefiles. These are called **nested
    targets**.
  - Translate all nested targets into literal targets relative to the
    execution directory.
  - Output rules for nested targets to the nested rule file.
  - `autorecurse nestedrules . . .` returns.
  - `make` reads the nested rule file.
- `make` executes.
- `autorecurse` deletes the nested update file. The nested rule file is
  kept for future invocations.

### Locating Nested Makefiles

`autorecurse` searches for nested makefiles starting in the execution
directory. For each folder evaluated, `autorecurse` searches for one of
the following file names, in order: `GNUmakefile`, `makefile`, and
`Makefile` [\[ref\]][9]. The first file name found in the folder is
selected as that folder's nested makefile. There is at most one nested
makefile per folder.

If a nested makefile is found in a folder, its subfolders are also
searched for nested makefiles. If no nested makefile is found in a
folder, its subfolders are not searched. This allows `autorecurse` to
skip folders in file structures where not all subfolders are intended
for `make`. To force `autorecurse` to search a folder's subfolders, the
user may place an empty makefile in the folder.

If `autorecurse` identifies a nested makefile, and that nested makefile
also happens to be listed on the command line with a `-f` option,
`autorecurse` takes no special action. The nested makefile is still used
to create nested target rules in the nested rule file. In most cases,
the rules in the `-f` file override the rules in the nested rule file,
and `make` issues a warning. Errors may occur if the `-f` file is
intended to be executed from another execution directory.

# Links Index

- [Remaking Makefiles (GNU Make manual)][7]
- [Implicit Rules (GNU Make manual)][8]
- [Default Makefile Names (GNU Make manual)][9]

[7]: https://www.gnu.org/software/make/manual/html_node/Remaking-Makefiles.html
[8]: https://www.gnu.org/software/make/manual/html_node/Implicit-Rules.html
[9]: https://www.gnu.org/software/make/manual/html_node/Makefile-Names.html


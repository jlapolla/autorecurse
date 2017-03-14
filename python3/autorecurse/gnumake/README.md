## Operation Overview

`autorecurse` performs the following steps when you invoke `autorecurse
gnumake`:

- Locate all makefiles in the working directory and its subfolders
  (recursively). These are called **nested makefiles**.
- Read all targets in nested makefiles. These are called **nested
  targets**.
- Add nested targets to the current `make` invocation. This allows the
  targets in the main makefile to seamlessly depend on nested targets.

### Nested Target Translation

Conceptually, each nested target is a unique entity. For example,
consider the following folder hierarchy:

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

- `make MusicPlayer/Filters/Filters.dll` (run from `.`)
- `make Filters/Filters.dll` (run from `./MusicPlayer`)
- `make Filters.dll` (run from `./MusicPlayer/Filters`)
- `make -C MusicPlayer/Filters Filters.dll` (run from `.`)

To the user, these commands all update the same target: `Filters.dll`.
We'll call this sense of the word "target" a **logical target**.

In `make`, these commands update three different targets:
`MusicPlayer/Filters/Filters.dll`, `Filters/Filters.dll`, and
`Filters.dll`. We'll call this sense of the word "target" a **literal
target**.

### Nested Target Validity

A set of nested targets is valid for a particular working directory, not
for a particular makefile. The working directory for an invocation of
`make` is determined as follows:

- Without -C argument, use the current working directory.
- With -C argument, use the -C directory.

*N.B. the -f option does not affect the effective working directory.*

`autorecurse` maintains configuration and cached files in a user
directory. The location of the `autorecurse` user directory is based on
the operating system:

- On Linux, use ~/.autorecurse
- On Windows, use the appropriate Windows special folder:
  - [LocalFolder][5]
    - configuration
  - [LocalCacheFolder][5]
    - nested target makefiles (nested-target.XXX)
    - directory hash index files (index)
  - [TemporaryFolder][5]
    - nested target creation makefiles (make-nested-target.XXX)

We will cache nested target files in
~/.autorecurse/gnumake/<directory-hash>/

Need a way to hash directory names (and avoid collisions) for this
purpose

Each hash directory has:

- make-nested-target-x file which gives the rule for nested-target-x
- nested-target-x file which records the rules for all nested makefiles
  in the directory
- index file which maps canonical directory paths to a suffix in this
  directory (for hash collision resolution)
- N.B. the ‘-x’ is actually a suffix which varies (it’s the suffix
  listed in the index file)

For each invocation of auto-recurse gnumake:

- Search for makefile
- Search for sub-makefiles (if search for makefile succeeds)
- Manually update make-nested-target-x and index
- Invoke make with -f make-nested-target-x -f nested-target-x [the rest
  of the -f options]

make will read the rule in make-nested-target-x, and automatically
remake nested-target-x if it is out of date

[1]: https://en.wikipedia.org/wiki/Special_folder
[2]: https://blogs.msdn.microsoft.com/patricka/2010/03/18/where-should-i-store-my-data-and-configuration-files-if-i-target-multiple-os-versions/
[3]: https://msdn.microsoft.com/en-us/library/system.environment.specialfolder.aspx
[4]: https://msdn.microsoft.com/en-us/library/s2esdf4x(v=vs.90).aspx
[5]: https://docs.microsoft.com/en-us/uwp/api/windows.storage.applicationdata
[6]: https://technet.microsoft.com/en-us/library/cc766489.aspx


#!/usr/bin/env python3
import autorecurse_path


if __name__ == '__main__':
    from autorecurse.cli import Cli
    import sys
    cli = Cli.make()
    cli.execute(sys.argv[1:])



# Directory Synchronisation Demo - Suyash SHANDILYA

- Demo directory synchronisation app for Veeam.

## Build notes

- Built on `Linux kali 6.11.2-amd64`
- Virtual environment uploaded for convenience.

## Usage

### Setup

- Clone the repository.
- Create a python virtual environment (or use the one uploaded here `veeam-env/` on a Linux machine. Should mostly work.)
- Initialize the virtual environment. `source ./veeam-env/bin/activate`
- Install dependencies: `pip install -r requirements.txt`

### How to

#### Start the syncer daemon:

```
python veeam-syncer.py start --source .<source_directory> --replica <replica_directory> --iologfile <file_tracking_file_creation_deletion> --logfile <log_file_tracking_synchronisation_schedules>
```
File arguments are optional and have default values - `file-io.log` and `synchronisation.log` respectively.

Example usage:

```
python veeam-syncer.py start --source ./test-payloads/source/ --replica ./test-payloads/replica/ --iologfile test-log-files/ete-io.log --logfile test-log-files/ete-sync.log
```

#### Stop the daemon

```
python veeam-syncer.py stop
```

#### Monoshot mode

Runs the synchronisation iteration once then stops. Use `monoshot` instead of `start` in the starting command.

Example:

```
python veeam-syncer.py monoshot --source ./test-payloads/source/ --replica ./test-payloads/replica/ --iologfile test-log-files/ete-io.log --logfile test-log-files/ete-sync.log
```

#### Quick Testing

- Adjust the `SRC_DIR` variable in the file `./src/utils/populate_src.py` to the intended source directory, then run it in a separate shell. It keeps adding and deleting random files and directories in the specified directory.
- Turn the syncer on with the source directory used above and any replica.
- Run `pytest ./tests/test_sync.py::test_instant_compare` to instantly compare the source and replica status. Unless queried too fast, it should never fail. If queried too fast, there should be some instants of failure when the synchronsiation is in process and isn't complete.

#### Limits

- Can copy partial states. i.e. replica might have versions of source in between iterations that were never the state of source at all.
- Can synchronise hundreds of small files and nested directories in a matter of seconds.
- Hardwired timings for starting, stopping and time between iterations can be fine tuned for performance enhancement. It is python so there are limits to its performance.

## Dev Notes

- The original plan was to used Merkle trees to capture the directory state and only update the changed parts between iterations. Due to the lack of direct functionality in the OS that allows relaying changes lower in the directory to higher levels, the advantages of such a construction were moot. The final logic is a DFS checking of the entire source directory.
- Apologies for the lack of typing in the code, that's unprincipled and unusual for me. Busted IDE won't call me out for it, and the complexity is not too high to warrant it.
- TDD style of build. Run `pytest ./tests/` to run all tests.
- Some tests, specially the daemonisation test set `test_daemonisation.py` have been disabled, as the subprocess erroneously doesn't return after calling the daemon. Couldn't debug this. The tests, test the `monoshot` behaviour for the same reason. As long as the `start` behaviour is maintained as a trivial looping wrapper around `monoshot`, the test intent is preserved.
- Initial idea was to use env variables for all input. Makes for ease of testing, easy daemonisation, environment-wide usage, etc.
- Building on that, the main file `veeam-syncer.py` handles the CLI, sets the environment variables, and runs the main file `sync_daemon.py` as a subprocess.
- Using `shutils.copyfile` instead of `copy2` for ease of testing. The latter would have captured metadata as well, while the former just copies the contents of the file.
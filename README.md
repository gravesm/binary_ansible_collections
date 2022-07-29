# Binary Ansible Collections

Though most Ansible modules are written in Python, it also has the ability to run binary modules. This is interesting, but leaves the step of actually creating the binary up to the plugin author. In this demo I wanted to make use of Ansible collections to try and make the compilation step invisible to both the playbook author and the plugin author. This is done through the use of action plugins.

## Implementation

There are two collections in this demo. The first, `gravesm.binary` contains a single action plugin. This plugin is run first and handles compiling the correct binary module for the remote host's OS and architecture, and then passing this binary on to Ansible to get run on the remote host. In this example, the action plugin is for modules written in Go, but the same principle could be applied to other languages.

The second collection is an example collection written in Go. It just has one module, `system`, that prints GOOS and GOARCH. There are only two things that need to be done to create a collection in Go:

1. Put an action plugin redirect in your `meta/runtime.yml` for each module in your collection to the `gravesm.binary.golang` plugin.
2. Put each of your module's main package in `cmd/<module>/`.

In the example collection, the `meta/runtime.yml` looks like:

```yaml
plugin_routing:
  action:
    system:
      redirect: gravesm.binary.golang
```

and the `gravesm.golang.system` module's main package is in `collections/ansible_collections/gravesm/golang/cmd/system/`. Of course, you can structure the rest of your Go code however you want as this collection is just a regular Go module. There is no Python at all in the `gravesm.golang` collection, it is entirely Go. When the playbook is run, the compiled binaries will get written to `plugins/modules/<module>_<GOOS>_<GOARCH>`.

## Example

In this example, we'll connect to two hosts, one a Debian system and one an OpenBSD system and use the `gravesm.golang.system` module to print the remote host's GOOS and GOARCH values:

```yaml
# playbook.yml
- hosts: servers
  tasks:
    - gravesm.golang.system:
```

Before we run this, let's look at the contents of the `gravesm.golang` collection:

```
$ tree collections/ansible_collections/gravesm/golang
collections/ansible_collections/gravesm/golang/
├── cmd
│   └── system
│       └── main.go
├── galaxy.yml
├── go.mod
└── meta
    └── runtime.yml

3 directories, 4 files
```

Now, let's run the playbook:

```
$ ansible-playbook playbook.yml -v

PLAY [servers] ******************************************************************************************************************************

TASK [Gathering Facts] **********************************************************************************************************************
ok: [debian]
ok: [openbsd]

TASK [gravesm.golang.system] ****************************************************************************************************************
ok: [debian] => {"changed": false, "msg": "OS: linux; Architecture: amd64"}
ok: [openbsd] => {"changed": false, "msg": "OS: openbsd; Architecture: amd64"}

PLAY RECAP **********************************************************************************************************************************
debian                     : ok=2    changed=0    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
openbsd                    : ok=2    changed=0    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
```

And if we look at the contents of the `gravesm.golang` collection now, we can see that it created two different versions of the `system` module for each OS and architecture:

```
$ tree collections/ansible_collections/gravesm/golang/
collections/ansible_collections/gravesm/golang/
├── cmd
│   └── system
│       └── main.go
├── galaxy.yml
├── go.mod
├── meta
│   └── runtime.yml
└── plugins
    └── modules
        ├── system_linux_amd64
        └── system_openbsd_amd64

5 directories, 6 files
```

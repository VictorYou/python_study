# Lab State Service WEB UI


'Lab State Service WEB UI' supports basic administrator use cases:

  - Shows the content of the Lab State Service
    - lab info, lab state info (=snapshots) and lab reservation status
  - Admin operations:
     - reserve lab, release lab
     - create new lab, remove lab
     - show and edit admin server access parameters of the snapshot

# Documentation

  - Lab State Service WIKI: https://confluence.int.net.nokia.com/display/~m4koskin/NetAct+continuous+delivery+pipeline
  - Lab State Service Development WIKI: https://confluence.int.net.nokia.com/display/~m4koskin/SW+Verification+pipeline+development+plan


### Setup in localhost

**Clone 'cicdna' repository from GIT**

```sh
$ mkdir GIT
$ cd GIT
$ git clone ssh://<username>@gerrite1.ext.net.nokia.com:8282/netact/cicdna
```

**Start 'Lab State Service' in localhost and import some dummy data into service**

```sh
$ cd .../GIT/cicdna/state_service
$ cat README.md
$ docker-compose build
$ docker-compose up -d
$ cd src
$ python client.py -l DEBUG -lf client.log  -u admin create-test-labs
$ python client.py -l DEBUG -lf client.log  -u admin show-labs
```

**Install 'CORS Everywhere'-plugin into firefox browser and enable it.**

**Start 'Lab State Service WEB UI' from URL:**
  - file:///root/.../cicdna/state_service/ui/production/index.html




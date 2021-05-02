# Chronos
## Introduction
Chronos is an open source python based framework developed by the Incident Response team at OTORIO.

During incident investigations there are different evidences that can be used in order to detect the attacker. Many
times we try to get the whole picture of the attack and in order to successfully achieve it we need to tell the sequence
of events that happened in the host. We can build this sequence by using the timestamps from the different evidence that
we can find on the machine.

This framework was developed to run many parsers and store them in a dedicated DB, so the analysis process will be
simpler - for example by creating dashboards or using jupyter notebooks.

Another big advantage is that all the times become relative to each other. Some programs like the event viewer are 
displaying the time according to the viewers time zone, which may result with inconsistent times and weird sequence. 
Viewing all the logs from a single source will keep your times aligned with each other.

The framework uses many Windows utilities and as such is designed to run on Windows machine.

## Requirements
* Python 3 
  * The framework code
* Windows 8
  * If you are running less than Windows 8 you will NOT be able to process Windows 10 prefetch files.
* Microsoft .NET 4.6.2
  * For Eric Zimmerman tools
  
## Tested on environment
* Python 3.7
* Windows 10
* Microsoft .NET 4.8

## Installation
In order to install the framework, all you need is to clone this repository and install the required modules with
the powershell script called [install.ps1](install.ps1), which requires powershell v5 to be installed.

### Manuel Installation
On the other hand, you can run the installation manually by running all the commands from the script

Install the required python modules by running 
```markdown
pip install -r requirements.txt
```
To make sure that the framework will work as expected, make sure that:
* There is a [Tools](Tools) directory, which contains all the required tools in the right positions
  * Follow the downloads at installs.ps1
* The wmi parsing is done by the tools at https://github.com/fireeye/flare-wmi, so you need to
run the setup manually for it to work
  ```shell
  cd flare-wmi-master/python-cim/ 
  python setup.py install
  ```
  * In case you run this project under pycharm, remember that pycharm is using virtual environment, so you would need
    to run the setup within it also (to enter the venv run `.\venv\Scripts\activate`)

We are using the script Get-ZimmermanTools.ps1 to download all the tools of Eric Zimmerman, including tools we 
are currently not using. 
In case you want to download only the used tools check the [tools list](TOOLS_AND_CREDITS.md).

## Usage
### Evidence
The evidence path is a directory. The name is the computer name from which the evidences were collected, and the
internal structure will be like the regular OS structure (although not mandatory, this is how we done it so far).

The desired path will look like:
* Desktop-1234567\C
* Server05\C

This structure can achieved when using different tools like:
* CyLR (https://github.com/orlikoski/CyLR)
  * can be used to collect evidences from live system
* Kape (https://www.kroll.com/en/insights/publications/cyber/kroll-artifact-parser-extractor-kape)
  * can be used on mounted images as well as on live systems

### Running the framework
Running example:
```shell
python3 chronos.py --eventname case1 --evidences E:\case1\victims\Laptop01\C --host my_elastic_server --port 9200 --db-user user --db-password password --bulk 500 
```

### Supported flags
> `-n`, `--eventname` - The name of the current event, required
>
> `-e`, `--evidences` - Path of the evidences to parse, required 
>
> `--host` - The db address
>
> `-p`, `--port` - The db port
>
> `--db-user` - The db user for authentication
>
> `--db-password` - The password of the db user
>
> `--bulk` - The bulk size to index with
>
> `--file` - Json with paths to parse (add to defaults)
>
> `--file-only` - Json with paths to parse (ignore defaults)
> 
> `--dump` - Dump the results to folder 

In case neither `--host` nor `--dump` mentioned, the results will be dumped to temp directory under the project 

## Customization
### Paths
The first thing we will need is to know what is the path for every raw data file in the evidence folder, to do this you
need to add your path to the "get_significant_paths" function. The path can be full path to a directory or a file and it
can contain a wildcard (*) to catch multiple paths.

Every parsing function will get only the "paths" dictionary that will be returned from this function, and will need to
choose the path it is using. By this way we can call the parsers in a generic way and using the same calling
conventions.

```python
def get_significant_paths(evidences_path):
    paths = {}
    paths["root"] = evidences_path
    paths["reg_config_path"] = os.path.join(evidences_path, "Windows", "system32", "config")
    paths["all_users_paths"] = os.path.join(evidences_path, "users", "*")
    paths['browsing_history_chrome'] = os.path.join(evidences_path, 'Users', '*', "AppData", "Local", "Google",
                                                    "Chrome", "User Data", "Default", "History")
    ...

    return paths
```

Other option is to use a file of custom paths to enrich the analysis. 
You can pass the `--file` flag to pass a json file of extra paths you want to analyze, 
or pass the `--file-only` which will ignore the default paths we supported and will use only the paths from the custom
file.

Example of possible file 
```markdown
{
  "iis": "C:\additionals_evidences_to_collect\IIS",
  "hiberfil":  "C:\Hiberfil.sys"
}
```
The key is used by the code to identify the path and the value is the path of the evidences on disk

### Main
The main will run the wrapper functions of the different parsers. 
All those functions are stored at [parsers_wrapper.py](parsers_wrapper.py) and loaded dynamically, 
so new functions should be added there.
This is probably the only file you would need to modify with new parsers you would like to add.

We call those functions using
```python
executor.submit(func, paths, config): func for func in all_functions
```
so they all must use the same signature, which will be
```markdown
Args:
    paths: Dictionary of all the paths to get the relevant path from
    config: A namedtuple object that have all the config for the parser 
```

After running the parsers, the data will be indexed to a desired DB, so the analysts wil be able to detect the attacker

All this process is done in a threadpool, so all the parsing is done simultaneously which can save significant time.


### Parsers
There is a base parser ([parser_base.py](parsers/parser_base.py)) that all the parsers would inherit and use his 
functions, and implement its "parse" function.
Eventually, there are 3 stages to the parsing process

#### Stage 1

The first stage is responsible to transform the raw data from the evidence path to a convenient format that we can
read (csv, json, simple text format), the first parser can be an internal tool, or some code from the internet.

> ⚠️You can run the framework on multiple evidences simultaneously, so if you're using a tool that will
dump the result to disk, make sure it will have a unique name, so it won't overwrite the results of other run
 

#### Stage 2

The second stage is responsible to read the output from the first stage and transform the data to a list of JSONs that
can be indexed to elastic, implementing the "parse" function of the BaseParser.

The second stage also need to change the format of specific values to supported format (i.e the timestamp will
transform to iso format all over the project), and the names of the fields (currently the only field required to change 
is the timestamp field, witch should be called "time")

The result of this stage will be one of the following: 
* A tuple that will consist of the index name it will be indexed to, and the data returned from the parsing process, 
  for example -> (index_name, [list of jsons])
  
* A list that is build from tuples, mainly for supporting the dump option, so these parsers will create the result in a
  subdirectory to not spoof the main directory (for example for evtx). Each of the tuple in the list will be from the 
  same format as regular tuples -> [(index_name, [list of jsons]), ...].
  The folder created in case of dump will be the first part of the index name (splitted by "-"), for example the list
  [("evtx-security", [list of jsons])] will create a folder named evtx (if not exists) and save the data there. 

#### Stage 3

The third stage is responsible to save the data, it will dump the result either to disk or to the DB (or both), based on
the configuration the parser received


#### Example
One of the collected evidences is the security event log. In order to be able to save it in the elastic, we first need
to parse it to JSON format (this is the first stage), make some customizations to that json, so it will fit the 
DB structure (this is the second stage) and then send the json to the DB for later analysis. 

#### Notes
> * When using your custom parser, you can combine those stages in one function, they are only guiding lines.
> * Although those are different stages, we still implement all of them in a single module
> * Eventually when you will write your own modules, you can do it any way you want, those are just recommendations 


### Indexing
The saved results are stored at a DB server in order to be able to query big amount of data efficiently. The DB
we chose to use in the default implementation is Elasticsearch (https://www.elastic.co/), but eventually the code
returns JSONs of data, so you can replace the backend with your favorite DB as well or make the necessary changes to
custom the data to your DB.

#### Index format
After running the framework, new indices will be created in the elastic DB. Each index will be named with the format of
```markdown
{eventname}-{hostname}-{logs}-{date}
```
Examples:
* incident_a-laptop01-prefetch-2019-11-18-13-30-00
* customer_b-dektop1234-evtx-security-2019-11-18-13-30-00

## Query the DB
There is a known format of signatures called SIGMA (https://github.com/SigmaHQ/sigma). This is a very comfortable format
which can be translated to many SIEM products. Under the SIGMA git repository, there is a tool called sigmac, which can
preform this translation.
As our backend is elasticsearch, we will wish to transform those rules to a format which will allow us a run suitable
queries.

For this reason, we added a directory called [sigma support](sigma support), which contain 2 files:
* [fields.yml](fields.yml) - A yaml file which can be used as a config file for sigmac, for example:
  > tools/sigmac -t es-qs -c fields.yml rules/windows/builtin/win_susp_lsass_dump.yml
* [create_sigma_config.py](create_sigma_config.py) - A python script which can be used to generate this config. The
advantage of the script is that it can be used to generate a config file which will match all the fields in the DB.
  The source for this script is the dump result of chronos, and the destination is the result file path.
  > create_sigma_config.py -d C:\temp\host-dump-dir -o C:\temp\fields.yml


Thank You Industry 🙏
--------
As this framework is using many open source tools developed by many researchers, we would like to thank them for their
hard work and encourage them and others to keep the great job.

### Tools used
This project, provided "as is", depending on some tools developed by different people, and you can find the 
list of tools at [TOOLS_AND_CREDITS.md](TOOLS_AND_CREDITS.md).
This text file contains tools as they provided and some public code with modifications


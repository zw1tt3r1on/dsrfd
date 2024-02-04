# dsrfd
dsrfd stands for ds_store recursive file downloader and it is a simple automation tool to exploit DS_Store file disclosures

# Requirements
dsrfd uses python 3 and needs the following dependencies 

```
pip install ds-store requests
```

# Usage
dsrfd can be used to check for a single domain by running the command
```
dsrfd.py --domain https://www.example_site.com/
```

or you can also pass it a list of domains from a text file
```
dsrfd.py --list list_to_check.txt
```

### Credits
This is based of the work of lijiejie and I have just upgraded it to be able to pass a list of domains for more efficient scanning and automation
Original repository - https://github.com/lijiejie/ds_store_exp

Generate fake REDCap form data respecting choices and branching logics


### Setup

- > pip install -r requirements.txt

- > cp config.py.example config.py

- Put your REDCap API TOKEN in `config.py`

- > gen-fake-data/gen_data.py --help

### Generate

    gen-fake-data/gen_data.py --dict AMPSCZFakeData_DataDictionary_2021-06-10.csv \
    --template AMPSCZFakeData_ImportTemplate_2021-06-10.csv \
    --map AMPSCZFakeData_InstrumentDesignations_2021-06-10.csv \
    --outPrefix fake_data/data --caselist chr_ids.txt --arm 1 


### Upload

> for i in fake_data/*csv; do echo $i; gen-fake-data/import_records.py $i; done


### Verify

* Login to REDCap
* Navigate to your project webpage
* See the `Record Status Dashboard` and `Data Exports, Reports, and Stats` tabs from the left sidebar

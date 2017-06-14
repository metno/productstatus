# Productstatus

Productstatus is an index of meteorological products, optimized for operational use.

## Theory of operation

Meteorological data, or _products_, are obtained using a number of methods:

* Transform observations to forecasts using high-performance computers
* Post-processing using FIMEX or other tools
* Retrieving files from other sources

Once made available, data is regularly accessed by a diverse and heteorogenous
selection of downstream processing systems. Some of these systems need to be
notified about new product generation, and can often make use of metadata
such as reference time and process lineage.

When a product is persisted, in form of a file or object, it may be registered
in the Productstatus index. See [data model](#data-model) for details about
what information is persisted. Upon registration, an event is emitted on a
message queue, so that downstream consumers are notified immediately of its
existence.

## Data model

All models are assigned a universally unique identifier (UUID), a randomized,
permanent identifier which must be used whenever an unchanging reference to a
Productstatus object is needed.

### Product definition

| Field | Type | Description |
| ----- | ---- | ----------- |
| UUID  | `[16]int8` | Primary key. |
| Title | `string` | Name of the product. |
| Abstract | `string` | Long description of the product. |

### Product

| Field | Type | Description |
| ----- | ---- | ----------- |
| UUID  | `[16]int8` | Primary key. |
| Definition  | `[16]int8` | Foreign key to _Product definition_ model. |
| ReferenceTime | `time.Time` | Timestamp of the start of validity for the entire product. |
| FileType | `string` | File type, typically one of _netcdf_, _grib1_, _grib2_. |
| URL | `map[string]string` | List of URLs to this file, one for each location. |
| IpfsHash | `string` | [IPFS](https://ipfs.io/) hash of the file. |
| Begin | `time.Time` | Start timestamp of product validity. |
| End | `time.Time` | End timestamp of product validity. |
| Revision | `int` | Auto-incrementing field which increases if all other fields are equal. |

### Discovery and use metadata

Products need a minimal amount of metadata, in order to make operational
products available for harvesting or indexing by NorDataNet. Relevant standard
according to the NorDataNet specification is _MMD_, which is compliant with
ISO19115/GCMD DIF.

The following metadata elements are mandatory in ISO 19115:

* Data set title
* Data set reference date
* Data set language
* Data set topic category
* Abstract describing the data set
* Metadata point of contact
* Metadata date stamp

These attributes may be stored in NetCDF files, along with the _use metadata_.
The only information needed in Productstatus is a name, slug, or other
mechanism of discerning one data set from another when running queries.

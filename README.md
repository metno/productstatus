# Productstatus

Productstatus is an index of meteorological products, optimized for operational use.

## Theory of operation

Meteorological data, or _products_, are obtained using a number of methods:

* Transform observations to forecasts using high-performance computers
* Post-processing using FIMEX or other tools
* Retrieving files from other sources

Once made available, data is regularly accessed by a diverse and heteorogenous
selection of downstream processing systems. Some of these systems want to be
notified that a new product is available, in order to update user interfaces,
provide metrics, start a process, fill caches, or similar tasks.

When a product is persisted on disk, it is usually in the form of a file. This
file may be scanned for metadata and submitted to Productstatus for indexing.
After successfully indexing the metadata, a message is emitted on a
publish/subscribe message queue, so that downstream consumers are notified
immediately of its existence.

See [data model](#data-model) for details on what information is persisted.

## Data synchronization

A customizable selection of products must be synchronized immediately to a
number of client systems once it becomes available. Examples of this include
synchronization between Lustre stores A+B; transferring data from the Lustre
stores to the MET API caches; and pushing a smaller selection of products to
backup locations.

Data synchronization requirements:

* Data integrity. The transferred files must be guaranteed to be exactly equal
  to the original files.
* Resource utilization should be disk bound.
* Ability to survive network outages and recover quickly.
* Immediate synchronization when products become available.
* Client-side runtime and configuration of product selection.

### rsync

| Pros | Cons |
| ---- | ---- |
| Battle-tested | Requires SSH credentials |
| Stable code base | Lacks automatic restart/resume |
| In-house competence | Requires separate state table and logic for transfers |

### BitTorrent

| Pros | Cons |
| ---- | ---- |
| Decentralized distribution | May require peer blacklist configuration to avoid long-distance transfers |
| BitTorrent client keeps state | May be slower on local transfers |
| Anonymous transfers | Network, memory and CPU overhead |
| External distribution | |
| File paths are irrelevant | |

## Lifecycle management

Data synchronization will result in hard drives being filled up. On most
systems, only operational data is needed. Operational data is data that is
useful for predicting the weather from the current point in time. At MET
Norway, operational data is maximum three days old.

Once a product has been indexed in Productstatus, other clients will start to
rely on its availability. After a certain time period has passed, the data is
considered non-operational, and it may be deleted to reclaim disk space. This
deletion process can be handled by a cron job or a daemon program. The expiry
time for the product must be stored in the Productstatus index so that clients
know that the data will be unavailable, and can in turn give proper feedback to
their users or clients.

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
| ProductDefinition  | `[16]int8` | Foreign key to _Product definition_ model. |
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

### Product validity metrics

Metrics about average, mean, and Nth percentile of certain variables might be
useful to examine model performance and integrity. Threshold values are equally
useful, in order to enable alerting. These metrics might be calculated and
submitted to the Productstatus index. The threshold values can be defined by
the NetCDF producer, and stored as variable attributes in the NetCDF file.

| Field | Type | Description |
| ----- | ---- | ----------- |
| UUID  | `[16]int8` | Primary key. |
| Product | `[16]int8` | Foreign key to _Product_ model. |
| Metric | `string` | Metric name. |
| Value | `float64` | Metric value. |

# P3-WU25 Network citation and release boundary

Status: operators and registered DOIs are frozen; raw redistribution remains
closed pending operator-specific licence confirmation.

The five-station archive evaluation network now has an explicit citation
disposition. FDSN registers `10.7914/SN/IC`, `10.7914/SN/IU` and
`10.7914/SN/TW`. It reports no network DOI for HK or MY, so those data must cite
the Hong Kong Observatory and Malaysian Meteorological Service together with
their FDSN network pages. EarthScope/SAGE service acknowledgement is required in
addition to the network citations.

EarthScope states that network owners specify licences and that, when no licence
has been declared, the facility distributes data as CC BY 4.0. The present audit
does not infer absence of a declaration from the FDSN page. Until each operator-
specific licence is checked, `raw_redistribution_authorized` remains false for
all five networks. MiniSEED and StationXML stay off Git; compact requests,
hashes, failures and derived QC metrics may be versioned.

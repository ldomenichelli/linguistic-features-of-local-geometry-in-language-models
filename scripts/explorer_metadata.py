"""Definitions and granularity for the released locality diagnostics."""
NEIGHBOURHOOD_METRICS = [
 ('radius','Neighbourhood radius','number','Euclidean distance from the query representation to the furthest neighbour in the selected rank interval. Distances use unnormalised representations and are model/layer specific.'),
 ('random_median_distance','Median reference distance','number','Median Euclidean distance from this query representation to all 15,000 reference representations; a per-query baseline.'),
 ('radius_ratio','Relative radius','number','Neighbourhood radius divided by this query’s median reference distance. This dimensionless ratio is relative to the recorded reference set.'),
 ('mean_distance','Mean neighbour distance','number','Mean Euclidean query-to-neighbour distance within the selected rank interval.'),
 ('same_source','Same-source neighbours','ratio','Fraction of selected neighbours from the same Pile component as the query excerpt.'),
 ('same_source_null','Same-source reference baseline','ratio','Fraction of all reference excerpts from the query’s Pile component; the expected same-source fraction under uniform reference sampling.'),
 ('same_source_gain','Same-source excess','ratio','Same-source neighbour fraction minus the same-source reference baseline. Displayed in percentage points.'),
 ('source_entropy','Normalised source entropy','number','Shannon entropy of Pile-component proportions in the selected neighbourhood, divided by the logarithm of the number of corpus components in the audit.'),
 ('source_entropy_random_mean','Random-neighbourhood entropy','number','Recorded mean normalised source entropy of 300 uniformly sampled reference groups of the same size.'),
 ('unique_sources','Distinct sources','count','Number of distinct Pile components represented among the selected neighbours.'),
 ('tfidf_cosine','Mean lexical cosine','number','Mean word TF-IDF cosine similarity between the query and its selected neighbours. The vocabulary and IDF weights were fitted on the reference set only.'),
 ('tfidf_random','Random lexical baseline','number','Mean TF-IDF cosine similarity between this query and all reference excerpts.'),
 ('tfidf_gain','Lexical cosine excess','number','Mean neighbour TF-IDF cosine minus the random lexical baseline.'),
 ('tfidf_source_matched_random','Source-matched lexical baseline','number','Recorded expected TF-IDF cosine under a random reference draw matched to the neighbourhood’s source composition.'),
 ('tfidf_source_matched_gain','Source-matched lexical excess','number','Mean neighbour TF-IDF cosine minus the source-matched lexical baseline.'),
 ('zero_distance_fraction','Zero-distance neighbours','ratio','Fraction of selected neighbour distances equal to zero in the recorded distance calculation.'),
]

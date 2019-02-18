
###########################################################################
# TOP ARTICLE SCHEMA
###########################################################################

# Key Schema definition for top articles
key_schema_str = """
{
    "namespace": "articles",
    "name":"key",
    "type":"record",
    "fields" : [
        {"name" : "url", "type" : "string"}
    ]
}
"""

# Value Schema definition for top articles
value_schema_str = """
{
   "namespace": "articles",
   "name": "value",
   "type": "record",
   "fields" : [
        {"name" : "url", "type" : "string"},
        {"name" : "timestamp", "type" : "string"}
   ]
}
"""


###########################################################################
# PAGEVIEW SCHEMA
###########################################################################

# Key Schema definition for a pageview
key_schema_pv_str = """
{
    "namespace": "pageview",
    "name":"key",
    "type":"record",
    "fields" : [
        {"name" : "pageview_id", "type" : "string"}
    ]
}
"""

# Value Schema definition for a pageview
value_schema_pv_str = """
{
   "namespace": "pageview",
   "name": "value",
   "type": "record",
   "fields" : [
        {"name" : "email", "type" : "string"},
        {"name" : "url", "type" : "string"},
        {"name" : "timestamp", "type" : "string"},
        {"name" : "pageview_id", "type" : "string"}
   ]
}
"""

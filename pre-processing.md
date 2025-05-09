---
jupytext:
  formats: md:myst
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.16.2
kernelspec:
  display_name: Python 3 (ipykernel)
  language: python
  name: python3
---

```{code-cell} ipython3
import ibis
from ibis import _
from minio import Minio
import streamlit as st
from datetime import timedelta
```

```{code-cell} ipython3
# Get signed URLs to access license-controlled layers
key = st.secrets["MINIO_KEY"]
secret = st.secrets["MINIO_SECRET"]
client = Minio("minio.carlboettiger.info", key, secret)

parquet = client.get_presigned_url(
    "GET",
    "shared-tpl",
    "tpl.parquet",
    expires=timedelta(hours=2),
)
```

```{code-cell} ipython3
con = ibis.duckdb.connect()
df = con.read_parquet(parquet)
```

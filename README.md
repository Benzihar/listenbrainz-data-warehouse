# ListenBrainz Data Warehouse

## Overview
A scalable data warehouse solution built using Python and DuckDB to process ListenBrainz listening events.

## Architecture
- Bronze Layer (Raw JSON ingestion)
- Silver Layer (Dimensions & Fact)
- Gold Layer (Analytics)

## Technologies
- Python
- DuckDB
- NDJSON
- Git
- Logging & Audit Framework

## Project Structure

ListenBrainz_Data_Warehouse
        │
 ┌──────┴─────────┐
 │                │
config          docs
 │                │
Extraction      Design Document

        │
       src
 ┌──────┼──────────┬──────────┐
 │      │          │          │
bronze common   database   silver

## Features
- Configuration-driven ETL
- File audit logging
- Object audit logging
- Incremental architecture
- Raw data preservation****

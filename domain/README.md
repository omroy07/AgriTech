# Domain Schemas

This directory defines shared domain contracts used across AgriTech.

## Purpose
- Single source of truth for core entities
- Prevent schema drift across features
- Prepare project for backend & ML integration

## Current Schemas
- Crop
- GrowthStage
- SoilData
- PredictionResult

## Usage
Schemas are **contracts**, not enforcement.
Validation should happen only at system boundaries.
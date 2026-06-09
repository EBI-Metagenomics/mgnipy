#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2024-2025 EMBL - European Bioinformatics Institute
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# original version downloaded from: https://github.com/EBI-Metagenomics/mgnify-pipelines-toolkit/blob/595e5bb04a08d6dab5b04e1f4c3afaca1c6a17b2/mgnify_pipelines_toolkit/constants/tax_ranks.py
# downloaded on: 09-Jun-2026

SILVA_TAX_RANKS = [
    "Superkingdom",
    "Kingdom",
    "Phylum",
    "Class",
    "Order",
    "Family",
    "Genus",
    "Species",
]
PR2_TAX_RANKS = [
    "Domain",
    "Supergroup",
    "Division",
    "Subdivision",
    "Class",
    "Order",
    "Family",
    "Genus",
    "Species",
]
MOTUS_TAX_RANKS = [
    "Kingdom",
    "Phylum",
    "Class",
    "Order",
    "Family",
    "Genus",
    "Species",
]

SHORT_SILVA_TAX_RANKS = ["sk", "k", "p", "c", "o", "f", "g", "s"]
SHORT_MOTUS_TAX_RANKS = ["k", "p", "c", "o", "f", "g", "s"]
SHORT_PR2_TAX_RANKS = ["d", "sg", "dv", "sdv", "c", "o", "f", "g", "s"]

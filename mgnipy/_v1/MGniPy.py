
# following the R package pipeline
import requests
import pandas as pd
import os
import numpy as np
import json
import time
import anndata as ad



class MgnifyClient():
    """
    TODO Class to interact with the Mgnify API.
    """

    def __init__(
            self, 
            base_url='https://www.ebi.ac.uk/metagenomics/api/v1',
            cache_dir='tmp/mgnify_cache'
        ):

        self.base_url = base_url
        self.cache_dir = cache_dir

    # def get_studies(self, page=1, size=100):
    #     """
    #     Get a list of studies from the Mgnify API.
    #     """
    #     url = f"{self.base_url}/studies?page={page}&size={size}"
    #     response = requests.get(url)
    #     response.raise_for_status()
    #     return response.json()



# current mgnifapi
def split_taxa_cols_at(
    at:str='g',
    levels:list = ['sk', 'k', 'p', 'c', 'o', 'f', 'g', 's']
)->list:

    if at not in levels:
        raise ValueError(
            f"level must be one of {levels}, got {at}"
        )

    up_to_index = levels.index(at)
    # return all levels up to and including up_to
    return levels[:up_to_index + 1], levels[up_to_index+1:]


def prep_taxa_file(
        file:str, 
        pipe_ver:int|float, 
        sep:str='\t',
        rel_abund:bool=False,
        fname_in_col:bool=True,
        index_col:str="#SampleID"
    )-> pd.DataFrame:

    # preconditions
    # check file exists
    assert_path(file)
    # check pipe_ver is numeric
    if not isinstance(pipe_ver, (int, float)):
        try:
            pipe_ver = float(pipe_ver)
        except TypeError:
            print(f"pipe_ver must be a numeric value: {pipe_ver}")

    # read the file
    df = pd.read_csv(file, sep=sep, index_col=index_col)
    
    # cleaning needed due to inconsistent vers output files
    if pipe_ver < 4.0:
        # replace Roots
        df.index = df.index.str.replace("Root;k__Archaea;", "sk__Archaea;k__;")
        df.index = df.index.str.replace("Root;k__Bacteria;", "sk__Bacteria;k__;")
        df.index = df.index.str.replace("Root;k__Bacteria", "sk__Bacteria")
        df.index = df.index.str.replace("Root;k__Archaea", "sk__Archaea")
        df.index = df.index.str.replace("Root;k__Mitochondria", "sk__Mitochondria")
        # re.substitute for Archaea
        #df.index = df.index.map(lambda x: re.sub(r"^Archaea", "sk__Archaea", x))

        df.index = df.index.str.rstrip(";s__")
        df.index = df.index.str.rstrip(";g__")
        df.index = df.index.str.rstrip(";f__")
        df.index = df.index.str.rstrip(";o__")
        df.index = df.index.str.rstrip(";c__")
        df.index = df.index.str.rstrip(";p__")
        df.index = df.index.str.rstrip(";k__")

        # more cleaning
        df.index = df.index.str.replace("[", "")
        df.index = df.index.str.replace("]", "")
        df.index = df.index.str.rstrip("s")
        df.index = df.index.str.replace("s;", ";")       
        
        try:
            df = df.drop("Root")
        except:
            print(f"Root not found in {file}, skipping drop.")

        # postcondition check if any Root taxa are still present
        root_count = df.index.str.contains('Root').sum()
        assert root_count == 0, f"Root taxa still present in index: {root_count}"

    # additional cleaning 
    # drop cols with all zeros
    df = df.loc[: , ((df!=0).any())]
    # some duped indices after cleaning, so sum them
    df = df.groupby(level=0).sum()

    if fname_in_col:
        fname = os.path.splitext(os.path.basename(file))[0]
        df.columns = [f"{fname}_{x}" for x in df.columns]

    if rel_abund:
       # normalize each column by its sum
       df = df.transform(lambda x: x / x.sum(), axis=0) 

       # check if all columns sum to 1, check normalization
       assert (round(df.sum(), 2) == 1.00).all(), f"Not all columns sum to 1 in {file}"        

    return df


def merge_taxa_files(
    taxa_files:dict,
    l_suffix:str='_x',
    r_suffix:str='_y'
)->pd.DataFrame:

    # init
    all_abund = pd.DataFrame()

    for i, df in taxa_files.items():
        all_abund = all_abund.join(df, how='outer', lsuffix=l_suffix, rsuffix=r_suffix)

    return all_abund.reset_index()


def taxa_to_dict(taxon:str) -> dict:
    """
    Convert a taxon string to a dictionary.
    """
    pairs = [x.split('__') for x in taxon.split(';')]
    return {x[0]: x[1] if x[1]!='' else np.nan for x in pairs if len(x) == 2}


def convert_taxa_col(
    df:pd.DataFrame, 
    taxa_col:str='#SampleID', 
    drop_col:bool=True,
) -> pd.DataFrame:
    """
    Convert a column of taxa strings to additional taxonomic class columns in df.
    """
    if taxa_col not in df.columns:
        raise ValueError(f"{taxa_col} not found in DataFrame columns.")
    
    # generate dict
    taxa_dicts = df[taxa_col].apply(taxa_to_dict)

    new_df = pd.concat([pd.DataFrame(list(taxa_dicts)), df], axis=1)

    if drop_col:
        new_df = new_df.drop(columns=[taxa_col])

    return new_df


def drop_samples(
    df,
    zeros_thresh:float = 0.95,
    counts_thresh:int|float = 0.5,
)-> pd.DataFrame:
    
    # drop if more zeros than threshold
    df = df.loc[:, (df==0).sum() / df.notna().sum() < zeros_thresh]

    if isinstance(counts_thresh, int):
        # drop if total reads per sample under count threshold
        df = df.loc[:, df.notna().sum() > counts_thresh]
    elif isinstance(counts_thresh, float):
        # drop if total reads per sample under quantile threshold
        counts_thresh = df.notna().sum().quantile(counts_thresh)
        df = df.loc[:, df.notna().sum() > counts_thresh]
    else:
        raise ValueError(f"counts_thresh must be int or float, got {type(counts_thresh)}")
    return df


def agg_taxa_level(
    df: pd.DataFrame, 
    level:str='g', 
    fill_na:None|str='-'
) -> pd.DataFrame:
    """
    Aggregate taxa to a specific taxonomic level.
    """
    
    taxa_levels, rm_levels = split_taxa_cols_at(at=level)

    df_smaller = df.dropna(subset=[level]).copy()
    
    if fill_na is not None:
        for col in taxa_levels:
            df_smaller[col] = df_smaller[col].fillna(fill_na)

    # aggregate to the level
    df_agg = df_smaller.groupby(taxa_levels).sum().reset_index()
    # drop levels after specified level
    df_agg = df_agg.drop(columns=rm_levels)

    return df_agg


def query_sample_metadata(
    fpath:str,
    attributes:dict = {
        'sample-name': 'sample_name',
        'sample-desc': 'sample_description',
        'longitude': 'longitude',
        'latitude': 'latitude',
        'collection-date': 'collection_date',
        'analysis-completed': 'analysis_completed_date',
        'geo-loc-name': 'geolocation',
    }
)-> pd.DataFrame:
    
    with open(fpath, 'r') as file:
        data = json.load(file)

    # to a dataframe
    df = pd.DataFrame(data)

    # pull out the attributes of interest
    for attr_name, new_name in attributes.items():
        df[new_name] = df['attributes'].apply(lambda x: x.get(attr_name, None))

    return df


def clean_df(
    dfs: pd.DataFrame,
    drop_obs_if_na:list = ['longitude', 'latitude', 'collection_date'],
    date_cols:list = ['collection_date', 'analysis_completed_date'],
    drop_cols:list = ['attributes', 'links', 'relationships'],
    lowercase_cols:list = ['biomes', 'biome'],
    date_elements:bool = True,
    dedupe:bool = True
    ):
    """probs temp func"""

    # drop rows with missing values in key columns
    df = dfs.dropna(subset=drop_obs_if_na).copy()

    for attr in date_cols:
        if attr not in df.columns:
            raise ValueError(f"{attr} not found in DataFrame columns.")
        # convert col to datetime
        df[attr] = pd.to_datetime(df[attr])

        if date_elements:
            # pull out date elements
            df[f'{attr}_year'] = df[attr].dt.year
            df[f'{attr}_month'] = df[attr].dt.month
            df[f'{attr}_day'] = df[attr].dt.day

    # drop the original attributes column
    df = df.drop(columns=drop_cols)

    if dedupe:
    # drop duplicates
        df = df.drop_duplicates()

    for col in lowercase_cols:
        if col in df.columns:
            # convert to lowercase
            df[col] = df[col].str.lower()
        else:
            print(f"{col} not found in DataFrame columns, skipping lowercase conversion.")

    return df
    

def add_analysis_metadata(
    sample_df:pd.DataFrame,
    analysis_df:pd.DataFrame,
    on_sample_col:list = ['id'],
    on_analysis_col:list = ['sample_id'],
    how='left',
):
    return sample_df.merge(
        analysis_df, 
        how=how, 
        left_on=on_sample_col,
        right_on=on_analysis_col,
        suffixes=('_sample', '_analysis')
    )


def find_missing_geolocation(
    df:pd.DataFrame,
    longitude_col:str = 'longitude',
    latitude_col:str = 'latitude',
    geolocation_col:str = 'geolocation',
    geolocation_type:str = 'country',
    cache_dir:str = 'tmp/mgnify_cache/find_missing_geoloc.csv',
):
    # check cache first
    if os.path.exists(cache_dir):
        print(f"Cache found at {cache_dir}, loading...")
        find_missing_geoloc = pd.read_csv(cache_dir)

    else:
        # fill in missing geolocation data using geopy
        # init
        geolocator = Nominatim(user_agent="gis_assignment")
        # how many missing geolocation data?
        print(df[geolocation_col].isna().sum(), " missing geolocation data")

        find_missing_geoloc = df[
            df[geolocation_col].isna()
        ][[latitude_col, longitude_col]].drop_duplicates().reset_index(drop=True)
        # init col
        find_missing_geoloc[cache_dir+geolocation_type] = ""

        # o kfor now
        for i in find_missing_geoloc.index:

            lat = find_missing_geoloc.loc[i, latitude_col]
            lon = find_missing_geoloc.loc[i, longitude_col]
            # search
            location = geolocator.reverse((lat, lon), language='en')

            if location is not None:
                located = location.raw['address'].get(geolocation_type)
                find_missing_geoloc.loc[i, cache_dir+geolocation_type] = located

            # verbose
            if i % 10 == 0:
                print(f"Processing index {i}: {located}")

            time.sleep(1)

        # save the results to cache 
        find_missing_geoloc.to_csv(cache_dir, index=False)

    # add back to original df
    # temp column for geolocation
    df_new = pd.merge(
        df, find_missing_geoloc,
        on = [latitude_col, longitude_col],
        how='left',
    ) 
    # replace with located geolocation if na
    df_new[geolocation_col] = np.where(
        df_new[geolocation_col].isna(), 
        df_new[cache_dir+geolocation_type], 
        df_new[geolocation_col]
    )
    # drop temp column
    return df_new.drop(columns=[cache_dir+geolocation_type]) 


def combine_abund_meta(
    df_abund:pd.DataFrame,
    df_meta:pd.DataFrame, 
    level:str='g',
):
    
    """yikes this is not reusable, but it works for now"""
    # pivot abundance table
    df_pivot = df_abund.melt(
        id_vars=split_taxa_cols_at(at=level)[0],
        var_name='fname_run_id',
        value_name='raw_counts'
    )

    df_more_info = df_pivot['fname_run_id'].str.split('_', expand=True, n=2)
    df_more_info.columns = ['study_id', 'erp_id', 'further']
    df_more_info['vers_assemb_id'] = df_more_info['further'].str.split('_v', expand=True)[1]
    df_more_info['pipeline_version'] = df_more_info['vers_assemb_id'].str.split('_', expand=True)[0].astype(float)
    df_more_info['assembly_run_id'] = df_more_info['vers_assemb_id'].str.split('_', expand=True)[1]
    df_more_info = df_more_info.drop(columns=['further', 'vers_assemb_id'])

    df_pivot = pd.concat([df_pivot, df_more_info], axis=1)


    # adding metadata
    df_mgnify = df_meta.merge(df_pivot, on=['study_id', 'assembly_run_id', 'pipeline_version'], how='inner')

    df_mgnify = df_mgnify.drop_duplicates()
    
    return df_mgnify


def pivot_combo_data(
    df:pd.DataFrame, 
    level:str='g',
    value_col:str = 'raw_counts',
    obs_cols:list = [
        'analysis_id', 'sample_id', 'assembly_run_id', 'experiment_type',
        'pipeline_version', 'study_id', 'instrument_platform', 'sample_name',
        'biosample', 'sample_description', 'latitude', 'longitude',
        'geolocation', 'biome_feature', 'biome_material', 'id',
        'collection_date', 'collection_date_year', 'collection_date_month', 'collection_date_day',
        'analysis_completed_date', 'analysis_completed_date_year',
        'analysis_completed_date_month', 'analysis_completed_date_day',
        'fname_run_id', 'erp_id', 'study_name', 'n_samples', 'biomes'
    ]
) -> pd.DataFrame:
    """
    Pivot the combined data to have taxa levels as columns.
    """
    df_piv = pd.pivot(
        df,
        values=value_col,
        columns=split_taxa_cols_at(at=level)[0],
        index=obs_cols,
    )

    # drop all null taxa 
    df_piv = df_piv.loc[:, ~df_piv.isna().all()]

    return df_piv


def multidf_to_adata(
    df: pd.DataFrame,
    outpath:str|None = None,
    obs_prefix:str = 'sample_',
    var_prefix:str = 'genus_'
)->ad.AnnData:
    """
    Convert a multiindex DataFrame to an AnnData object.
    """
    # init
    adata = ad.AnnData(df.values)

    # set indices for obs (rows) and var (columns)
    adata.obs_names = [f"{obs_prefix}{i:d}" for i in range(adata.n_obs)]
    adata.var_names = [f"{var_prefix}{i:d}" for i in range(adata.n_vars)]

    # add multiindex as metadata
    for name in df.index.names:
        adata.obs[name] = pd.Categorical(df.index.get_level_values(name).astype(str))

    for name in df.columns.names:
        adata.var[name] = pd.Categorical(df.columns.get_level_values(name))

    if outpath is not None:
        adata.write(outpath)

    return adata


def agg_other_taxa(
        adata: ad.AnnData, 
        layer: None | str = None,
        keep_top=5, 
        agg_name='Other taxa',
        taxa_map: None | str | dict = None,
        sample_map: None | str | dict = None
    ):
    """sample x taxa df"""

    # indices of top taxa to not agg
    keep = adata.to_df(layer=layer).sum(axis=0).nlargest(keep_top, keep='all').index
    # other taxa to aggregate
    others = adata.to_df(layer=layer).sum(axis=0).nsmallest(len(adata.var)-keep_top, keep='all').index
    # new adata with only top taxa
    adata_keep = adata[:, keep]
    # add sum of other taxa as new obs 
    adata_keep.obs[agg_name] = adata[:, others].X.sum(axis=1)

    df_agg = pd.concat([adata_keep.to_df(layer=layer), adata_keep.obs[[agg_name]]], axis=1)

    if isinstance(taxa_map, dict):
        df_agg = df_agg.rename(columns=taxa_map)
    elif isinstance(taxa_map, str):
        df_agg = df_agg.rename(columns=adata_keep.var[taxa_map].to_dict())
    elif taxa_map is None: 
        pass
    else: 
        raise TypeError(f"taxa_map must be dict, str or None, not {type(taxa_map)}")
    
    if isinstance(sample_map, dict):
        df_agg.index = df_agg.index.map(sample_map)
    elif isinstance(sample_map, str):
        df_agg.index = df_agg.index.map(adata_keep.obs[sample_map].to_dict())
    elif sample_map is None:
        pass
    else:
        raise TypeError(f"sample_map must be dict, str or None, not {type(sample_map)}")
    
    return df_agg

#-----------------------------------------------------------------------------------------------------------------------------------------
# importation des bibliothèques nécessaires 
#-----------------------------------------------------------------------------------------------------------------------------------------
import pandas as pd
import geopandas as gpd
#-----------------------------------------------------------------------------------------------------------------------------------------

#-----------------------------------------------------------------------------------------------------------------------------------------
# Chargement des données rei et balance de la MEL
#-----------------------------------------------------------------------------------------------------------------------------------------
df_rei = pd.read_csv("df_rei_fb_fnb_mel.csv")
df_balance = pd.read_csv("df_balance_mel.csv")
df_code_postal = pd.read_excel("INSEE_CODEPOSTAL.xlsx", sheet_name="Feuil1", dtype={"COM": "string", "DEP": "string" , "N_INSEE": "string"})
#-----------------------------------------------------------------------------------------------------------------------------------------

#-----------------------------------------------------------------------------------------------------------------------------------------
# agregation des données de la balance par ville et calcul du total des dépenses, des recettes et du solde
#-----------------------------------------------------------------------------------------------------------------------------------------
df_balance_agg = df_balance.groupby(['COM','INSEE']).agg({'SD': 'sum', 'SC': 'sum'}).reset_index()
df_balance_agg['solde'] = df_balance_agg['SC'] - df_balance_agg['SD']
#-----------------------------------------------------------------------------------------------------------------------------------------



#-----------------------------------------------------------------------------------------------------------------------------------------
# unification de la balance et du rei par ville pour avoir une vue d'ensemble des finances publiques de la MEL
#-----------------------------------------------------------------------------------------------------------------------------------------
df_finances_publiques_mel = pd.merge(df_balance_agg, df_rei,left_on='COM', right_on='COM', how='left')
df_code_postal["N_INSEE"] = df_code_postal["N_INSEE"].astype(str).str.strip()
df_finances_publiques_mel["COM"] = df_finances_publiques_mel["COM"].astype(str).str.strip()

df_finances_publiques_mel = pd.merge(df_code_postal, df_finances_publiques_mel,left_on='N_INSEE', right_on='COM', how='left')
df_finances_publiques_mel["ville_dep_pays"] = df_finances_publiques_mel["LIBVILLE"] + ", France"
#-----------------------------------------------------------------------------------------------------------------------------------------


    # calcul de la base fiscale, des taux et des produits fiscaux pour les communes de la MEL
df_finances_publiques_mel["BASE_FILCAL_FNB"] = (
    df_finances_publiques_mel["B31TAFNB"].astype(float) *
    df_finances_publiques_mel["B32TAFNB"].astype(float) -
    df_finances_publiques_mel["B33TAFNB"].astype(float) 
)
df_finances_publiques_mel["TAUX_FILCAL_COM_FNB"] = (
    df_finances_publiques_mel["E16NB"].astype(float) / 100
)

df_finances_publiques_mel["BASE_FILCAL_FB"] = (
    (df_finances_publiques_mel["B31"].astype(float) * 
    df_finances_publiques_mel["B32"].astype(float)) -
    df_finances_publiques_mel["B33"].astype(float)
)
df_finances_publiques_mel["TAUX_FILCAL_COM_FB"] = (
    (df_finances_publiques_mel["E31"].astype(float) + df_finances_publiques_mel["E33"].astype(float))/100
)

df_finances_publiques_mel["BASE_FILCAL"] = df_finances_publiques_mel["BASE_FILCAL_FB"] + df_finances_publiques_mel["BASE_FILCAL_FNB"]
df_finances_publiques_mel["REC_FILCAL_COM"] = (
    df_finances_publiques_mel["BASE_FILCAL_FB"] * df_finances_publiques_mel["TAUX_FILCAL_COM_FB"] + 
    df_finances_publiques_mel["BASE_FILCAL_FNB"] * df_finances_publiques_mel["TAUX_FILCAL_COM_FNB"]

)
df_finances_publiques_mel["REC_FILCAL_COM"] = df_finances_publiques_mel["REC_FILCAL_COM"].astype(float)

df_finances_publiques_mel["TAUX_FILCAL_MEL_FB"] = df_finances_publiques_mel["E32"].astype(float) /100
df_finances_publiques_mel["TAUX_FILCAL_MEL_FNB"] = df_finances_publiques_mel["E26NB"].astype(float) /100

df_finances_publiques_mel["REC_FILCAL_MEL"] = (
    df_finances_publiques_mel["BASE_FILCAL_FB"] * df_finances_publiques_mel["TAUX_FILCAL_MEL_FB"]  + 
    df_finances_publiques_mel["BASE_FILCAL_FNB"] * df_finances_publiques_mel["TAUX_FILCAL_MEL_FNB"]

)

#-----------------------------------------------------------------------------------------------------------------------------------------
# generation des fichiers csv des données sur les villes de la MEL et de leurs finances publiques
#-----------------------------------------------------------------------------------------------------------------------------------------
df_finances_mel = df_finances_publiques_mel[[
    "LIB_COM_POSTAL","LIBCOM","LIBVILLE", "DEP",
    "ville_dep_pays", "SD", "SC", "solde", "BASE_FILCAL_FNB", "BASE_FILCAL_FB",
    "TAUX_FILCAL_COM_FB", "TAUX_FILCAL_COM_FNB","BASE_FILCAL", "REC_FILCAL_COM", "TAUX_FILCAL_MEL_FB", "TAUX_FILCAL_MEL_FNB", "REC_FILCAL_MEL",
    "SIREPCI"
]]
df_finances_mel.to_excel("finances_publiques_mel.xlsx", index=False)   
print(df_finances_publiques_mel )
#-----------------------------------------------------------------------------------------------------------------------------------------




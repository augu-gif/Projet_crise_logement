#-----------------------------------------------------------------------------------------------------------------------------------------
# importation des bibliothèques nécessaires 
#-----------------------------------------------------------------------------------------------------------------------------------------
import pandas as pd
#-----------------------------------------------------------------------------------------------------------------------------------------

#-----------------------------------------------------------------------------------------------------------------------------------------
# Chargement des données pour la comptabilité des communes et les REI 
#-----------------------------------------------------------------------------------------------------------------------------------------
data_rei = "REI_2024.csv"
data_balance = "balances-comptables-des-communes-en-2024.csv"
df_rei = pd.read_csv(data_rei, sep=";", encoding="latin-1")
df_balance = pd.read_csv(data_balance, sep=";", encoding="latin-1")
#-----------------------------------------------------------------------------------------------------------------------------------------

#-----------------------------------------------------------------------------------------------------------------------------------------
# dataset des données sur les villes de la France entière et de la MEL
#-----------------------------------------------------------------------------------------------------------------------------------------
df_villes = df_rei[["DEP", "COM", "LIBCOM", "Q03", "LIBREG"]] # france entière
df_mel = df_villes[df_villes["Q03"] == "Métropole Européenne de Lille"] # MEL uniquement
#-----------------------------------------------------------------------------------------------------------------------------------------

#-----------------------------------------------------------------------------------------------------------------------------------------
# df_rei garder que les colonnes qui contient FB et FNB afin de connaitre la puissance fiscal des communes de la MEL et de la France entière
#-----------------------------------------------------------------------------------------------------------------------------------------
id_cols = ["DEP", "COM", "LIBCOM", "Q03", "LIBREG"]
fb_fnb_cols = ["B11TAFNB","B12TAFNB","B13TAFNB","B31TAFNB","B32TAFNB","B33TAFNB","SYNFBDOTVLEI","TSEFBDOTVLEI","WCOMFB","WCOMFNB",
               "GEMAPIFBDOTVLEI","WEPCIFB","WEPCIFNB","WDEPFNB","TASAFBDOTVLEI","WREGFB","WREGFNB"]
df_rei_fb_fnb = df_rei[id_cols + fb_fnb_cols] # france entière
df_rei_fb_fnb_mel = df_rei_fb_fnb[df_rei_fb_fnb["Q03"] == "Métropole Européenne de Lille"] # MEL uniquement
#-----------------------------------------------------------------------------------------------------------------------------------------

#-----------------------------------------------------------------------------------------------------------------------------------------
# df_balance garder que les lignes de la MEL afin de se concentrer sur les données comptables des communes de la MEL
#-----------------------------------------------------------------------------------------------------------------------------------------
df_balance_mel = df_mel.merge(
    df_balance,
    left_on="COM",
    right_on="INSEE",
    how="left"
)
#-----------------------------------------------------------------------------------------------------------------------------------------

#-----------------------------------------------------------------------------------------------------------------------------------------
# df_balance garder que les lignes de compte commençant par 6 ou 7 afin de se concentrer sur les dépenses et les recettes de fonctionnement
#-----------------------------------------------------------------------------------------------------------------------------------------
df_balance_mel["COMPTE"] = df_balance_mel["COMPTE"].astype(str)
df_balance_mel = df_balance_mel[df_balance_mel["COMPTE"].str.startswith("6") | df_balance_mel["COMPTE"].str.startswith("7")]
#-----------------------------------------------------------------------------------------------------------------------------------------

#-----------------------------------------------------------------------------------------------------------------------------------------
# generation des fichiers csv des données sur les villes, les REI et la comptabilité des communes de la MEL
#-----------------------------------------------------------------------------------------------------------------------------------------
df_villes.to_csv("villes_france.csv", index=False)
df_mel.to_csv("villes_mel.csv", index=False)
df_rei_fb_fnb.to_csv("df_rei_fb_fnb.csv", index=False)
df_rei_fb_fnb_mel.to_csv("df_rei_fb_fnb_mel.csv", index=False)
df_balance_mel.to_csv("df_balance_mel.csv", index=False)
#-----------------------------------------------------------------------------------------------------------------------------------------
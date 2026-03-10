#-----------------------------------------------------------------------------------------------------------------------------------------
# importation des bibliothèques nécessaires
#-----------------------------------------------------------------------------------------------------------------------------------------
import pandas as pd

#-----------------------------------------------------------------------------------------------------------------------------------------
# Chargement des données pour la comptabilité des communes et les REI
#-----------------------------------------------------------------------------------------------------------------------------------------

data_rei = "REI_2024.csv"
data_balance = "balances-comptables-des-communes-en-2024.csv"
df_rei = pd.read_csv(data_rei, sep=";", encoding="latin-1")
df_balance = pd.read_csv(data_balance, sep=";", encoding="latin-1")

# generation du fichier csv des données sur les villes
df_villes = df_rei[["DEP", "COM", "LIBCOM", "Q03", "LIBREG"]]
df_villes.head()
df_villes.to_csv("villes_france.csv", index=False)
# generation du fichier csv des données sur les villes de la MEL
df_mel = df_villes[df_villes["Q03"] == "Métropole Européenne de Lille"]
df_mel.to_csv("villes_mel.csv", index=False)

#-----------------------------------------------------------------------------------------------------------------------------------------
# df_rei garder que les colonnes qui contient FB et FNB afin de connaitre la puissance fiscal des communes
#-----------------------------------------------------------------------------------------------------------------------------------------

# Colonnes d'identification à conserver
id_cols = ["DEP", "COM", "LIBCOM", "Q03", "LIBREG"]
# Sélection automatique des colonnes contenant FB ou FNB
fb_fnb_cols = [col for col in df_rei.columns if "FB" in col or "FNB" in col]
# Création des dataset
df_rei_fb_fnb = df_rei[id_cols + fb_fnb_cols]
df_rei_fb_fnb.to_csv("df_rei_fb_fnb.csv", index=False)

df_rei_fb_fnb_mel = df_rei_fb_fnb[df_rei_fb_fnb["Q03"] == "Métropole Européenne de Lille"]
df_rei_fb_fnb_mel.to_csv("df_rei_fb_fnb_mel.csv", index=False)

#-----------------------------------------------------------------------------------------------------------------------------------------
# df_balance garder que les lignes de la MEL
#-----------------------------------------------------------------------------------------------------------------------------------------
df_balance_mel = df_mel.merge(
    df_balance,
    left_on="COM",
    right_on="INSEE",
    how="left"
)
df_balance_mel.to_csv("df_balance_mel.csv", index=False)
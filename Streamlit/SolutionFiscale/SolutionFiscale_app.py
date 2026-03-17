import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as xp
import plotly.graph_objects as go

# Les labels s'affichaient mal donc il a fallu une touche beauté en CSS
st.markdown("""
<style>
[data-testid="stMetricValue"] {
    font-size: 20px;
}

[data-testid="stMetricLabel"] {
    font-size: 22px;
}
            
[data-testid="stHeaderLabel"]{
    font-size: 30px;
}
</style>
""", unsafe_allow_html=True)

# Stockage de la data
@st.cache_data
def load_data():
    # On utilise des chemins relatifs au dossier de l'app
    finance = pd.read_excel("dataset_bi/finances_publiques_mel.xlsx", sheet_name="finances_2024")
    
    finance_prev = pd.read_excel("dataset_bi/finances_mel_5ans.xlsx", sheet_name="finances_mel_5ans")
    
    dvf = pd.read_excel("dataset_bi/DVF_MEL.xlsx", sheet_name="DVF_MEL")
    
    # Pour les CSV, assure-toi qu'ils sont aussi dans le dépôt
    repartition = pd.read_csv("dataset_bi/RepartitionSansAbris_MEL.csv")
    logements_vacants = pd.read_excel("dataset_bi/LogementsVacants_MEL_Exploitable.xlsx",
                                    sheet_name ="LogementsVacants_MEL_Exploitabl")

    return finance, finance_prev, dvf, repartition, logements_vacants

finance, finance_prev, dvf, repartition, logements_vacants = load_data()
# !Stockage de la data

# Prix sur surface bati
@st.cache_data
def compute_constants(dvf):
    return dvf["prix_m2"].mean() * dvf["Surface reelle bati"].mean()

denumerateur = compute_constants(dvf)
# !Prix sur surface bati

# Formatage de chiffres
def format_millions(value):
    return f"{value/1_000_000:.2f} M"

def format_milliards(value):
    return f"{value/1_000_000_000:.2f} Mds"
# !Formatage de chiffres

options_communes = [""] + list(finance["LIBVILLE"].unique())

commune = st.selectbox(
    "Sélectionner une commune",
    options=options_communes,
    index=0, # Sélectionne l'option "" par défaut
    placeholder="Choisissez une ville..."
)

finance_filtered = finance.copy()
finance_prev_filtered = finance_prev.copy()

# Si une commune est sélectionnée, on applique le filtre
# Sinon, on garde les dataframes entiers (donc la somme = total MEL)
if commune != "":
    # Filtre dataset actuel
    finance_filtered = finance[finance["LIBVILLE"] == commune]
    
    mask = finance_prev["2026_LIB_COM_POSTAL"] \
        .str.replace(r"^\d+\s*", "", regex=True) \
        .str.contains(commune, case=False, na=False)

    finance_prev_filtered = finance_prev[mask]
    
    label_entete = commune
else:
    label_entete = "MEL (Total)"

# ------------- SLIDERS --------------
col1, col2 = st.columns(2, border=True)

with col1:
    with st.form("simulation"):
        tx_fiscale = st.slider("Taux fiscal", 0.0, 10.0, step=.1)
        prct_inv_log = st.slider("Pourcentage d'investissement", 0.0, 50.0, step=.5)
        submit = st.form_submit_button("Simuler")

# Gain fiscal + Cout investi 
with col2:

    nouv_val_fiscal = (
        finance_filtered["recettes_fiscales"]
        + finance_filtered["base_FPB"] * tx_fiscale
    )

    gain_fiscal = (
        nouv_val_fiscal
        - finance_filtered["recettes_fiscales"]
    ).sum()

    cout_investi = (
        nouv_val_fiscal * (prct_inv_log/100)
    ).sum()

    st.metric("Gain fiscal en 2026", format_millions(gain_fiscal))
    st.metric("Coût investi en 2026", format_millions(cout_investi))
# ------------- SLIDERS --------------

# Valeurs fiscales en st.metrics
with st.container(horizontal=True):

    recettes_actuelles = finance_filtered["recettes_fiscales"].sum()

    st.metric(
        f"Valeur fiscale actuelle ({commune})",
        format_millions(recettes_actuelles)
    )

    st.metric(
        "Nouvelle valeur fiscale",
        format_millions(recettes_actuelles + gain_fiscal)
    )
# !Valeurs fiscales en st.metrics

# 2. Prévisions sur 5 ans
resultats_nb_logement = []
investissements = []
annees = range(2028, 2032)

# FORCER le choix de la source à chaque itération
if commune != "":
    mask = finance_prev["2026_LIB_COM_POSTAL"] \
        .str.replace(r"^\d+\s*", "", regex=True) \
        .str.contains(commune, case=False, na=False)

    df_travail = finance_prev[mask]
else:
    # Si pas de commune, on prend TOUTE la MEL pour l'année en cours
    df_travail = finance_prev

# Calcul pour 2027 car elle ne doit pas entrer dans la boucle
tx = df_travail["2027_TAUX_FILCAL_COM_FB"]
tx_fis_modif = tx + (tx_fiscale/100)
rec_previous = df_travail["2027_REC_FILCAL_COM"] - (df_travail["2027_BASE_FILCAL_FB"] * tx) + (df_travail["2027_BASE_FILCAL_FB"] * tx_fis_modif)
base_fisc_previous = df_travail["2027_BASE_FILCAL_FB"]

nb_log_previous = rec_previous * (prct_inv_log/100) / denumerateur 
log_2027 = float(nb_log_previous.sum())
resultats_nb_logement.append(log_2027)

rec_2026 = df_travail["2026_REC_FILCAL_COM"] - (df_travail["2026_BASE_FILCAL_FB"] * tx) + (df_travail["2026_BASE_FILCAL_FB"] * tx_fis_modif)
inv_2027 = rec_2026 * (prct_inv_log/100)
investissements.append(inv_2027)
# !Calcul pour 2027 car elle ne doit pas entrer dans la boucle

# Calcul fiscal sur les années projetées
for annee in annees:
    year = str(annee)

    previous_investi = rec_previous * (prct_inv_log/100)
    investissements.append(previous_investi)

    # 0.06 est une part fiscale ajoutée par les investissements
    base_fisc_curr = base_fisc_previous + previous_investi * 0.06 

    rec_curr = rec_previous + (base_fisc_curr - base_fisc_previous) * tx_fis_modif
    
    nb_log = rec_curr * (prct_inv_log/100) / denumerateur    

    resultats_nb_logement.append(nb_log)

    base_fisc_previous = base_fisc_curr
    rec_previous = rec_curr
# !Calcul fiscal sur les années projetées

annees = range(2027,2032)

# Metric investissement
st.header("Investissement par année", width = "stretch")
with st.container(horizontal=True):
    cols = st.columns(5)
    for i, annee in enumerate(annees):

        with cols[i]:
            valeur_raw = investissements[i]
            if isinstance(valeur_raw, (pd.Series, list, np.ndarray)):
                valeur_float = float(pd.Series(valeur_raw).sum())
            else:
                valeur_float = float(valeur_raw)

            
            if valeur_float > 1000000000:
                st.metric(
                    label=str(annee),
                    value=format_milliards(valeur_float))
            else:
                st.metric(
                    label = str(annee),
                    value = format_millions(valeur_float))
# !Metric investissement
                
# Metric logements réhabilités        
st.header("Nombre prévisionnel de logements réhabilités", width ="stretch")
with st.container(horizontal=True):
    cols = st.columns(5)
    for i, annee in enumerate(annees):

        with cols[i]:
            # On récupère la valeur brute de la liste
            valeur_raw = resultats_nb_logement[i]
                
            # Conversion sécurisée : 
            # Si c'est une Series Pandas, on prend la somme (ou .item())
            # Si c'est déjà un nombre, float() suffit
            if hasattr(valeur_raw, 'sum'):
                valeur_float = float(valeur_raw.sum())
            else:
                valeur_float = float(valeur_raw)
            
            # Affichage avec arrondi pour la propreté
            st.metric(label=str(annee), value=int(round(valeur_float)))
# !Metric logements réhabilités        

# Relogement des sans-abris
if commune == "":
    amount_log_vac = logements_vacants["pp_vacant_plus_2ans_24"].sum()

    agglo = {"2027": resultats_nb_logement[0], 
            "2028": resultats_nb_logement[1], 
            "2029": resultats_nb_logement[2], 
            "2030": resultats_nb_logement[3], 
            "2031": resultats_nb_logement[4]}

    # --- Préparation des données ---
    annees_proj = ["2026", "2027", "2028", "2029", "2030", "2031"]
    
    sdf = repartition.iloc[:-1]

    # --- 2. Simulation de la décroissance ---
    besoin_sa_simule = []

    # Initialisation 2026 (Nombre réel sans relogement)
    sa_2026 = sdf["sans_abris_2026"].sum()
    besoin_sa_simule.append(sa_2026)

    sa_actuel = sa_2026

    # Boucle sur les années de simulation (2027 à 2031)
    # Note : resultats_nb_logement contient les valeurs de 2027 à 2031
    for i, annee in enumerate(annees_proj[1:]): # On commence à l'index 1 (2027)
    
        # Récupération du nombre de nouveaux logements financés cette année-là
        # On utilise l'index i car resultats_nb_logement[0] est 2027
        val_constr = resultats_nb_logement[i]
        nb_log_nouveaux = float(val_constr.sum()) if hasattr(val_constr, 'sum') else float(val_constr)
    
        # Calcul de l'impact social : 4 sans-abris logés par logement
        personnes_logees = nb_log_nouveaux
    
        # On soustrait l'impact du stock de l'année précédente
        # (On prend le chiffre projeté de l'année et on applique l'effort cumulé)
        sa_naturel_annee = sa_actuel
        sa_apres_relogement = max(0, sa_naturel_annee - personnes_logees)
    
        besoin_sa_simule.append(sa_apres_relogement)
        sa_actuel = sa_apres_relogement

    # --- 3. Création du graphique Plotly (Line Chart Unique) ---
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=annees_proj, 
        y=besoin_sa_simule,
        name="Nombre de Sans-abris",
        line=dict(color='firebrick', width=4, shape='spline'), # 'spline' pour une courbe lissée
        mode='lines+markers+text',
        text=[int(val) for val in besoin_sa_simule],
        textposition="top center"
    ))

    fig.update_layout(
        title=f"Projection de la résorption du sans-abrisme : 2026-2031 ({label_entete})",
        xaxis_title="Année",
        yaxis_title="Nombre de sans-abris",
        template="plotly_white",
        yaxis=dict(range=[0, max(besoin_sa_simule) * 1.2]), # Pour laisser de la place aux étiquettes
        hovermode="x unified"
    )

    st.plotly_chart(fig, use_container_width=True)
# !Relogement des sans-abris
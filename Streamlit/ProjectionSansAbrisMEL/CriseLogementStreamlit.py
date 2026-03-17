import pandas as pd
import plotly.express as px
from urllib.request import urlopen
import json
import streamlit as st

# Charger le CSV
sdf = pd.read_csv("RepartitionSansAbris_MEL.csv")

# Créer deux colonnes pour l'affichage
col1, col2 = st.columns(2, border= True)

with col1:
    st.header("Prédiction")
    
    # Slider pour l'année
    date_value = st.slider("Année", 2026, 2036)
    
    # Remplir les NaN par 0 pour la colonne de l'année sélectionnée
    sdf[f'sans_abris_{date_value}'] = sdf[f'sans_abris_{date_value}'].fillna(0)
    
    # Afficher le total
    last_value = sdf[f'sans_abris_{date_value}'].iloc[-1]

    if date_value > 2026:
        prev_value = sdf[f'sans_abris_{date_value-1}'].iloc[-1]
        delta = last_value - prev_value
    else:
        delta = None

    st.metric("Sans abris", last_value, delta= delta)

    first_value = sdf[f'sans_abris_2026'].iloc[-1] if date_value > 2026 else None

    if first_value:
        pct = ((last_value - first_value) / first_value) * 100
        st.metric("Évolution depuis 2026 (%)", f"{pct:.1f} %")
    
    with st.expander("Montrer les villes les plus affectées"):
        top5 = (
            sdf.iloc[:-1]  # enlève la ligne Total
            .loc[sdf[f"sans_abris_{date_value}"] > 90]
            .sort_values(by=f"sans_abris_{date_value}", ascending=False)
            .head(5)
            )

        for _, row in top5.iterrows():
            st.metric(
                label=row["LIBVILLE"],
                value=row[f"sans_abris_{date_value}"]
            )

with col2:
    st.header("Carte de Lille")

    # Charger le GeoJSON
    with urlopen("https://data.lillemetropole.fr/data/ogcapi/collections/limite_administrative:mel_comm_orga/items?limit=100") as response:
        communes = json.load(response)

    geojson = {
        "type": "FeatureCollection",
        "features": []
    }

    # Filtrer uniquement les géométries valides
    for f in communes["features"]:
        if f["geometry"] is not None:
            geojson["features"].append(f)

    # Nettoyage des noms de communes pour correspondance GeoJSON
    sdf["LIBVILLE"] = (
        sdf["LIBVILLE"]
        .astype(str)
        .str.strip()               # supprime espaces avant/après
        .str.replace("’", "'", regex=False)  # remplacer apostrophes typographiques
        )

    # Supprimer la ligne 'Total' si présente
    sdf = sdf[sdf["LIBVILLE"].str.lower() != "total"]

    # Remplir les NaN
    sdf[f'sans_abris_{date_value}'] = sdf[f'sans_abris_{date_value}'].fillna(0)

    # Normaliser les codes INSEE
    sdf["LIBVILLE"] = sdf["LIBVILLE"].astype(str).str.strip().str.zfill(5)
    for feature in geojson["features"]:
        feature["properties"]["nom"] = str(feature["properties"]["nom"]).strip().zfill(5)
    
    sdf = sdf.iloc[:-1]

    # Créer la carte
    fig = px.choropleth(
        sdf,
        geojson=geojson,
        locations="LIBVILLE",
        featureidkey="properties.nom",
        color=f'sans_abris_{date_value}',
        projection="mercator",
        title=str(date_value),
        color_continuous_scale= "Reds"
    )

    # Ajuster l'affichage pour toutes les communes
    fig.update_geos(fitbounds="geojson", visible=False)
    # fig.update_layout(margin={"r":0,"t":30,"l":0,"b":0})

    st.plotly_chart(fig, use_container_width=True)

bar = px.bar(
        sdf.iloc[:-1],
        x="LIBVILLE",
        y=f"sans_abris_{date_value}",
        hover_name="LIBVILLE",
        color=f"sans_abris_{date_value}",
        title=f"Nombre de sans-abris par commune ({date_value})",
        color_continuous_scale= "Reds",
    )

bar.update_layout(xaxis_title=None,
                  yaxis_title=None)

st.plotly_chart(bar, use_container_width=True)
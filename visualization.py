# visualization.py
# Author: Fairoz Khan
# Description: Module for creating advanced visualizations using Plotly

import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import logging

def plot_comparison_with_annotations(health_df, economic_df, health_indicator, economic_indicator, country_codes):
    """Plot comparison with annotations for key events for multiple countries."""
    try:
        logger.info("Generating comparison chart with annotations.")
        fig = go.Figure()

        # Define colors for different countries
        colors = px.colors.qualitative.Plotly
        color_map = {country: colors[i % len(colors)] for i, country in enumerate(country_codes)}

        for country in country_codes:
            # Filter health data for the specified country
            health_country_df = health_df[health_df['country_code'] == country]
            economic_country_df = economic_df[economic_df['series_id'] == economic_indicator]

            if health_country_df.empty:
                logger.warning(f"No health data found for country code '{country}'. Skipping.")
                st.warning(f"No health data found for country code '{country}'. Skipping.")
                continue
            if economic_country_df.empty:
                logger.warning(f"No economic data found for series_id '{economic_indicator}' for country '{country}'. Skipping.")
                st.warning(f"No economic data found for series_id '{economic_indicator}' for country '{country}'. Skipping.")
                continue

            # Add health data trace
            fig.add_trace(go.Scatter(
                x=health_country_df['Year'],
                y=health_country_df[health_indicator],
                name=f"{health_indicator} ({country})",
                line=dict(color=color_map[country], dash='solid')
            ))

            # Add economic data trace
            fig.add_trace(go.Scatter(
                x=economic_country_df['Year'],
                y=economic_country_df['value'],
                name=f"{economic_indicator} ({country})",
                line=dict(color=color_map[country], dash='dash'),
                yaxis="y2"
            ))

            # Add annotations (e.g., peak values) for each country
            if not health_country_df[health_indicator].isna().all():
                max_health = health_country_df[health_indicator].max()
                max_health_year = health_country_df.loc[health_country_df[health_indicator].idxmax(), 'Year']
                fig.add_annotation(
                    x=max_health_year,
                    y=max_health,
                    text=f"Peak Health ({country}): {max_health:.2f}",
                    showarrow=True,
                    arrowhead=2,
                    ax=0,
                    ay=-40,
                    font=dict(color=color_map[country])
                )

            if not economic_country_df['value'].isna().all():
                max_econ = economic_country_df['value'].max()
                max_econ_year = economic_country_df.loc[economic_country_df['value'].idxmax(), 'Year']
                fig.add_annotation(
                    x=max_econ_year,
                    y=max_econ,
                    text=f"Peak Economic ({country}): {max_econ:.2f}",
                    showarrow=True,
                    arrowhead=2,
                    ax=0,
                    ay=40,
                    font=dict(color=color_map[country])
                )

        # Update layout for dual y-axes
        fig.update_layout(
            title=f"Comparison of {health_indicator} and {economic_indicator}",
            xaxis=dict(title="Year"),
            yaxis=dict(
                title=f"{health_indicator} (Health)",
                titlefont=dict(color="blue"),
                tickfont=dict(color="blue")
            ),
            yaxis2=dict(
                title=f"{economic_indicator} (Economic)",
                titlefont=dict(color="green"),
                tickfont=dict(color="green"),
                overlaying="y",
                side="right"
            ),
            legend=dict(x=0.5, y=-0.2, orientation="h"),
            margin=dict(l=50, r=50, t=100, b=100)
        )

        st.plotly_chart(fig, use_container_width=True)
        logger.info("Comparison chart generated successfully.")

    except Exception as e:
        logger.error(f"Error generating comparison chart: {e}")
        st.error(f"Error generating comparison chart: {e}")


def plot_cross_country_heatmap(health_df, health_indicator):
    """Plot heatmap to compare health indicators across countries."""
    try:
        logger.info(f"Generating heatmap for '{health_indicator}'.")
        if health_indicator not in health_df.columns:
            logger.error(f"Health indicator '{health_indicator}' not found in the data.")
            st.error(f"Health indicator '{health_indicator}' not found in the data.")
            return

        # Pivot the DataFrame to have countries on one axis and years on the other
        pivot_df = health_df.pivot(index='country_code', columns='Year', values=health_indicator)

        fig = px.imshow(
            pivot_df,
            labels=dict(x="Year", y="Country Code", color=health_indicator),
            x=sorted(pivot_df.columns),
            y=sorted(pivot_df.index),
            color_continuous_scale="Viridis",
            title=f"Heatmap of {health_indicator} Across Countries and Years"
        )

        st.plotly_chart(fig, use_container_width=True)
        logger.info("Heatmap generated successfully.")

    except Exception as e:
        logger.error(f"Error generating heatmap: {e}")
        st.error(f"Error generating heatmap: {e}")


# Configure Logging
logging.basicConfig(
    level=logging.INFO,  # Change to DEBUG for more verbosity
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

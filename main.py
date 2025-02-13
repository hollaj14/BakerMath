import streamlit as st
import pandas as pd
from utils import (
    validate_percentage, 
    calculate_ingredient_weight, 
    format_weight,
    calculate_flour_weight_from_portions
)

def main():
    # Initialize variables that might be used in different calculation paths
    flour_weight = None
    starter_percentage = 20.0
    starter_hydration = 100.0
    portion_count = 4
    portion_weight = 200.0
    starter_water = 0.0

    st.set_page_config(
        page_title="Baker's Percentage Calculator",
        page_icon="🍞",
        layout="wide"
    )

    # Custom CSS remains the same...
    st.markdown("""
        <style>
        .stAlert {
            margin-top: 1rem;
        }
        .ingredient-row {
            margin-bottom: 1rem;
        }
        .result-container {
            padding: 1rem;
            background-color: #f8f9fa;
            border-radius: 0.5rem;
        }
        </style>
    """, unsafe_allow_html=True)

    st.title("🍞 Baker's Percentage Calculator")

    with st.expander("ℹ️ What are Baker's Percentages?"):
        st.markdown("""
            Baker's percentages are a way of expressing ingredient quantities as percentages of the flour weight:
            - Flour is always 100%
            - Other ingredients are expressed as a percentage of the flour weight
            - Total percentages can exceed 100%

            Example: If a recipe calls for 1000g flour and 65% hydration, you need 650g water.
        """)

    # Calculation mode selector
    calc_mode = st.radio(
        "Choose calculation method",
        ["Dough portions", "Flour weight"],
        index=0
    )

    # Main input section
    if calc_mode == "Flour weight":
        flour_weight = st.number_input(
            "Total Flour Weight (g)",
            min_value=0.0,
            value=1000.0,
            step=100.0,
            format="%g"  # Remove trailing zeros
        )
    else:  # Dough portions
        col1, col2 = st.columns(2)
        with col1:
            portion_count = st.number_input(
                "Number of portions",
                min_value=1,
                value=4,
                step=1
            )
        with col2:
            portion_weight = st.number_input(
                "Weight per portion (g)",
                min_value=0.0,
                value=200.0,
                step=50.0,
                format="%g"
            )

    # Hydration settings
    hydration = st.number_input(
        "Desired Hydration Percentage",
        min_value=50.0,
        max_value=100.0,
        value=65.0,
        step=1.0,
        format="%g"
    )

    # Sourdough starter settings
    use_starter = st.checkbox("Include Sourdough Starter", value=False)

    if use_starter:
        col1, col2 = st.columns(2)
        with col1:
            starter_percentage = st.number_input(
                "Starter Percentage (of flour weight)",
                min_value=5.0,
                max_value=50.0,
                value=20.0,
                step=1.0,
                format="%g"
            )
        with col2:
            starter_hydration = st.number_input(
                "Starter Hydration Ratio",
                min_value=50.0,
                max_value=150.0,
                value=100.0,
                step=1.0,
                format="%g"
            )

    # Initialize session state for ingredient rows if not exists
    if 'ingredients' not in st.session_state:
        st.session_state.ingredients = [
            {"name": "Salt", "percentage": 2},
            {"name": "", "percentage": 0},
        ]

    # Calculate base percentages
    salt_yeast_percentage = sum(
        ingredient["percentage"]
        for ingredient in st.session_state.ingredients
        if ingredient["name"] and validate_percentage(ingredient["percentage"])
    )

    # Add hydration to total percentage
    total_percentage = 100 + salt_yeast_percentage + hydration

    # Adjust for starter if used
    if use_starter:
        # Calculate starter contributions only if we have valid inputs
        if starter_percentage is not None and starter_hydration is not None:
            starter_flour = starter_percentage * (100 / (100 + starter_hydration))
            starter_water = starter_percentage * (starter_hydration / (100 + starter_hydration))
            required_additional_water = hydration - starter_water
            total_percentage = 100 + salt_yeast_percentage + required_additional_water

    # Calculate flour weight from portions if needed
    if calc_mode == "Dough portions":
        if portion_count and portion_weight:
            flour_weight = calculate_flour_weight_from_portions(
                portion_count,
                portion_weight,
                total_percentage
            )

    # Rest of the code remains the same...
    st.subheader("Additional Ingredients")

    for idx, ingredient in enumerate(st.session_state.ingredients):
        col1, col2, col3 = st.columns([2, 1, 1])

        with col1:
            name = st.text_input(
                f"Ingredient Name {idx+1}",
                value=ingredient["name"],
                key=f"name_{idx}"
            )

        with col2:
            percentage = st.number_input(
                f"Percentage {idx+1}",
                min_value=0.0,
                max_value=200.0,
                value=float(ingredient["percentage"]),
                step=1.0,
                format="%g",
                key=f"percentage_{idx}"
            )

        st.session_state.ingredients[idx]["name"] = name
        st.session_state.ingredients[idx]["percentage"] = percentage

    # Add/Remove ingredient buttons
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("➕ Add Ingredient") and len(st.session_state.ingredients) < 10:
            st.session_state.ingredients.append({"name": "", "percentage": 0})
            st.rerun()

    with col2:
        if st.button("➖ Remove Ingredient") and len(st.session_state.ingredients) > 1:
            st.session_state.ingredients.pop()
            st.rerun()

    # Calculate and display results
    if flour_weight:
        st.subheader("Results")

        results_data = []

        # Add flour
        results_data.append({
            "Ingredient": "Flour",
            "Percentage": "100%",
            "Weight": format_weight(flour_weight)
        })

        # Add starter if used
        if use_starter:
            starter_weight = calculate_ingredient_weight(flour_weight, starter_percentage)
            if starter_weight is not None:
                starter_flour_weight = starter_weight * (100 / (100 + starter_hydration))
                starter_water_weight = starter_weight * (starter_hydration / (100 + starter_hydration))

                results_data.append({
                    "Ingredient": "Sourdough Starter",
                    "Percentage": f"{starter_percentage}%",
                    "Weight": format_weight(starter_weight)
                })

                # Calculate additional water needed
                required_additional_water = (hydration - starter_water)
                water_weight = calculate_ingredient_weight(flour_weight, required_additional_water)

                results_data.append({
                    "Ingredient": "Additional Water",
                    "Percentage": f"{required_additional_water:.1f}%",
                    "Weight": format_weight(water_weight)
                })
        else:
            # Add water without starter adjustment
            water_weight = calculate_ingredient_weight(flour_weight, hydration)
            results_data.append({
                "Ingredient": "Water",
                "Percentage": f"{hydration}%",
                "Weight": format_weight(water_weight)
            })

        # Add other ingredients
        for ingredient in st.session_state.ingredients:
            if ingredient["name"] and validate_percentage(ingredient["percentage"]):
                weight = calculate_ingredient_weight(flour_weight, ingredient["percentage"])
                results_data.append({
                    "Ingredient": ingredient["name"],
                    "Percentage": f"{ingredient['percentage']}%",
                    "Weight": format_weight(weight)
                })

        # Create results table
        if results_data:
            df = pd.DataFrame(results_data)
            st.dataframe(
                df,
                hide_index=True,
                use_container_width=True
            )

            # Total weight calculation
            total_weight = sum([
                float(weight.replace(',', '').replace(' g', ''))
                for weight in df['Weight']
                if weight != "Invalid input"
            ])

            st.info(f"Total Dough Weight: {format_weight(total_weight)}")

            if calc_mode == "Dough portions":
                actual_portion_weight = total_weight / portion_count
                st.success(
                    f"Each portion will weigh approximately: {format_weight(actual_portion_weight)}"
                )

    # Reset button
    if st.button("🔄 Reset Calculator"):
        st.session_state.ingredients = [
            {"name": "Salt", "percentage": 2},
            {"name": "", "percentage": 0},
        ]
        st.rerun()

    # Footer
    st.markdown("---")
    st.markdown(
        "Made with ❤️ for bakers everywhere | "
        "💡 Tip: Use this calculator to scale your recipes up or down easily!"
    )

if __name__ == "__main__":
    main()

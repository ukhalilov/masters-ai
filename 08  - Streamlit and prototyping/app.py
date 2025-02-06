import streamlit as st
import matplotlib.pyplot as plt

def main():
    # Make the UI full width
    st.set_page_config(layout="wide")

    # Page title
    st.title("Movie & TV Shows Q&A (UI Only)")

    # Top-of-page user input (purely for demonstration, no processing)
    user_input = st.text_input("Enter your question:", value="", key="user_input_box")
    submit_clicked = st.button("Submit")

    # Split layout: left column (Assistant Reply), right column (Sample Chart)
    left_col, right_col = st.columns([2, 2])

    with left_col:
        st.markdown("### Assistant Reply")
        st.write("This is a hardcoded reply. No database or API calls are made here.")

    with right_col:
        st.markdown("### Sample Chart")
        st.write("Below is a static chart with random data (no real DB/LLM).")

        # Create a simple bar chart with hardcoded data
        fig, ax = plt.subplots(figsize=(6, 4))
        categories = ["A", "B", "C", "D", "E"]
        values = [10, 20, 5, 15, 30]
        ax.bar(categories, values)
        ax.set_title("Hardcoded Sample Bar Chart")
        ax.set_ylabel("Value")

        st.pyplot(fig)

    # Optional: If submit is clicked, just show a message (no backend logic)
    if submit_clicked and user_input.strip():
        st.success(f"You entered: {user_input}")
    elif submit_clicked:
        st.warning("Please enter some text before submitting.")


if __name__ == "__main__":
    main()

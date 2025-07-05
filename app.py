import streamlit as st
import pandas as pd
from parser import process_pdf_files
from visualize import visualize_category_spending
from database import create_table, insert_transactions, fetch_all_transactions, clear_transactions

def main():
    st.title("Expense Tracker")

    with st.expander("⚠️ Reset All Data Options"):
        if st.checkbox("I want to reset all stored data"):
            if st.button("🔄 Reset Now"):
                st.session_state.pop('final_df', None)
                clear_transactions()
                st.success("All data has been reset. Please upload new files.")
                return  # stop further execution after reset


    uploaded_files = st.file_uploader(
        "Upload one or more PDF files",
        type=["pdf"],
        accept_multiple_files=True,
    )

    if uploaded_files:
        with st.spinner("Processing PDFs... this may take a moment."):
            final_df, processed_files = process_pdf_files(uploaded_files)

        if final_df.empty:
            st.error("No transactions extracted. Please try different files or check logs.")
            return
        insert_transactions(final_df)  # save to SQLite
    
        st.success(f"Processed {len(processed_files)} PDF files successfully!")
        st.write("Files processed:", ", ".join(processed_files))

        st.session_state['final_df'] = final_df
    else:
        final_df = fetch_all_transactions()
        if final_df.empty:
            st.info("Please upload PDF files to begin.")
            return
        
    st.header("Top 10 Categories by Total Spending (Excluding Payments)")

    # Exclude 'Payments' category for analysis
    exclude_categories = ['payment', 'payments', 'cashback','cashbacks','transfer','transfer credit','payment credit']
    filtered_df = final_df[~final_df['category'].str.lower().isin([cat.lower() for cat in exclude_categories])]

    if filtered_df.empty:
        st.warning("No Expense data available.")
        return

    # Show net amount by file
    st.header("Net Amount by Source File")

    net_by_file = (
        filtered_df.groupby('source_file')['amount']
        .sum()
        .reset_index()
        .rename(columns={'amount': 'net_amount'})
    )

    net_by_file['net_amount'] = net_by_file['net_amount'].round(2)

    st.dataframe(net_by_file)

    st.header("top 10 categories by spend amount")

    # Aggregate top 10 categories by spend amount
    top_categories = (
        filtered_df.groupby('category')['amount']
        .sum()
        #.abs()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
    )

    # Show table with top categories and amounts
    st.dataframe(top_categories)

    # Visualize spending by category
    visualize_category_spending(filtered_df, "category_spending.png")
    st.image("category_spending.png")

    # Show total payments as a summary
    payments_sum = final_df[final_df['category'].str.lower() == 'payment']['amount'].sum()
    st.markdown(f"### Total Payments (last month): {payments_sum:.2f}")

    # Show total payments as a summary
    cashback_sum = final_df[final_df['category'].str.lower() == 'cashback']['amount'].sum()
    st.markdown(f"### Total Cashback (last month): {cashback_sum:.2f}")

    Emisum = final_df[final_df['category'].str.lower() == 'loan payment']['amount'].sum()
    st.markdown(f"### Total EMI (last month): {Emisum:.2f}")

    TFsum = final_df[final_df['category'].str.lower() == 'transfer credit']['amount'].sum()
    st.markdown(f"### Total Transfer Credit (last month): {TFsum:.2f}")


if __name__ == "__main__":
    main()
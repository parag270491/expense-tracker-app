import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

sns.set_theme(style="whitegrid")  # cleaner style

def visualize_category_spending(df, output_chart_path):
    """Generates a polished bar chart of category-wise spending and saves it."""
    if df.empty:
        print("No data to visualize.")
        return

    category_sums = df.groupby('category')['amount'].sum().reset_index()
    category_sums = category_sums.sort_values(by='amount', ascending=False)

    plt.figure(figsize=(14, 8))
    barplot = sns.barplot(data=category_sums, x='category', y='amount', palette="viridis")

    plt.xlabel('Category', fontsize=14)
    plt.ylabel('Sum of Amount', fontsize=14)
    plt.title('Sum of Amount by Category', fontsize=16)
    plt.xticks(rotation=45, ha='right', fontsize=12)
    plt.yticks(fontsize=12)

    # Add value labels on top of bars
    for p in barplot.patches:
        height = p.get_height()
        barplot.annotate(f'{height:,.2f}',
                         (p.get_x() + p.get_width() / 2, height),
                         ha='center', va='bottom',
                         fontsize=11, color='black', xytext=(0, 5),
                         textcoords='offset points')

    plt.tight_layout()
    plt.savefig(output_chart_path)
    plt.close()

    print(f"Category spending chart saved to {output_chart_path}")

def get_top_categories_table(df, top_n=10):
    """Returns a DataFrame of top N categories by total amount spent."""
    if df.empty:
        return pd.DataFrame()

    category_sums = df.groupby('category')['amount'].sum().reset_index()
    category_sums = category_sums.sort_values(by='amount', ascending=False).head(top_n)
    category_sums['amount'] = category_sums['amount'].round(2)
    return category_sums.reset_index(drop=True)
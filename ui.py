import streamlit as st
import pandas as pd
from datetime import datetime
from app import get_company_news

# Toggle authentication on/off
REQUIRE_AUTH = False

def check_password():
    """Returns `True` if the user had the correct password."""
    if not REQUIRE_AUTH:
        return True

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["username"] in st.secrets["passwords"] and st.session_state["password"] == st.secrets["passwords"][st.session_state["username"]]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store password
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show inputs for username + password.
        st.text_input("Username", key="username")
        st.text_input("Password", type="password", key="password")
        st.button("Login", on_click=password_entered)
        return False
    elif not st.session_state["password_correct"]:
        # Password not correct, show input + error.
        st.text_input("Username", key="username")
        st.text_input("Password", type="password", key="password")
        st.button("Login", on_click=password_entered)
        st.error("😕 User not known or password incorrect")
        return False
    else:
        # Password correct.
        return True

def main():
    st.title("Company News Dashboard")
    
    # Fetch data
    with st.spinner('Fetching news data...'):
        news_data = get_company_news()
    
    if not news_data:
        st.error("Failed to fetch news data. Please check your API connection.")
        return
    
    # Convert to DataFrame
    df = pd.DataFrame(news_data)
    
    # Convert timestamp to datetime
    df['date'] = pd.to_datetime(df['date'])
    
    # Sidebar filters
    st.sidebar.header("Filters")
    
    # Create a list of unique companies with their symbols
    company_symbols = sorted(df[['company', 'symbol']].drop_duplicates().values.tolist())
    company_options = ['All'] + [f"{company} ({symbol})" for company, symbol in company_symbols]
    
    selected_company = st.sidebar.selectbox(
        "Search Company",
        company_options,
        format_func=lambda x: x
    )
    
    # Extract symbol from selection for filtering
    selected_symbol = 'All'
    if selected_company != 'All':
        selected_symbol = selected_company.split('(')[-1].strip(')')
    
    # Category filter with checkboxes
    st.sidebar.subheader("Select Categories")
    # Filter out None values and convert to list
    categories = sorted([cat for cat in df['category'].unique() if cat is not None])
    selected_categories = {}
    for category in categories:
        # Initialize all checkboxes as checked (True)
        selected_categories[category] = st.sidebar.checkbox(category, value=True)
    
    # Date range filter
    min_date = df['date'].min().date()
    max_date = df['date'].max().date()
    
    start_date = st.sidebar.date_input("Start Date", min_date, min_value=min_date, max_value=max_date)
    end_date = st.sidebar.date_input("End Date", max_date, min_value=min_date, max_value=max_date)
    
    # Apply filters
    filtered_df = df.copy()
    
    if selected_symbol != 'All':
        filtered_df = filtered_df[filtered_df['symbol'] == selected_symbol]
    
    # Filter by selected categories
    selected_category_list = [category for category, is_selected in selected_categories.items() if is_selected]
    filtered_df = filtered_df[filtered_df['category'].isin(selected_category_list)]
    
    filtered_df = filtered_df[
        (filtered_df['date'].dt.date >= start_date) &
        (filtered_df['date'].dt.date <= end_date)
    ]
    
    # Display results
    st.subheader(f"Showing {len(filtered_df)} news items")
    
    # Display news items
    for _, row in filtered_df.iterrows():
        with st.expander(f"{row['date'].strftime('%Y-%m-%d %H:%M')} - {row['company']} - [{row['category']}] - {row['title']}"):
            st.write(f"**Symbol:** {row['symbol']}")
            st.write(f"**Exchange:** {row['exchange']}")
            if row.get('url'):
                st.write(f"[Read More]({row['url']})")

if __name__ == "__main__":
    if check_password():
        main()
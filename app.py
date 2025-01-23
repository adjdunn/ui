import requests
import streamlit as st

def get_company_news():
    """
    Fetches company news from the API
    Returns: JSON response with news data
    """
    url = "https://company-news-api.onrender.com/news?limit=500"
    headers = {
        "X-API-Key": st.secrets["api_keys"]["news_api"],
        "accept": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching news: {e}")
        return None

# Example usage
if __name__ == "__main__":
    news = get_company_news()
    if news:
        print(len(news))
    else:
        print("Failed to fetch news. Please check your API key and network connection.")


##Curl
#    curl -X GET "https://company-news-api.onrender.com/news?limit=1000" -H "X-API-Key: 57b23eea9ff100deea0b7dd9e6bc6b1b" -H "accept: application/json"